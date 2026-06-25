<template>
  <div id="app-root">
    <!-- 顶部导航栏 -->
    <header class="app-header">
      <div class="header-inner">
        <router-link class="logo" to="/">
          <span class="logo-icon">🎬</span>
          <span class="logo-text">电影推荐</span>
        </router-link>
        <nav class="nav-links">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            class="nav-item"
            :class="{ active: $route.path === item.path }"
            :to="item.path"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-label">{{ item.label }}</span>
          </router-link>
        </nav>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="main-content">
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>

    <!-- 底部 -->
    <footer class="app-footer">
      <span>🎬 电影协同过滤推荐系统</span>
      <span class="footer-divider">·</span>
      <span>数据来源 GroupLens</span>
      <span class="footer-divider">·</span>
      <span>Item-Based & User-Based CF</span>
    </footer>
  </div>
</template>

<script setup>
const navItems = [
  { path: '/', icon: '🏠', label: '首页' },
  { path: '/overview', icon: '📊', label: '数据' },
  { path: '/similar', icon: '🔍', label: '相似' },
  { path: '/recommend', icon: '🎯', label: '推荐' },
  { path: '/evaluate', icon: '📈', label: '评估' },
]
</script>

<style>
/* ============================================================
   设计系统：轻量柔和浅新拟态
   主色：低饱和薄荷绿 + 马卡龙辅色
   ============================================================ */

/* --- 设计 Token --- */
:root {
  /* 主色 */
  --primary: #7ec9a6;
  --primary-light: #b8e6d0;
  --primary-bg: #e8f7f0;
  --primary-hover: #6abb92;

  /* 辅助色 — 马卡龙 */
  --accent-pink: #f5d6d6;
  --accent-orange: #f5e1c4;
  --accent-lavender: #d6d8f5;
  --accent-blue: #c4e0f5;
  --accent-yellow: #f5edc4;

  /* 背景 */
  --bg-page: #f8faf9;
  --bg-card: #ffffff;
  --bg-soft: #f0f5f2;
  --bg-hover: #f5faf7;

  /* 文字 */
  --text-primary: #3d4f4a;
  --text-secondary: #7a8f88;
  --text-muted: #aab7b0;
  --text-on-primary: #ffffff;

  /* 阴影 — 极淡弥散 */
  --shadow-sm: 0 2px 8px rgba(126, 201, 166, 0.08);
  --shadow-md: 0 4px 20px rgba(126, 201, 166, 0.10);
  --shadow-lg: 0 8px 32px rgba(126, 201, 166, 0.12);

  /* 圆角 */
  --radius-sm: 10px;
  --radius-md: 16px;
  --radius-lg: 24px;
  --radius-xl: 32px;

  /* 字体 */
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial,
    sans-serif;
  --font-weight-light: 300;
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;

  /* 间距 */
  --space-xs: 6px;
  --space-sm: 10px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
}

/* --- 全局重置 --- */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-family);
  font-weight: var(--font-weight-regular);
  color: var(--text-primary);
  background-color: var(--bg-page);
  line-height: 1.6;
  min-height: 100vh;
}

a {
  color: var(--primary);
  text-decoration: none;
  transition: color 0.2s;
}
a:hover {
  color: var(--primary-hover);
}

/* --- 应用根容器 --- */
#app-root {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* ============================================================
   导航栏
   ============================================================ */
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(126, 201, 166, 0.12);
  padding: 0 var(--space-lg);
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  color: var(--text-primary) !important;
}
.logo-icon {
  font-size: 1.5rem;
}
.logo-text {
  font-size: 1.15rem;
  font-weight: var(--font-weight-semibold);
  letter-spacing: 0.5px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary) !important;
  transition: all 0.25s ease;
  position: relative;
}

.nav-item:hover {
  background: var(--primary-bg);
  color: var(--primary) !important;
}

.nav-item.active {
  background: var(--primary-bg);
  color: var(--primary) !important;
}

.nav-item.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background: var(--primary);
  border-radius: 2px;
}

.nav-icon {
  font-size: 1.1rem;
}
.nav-label {
  font-size: 0.88rem;
}

/* ============================================================
   主内容
   ============================================================ */
.main-content {
  flex: 1;
  padding: var(--space-xl) var(--space-lg);
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

/* ============================================================
   通用卡片
   ============================================================ */
.card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--space-lg);
  transition: box-shadow 0.3s ease, transform 0.3s ease;
  border: 1px solid rgba(126, 201, 166, 0.06);
}

.card:hover {
  box-shadow: var(--shadow-md);
}

