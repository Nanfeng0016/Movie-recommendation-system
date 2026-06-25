"""
电影评分协同过滤推荐系统
========================
基于 MovieLens 100K 数据集实现的用户协同过滤 & 物品协同过滤推荐系统。
技术栈：Streamlit + Pandas + NumPy + Scikit-learn + Matplotlib + Seaborn
"""

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
# train_test_split 可用于高级评估，当前通过随机采样实现
import matplotlib.pyplot as plt
import seaborn as sns
import os
import urllib.request
import zipfile
from pathlib import Path

# ============================================================
# 0. 页面配置
# ============================================================
st.set_page_config(
    page_title="电影协同过滤推荐系统",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 1. 数据加载模块
# ============================================================
@st.cache_data
def load_data():
    """读取评分数据和电影信息，返回 ratings_df, movies_df, genre_names"""
    # 自动下载数据集（如果不存在）
    data_dir = Path("ml-100k")
    if not data_dir.exists():
        with st.spinner("正在下载 MovieLens 100K 数据集..."):
            url = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
            zip_path = "ml-100k.zip"
            urllib.request.urlretrieve(url, zip_path)
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(".")
            os.remove(zip_path)
        st.success("数据集下载完成！")

    # 读取评分数据 u.data（tab 分隔）
    ratings_cols = ["user_id", "movie_id", "rating", "timestamp"]
    ratings = pd.read_csv(
        "ml-100k/u.data", sep="\t", names=ratings_cols, encoding="latin-1"
    )

    # 读取电影信息 u.item（pipe 分隔，含 19 种类型标记）
    genre_names = [
        "unknown", "Action", "Adventure", "Animation", "Children's",
        "Comedy", "Crime", "Documentary", "Drama", "Fantasy",
        "Film-Noir", "Horror", "Musical", "Mystery", "Romance",
        "Sci-Fi", "Thriller", "War", "Western",
    ]
    item_cols = (
        ["movie_id", "title", "release_date", "video_release_date", "imdb_url"]
        + genre_names
    )
    movies = pd.read_csv(
        "ml-100k/u.item", sep="|", names=item_cols, encoding="latin-1"
    )
    # 只保留有用字段
    movies = movies[["movie_id", "title", "release_date"] + genre_names]

    # 读取类型名称
    genre_df = pd.read_csv(
        "ml-100k/u.genre", sep="|", names=["genre", "index"], encoding="latin-1"
    )
    genre_list = genre_df[genre_df["index"] != ""]["genre"].tolist()

    return ratings, movies, genre_list


ratings, movies, genre_list = load_data()

# ============================================================
# 2. 矩阵构建模块
# ============================================================
@st.cache_data
def build_matrices(_ratings):
    """构建用户-电影评分矩阵（行=用户，列=电影）"""
    rating_matrix = _ratings.pivot_table(
        index="user_id", columns="movie_id", values="rating"
    )
    # 填充 NaN 为 0（实际应用中可用均值填充，这里用 0 便于相似度计算）
    rating_matrix_filled = rating_matrix.fillna(0)
    return rating_matrix, rating_matrix_filled


rating_matrix, rating_matrix_filled = build_matrices(ratings)

# ============================================================
# 3. 相似度计算模块
# ============================================================
@st.cache_data
def compute_item_similarity(matrix_filled):
    """计算物品（电影）相似度矩阵 —— 余弦相似度"""
    # matrix_filled: users × movies，转置后变成 movies × users
    item_sim = cosine_similarity(matrix_filled.T)
    item_sim_df = pd.DataFrame(
        item_sim,
        index=matrix_filled.columns,
        columns=matrix_filled.columns,
    )
    return item_sim_df


@st.cache_data
def compute_user_similarity(matrix_filled):
    """计算用户相似度矩阵 —— 余弦相似度"""
    user_sim = cosine_similarity(matrix_filled)
    user_sim_df = pd.DataFrame(
        user_sim,
        index=matrix_filled.index,
        columns=matrix_filled.index,
    )
    return user_sim_df


item_similarity = compute_item_similarity(rating_matrix_filled)
user_similarity = compute_user_similarity(rating_matrix_filled)

# ============================================================
# 4. 推荐预测模块
# ============================================================

# --- 4a. 基于物品的协同过滤 ---
def item_based_predict(user_id, movie_id, k=20):
    """
    预测用户对某电影的评分（基于物品协同过滤）
    公式：pred = Σ(sim(i,j) * rating(u,j)) / Σ|sim(i,j)|
    其中 j 是用户 u 评分过的、与电影 i 最相似的 k 个电影
    """
    if movie_id not in item_similarity.columns:
        return np.nan
    if user_id not in rating_matrix.index:
        return np.nan

    user_ratings = rating_matrix.loc[user_id]  # Series
    rated_movies = user_ratings[user_ratings.notna()].index.tolist()

    if not rated_movies:
        return np.nan

    # 获取与目标电影相似的电影
    sim_scores = item_similarity[movie_id].drop(movie_id, errors="ignore")

    # 只看用户评分过的电影
    sim_scores = sim_scores[sim_scores.index.isin(rated_movies)]

    if sim_scores.empty:
        return np.nan

    # 取最相似的 k 个
    top_k = sim_scores.nlargest(k)
    top_ratings = user_ratings[top_k.index]

    # 加权平均预测
    numerator = np.sum(top_k.values * top_ratings.values)
    denominator = np.sum(np.abs(top_k.values))
    if denominator == 0:
        return np.nan
    return numerator / denominator


def item_based_topn(user_id, n=10, k=20):
    """为用户生成 TopN 推荐（基于物品协同过滤），排除已评分电影"""
    if user_id not in rating_matrix.index:
        return pd.DataFrame()

    user_ratings = rating_matrix.loc[user_id]
    rated_movies = user_ratings[user_ratings.notna()].index.tolist()
    unrated_movies = [m for m in rating_matrix.columns if m not in rated_movies]

    predictions = []
    for movie_id in unrated_movies:
        pred = item_based_predict(user_id, movie_id, k)
        if not np.isnan(pred):
            predictions.append((movie_id, pred))

    predictions.sort(key=lambda x: x[1], reverse=True)
    top_n = predictions[:n]

    result = []
    for movie_id, pred_rating in top_n:
        title = movies[movies["movie_id"] == movie_id]["title"].values[0]
        result.append(
            {"movie_id": movie_id, "title": title, "predicted_rating": round(pred_rating, 2)}
        )
    return pd.DataFrame(result)


# --- 4b. 基于用户的协同过滤 ---
def user_based_predict(user_id, movie_id, k=20):
    """
    预测用户对某电影的评分（基于用户协同过滤）
    公式：pred = mean(u) + Σ(sim(u,v) * (rating(v,i) - mean(v))) / Σ|sim(u,v)|
    其中 v 是与用户 u 最相似的 k 个用户
    """
    if user_id not in user_similarity.columns:
        return np.nan
    if movie_id not in rating_matrix.columns:
        return np.nan

    # 目标用户的平均评分
    user_mean = rating_matrix.loc[user_id].mean()

    # 获取与目标用户相似的用户（排除自身）
    sim_scores = user_similarity[user_id].drop(user_id, errors="ignore")

    # 只看评分过该电影的用户
    rated_by = rating_matrix[movie_id].dropna()
    sim_scores = sim_scores[sim_scores.index.isin(rated_by.index)]

    if sim_scores.empty:
        return np.nan

    # 取最相似的 k 个
    top_k = sim_scores.nlargest(k)

    numerator = 0.0
    denominator = 0.0
    for v, sim in top_k.items():
        v_mean = rating_matrix.loc[v].mean()
        v_rating = rating_matrix.loc[v, movie_id]
        numerator += sim * (v_rating - v_mean)
        denominator += abs(sim)

    if denominator == 0:
        return np.nan
    return user_mean + numerator / denominator


def user_based_topn(user_id, n=10, k=20):
    """为用户生成 TopN 推荐（基于用户协同过滤），排除已评分电影"""
    if user_id not in rating_matrix.index:
        return pd.DataFrame()

    user_ratings = rating_matrix.loc[user_id]
    rated_movies = user_ratings[user_ratings.notna()].index.tolist()
    unrated_movies = [m for m in rating_matrix.columns if m not in rated_movies]

    predictions = []
    for movie_id in unrated_movies:
        pred = user_based_predict(user_id, movie_id, k)
        if not np.isnan(pred):
            predictions.append((movie_id, pred))

    predictions.sort(key=lambda x: x[1], reverse=True)
    top_n = predictions[:n]

    result = []
    for movie_id, pred_rating in top_n:
        title = movies[movies["movie_id"] == movie_id]["title"].values[0]
        result.append(
            {"movie_id": movie_id, "title": title, "predicted_rating": round(pred_rating, 2)}
        )
    return pd.DataFrame(result)


# --- 4c. 查找相似电影 ---
def get_similar_movies(movie_id, n=10):
    """返回与指定电影最相似的 n 部电影"""
    if movie_id not in item_similarity.columns:
        return pd.DataFrame()
    sim = item_similarity[movie_id].drop(movie_id, errors="ignore").nlargest(n)
    result = []
    for mid, score in sim.items():
        title = movies[movies["movie_id"] == mid]["title"].values[0]
        result.append(
            {"movie_id": mid, "title": title, "similarity": round(score, 4)}
        )
    return pd.DataFrame(result)


# ============================================================
# 5. 模型评估模块
# ============================================================
def evaluate_rmse(method="item", k=20, sample_size=5000):
    """
    随机抽取评分作为测试集，计算 RMSE
    method: "item" | "user"
    """
    # 随机采样评分记录
    if len(ratings) > sample_size:
        test_sample = ratings.sample(n=sample_size, random_state=42)
    else:
        test_sample = ratings.copy()

    errors = []
    total = len(test_sample)
    progress_bar = st.progress(0, text="评估中...")

    for i, (_, row) in enumerate(test_sample.iterrows()):
        uid, mid, true_r = int(row["user_id"]), int(row["movie_id"]), row["rating"]

        if method == "item":
            pred = item_based_predict(uid, mid, k)
        else:
            pred = user_based_predict(uid, mid, k)

        if not np.isnan(pred):
            errors.append((true_r - pred) ** 2)

        if (i + 1) % 500 == 0:
            progress_bar.progress(
                (i + 1) / total, text=f"评估中... {i+1}/{total}"
            )

    progress_bar.empty()
    if not errors:
        return np.nan
    return np.sqrt(np.mean(errors))


def evaluate_hit_rate(method="item", k=20, topn=10, n_users=50):
    """
    计算命中率：对每位用户，隐藏一部评分 ≥4 的电影，
    若推荐列表命中该电影则记为命中。
    """
    # 选取活跃用户（评分 ≥ 20 部电影）
    user_counts = ratings.groupby("user_id").size()
    active_users = user_counts[user_counts >= 20].index.tolist()
    sample_users = np.random.choice(active_users, size=min(n_users, len(active_users)), replace=False)

    hits = 0
    total = 0
    progress_bar = st.progress(0, text="命中率评估中...")

    for i, uid in enumerate(sample_users):
        uid = int(uid)
        user_ratings = ratings[ratings["user_id"] == uid]
        high_rated = user_ratings[user_ratings["rating"] >= 4]

        if high_rated.empty:
            continue

        # 随机隐藏一部高分电影（命中率评估的留一法）
        hidden = high_rated.sample(1).iloc[0]
        hidden_mid = int(hidden["movie_id"])

        # 注：为简化演示，直接使用全局矩阵推荐；
        # 严格评估应排除隐藏评分后重新计算相似度矩阵
        if method == "item":
            recs = item_based_topn(uid, n=topn, k=k)
        else:
            recs = user_based_topn(uid, n=topn, k=k)

        if not recs.empty and hidden_mid in recs["movie_id"].values:
            hits += 1
        total += 1

        progress_bar.progress((i + 1) / len(sample_users), text=f"命中率评估... {i+1}/{len(sample_users)}")

    progress_bar.empty()
    if total == 0:
        return 0
    return hits / total


# ============================================================
# 6. Streamlit 界面
# ============================================================
st.title("🎬 电影协同过滤推荐系统")
st.markdown(
    """
基于 **MovieLens 100K** 数据集（943 用户 × 1682 电影 × 100000 评分），
实现**基于物品（Item-Based）**和**基于用户（User-Based）**的协同过滤推荐。
"""
)

# ---- 侧边栏 ----
st.sidebar.header("⚙️ 参数设置")
k_neighbors = st.sidebar.slider("邻近数量 K", min_value=5, max_value=50, value=20, step=5)
top_n = st.sidebar.slider("TopN 推荐数量", min_value=5, max_value=30, value=10, step=5)
cf_method = st.sidebar.radio("协同过滤方法", ["Item-Based（物品）", "User-Based（用户）"])

# ---- 主界面：Tab 页 ----
tab_overview, tab_similar, tab_recommend, tab_evaluate = st.tabs(
    ["📊 数据概览", "🔍 相似电影查找", "🎯 个性化推荐", "📈 模型评估"]
)

# ========================
# Tab 1: 数据概览
# ========================
with tab_overview:
    st.header("数据概览")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("用户数", ratings["user_id"].nunique())
    with col2:
        st.metric("电影数", ratings["movie_id"].nunique())
    with col3:
        st.metric("评分数", len(ratings))

    st.subheader("评分分布")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    # 评分分布直方图
    axes[0].hist(ratings["rating"], bins=5, edgecolor="black", color="steelblue", alpha=0.8)
    axes[0].set_title("评分分布直方图")
    axes[0].set_xlabel("评分")
    axes[0].set_ylabel("频次")

    # 每位用户评分数量分布
    user_rating_counts = ratings.groupby("user_id").size()
    axes[1].hist(user_rating_counts, bins=30, edgecolor="black", color="darkorange", alpha=0.8)
    axes[1].set_title("用户评分数量分布")
    axes[1].set_xlabel("评分数量")
    axes[1].set_ylabel("用户数")

    # 每部电影被评分次数分布
    movie_rating_counts = ratings.groupby("movie_id").size()
    axes[2].hist(movie_rating_counts, bins=30, edgecolor="black", color="seagreen", alpha=0.8)
    axes[2].set_title("电影被评分次数分布")
    axes[2].set_xlabel("被评分次数")
    axes[2].set_ylabel("电影数")

    plt.tight_layout()
    st.pyplot(fig)

    # 评分矩阵稀疏度
    st.subheader("评分矩阵信息")
    total_cells = rating_matrix.shape[0] * rating_matrix.shape[1]
    non_zero = rating_matrix.notna().sum().sum()
    sparsity = 1 - (non_zero / total_cells)
    st.write(f"- 矩阵形状：**{rating_matrix.shape[0]}** 用户 × **{rating_matrix.shape[1]}** 电影")
    st.write(f"- 有评分条目：**{non_zero}**")
    st.write(f"- 稀疏度：**{sparsity:.2%}**")

    # 电影类型分布
    st.subheader("电影类型分布")
    genre_counts = {}
    for g in genre_list:
        genre_counts[g] = movies[g].sum()
    genre_series = pd.Series(genre_counts).sort_values(ascending=False)
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    genre_series.plot(kind="bar", ax=ax2, color="coral", edgecolor="black", alpha=0.8)
    ax2.set_title("各类型电影数量")
    ax2.set_xlabel("类型")
    ax2.set_ylabel("电影数量")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig2)

    # 评分数据样例
    st.subheader("评分数据样例")
    st.dataframe(ratings.head(10), use_container_width=True)

    st.subheader("电影数据样例")
    st.dataframe(movies[["movie_id", "title", "release_date"]].head(10), use_container_width=True)

