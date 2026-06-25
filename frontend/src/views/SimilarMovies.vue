<template>
  <div class="similar">
    <h2 class="page-title">🔍 相似电影查找</h2>

    <!-- 控制面板 -->
    <div class="card mb-lg">
      <div class="card-body">
        <div class="control-grid">
          <div class="control-item">
            <label class="form-label">🎬 选择电影</label>
            <select class="form-select" v-model="selectedMovieId">
              <option value="">— 请选择电影 —</option>
              <option v-for="m in movieList" :key="m.movie_id" :value="m.movie_id">{{ m.title }}</option>
            </select>
          </div>
          <div class="control-item">
            <label class="form-label">📌 显示数量：{{ similarCount }}</label>
            <input type="range" class="form-range" v-model.number="similarCount" min="5" max="20" />
          </div>
          <div class="control-item">
            <label class="form-label">🔎 搜索</label>
            <input class="form-control" v-model="searchQuery" placeholder="输入电影名称…" @input="searchMovies" />
          </div>
          <div class="control-item control-btn">
            <button class="btn btn-primary" @click="loadSimilar" :disabled="!selectedMovieId || loading">
              <span v-if="loading" class="spinner" style="width:14px;height:14px;border-width:2px"></span>
              {{ loading ? '查找中…' : '查找相似电影' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 结果 -->
    <div v-if="similarMovies.length > 0" class="card">
      <div class="card-header">
        与「{{ selectedMovieTitle }}」最相似的 {{ similarMovies.length }} 部电影
      </div>
      <div class="card-body">
        <div class="chart-container" style="min-height:340px"><canvas ref="chartRef"></canvas></div>
        <div class="table-wrapper mt-md">
          <table class="table">
            <thead><tr><th>#</th><th>电影名称</th><th>相似度</th></tr></thead>
            <tbody>
              <tr v-for="(m, i) in similarMovies" :key="m.movie_id">
                <td class="text-secondary">{{ i + 1 }}</td>
                <td class="fw-medium">{{ m.title }}</td>
                <td>
                  <div class="sim-bar">
                    <div class="progress" style="flex:1">
                      <div class="progress-bar" :class="simClass(m.similarity)" :style="{ width: m.similarity * 100 + '%' }"></div>
                    </div>
                    <span class="badge" :class="simBadgeClass(m.similarity)">{{ (m.similarity * 100).toFixed(1) }}%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-else-if="searched" class="alert alert-info">💡 请选择一部电影并点击「查找相似电影」</div>

    <!-- 热门电影快速入口 -->
    <div class="card mt-lg">
      <div class="card-header">🔥 热门电影（点击查看相似）</div>
      <div class="table-wrapper">
        <table class="table">
          <thead><tr><th>#</th><th>电影名称</th><th>评分</th><th>人数</th></tr></thead>
          <tbody>
            <tr v-for="(m, i) in popularMovies" :key="m.movie_id" class="clickable-row" @click="quickSelect(m.movie_id)">
              <td>{{ i + 1 }}</td><td class="fw-medium">{{ m.title }}</td>
              <td><span class="badge badge-mint">⭐ {{ m.rating_mean }}</span></td>
              <td class="text-secondary">{{ m.rating_count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { getMovies, getSimilarMovies, getPopularMovies } from '../api/index.js'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

const movieList = ref([])
const selectedMovieId = ref(null)
const selectedMovieTitle = ref('')
const similarCount = ref(10)
const similarMovies = ref([])
const loading = ref(false)
const searched = ref(false)
const searchQuery = ref('')
const popularMovies = ref([])
const chartRef = ref(null)
let chart = null

onMounted(async () => {
  const [mr, pr] = await Promise.all([getMovies({ page: 1, page_size: 200 }), getPopularMovies(10)])
  movieList.value = mr.data.items
  popularMovies.value = pr.data.items
})

function searchMovies() {
  if (!searchQuery.value) { getMovies({ page: 1, page_size: 200 }).then(r => movieList.value = r.data.items); return }
  getMovies({ search: searchQuery.value, page_size: 50 }).then(r => movieList.value = r.data.items).catch(() => {})
}

function quickSelect(id) {
  selectedMovieId.value = id
  loadSimilar()
}

async function loadSimilar() {
  if (!selectedMovieId.value) return
  loading.value = true; searched.value = true
  try {
    const movie = movieList.value.find(m => m.movie_id === selectedMovieId.value)
    selectedMovieTitle.value = movie ? movie.title : ''
    const res = await getSimilarMovies(selectedMovieId.value, similarCount.value)
    similarMovies.value = res.data.items || []
    await nextTick(); renderChart()
  } catch (err) { similarMovies.value = []
  } finally { loading.value = false }
}

function simClass(s) {
  return s >= 0.5 ? 'mint' : s >= 0.3 ? 'pink' : 'orange'
}
function simBadgeClass(s) {
  return s >= 0.5 ? 'badge-green' : s >= 0.3 ? 'badge-pink' : 'badge-orange'
}

function renderChart() {
  if (chart) chart.destroy()
  if (!chartRef.value || !similarMovies.value.length) return
  const rev = [...similarMovies.value].reverse()
  chart = new Chart(chartRef.value, {
    type: 'bar',
    data: {
      labels: rev.map(m => m.title.length > 22 ? m.title.slice(0, 22) + '…' : m.title),
      datasets: [{
        label: '相似度',
        data: rev.map(m => m.similarity),
        backgroundColor: rev.map(m =>
          m.similarity >= 0.5 ? 'rgba(126, 201, 166, 0.60)' :
          m.similarity >= 0.3 ? 'rgba(245, 214, 214, 0.60)' :
          'rgba(245, 225, 196, 0.60)'
        ),
        borderColor: rev.map(m =>
          m.similarity >= 0.5 ? 'rgba(126, 201, 166, 0.9)' :
          m.similarity >= 0.3 ? 'rgba(245, 214, 214, 0.9)' :
          'rgba(245, 225, 196, 0.9)'
        ),
        borderWidth: 1, borderRadius: 4,
      }],
    },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { beginAtZero: true, max: 1, title: { display: true, text: '余弦相似度' }, grid: { color: 'rgba(126,201,166,0.06)' } },
        y: { grid: { display: false } },
      },
    },
  })
}
</script>

<style scoped>
.page-title {
  font-size: 1.4rem;
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--space-lg);
}
.control-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr auto;
  gap: var(--space-md);
  align-items: end;
}
@media (max-width: 768px) {
  .control-grid { grid-template-columns: 1fr; }
}
.control-btn {
  display: flex;
  align-items: end;
}
.control-btn .btn {
  min-width: 140px;
}
.sim-bar {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}
.clickable-row {
  cursor: pointer;
}
.clickable-row:hover td {
  background: var(--bg-hover);
}
</style>
