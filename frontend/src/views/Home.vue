<template>
  <div class="home">
    <!-- Hero 区域 — 浅薄荷绿柔和渐变 -->
    <div class="hero-card">
      <div class="hero-content">
        <div class="hero-avatar">
          <span class="avatar-icon">🎬</span>
        </div>
        <h1 class="hero-title">电影协同过滤推荐系统</h1>
        <p class="hero-desc">
          基于 <strong>MovieLens 100K</strong> 数据集 · 
          <strong>Item-Based</strong> & <strong>User-Based</strong> 协同过滤
        </p>
        <div class="hero-meta">
          <span class="meta-chip">943 位用户</span>
          <span class="meta-chip">1682 部电影</span>
          <span class="meta-chip">100000 条评分</span>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div v-if="!loading" class="stats-grid">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</div>
        <div class="stat-label">{{ stat.label }}</div>
      </div>
    </div>
    <div v-else class="loading-wrap">
      <div class="spinner"></div>
      <div class="loading-text">正在加载数据…</div>
    </div>

    <!-- 功能快捷入口 -->
    <div class="feature-grid">
      <router-link
        v-for="card in featureCards"
        :key="card.title"
        :to="card.to"
        class="feature-card"
        :style="{ '--card-accent': card.accent }"
      >
        <div class="feature-icon-wrap">
          <span class="feature-icon">{{ card.icon }}</span>
        </div>
        <h3 class="feature-title">{{ card.title }}</h3>
        <p class="feature-desc">{{ card.desc }}</p>
        <span class="feature-arrow">→</span>
      </router-link>
    </div>

    <!-- 热门电影 -->
    <div class="card mt-lg" v-if="popularMovies.length > 0">
      <div class="card-header">🔥 热门高分电影</div>
      <div class="table-wrapper">
        <table class="table">
          <thead>
            <tr><th>#</th><th>电影名称</th><th>平均评分</th><th>评分人数</th></tr>
          </thead>
          <tbody>
            <tr v-for="(movie, idx) in popularMovies" :key="movie.movie_id">
              <td class="text-secondary">{{ idx + 1 }}</td>
              <td class="fw-medium">{{ movie.title }}</td>
              <td>
                <span class="badge" :class="ratingBadge(movie.rating_mean)">
                  ⭐ {{ movie.rating_mean }}
                </span>
              </td>
              <td class="text-secondary">{{ movie.rating_count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getStats, getPopularMovies } from '../api/index.js'

const loading = ref(true)
const stats = ref([])
const popularMovies = ref([])

const featureCards = [
  { icon: '📊', title: '数据概览', desc: '查看评分分布、类型分布与矩阵信息', to: '/overview', accent: '#7ec9a6' },
  { icon: '🔍', title: '相似电影', desc: '选择一部电影，查找风格相近的影片', to: '/similar', accent: '#f5d6d6' },
  { icon: '🎯', title: '个性化推荐', desc: '输入用户 ID，获取专属电影推荐', to: '/recommend', accent: '#f5e1c4' },
  { icon: '📈', title: '模型评估', desc: '评估 RMSE、命中率与相似度矩阵', to: '/evaluate', accent: '#d6d8f5' },
]

function ratingBadge(rating) {
  if (rating >= 4.5) return 'badge-green'
  if (rating >= 4.0) return 'badge-mint'
  return 'badge-orange'
}

onMounted(async () => {
  try {
    const [statsRes, popularRes] = await Promise.all([
      getStats(),
      getPopularMovies(10),
    ])
    const s = statsRes.data
    stats.value = [
      { label: '用户数', value: s.user_count, color: 'var(--primary)' },
      { label: '电影数', value: s.movie_count, color: '#b57a7a' },
      { label: '评分数', value: s.rating_count.toLocaleString(), color: '#b5946a' },
      { label: '稀疏度', value: (s.sparsity * 100).toFixed(2) + '%', color: '#7a7ab5' },
    ]
    popularMovies.value = popularRes.data.items
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* --- Hero --- */
.hero-card {
  background: linear-gradient(145deg, #e8f7f0 0%, #f5faf7 100%);
  border-radius: var(--radius-xl);
  padding: var(--space-2xl) var(--space-lg);
  margin-bottom: var(--space-xl);
  border: 1px solid rgba(126, 201, 166, 0.10);
  box-shadow: var(--shadow-sm);
}

.hero-content {
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}

.hero-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--bg-card);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-md);
  box-shadow: 0 4px 16px rgba(126, 201, 166, 0.15);
}
.avatar-icon { font-size: 2rem; }

.hero-title {
  font-size: 1.6rem;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
  line-height: 1.3;
}

.hero-desc {
  font-size: 0.95rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.hero-meta {
  display: flex;
  justify-content: center;
  gap: var(--space-sm);
  margin-top: var(--space-lg);
  flex-wrap: wrap;
}

.meta-chip {
  display: inline-block;
  padding: 5px 14px;
  border-radius: 20px;
  background: var(--bg-card);
  font-size: 0.8rem;
  color: var(--text-secondary);
  box-shadow: var(--shadow-sm);
}

/* --- 统计卡片网格 --- */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
  margin-bottom: var(--space-xl);
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* --- 功能卡片网格 --- */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
  margin-bottom: var(--space-lg);
}

@media (max-width: 768px) {
  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.feature-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  border: 1px solid rgba(126, 201, 166, 0.06);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
  position: relative;
  color: var(--text-primary) !important;
  display: block;
}

.feature-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-3px);
  border-color: rgba(126, 201, 166, 0.15);
}

.feature-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--primary-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-md);
}

.feature-card:nth-child(1) .feature-icon-wrap { background: #e8f7f0; }
.feature-card:nth-child(2) .feature-icon-wrap { background: #fef0f0; }
.feature-card:nth-child(3) .feature-icon-wrap { background: #fef5ea; }
.feature-card:nth-child(4) .feature-icon-wrap { background: #eeeeff; }

.feature-icon { font-size: 1.4rem; }

.feature-title {
  font-size: 1rem;
  font-weight: var(--font-weight-semibold);
  margin-bottom: 6px;
}

.feature-desc {
  font-size: 0.82rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.feature-arrow {
  position: absolute;
  top: var(--space-md);
  right: var(--space-md);
  font-size: 1rem;
  color: var(--text-muted);
  transition: transform 0.2s;
}

.feature-card:hover .feature-arrow {
  transform: translateX(3px);
  color: var(--primary);
}

/* --- Loading --- */
.loading-wrap {
  text-align: center;
  padding: var(--space-2xl);
}
</style>
