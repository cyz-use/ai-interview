"""SQLite 数据库 —— 初始化表结构，存储面试记录。"""

import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "interviews.db")


def _get_conn() -> sqlite3.Connection:
    """获取数据库连接（自动创建目录和文件）。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """初始化数据库，创建 interviews 表（如不存在）。"""
    conn = _get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            job_category TEXT NOT NULL,
            resume_text TEXT NOT NULL,
            final_report_json TEXT NOT NULL,
            total_score INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_interview(
    job_category: str,
    resume_text: str,
    final_report: dict,
    total_score: int,
) -> None:
    """
    保存一次面试记录到数据库。

    参数:
        job_category: 面试岗位类别
        resume_text: 使用的简历文本
        final_report: 最终评估报告（dict）
        total_score: 综合总分
    """
    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO interviews (timestamp, job_category, resume_text, final_report_json, total_score)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(),
            job_category,
            resume_text,
            json.dumps(final_report, ensure_ascii=False),
            total_score,
        ),
    )
    conn.commit()
    conn.close()
