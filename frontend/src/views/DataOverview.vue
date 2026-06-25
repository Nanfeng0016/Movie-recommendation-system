<template>
  <div class="overview">
    <h2 class="page-title">📊 数据概览</h2>

    <!-- 加载态 -->
    <div v-if="loading" class="loading-wrap">
      <div class="spinner"></div>
      <div class="loading-text">正在加载数据…</div>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="alert alert-warning mb-lg">
      ⚠️ {{ error }}
      <button class="btn btn-sm btn-outline" style="margin-left:auto" @click="fetchData">重试</button>
    </div>

    <!-- 数据内容 -->
    <template v-else>
      <!-- 统计卡片 -->
      <div class="stats-grid">
        <div class="stat-card" v-for="stat in stats" :key="stat.label">
          <div class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>

      <!-- 图表行 -->
      <div class="chart-row">
        <div class="card chart-card">
          <div class="card-header">评分分布</div>
          <div class="chart-container"><canvas ref="ratingDistChartRef"></canvas></div>
        </div>
        <div class="card chart-card">
          <div class="card-header">用户评分数量分布</div>
          <div class="chart-container"><canvas ref="userDistChartRef"></canvas></div>
        </div>
        <div class="card chart-card">
          <div class="card-header">电影被评分次数分布</div>
          <div class="chart-container"><canvas ref="movieDistChartRef"></canvas></div>
        </div>
      </div>

      <!-- 类型分布 -->
      <div class="card mb-lg">
        <div class="card-header">电影类型分布</div>
        <div class="chart-container" style="min-height:320px"><canvas ref="genreChartRef"></canvas></div>
      </div>

      <!-- 矩阵信息 -->
      <div class="card mb-lg">
        <div class="card-header">📐 评分矩阵信息</div>
        <div class="matrix-grid">
          <div class="matrix-item" v-for="info in matrixInfo" :key="info.label">
            <span class="matrix-label">{{ info.label }}</span>
            <span class="matrix-value">{{ info.value }}</span>
          </div>
        </div>
      </div>

      <!-- 数据样例 -->
      <div class="sample-grid">
        <div class="card">
          <div class="card-header">评分数据样例</div>
          <div class="table-wrapper">
            <table class="table">
              <thead><tr><th>用户ID</th><th>电影ID</th><th>评分</th><th>时间戳</th></tr></thead>
              <tbody>
                <tr v-for="row in sampleRatings" :key="row.user_id + '-' + row.movie_id">
                  <td>{{ row.user_id }}</td><td>{{ row.movie_id }}</td>
                  <td><span class="badge badge-mint">{{ row.rating }}</span></td>
                  <td class="text-secondary">{{ row.timestamp }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="card">
          <div class="card-header">电影数据样例</div>
          <div class="table-wrapper">
            <table class="table">
              <thead><tr><th>ID</th><th>电影名称</th><th>发行日期</th></tr></thead>
              <tbody>
                <tr v-for="row in sampleMovies" :key="row.movie_id">
                  <td>{{ row.movie_id }}</td><td>{{ row.title || '-' }}</td>
                  <td class="text-secondary">{{ row.release_date || '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import {
  getStats, getRatingDistribution, getUserRatingsDistribution,
  getMovieRatingsDistribution, getGenreDistribution, getMovies,
} from '../api/index.js'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const ratingDistChartRef = ref(null)
const userDistChartRef = ref(null)
const movieDistChartRef = ref(null)
const genreChartRef = ref(null)

const loading = ref(true)
const error = ref(null)
const stats = ref([])
const matrixInfo = ref([])
const sampleRatings = ref([
  { user_id: 1, movie_id: 1, rating: 5, timestamp: 874965758 },
  { user_id: 1, movie_id: 2, rating: 3, timestamp: 887431973 },
])
const sampleMovies = ref([])

let charts = []

// 保存图表数据，等待 DOM 就绪后再绘制
let pendingChartData = null

async function fetchData() {
  loading.value = true
  error.value = null
  pendingChartData = null
  try {
    const [statsRes, rdRes, udRes, mdRes, gdRes, mvRes] = await Promise.all([
      getStats(), getRatingDistribution(), getUserRatingsDistribution(),
      getMovieRatingsDistribution(), getGenreDistribution(), getMovies({ page: 1, page_size: 8 }),
    ])
    const s = statsRes.data
    stats.value = [
      { label: '用户数', value: s.user_count, color: 'var(--primary)' },
      { label: '电影数', value: s.movie_count, color: '#b57a7a' },
      { label: '评分数', value: s.rating_count.toLocaleString(), color: '#b5946a' },
      { label: '稀疏度', value: (s.sparsity * 100).toFixed(2) + '%', color: '#7a7ab5' },
    ]
    matrixInfo.value = [
      { label: '矩阵形状', value: `${s.matrix_shape[0]} 用户 × ${s.matrix_shape[1]} 电影` },
      { label: '有评分条目', value: s.non_zero.toLocaleString() },
      { label: '稀疏度', value: (s.sparsity * 100).toFixed(2) + '%' },
    ]
    sampleMovies.value = mvRes.data.items || []

    // 保存图表数据，等 DOM 渲染后再绘制
    pendingChartData = {
      ratingDist: rdRes.data,
      userCounts: udRes.data.data,
      movieCounts: mdRes.data.data,
      genreData: gdRes.data,
    }
  } catch (err) {
    console.error('数据加载失败:', err)
    if (err.message && err.message.includes('Network Error')) {
      error.value = '无法连接到后端，请确认 FastAPI 是否已启动（http://localhost:8000）'
    } else if (err.response) {
      const status = err.response.status
      const data = err.response.data
      const detail = data?.detail
      const msg = Array.isArray(detail)
        ? detail.map(d => d.msg || JSON.stringify(d)).join('; ')
        : (typeof detail === 'string' ? detail : JSON.stringify(data))
      error.value = `请求失败 (${status})：${msg}`
    } else {
      error.value = `请求错误：${err.message || '未知错误'}`
    }
  } finally {
    // 先切换到数据视图 (loading=false → v-else 渲染 canvas)
    loading.value = false
    // 等待 DOM 更新，canvas ref 就绪后再创建图表
    await nextTick()
    if (pendingChartData) {
      destroyCharts()
      buildCharts(
        pendingChartData.ratingDist,
        pendingChartData.userCounts,
        pendingChartData.movieCounts,
        pendingChartData.genreData,
      )
    }
  }
}

function destroyCharts() {
  charts.forEach(c => c.destroy())
  charts = []
}

function buildCharts(ratingDist, userCounts, movieCounts, genreData) {
  // 1. 评分分布
  if (ratingDistChartRef.value && ratingDist) {
    const c = new Chart(ratingDistChartRef.value, {
      type: 'bar',
      data: {
        labels: ratingDist.labels || [],
        datasets: [{
          label: '频次',
          data: ratingDist.values || [],
          backgroundColor: 'rgba(126, 201, 166, 0.60)',
          borderColor: 'rgba(126, 201, 166, 0.9)',
          borderWidth: 1,
          borderRadius: 4,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: '频次' }, grid: { color: 'rgba(126,201,166,0.06)' } },
          x: { title: { display: true, text: '评分' }, grid: { display: false } },
        },
      },
    })
    charts.push(c)
  }

  // 2. 用户评分数量分布
  if (userDistChartRef.value && userCounts && userCounts.length) {
    const bins = 20, min = Math.min(...userCounts), max = Math.max(...userCounts)
    const w = (max - min) / bins || 1
    const counts = new Array(bins).fill(0)
    userCounts.forEach(v => { counts[Math.min(Math.floor((v - min) / w), bins - 1)]++ })
    const c = new Chart(userDistChartRef.value, {
      type: 'bar',
      data: {
        labels: counts.map((_, i) => `${Math.round(min + i * w)}-${Math.round(min + (i + 1) * w)}`),
        datasets: [{ label: '用户数', data: counts,
          backgroundColor: 'rgba(245, 214, 214, 0.60)',
          borderColor: 'rgba(245, 214, 214, 0.9)',
          borderWidth: 1, borderRadius: 4,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: 'rgba(126,201,166,0.06)' } },
          x: { ticks: { display: false } },
        },
      },
    })
    charts.push(c)
  }

  // 3. 电影被评分次数分布
  if (movieDistChartRef.value && movieCounts && movieCounts.length) {
    const bins = 20, min = Math.min(...movieCounts), max = Math.max(...movieCounts)
    const w = (max - min) / bins || 1
    const counts = new Array(bins).fill(0)
    movieCounts.forEach(v => { counts[Math.min(Math.floor((v - min) / w), bins - 1)]++ })
    const c = new Chart(movieDistChartRef.value, {
      type: 'bar',
      data: {
        labels: counts.map((_, i) => `${Math.round(min + i * w)}-${Math.round(min + (i + 1) * w)}`),
        datasets: [{ label: '电影数', data: counts,
          backgroundColor: 'rgba(245, 225, 196, 0.60)',
          borderColor: 'rgba(245, 225, 196, 0.9)',
          borderWidth: 1, borderRadius: 4,
        }],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, grid: { color: 'rgba(126,201,166,0.06)' } },
          x: { ticks: { display: false } },
        },
      },
    })
    charts.push(c)
  }

  // 4. 类型分布
  if (genreChartRef.value && genreData && genreData.labels) {
    const c = new Chart(genreChartRef.value, {
      type: 'bar',
      data: {
        labels: genreData.labels,
        datasets: [{ label: '电影数量', data: genreData.values || [],
          backgroundColor: 'rgba(214, 216, 245, 0.60)',
          borderColor: 'rgba(214, 216, 245, 0.9)',
          borderWidth: 1, borderRadius: 4,
        }],
      },
      options: {
        indexAxis: 'y',
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { beginAtZero: true, title: { display: true, text: '电影数量' }, grid: { color: 'rgba(126,201,166,0.06)' } },
          y: { grid: { display: false } },
        },
      },
    })
    charts.push(c)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.page-title {
  font-size: 1.4rem;
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--space-lg);
  color: var(--text-primary);
}

.loading-wrap {
  text-align: center;
  padding: var(--space-2xl);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}
@media (max-width: 640px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}

.chart-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}
@media (max-width: 900px) {
  .chart-row { grid-template-columns: 1fr; }
}

.chart-card .card-header {
  font-size: 0.9rem;
}

.matrix-grid {
  display: flex;
  gap: var(--space-xl);
  flex-wrap: wrap;
}
.matrix-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.matrix-label {
  font-size: 0.82rem;
  color: var(--text-secondary);
}
.matrix-value {
  font-size: 1.1rem;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.sample-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
}
@media (max-width: 768px) {
  .sample-grid { grid-template-columns: 1fr; }
}
</style>
