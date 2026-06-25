import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// ---- 统计信息 ----
export function getStats() {
  return api.get('/stats')
}

// ---- 电影 ----
export function getMovies(params = {}) {
  return api.get('/movies', { params })
}

export function getMovieDetail(movieId) {
  return api.get(`/movies/${movieId}`)
}

export function getSimilarMovies(movieId, n = 10) {
  return api.get(`/movies/${movieId}/similar`, { params: { n } })
}

export function getMovieRatingsDistribution() {
  return api.get('/movies/ratings-distribution')
}

export function getPopularMovies(limit = 10) {
  return api.get('/popular-movies', { params: { limit } })
}

// ---- 用户 ----
export function getUserRatings(userId, limit = 15) {
  return api.get(`/users/${userId}/ratings`, { params: { limit } })
}

export function getUserRatingsDistribution() {
  return api.get('/users/ratings-distribution')
}

// ---- 推荐 ----
export function getRecommendations(userId, { method = 'item', n = 10, k = 20 } = {}) {
  return api.get(`/recommend/${userId}`, { params: { method, n, k } })
}

// ---- 类型 ----
export function getGenres() {
  return api.get('/genres')
}

export function getGenreDistribution() {
  return api.get('/genres/distribution')
}

// ---- 评分分布 ----
export function getRatingDistribution() {
  return api.get('/ratings/distribution')
}

// ---- 相似度矩阵 ----
export function getSimilarityMatrix(type = 'item', size = 50) {
  return api.get('/similarity-matrix', { params: { type, size } })
}

export default api