# ========================
# Tab 2: 相似电影查找
# ========================
with tab_similar:
    st.header("相似电影查找（基于物品协同过滤）")

    # 电影选择
    movie_titles = movies["title"].tolist()
    selected_title = st.selectbox(
        "选择一部电影，查找与其最相似的电影：",
        movie_titles,
        index=movie_titles.index("Toy Story (1995)"),
    )
    selected_movie_id = movies[movies["title"] == selected_title]["movie_id"].values[0]

    num_similar = st.slider("显示相似电影数量", 5, 20, 10, key="sim_count")

    if st.button("查找相似电影", type="primary"):
        similar_movies = get_similar_movies(selected_movie_id, n=num_similar)
        if not similar_movies.empty:
            st.subheader(f"与「{selected_title}」最相似的 {num_similar} 部电影：")

            # 可视化
            fig3, ax3 = plt.subplots(figsize=(10, 5))
            colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(similar_movies)))
            bars = ax3.barh(
                similar_movies["title"][::-1],
                similar_movies["similarity"][::-1],
                color=colors[::-1],
                edgecolor="black",
            )
            ax3.set_xlabel("余弦相似度")
            ax3.set_title(f"与「{selected_title}」最相似的电影")
            plt.tight_layout()
            st.pyplot(fig3)

            st.dataframe(similar_movies, use_container_width=True)
        else:
            st.warning("未找到相似电影，请检查数据。")

    # 热门电影推荐入口
    st.divider()
    st.subheader("热门电影快速查看")
    popular_movies = (
        ratings.groupby("movie_id")
        .agg(rating_count=("rating", "count"), rating_mean=("rating", "mean"))
        .query("rating_count >= 100")
        .sort_values("rating_mean", ascending=False)
        .head(10)
        .reset_index()
    )
    popular_movies = popular_movies.merge(movies[["movie_id", "title"]], on="movie_id")
    popular_movies = popular_movies[["movie_id", "title", "rating_mean", "rating_count"]]
    popular_movies.columns = ["电影ID", "电影名称", "平均评分", "评分人数"]
    popular_movies["平均评分"] = popular_movies["平均评分"].round(2)
    st.dataframe(popular_movies, use_container_width=True)

