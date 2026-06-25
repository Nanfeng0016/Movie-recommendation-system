"""
FastAPI 后端 —— 电影协同过滤推荐系统
提供 REST API，供 Vue 前端调用。
"""
import os
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================
# 应用初始化
# ============================================================
app = FastAPI(
    title="电影协同过滤推荐系统 API",
    description="基于 MovieLens 100K 的协同过滤推荐系统后端",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 数据加载
# ============================================================
def download_data():
    """如果数据集不存在，自动下载"""
    data_dir = Path("ml-100k")
    if not data_dir.exists():
        print("正在下载 MovieLens 100K 数据集...")
        url = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
        zip_path = "ml-100k.zip"
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(".")
        os.remove(zip_path)
        print("数据集下载完成！")


def load_data():
    """加载评分、电影、类型数据"""
    download_data()

    # 评分数据
    ratings_cols = ["user_id", "movie_id", "rating", "timestamp"]
    ratings = pd.read_csv(
        "ml-100k/u.data", sep="\t", names=ratings_cols, encoding="latin-1"
    )

    # 类型名称
    genre_names = [
        "unknown", "Action", "Adventure", "Animation", "Children's",
        "Comedy", "Crime", "Documentary", "Drama", "Fantasy",
        "Film-Noir", "Horror", "Musical", "Mystery", "Romance",
        "Sci-Fi", "Thriller", "War", "Western",
    ]

    # 电影数据
    item_cols = (
        ["movie_id", "title", "release_date", "video_release_date", "imdb_url"]
        + genre_names
    )
    movies = pd.read_csv(
        "ml-100k/u.item", sep="|", names=item_cols, encoding="latin-1"
    )
    movies = movies[["movie_id", "title", "release_date"] + genre_names]

    # 类型列表
    genre_df = pd.read_csv(
        "ml-100k/u.genre", sep="|", names=["genre", "index"], encoding="latin-1"
    )
    genre_list = genre_df[genre_df["index"] != ""]["genre"].tolist()

    return ratings, movies, genre_list


def build_matrices(ratings):
    """构建用户-电影评分矩阵"""
    rating_matrix = ratings.pivot_table(
        index="user_id", columns="movie_id", values="rating"
    )
    rating_matrix_filled = rating_matrix.fillna(0)
    return rating_matrix, rating_matrix_filled


def compute_item_similarity(matrix_filled):
    """计算物品相似度矩阵"""
    item_sim = cosine_similarity(matrix_filled.T)
    item_sim_df = pd.DataFrame(
        item_sim,
        index=matrix_filled.columns,
        columns=matrix_filled.columns,
    )
    return item_sim_df


def compute_user_similarity(matrix_filled):
    """计算用户相似度矩阵"""
    user_sim = cosine_similarity(matrix_filled)
    user_sim_df = pd.DataFrame(
        user_sim,
        index=matrix_filled.index,
        columns=matrix_filled.index,
    )
    return user_sim_df


# 全局加载
ratings, movies, genre_list = load_data()
rating_matrix, rating_matrix_filled = build_matrices(ratings)
item_similarity = compute_item_similarity(rating_matrix_filled)
user_similarity = compute_user_similarity(rating_matrix_filled)

# ============================================================
# 推荐核心函数
# ============================================================
def item_based_predict(user_id, movie_id, k=20):
    """Item-based 协同过滤预测"""
    if movie_id not in item_similarity.columns or user_id not in rating_matrix.index:
        return None

    user_ratings = rating_matrix.loc[user_id]
    rated_movies = user_ratings[user_ratings.notna()].index.tolist()
    if not rated_movies:
        return None

    sim_scores = item_similarity[movie_id].drop(movie_id, errors="ignore")
    sim_scores = sim_scores[sim_scores.index.isin(rated_movies)]
    if sim_scores.empty:
        return None

    top_k = sim_scores.nlargest(k)
    top_ratings = user_ratings[top_k.index]

    numerator = np.sum(top_k.values * top_ratings.values)
    denominator = np.sum(np.abs(top_k.values))
    if denominator == 0:
        return None
    return float(numerator / denominator)


def item_based_topn(user_id, n=10, k=20):
    """Item-based TopN 推荐"""
    if user_id not in rating_matrix.index:
        return []

    user_ratings = rating_matrix.loc[user_id]
    rated_movies = set(user_ratings[user_ratings.notna()].index.tolist())
    unrated_movies = [m for m in rating_matrix.columns if m not in rated_movies]

    predictions = []
    for movie_id in unrated_movies:
        pred = item_based_predict(user_id, movie_id, k)
        if pred is not None:
            predictions.append((movie_id, pred))

    predictions.sort(key=lambda x: x[1], reverse=True)
    top_n = predictions[:n]

    result = []
    for movie_id, pred_rating in top_n:
        title = movies[movies["movie_id"] == movie_id]["title"].values[0]
        result.append({
            "movie_id": int(movie_id),
            "title": str(title),
            "predicted_rating": round(pred_rating, 2),
        })
    return result


def user_based_predict(user_id, movie_id, k=20):
    """User-based 协同过滤预测"""
    if user_id not in user_similarity.columns or movie_id not in rating_matrix.columns:
        return None

    user_mean = float(rating_matrix.loc[user_id].mean())

    sim_scores = user_similarity[user_id].drop(user_id, errors="ignore")
    rated_by = rating_matrix[movie_id].dropna()
    sim_scores = sim_scores[sim_scores.index.isin(rated_by.index)]

    if sim_scores.empty:
        return None

    top_k = sim_scores.nlargest(k)

    numerator = 0.0
    denominator = 0.0
    for v_id, sim in top_k.items():
        v_mean = float(rating_matrix.loc[v_id].mean())
        v_rating = rating_matrix.loc[v_id, movie_id]
        numerator += sim * (v_rating - v_mean)
        denominator += abs(sim)

    if denominator == 0:
        return None
    return float(user_mean + numerator / denominator)


def user_based_topn(user_id, n=10, k=20):
    """User-based TopN 推荐"""
    if user_id not in rating_matrix.index:
        return []

    user_ratings = rating_matrix.loc[user_id]
    rated_movies = set(user_ratings[user_ratings.notna()].index.tolist())
    unrated_movies = [m for m in rating_matrix.columns if m not in rated_movies]

    predictions = []
    for movie_id in unrated_movies:
        pred = user_based_predict(user_id, movie_id, k)
        if pred is not None:
            predictions.append((movie_id, pred))

    predictions.sort(key=lambda x: x[1], reverse=True)
    top_n = predictions[:n]

    result = []
    for movie_id, pred_rating in top_n:
        title = movies[movies["movie_id"] == movie_id]["title"].values[0]
        result.append({
            "movie_id": int(movie_id),
            "title": str(title),
            "predicted_rating": round(pred_rating, 2),
        })
    return result


def get_similar_movies(movie_id, n=10):
    """获取相似电影"""
    if movie_id not in item_similarity.columns:
        return []
    sim = item_similarity[movie_id].drop(movie_id, errors="ignore").nlargest(n)
    result = []
    for mid, score in sim.items():
        title = movies[movies["movie_id"] == mid]["title"].values[0]
        result.append({
            "movie_id": int(mid),
            "title": str(title),
            "similarity": round(float(score), 4),
        })
    return result


# ============================================================
# API 路由
# ============================================================

@app.get("/api/stats")
def get_stats():
    """获取数据基本统计信息"""
    user_count = int(ratings["user_id"].nunique())
    movie_count = int(ratings["movie_id"].nunique())
    rating_count = len(ratings)

    # 稀疏度
    total_cells = rating_matrix.shape[0] * rating_matrix.shape[1]
    non_zero = int(rating_matrix.notna().sum().sum())
    sparsity = round(1 - (non_zero / total_cells), 4)

    return {
        "user_count": user_count,
        "movie_count": movie_count,
        "rating_count": rating_count,
        "non_zero": non_zero,
        "sparsity": sparsity,
        "matrix_shape": list(rating_matrix.shape),
    }


@app.get("/api/movies")
def get_movies(
    search: str = "",
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """获取电影列表，支持搜索"""
    if search:
        filtered = movies[movies["title"].str.contains(search, case=False, na=False)]
    else:
        filtered = movies.copy()

    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    page_data = filtered.iloc[start:end]

    items = []
    for _, row in page_data.iterrows():
        items.append({
            "movie_id": int(row["movie_id"]),
            "title": str(row["title"]),
            "release_date": str(row["release_date"]) if pd.notna(row["release_date"]) else "",
        })

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@app.get("/api/movies/ratings-distribution")
def get_movie_ratings_distribution():
    """获取电影被评分次数分布"""
    counts = ratings.groupby("movie_id").size()
    return {
        "min": int(counts.min()),
        "max": int(counts.max()),
        "mean": round(float(counts.mean()), 2),
        "data": [int(x) for x in counts.values.tolist()],
    }


@app.get("/api/movies/{movie_id}")
def get_movie_detail(movie_id: int):
    """获取单部电影详情（含类型）"""
    row = movies[movies["movie_id"] == movie_id]
    if row.empty:
        return {"error": "电影不存在"}, 404

    row = row.iloc[0]
    genres = [g for g in genre_list if row[g] == 1]

    return {
        "movie_id": int(row["movie_id"]),
        "title": str(row["title"]),
        "release_date": str(row["release_date"]) if pd.notna(row["release_date"]) else "",
        "genres": genres,
    }


@app.get("/api/movies/{movie_id}/similar")
def get_similar_movies_api(movie_id: int, n: int = Query(10, ge=1, le=50)):
    """获取相似电影"""
    similar = get_similar_movies(movie_id, n=n)
    if not similar:
        return {"error": "电影不存在或无法计算相似度"}, 404
    return {"items": similar, "movie_id": movie_id, "count": len(similar)}


@app.get("/api/recommend/{user_id}")
def get_recommendations(
    user_id: int,
    method: str = Query("item", regex="^(item|user)$"),
    n: int = Query(10, ge=1, le=50),
    k: int = Query(20, ge=5, le=50),
):
    """获取个性化推荐"""
    if user_id not in rating_matrix.index:
        return {"error": "用户不存在"}, 404

    if method == "item":
        recs = item_based_topn(user_id, n=n, k=k)
    else:
        recs = user_based_topn(user_id, n=n, k=k)

    return {"items": recs, "user_id": user_id, "method": method, "count": len(recs)}


@app.get("/api/users/{user_id}/ratings")
def get_user_ratings(user_id: int, limit: int = Query(15, ge=1, le=100)):
    """获取用户评分历史"""
    if user_id not in rating_matrix.index:
        return {"error": "用户不存在"}, 404

    user_ratings_series = rating_matrix.loc[user_id].dropna().sort_values(ascending=False)
    items = []
    for mid, r in user_ratings_series.head(limit).items():
        title = movies[movies["movie_id"] == mid]["title"].values[0]
        items.append({
            "movie_id": int(mid),
            "title": str(title),
            "rating": float(r),
        })

    return {
        "items": items,
        "user_id": user_id,
        "total_ratings": int(len(user_ratings_series)),
    }


@app.get("/api/genres")
def get_genres():
    """获取所有电影类型"""
    return {"genres": genre_list, "count": len(genre_list)}


@app.get("/api/ratings/distribution")
def get_rating_distribution():
    """获取评分分布数据"""
    dist = ratings["rating"].value_counts().sort_index()
    return {
        "labels": [str(int(x)) for x in dist.index],
        "values": [int(x) for x in dist.values],
    }


@app.get("/api/users/ratings-distribution")
def get_user_ratings_distribution():
    """获取用户评分数量分布"""
    counts = ratings.groupby("user_id").size()
    return {
        "min": int(counts.min()),
        "max": int(counts.max()),
        "mean": round(float(counts.mean()), 2),
        "data": [int(x) for x in counts.values.tolist()],
    }


@app.get("/api/genres/distribution")
def get_genre_distribution():
    """获取各类型电影数量分布"""
    genre_counts = {}
    for g in genre_list:
        genre_counts[g] = int(movies[g].sum())
    sorted_genres = dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True))
    return {
        "labels": list(sorted_genres.keys()),
        "values": list(sorted_genres.values()),
    }


