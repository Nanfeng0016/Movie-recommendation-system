<template>
  <div class="recommend">
    <h2 class="page-title">🎯 个性化推荐</h2>

    <!-- 控制面板 -->
    <div class="card mb-lg">
      <div class="card-body">
        <div class="control-grid">
          <div class="control-item">
            <label class="form-label">👤 用户 ID</label>
            <input type="number" class="form-control" v-model.number="userId" min="1" max="943" placeholder="1–943" />
          </div>
          <div class="control-item">
            <label class="form-label">📌 TopN：{{ topN }}</label>
            <input type="range" class="form-range" v-model.number="topN" min="5" max="30" />
          </div>
          <div class="control-item">
            <label class="form-label">🔗 K 邻近：{{ kNeighbors }}</label>
            <input type="range" class="form-range" v-model.number="kNeighbors" min="5" max="50" />
          </div>
          <div class="control-item">
            <label class="form-label">⚙️ 方法</label>
            <div class="btn-group" style="display:flex;gap:4px">
              <button class="btn btn-sm" :class="method==='item'?'btn-primary':'btn-outline'" @click="method='item'">Item</button>
              <button class="btn btn-sm" :class="method==='user'?'btn-primary':'btn-outline'" @click="method='user'">User</button>
            </div>
          </div>
          <div class="control-item control-btn">
            <button class="btn btn-primary" @click="loadRecs" :disabled="!userId || loading">
              <span v-if="loading" class="spinner" style="width:14px;height:14px;border-width:2px"></span>
              {{ loading ? '计算中…' : '生成推荐' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 用户评分历史 -->
    <div v-if="userHistory.length > 0" class="card mb-lg">
      <div class="card-header">
        👤 用户 {{ userId }} 的评分历史（共 {{ userHistoryTotal }} 部）
      </div>
      <div class="table-wrapper">
        <table class="table">
          <thead><tr><th>#</th><th>电影名称</th><th>评分</th></tr></thead>
          <tbody>
            <tr v-for="(item, i) in userHistory" :key="item.movie_id">
              <td class="text-secondary">{{ i + 1 }}</td>
              <td class="fw-medium">{{ item.title }}</td>
              <td><span class="badge" :class="ratingBadge(item.rating)">⭐ {{ item.rating }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 推荐结果 -->
    <div v-if="recommendations.length > 0" class="card">
      <div class="card-header">
        🎯 用户 {{ userId }} 的 Top{{ topN }}（{{ methodLabel }} · K={{ kNeighbors }}）
      </div>
      <div class="card-body">
        <div class="chart-container" style="min-height:340px"><canvas ref="chartRef"></canvas></div>
        <div class="table-wrapper mt-md">
          <table class="table">
            <thead><tr><th>#</th><th>电影名称</th><th>预测评分</th></tr></thead>
            <tbody>
              <tr v-for="(item, i) in recommendations" :key="item.movie_id">
                <td class="text-secondary">{{ i + 1 }}</td>
                <td class="fw-medium">{{ item.title }}</td>
                <td>
                  <div class="sim-bar">
                    <div class="progress" style="flex:1">
                      <div class="progress-bar" :class="ratingBar(item.predicted_rating)" :style="{ width: item.predicted_rating / 5 * 100 + '%' }"></div>
                    </div>
                    <span class="badge" :class="ratingBadge(item.predicted_rating)">{{ item.predicted_rating }}</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-else-if="searched && !loading" class="alert alert-warning">
      ⚠️ 未生成推荐，请检查用户 ID 或参数
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { getUserRatings, getRecommendations } from '../api/index.js'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

const userId = ref(1)
const topN = ref(10)
const kNeighbors = ref(20)
const method = ref('item')
const loading = ref(false)
const searched = ref(false)
const recommendations = ref([])
const userHistory = ref([])
const userHistoryTotal = ref(0)
const chartRef = ref(null)
let chart = null

const methodLabel = computed(() => method.value === 'item' ? 'Item-Based' : 'User-Based')

function ratingBadge(r) {
  return r >= 4 ? 'badge-green' : r >= 3 ? 'badge-mint' : 'badge-orange'
}
function ratingBar(r) {
  return r >= 4 ? 'mint' : r >= 3 ? 'pink' : 'orange'
}

async function loadRecs() {
  if (!userId.value) return
  loading.value = true; searched.value = true
  try {
    const [hr, rr] = await Promise.all([
      getUserRatings(userId.value, 15),
      getRecommendations(userId.value, { method: method.value, n: topN.value, k: kNeighbors.value }),
    ])
    userHistory.value = hr.data.items || []
    userHistoryTotal.value = hr.data.total_ratings || 0
    recommendations.value = rr.data.items || []
    await nextTick(); renderChart()
  } catch (err) { recommendations.value = []
  } finally { loading.value = false }
}

function renderChart() {
  if (chart) chart.destroy()
  if (!chartRef.value || !recommendations.value.length) return
  const rev = [...recommendations.value].reverse()
  chart = new Chart(chartRef.value, {
    type: 'bar',
    data: {
      labels: rev.map(m => m.title.length > 22 ? m.title.slice(0, 22) + '…' : m.title),
      datasets: [{
        label: '预测评分',
        data: rev.map(m => m.predicted_rating),
        backgroundColor: rev.map(m =>
          m.predicted_rating >= 4 ? 'rgba(126, 201, 166, 0.60)' :
          m.predicted_rating >= 3 ? 'rgba(245, 214, 214, 0.60)' :
          'rgba(245, 225, 196, 0.60)'
        ),
        borderColor: rev.map(m =>
          m.predicted_rating >= 4 ? 'rgba(126, 201, 166, 0.9)' :
          m.predicted_rating >= 3 ? 'rgba(245, 214, 214, 0.9)' :
          'rgba(245, 225, 196, 0.9)'
        ),
        borderWidth: 1, borderRadius: 4,
      }],
    },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { beginAtZero: true, max: 5, title: { display: true, text: '预测评分' }, grid: { color: 'rgba(126,201,166,0.06)' } },
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
  grid-template-columns: 1fr 1fr 1fr 1fr auto;
  gap: var(--space-md);
  align-items: end;
}
@media (max-width: 900px) {
  .control-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 500px) {
  .control-grid { grid-template-columns: 1fr; }
}
.control-btn .btn {
  min-width: 120px;
}
.sim-bar {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}
</style>