# ========================
# Tab 3: 个性化推荐
# ========================
with tab_recommend:
    st.header("个性化推荐")

    user_id = st.number_input("输入用户 ID（1-943）：", min_value=1, max_value=943, value=1)

    # 显示该用户的评分历史（高分电影）
    if user_id in rating_matrix.index:
        user_ratings_series = rating_matrix.loc[user_id].dropna().sort_values(ascending=False)
        st.subheader(f"用户 {user_id} 的评分历史（共 {len(user_ratings_series)} 部）")
        user_history = []
        for mid, r in user_ratings_series.head(15).items():
            title = movies[movies["movie_id"] == mid]["title"].values[0]
            user_history.append({"movie_id": int(mid), "title": title, "rating": r})
        st.dataframe(pd.DataFrame(user_history), use_container_width=True)

    if st.button("生成推荐", type="primary"):
        with st.spinner("正在计算推荐..."):
            if "Item" in cf_method:
                recs = item_based_topn(user_id, n=top_n, k=k_neighbors)
            else:
                recs = user_based_topn(user_id, n=top_n, k=k_neighbors)

        if not recs.empty:
            st.subheader(f"为用户 {user_id} 的 Top{top_n} 推荐（{cf_method}，K={k_neighbors}）")
            st.dataframe(
                recs.style.background_gradient(subset=["predicted_rating"], cmap="RdYlGn"),
                use_container_width=True,
            )

            # 可视化
            fig4, ax4 = plt.subplots(figsize=(10, 5))
            colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(recs)))
            ax4.barh(
                recs["title"][::-1],
                recs["predicted_rating"][::-1],
                color=colors[::-1],
                edgecolor="black",
            )
            ax4.set_xlabel("预测评分")
            ax4.set_title(f"用户 {user_id} 的 Top{top_n} 推荐（{cf_method}）")
            ax4.axvline(x=3.0, color="red", linestyle="--", alpha=0.5, label="及格线 (3.0)")
            ax4.legend()
            plt.tight_layout()
            st.pyplot(fig4)
        else:
            st.warning("未生成推荐，请检查用户 ID 或参数。")