.card-header {
  font-size: 1.05rem;
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  padding-bottom: var(--space-md);
  margin-bottom: var(--space-md);
  border-bottom: 1px solid rgba(126, 201, 166, 0.10);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

/* ============================================================
   统计卡片
   ============================================================ */
.stat-card {
  background: linear-gradient(135deg, var(--primary-bg), #ffffff);
  border: 1px solid rgba(126, 201, 166, 0.12);
  border-radius: var(--radius-lg);
  padding: var(--space-lg) var(--space-md);
  text-align: center;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.3s ease;
}
.stat-card:hover {
  box-shadow: var(--shadow-md);
}

.stat-value {
  font-size: 2.2rem;
  font-weight: var(--font-weight-semibold);
  color: var(--primary);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 4px;
  font-weight: var(--font-weight-medium);
}

/* ============================================================
   按钮
   ============================================================ */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 24px;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  font-weight: var(--font-weight-medium);
  font-family: var(--font-family);
  cursor: pointer;
  border: none;
  transition: all 0.25s ease;
  line-height: 1.4;
}

.btn-primary {
  background: var(--primary);
  color: var(--text-on-primary);
  box-shadow: 0 2px 8px rgba(126, 201, 166, 0.25);
}
.btn-primary:hover {
  background: var(--primary-hover);
  box-shadow: 0 4px 16px rgba(126, 201, 166, 0.35);
  transform: translateY(-1px);
}
.btn-primary:active {
  transform: translateY(0);
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-outline {
  background: transparent;
  color: var(--primary);
  border: 1.5px solid var(--primary-light);
}
.btn-outline:hover {
  background: var(--primary-bg);
  border-color: var(--primary);
}

.btn-sm {
  padding: 6px 14px;
  font-size: 0.82rem;
}

/* ============================================================
   表单控件
   ============================================================ */
.form-label {
  display: block;
  font-size: 0.85rem;
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.form-control {
  width: 100%;
  padding: 10px 14px;
  border: 1.5px solid rgba(126, 201, 166, 0.15);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  font-family: var(--font-family);
  color: var(--text-primary);
  background: var(--bg-card);
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
  outline: none;
}

.form-control:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(126, 201, 166, 0.12);
}

.form-control::placeholder {
  color: var(--text-muted);
}

.form-select {
  width: 100%;
  padding: 10px 14px;
  border: 1.5px solid rgba(126, 201, 166, 0.15);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  font-family: var(--font-family);
  color: var(--text-primary);
  background: var(--bg-card);
  cursor: pointer;
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%237a8f88' stroke-width='1.5' fill='none'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 32px;
}
.form-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(126, 201, 166, 0.12);
}

.form-range {
  width: 100%;
  height: 6px;
  background: var(--primary-bg);
  border-radius: 3px;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}
.form-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  box-shadow: 0 1px 4px rgba(126, 201, 166, 0.3);
}
.form-range::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  border: none;
}

/* ============================================================
   进度条 / Badge
   ============================================================ */
.progress {
  width: 100%;
  height: 8px;
  background: var(--bg-soft);
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.4s ease;
}

.progress-bar.mint { background: var(--primary); }
.progress-bar.pink { background: var(--accent-pink); }
.progress-bar.orange { background: var(--accent-orange); }
.progress-bar.lavender { background: var(--accent-lavender); }

.badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: var(--font-weight-medium);
  line-height: 1.4;
}

.badge-mint { background: var(--primary-bg); color: var(--primary); }
.badge-pink { background: var(--accent-pink); color: #b57a7a; }
.badge-orange { background: var(--accent-orange); color: #b5946a; }
.badge-green { background: #d4edda; color: #2d6a4f; }
.badge-blue { background: var(--accent-blue); color: #5a7a94; }

/* ============================================================
   表格
   ============================================================ */
.table-wrapper {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.table th {
  padding: 12px 14px;
  font-size: 0.82rem;
  font-weight: var(--font-weight-semibold);
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  text-align: left;
  border-bottom: 1px solid rgba(126, 201, 166, 0.08);
}

.table td {
  padding: 12px 14px;
  font-size: 0.9rem;
  color: var(--text-primary);
  border-bottom: 1px solid rgba(126, 201, 166, 0.06);
}

.table tr:last-child td {
  border-bottom: none;
}

.table tr:hover td {
  background: var(--bg-hover);
}

/* ============================================================
   图表容器
   ============================================================ */
.chart-container {
  position: relative;
  width: 100%;
  min-height: 300px;
}

/* ============================================================
   警告 / 信息条
   ============================================================ */
.alert {
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.alert-info {
  background: var(--primary-bg);
  color: var(--primary);
}

.alert-warning {
  background: #fef8e8;
  color: #b5946a;
}

/* ============================================================
   Loading
   ============================================================ */
.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2.5px solid var(--primary-bg);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-top: var(--space-sm);
}

/* ============================================================
   底部
   ============================================================ */
.app-footer {
  text-align: center;
  padding: var(--space-md) var(--space-lg);
  font-size: 0.82rem;
  color: var(--text-muted);
  border-top: 1px solid rgba(126, 201, 166, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.footer-divider {
  color: var(--text-muted);
  opacity: 0.5;
}

/* ============================================================
   响应式
   ============================================================ */
@media (max-width: 768px) {
  .nav-label {
    display: none;
  }
  .nav-item {
    padding: 8px 10px;
  }
  .header-inner {
    height: 52px;
  }
  .main-content {
    padding: var(--space-md);
  }
  .stat-value {
    font-size: 1.6rem;
  }
}

/* ============================================================
   工具类
   ============================================================ */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.gap-xs { gap: var(--space-xs); }
.gap-sm { gap: var(--space-sm); }
.gap-md { gap: var(--space-md); }
.gap-lg { gap: var(--space-lg); }
.text-center { text-align: center; }
.text-secondary { color: var(--text-secondary); }
.text-muted { color: var(--text-muted); }
.fw-medium { font-weight: var(--font-weight-medium); }
.mt-sm { margin-top: var(--space-sm); }
.mt-md { margin-top: var(--space-md); }
.mt-lg { margin-top: var(--space-lg); }
.mb-sm { margin-bottom: var(--space-sm); }
.mb-md { margin-bottom: var(--space-md); }
.mb-lg { margin-bottom: var(--space-lg); }
.p-md { padding: var(--space-md); }
.p-lg { padding: var(--space-lg); }
</style>
