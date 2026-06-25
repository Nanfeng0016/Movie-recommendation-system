import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import DataOverview from '../views/DataOverview.vue'
import SimilarMovies from '../views/SimilarMovies.vue'
import Recommendations from '../views/Recommendations.vue'
import Evaluation from '../views/Evaluation.vue'

const routes = [
  { path: '/', name: 'Home', component: Home, meta: { title: '首页' } },
  { path: '/overview', name: 'Overview', component: DataOverview, meta: { title: '数据概览' } },
  { path: '/similar', name: 'Similar', component: SimilarMovies, meta: { title: '相似电影' } },
  { path: '/recommend', name: 'Recommend', component: Recommendations, meta: { title: '个性化推荐' } },
  { path: '/evaluate', name: 'Evaluate', component: Evaluation, meta: { title: '模型评估' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
