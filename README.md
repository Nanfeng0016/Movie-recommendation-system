<div align="center">

# 🎬 电影协同过滤推荐系统

基于 **MovieLens 100K** 数据集，实现 **Item-Based** 与 **User-Based** 协同过滤算法，  
提供 Vue 3 前端界面 + FastAPI 后端 API 的完整推荐系统。

![Vue 3](https://img.shields.io/badge/Vue-3.3-4FC08D?logo=vue.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.99-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## ✨ 功能特性

| 模块 | 功能 |
|------|------|
| 📊 **数据概览** | 评分分布、用户/电影分布、类型分布、矩阵稀疏度 |
| 🔍 **相似电影** | 基于物品协同过滤的相似电影推荐 |
| 🎯 **个性化推荐** | 输入用户 ID，配置 K 值，生成 TopN 推荐 |
| 📈 **模型评估** | RMSE 计算、命中率评估、方法对比、相似度矩阵热力图 |

## 🧠 算法

- **Item-Based CF**：基于物品余弦相似度，预测用户对未评分电影的评分
- **User-Based CF**：基于用户余弦相似度，利用相似用户的评分偏差进行预测
- **相似度度量**：余弦相似度（Cosine Similarity）
- **评估指标**：RMSE（均方根误差）、Hit Rate（命中率）

## 🏗️ 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3 (Composition API) + Vue Router + Axios + Chart.js |
| **构建工具** | Vite 5 |
| **后端** | FastAPI + Uvicorn |
| **数据处理** | Pandas + NumPy |
| **机器学习** | Scikit-learn (余弦相似度) |
| **数据源** | GroupLens MovieLens 100K (943 用户 × 1682 电影 × 10 万评分) |

## 🎨 设计风格

轻量柔和 **浅新拟态**（Soft Neumorphism）设计：

- 低饱和薄荷绿品牌主色 + 马卡龙辅助色
- 大面积留白 + 极淡弥散阴影
- 超大圆角卡片 + 毛玻璃导航栏
- 纤细无衬线字体 + 浅色模式

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 1. 克隆项目

```bash
git clone https://gitee.com/Nanfeng0016/movie.git
cd movie
```

### 2. 启动后端

```bash
# 创建虚拟环境（可选）
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS / Linux

# 安装依赖
pip install -r backend/requirements.txt

# 启动 FastAPI 服务
uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
```

后端运行在 http://localhost:8000  
API 文档访问 http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端运行在 http://localhost:5173

### 4. 访问

浏览器打开 **http://localhost:5173** 即可使用。

> 数据集 `ml-100k` 已包含在仓库中，如缺失会自动从 GroupLens 官网下载。

## 📁 项目结构

```
movie/
├── app.py                        # Streamlit 版本（备用）
├── start.bat                     # Windows 一键启动
│
├── backend/
│   ├── api.py                    # FastAPI 后端（所有 REST API）
│   └── requirements.txt          # Python 依赖
│
├── frontend/
│   ├── package.json              # Node 依赖
│   ├── vite.config.js            # Vite 配置（API 代理）
│   ├── index.html                # HTML 入口
│   └── src/
│       ├── main.js               # Vue 入口
│       ├── App.vue               # 根组件 + 全局样式（设计系统）
│       ├── router/index.js       # 路由配置
│       ├── api/index.js          # API 封装（Axios）
│       └── views/
│           ├── Home.vue          # 🏠 首页
│           ├── DataOverview.vue  # 📊 数据概览
│           ├── SimilarMovies.vue # 🔍 相似电影
│           ├── Recommendations.vue # 🎯 个性化推荐
│           └── Evaluation.vue    # 📈 模型评估
│
└── ml-100k/                      # MovieLens 100K 数据集
    ├── u.data                    # 评分数据
    ├── u.item                    # 电影信息
    ├── u.genre                   # 类型列表
    └── u.user                    # 用户信息
```

## 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stats` | 数据统计 |
| GET | `/api/movies` | 电影列表（支持搜索/分页） |
| GET | `/api/movies/{id}` | 电影详情 |
| GET | `/api/movies/{id}/similar` | 相似电影 |
| GET | `/api/recommend/{user_id}` | 个性化推荐 |
| GET | `/api/users/{id}/ratings` | 用户评分历史 |
| GET | `/api/ratings/distribution` | 评分分布 |
| GET | `/api/genres/distribution` | 类型分布 |
| GET | `/api/popular-movies` | 热门电影 |
| GET | `/api/similarity-matrix` | 相似度矩阵 |
| POST | `/api/evaluate/rmse` | RMSE 评估 |
| POST | `/api/evaluate/hit-rate` | 命中率评估 |

## 📊 数据说明

**MovieLens 100K** 数据集包含：

| 指标 | 数值 |
|------|------|
| 用户数 | 943 |
| 电影数 | 1,682 |
| 评分记录 | 100,000 |
| 评分范围 | 1–5 |
| 稀疏度 | ~93.7% |

## 📄 License

MIT License

## 🙏 致谢

- [GroupLens Research](https://grouplens.org/) — MovieLens 数据集
- [Vue.js](https://vuejs.org/) — 前端框架
- [FastAPI](https://fastapi.tiangolo.com/) — 后端框架
- [Chart.js](https://www.chartjs.org/) — 图表库
