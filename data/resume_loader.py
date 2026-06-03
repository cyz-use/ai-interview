"""简历数据加载器 —— 从 Kaggle Resume Dataset 下载真实简历数据集。

数据集：snehaanbhawal/resume-dataset
- 2484 份真实英文简历
- 24 个岗位类别
- 每条包含纯文本简历 (Resume_str)
- 首次运行会自动下载（约 62MB），后续使用缓存
"""

import random

import kagglehub
import pandas as pd

# ——— 加载 & 缓存 ———

_df_cache: pd.DataFrame | None = None


def _load_df() -> pd.DataFrame:
    """加载 Kaggle 简历数据集（带缓存）。"""
    global _df_cache
    if _df_cache is not None:
        return _df_cache

    path = kagglehub.dataset_download("snehaanbhawal/resume-dataset")
    csv_path = f"{path}/Resume/Resume.csv"
    _df_cache = pd.read_csv(csv_path)
    return _df_cache


# ——— 类别映射（Kaggle 原始名称 → 显示名称）———

_CATEGORY_DISPLAY = {
    "INFORMATION-TECHNOLOGY": "信息技术 (IT)",
    "ENGINEERING": "工程 (Engineering)",
    "FINANCE": "金融 (Finance)",
    "ACCOUNTANT": "会计 (Accountant)",
    "BANKING": "银行 (Banking)",
    "BUSINESS-DEVELOPMENT": "商业拓展 (Business Dev)",
    "CONSULTANT": "咨询 (Consultant)",
    "HEALTHCARE": "医疗健康 (Healthcare)",
    "SALES": "销售 (Sales)",
    "HR": "人力资源 (HR)",
    "DESIGNER": "设计 (Designer)",
    "DIGITAL-MEDIA": "数字媒体 (Digital Media)",
    "TEACHER": "教师 (Teacher)",
    "FITNESS": "健身 (Fitness)",
    "CONSTRUCTION": "建筑 (Construction)",
    "PUBLIC-RELATIONS": "公关 (PR)",
    "ADVOCATE": "律师 (Advocate)",
    "CHEF": "厨师 (Chef)",
    "AVIATION": "航空 (Aviation)",
    "ARTS": "艺术 (Arts)",
    "APPAREL": "服装 (Apparel)",
    "AGRICULTURE": "农业 (Agriculture)",
    "AUTOMOBILE": "汽车 (Automobile)",
    "BPO": "外包服务 (BPO)",
}

# 反向映射（显示名 → Kaggle 原始名）
_DISPLAY_TO_KAGGLE = {v: k for k, v in _CATEGORY_DISPLAY.items()}


def get_all_categories() -> list[str]:
    """返回所有可用岗位的显示名称列表。"""
    return list(_CATEGORY_DISPLAY.values())


def get_resume_by_job(job_category: str) -> str | None:
    """随机获取一份简历（保留旧接口兼容）。"""
    kaggle_cat = _DISPLAY_TO_KAGGLE.get(job_category, job_category)
    df = _load_df()
    subset = df[df["Category"] == kaggle_cat]
    if subset.empty:
        return None
    row = subset.sample(1).iloc[0]
    return _clean_resume(str(row["Resume_str"]))


def get_resume_list(job_category: str) -> list[dict]:
    """
    返回某岗位类别下所有简历的摘要列表，供用户选择。

    返回: [{index, preview, length}, ...]
    """
    kaggle_cat = _DISPLAY_TO_KAGGLE.get(job_category, job_category)
    df = _load_df()
    subset = df[df["Category"] == kaggle_cat]
    results = []
    for i, (_, row) in enumerate(subset.iterrows()):
        text = _clean_resume(str(row["Resume_str"]))
        compact = " ".join(text.split())[:120]
        results.append({"index": i, "preview": compact, "length": len(text)})
    return results


def get_resume_by_index(job_category: str, index: int) -> str | None:
    """
    根据岗位和索引（0-based），返回指定简历的完整文本。
    """
    kaggle_cat = _DISPLAY_TO_KAGGLE.get(job_category, job_category)
    df = _load_df()
    subset = df[df["Category"] == kaggle_cat]
    if subset.empty or index < 0 or index >= len(subset):
        return None
    return _clean_resume(str(subset.iloc[index]["Resume_str"]))


def _clean_resume(text: str) -> str:
    """清理简历文本的多余空白。"""
    text = text.strip()
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text


def get_stats() -> dict:
    """返回数据集统计信息（类别 + 数量），供调试使用。"""
    df = _load_df()
    stats = {}
    for kaggle_cat, display_name in _CATEGORY_DISPLAY.items():
        count = len(df[df["Category"] == kaggle_cat])
        stats[display_name] = count
    return stats