@app.get("/api/popular-movies")
def get_popular_movies(limit: int = Query(10, ge=1, le=30)):
    """获取热门电影（被评分 >= 100 次，按平均评分排序）"""
    popular = (
        ratings.groupby("movie_id")
        .agg(rating_count=("rating", "count"), rating_mean=("rating", "mean"))
        .query("rating_count >= 100")
        .sort_values("rating_mean", ascending=False)
        .head(limit)
        .reset_index()
    )
    popular = popular.merge(movies[["movie_id", "title"]], on="movie_id")
    items = []
    for _, row in popular.iterrows():
        items.append({
            "movie_id": int(row["movie_id"]),
            "title": str(row["title"]),
            "rating_mean": round(float(row["rating_mean"]), 2),
            "rating_count": int(row["rating_count"]),
        })
    return {"items": items}


@app.get("/api/similarity-matrix")
def get_similarity_matrix(
    type: str = Query("item", regex="^(item|user)$"),
    size: int = Query(50, ge=5, le=200),
):
    """获取相似度矩阵子集用于热力图"""
    if type == "item":
        top_ids = item_similarity.columns[:size].tolist()
        subset = item_similarity.loc[top_ids, top_ids]
    else:
        top_ids = user_similarity.columns[:size].tolist()
        subset = user_similarity.loc[top_ids, top_ids]

    return {
        "type": type,
        "size": size,
        "ids": [int(x) for x in top_ids],
        "matrix": [[round(float(v), 4) for v in row] for _, row in subset.iterrows()],
    }