# ========================
# Tab 4: 模型评估
# ========================
with tab_evaluate:
    st.header("模型评估")

    eval_col1, eval_col2 = st.columns(2)

    with eval_col1:
        st.subheader("RMSE 评估")
        eval_method = st.radio(
            "选择评估方法", ["item", "user"], format_func=lambda m: "Item-Based" if m == "item" else "User-Based",
            key="eval_method",
        )
        eval_sample = st.slider("评估样本量", 500, 5000, 2000, 500, key="eval_sample")
        eval_k = st.slider("K 值", 5, 50, k_neighbors, 5, key="eval_k")

        if st.button("计算 RMSE", type="primary"):
            with st.spinner(f"正在计算 RMSE（{eval_method.upper()}，K={eval_k}，{eval_sample} 条样本）..."):
                rmse = evaluate_rmse(method=eval_method, k=eval_k, sample_size=eval_sample)
            if not np.isnan(rmse):
                st.metric("RMSE", f"{rmse:.4f}")
                st.caption("RMSE 越低越好，表示预测评分与真实评分的偏差越小。")
            else:
                st.error("计算失败，请调整参数。")

    with eval_col2:
        st.subheader("命中率评估")
        hr_method = st.radio(
            "选择评估方法", ["item", "user"], format_func=lambda m: "Item-Based" if m == "item" else "User-Based",
            key="hr_method",
        )
        hr_users = st.slider("评估用户数", 10, 100, 30, 10, key="hr_users")
        hr_topn = st.slider("TopN", 5, 20, top_n, 5, key="hr_topn")

        if st.button("计算命中率", type="primary"):
            with st.spinner(f"正在计算命中率（{hr_method.upper()}，{hr_users} 位用户，Top{hr_topn}）..."):
                hit_rate = evaluate_hit_rate(
                    method=hr_method, k=k_neighbors, topn=hr_topn, n_users=hr_users
                )
            st.metric("命中率 (Hit Rate)", f"{hit_rate:.2%}")
            st.caption("命中率越高越好，表示推荐列表中命中用户真正喜欢电影的比例。")

    # 相似度矩阵可视化
    st.divider()
    st.subheader("相似度矩阵可视化")

    vis_option = st.radio(
        "可视化对象",
        ["物品相似度（前50部电影）", "用户相似度（前50位用户）"],
        horizontal=True,
    )

    if st.button("生成热力图", type="primary"):
        with st.spinner("生成热力图中..."):
            if "物品" in vis_option:
                top_ids = item_similarity.columns[:50]
                sim_subset = item_similarity.loc[top_ids, top_ids]
                title_label = "物品相似度热力图（前50部电影）"
            else:
                top_ids = user_similarity.columns[:50]
                sim_subset = user_similarity.loc[top_ids, top_ids]
                title_label = "用户相似度热力图（前50位用户）"

            fig5, ax5 = plt.subplots(figsize=(10, 8))
            sns.heatmap(sim_subset, cmap="coolwarm", center=0, ax=ax5,
                        xticklabels=False, yticklabels=False)
            ax5.set_title(title_label)
            ax5.set_xlabel("ID")
            ax5.set_ylabel("ID")
            plt.tight_layout()
            st.pyplot(fig5)

# ============================================================
# 7. 底部信息
# ============================================================
st.divider()
st.caption(
    "电影评分协同过滤推荐系统 | "
    "数据来源：GroupLens MovieLens 100K | "
    "算法：Item-Based & User-Based Collaborative Filtering | "
    "相似度：余弦相似度（Cosine Similarity）"
)