# ============================================================
# 评估 API
# ============================================================

class RmseRequest(BaseModel):
    method: str = "item"
    k: int = 20
    sample_size: int = 2000


class HitRateRequest(BaseModel):
    method: str = "item"
    k: int = 20
    topn: int = 10
    n_users: int = 30


@app.post("/api/evaluate/rmse")
def evaluate_rmse(req: RmseRequest):
    """随机采样评分记录，计算 RMSE"""
    sample_size = min(req.sample_size, len(ratings))
    test_sample = ratings.sample(n=sample_size, random_state=42)

    errors = []
    for _, row in test_sample.iterrows():
        uid, mid, true_r = int(row["user_id"]), int(row["movie_id"]), row["rating"]

        if req.method == "item":
            pred = item_based_predict(uid, mid, req.k)
        else:
            pred = user_based_predict(uid, mid, req.k)

        if pred is not None:
            errors.append((true_r - pred) ** 2)

    if not errors:
        return {"rmse": None, "error": "无法计算 RMSE"}

    rmse = np.sqrt(np.mean(errors))
    return {"rmse": round(float(rmse), 4), "method": req.method, "k": req.k, "samples": len(errors)}


@app.post("/api/evaluate/hit-rate")
def evaluate_hit_rate(req: HitRateRequest):
    """留一法评估命中率"""
    user_counts = ratings.groupby("user_id").size()
    active_users = user_counts[user_counts >= 20].index.tolist()
    sample_users = np.random.choice(
        active_users, size=min(req.n_users, len(active_users)), replace=False
    ).tolist()

    hits = 0
    total = 0
    for uid in sample_users:
        user_ratings = ratings[ratings["user_id"] == uid]
        high_rated = user_ratings[user_ratings["rating"] >= 4]

        if high_rated.empty:
            continue

        hidden = high_rated.sample(1).iloc[0]
        hidden_mid = int(hidden["movie_id"])

        if req.method == "item":
            recs = item_based_topn(uid, n=req.topn, k=req.k)
        else:
            recs = user_based_topn(uid, n=req.topn, k=req.k)

        rec_ids = [r["movie_id"] for r in recs]
        if hidden_mid in rec_ids:
            hits += 1
        total += 1

    hit_rate = hits / total if total > 0 else 0
    return {
        "hit_rate": round(float(hit_rate), 4),
        "hits": hits,
        "total": total,
        "method": req.method,
        "k": req.k,
        "topn": req.topn,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
