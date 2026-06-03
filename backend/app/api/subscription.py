"""
订阅 API —— 试用配额管理 + 手动升级（零成本版）。

付费流程：
  1. 新用户免费 3 次面试
  2. 次数用完 → 弹窗显示付款信息
  3. 用户付款后联系客服 → 后台手动升级为 pro
  4. 后续可接入微信支付自动化
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import verify_token
from app.api.deps import get_db
from app.models.db import User
from app.models.schemas import SubscriptionStatus

router = APIRouter()

# ========== 配置 ==========
FREE_TRIAL_COUNT = 3
# 付款信息（零成本方案：微信收款码 + 手动升级）
PAYMENT_INFO = {
    "price_monthly": 29,
    "price_yearly": 199,
    "qr_code_url": "/api/subscription/qrcode",  # 替换成真实收款码图片
    "contact": "付款后请截图发送至客服微信：xxx，或发送邮件至 xxx@example.com，注明你的用户名，即刻开通。",
}


@router.get("/status", response_model=SubscriptionStatus)
async def get_subscription_status(
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """获取当前用户的订阅状态。"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    remaining = max(0, user.max_trial_interviews - user.trial_interviews_used)

    return SubscriptionStatus(
        trial_interviews_used=user.trial_interviews_used,
        max_trial_interviews=user.max_trial_interviews,
        trial_remaining=remaining if user.subscription_tier == "free" else 999,
        subscription_tier=user.subscription_tier,
        can_interview=(
            user.subscription_tier != "free" or user.trial_interviews_used < user.max_trial_interviews
        ),
    )


@router.get("/payment-info")
async def get_payment_info(user_id: str = Depends(verify_token)):
    """获取付款信息（价格 + 收款码 + 说明）。"""
    return PAYMENT_INFO


@router.post("/upgrade")
async def upgrade_user(
    username: str,
    tier: str = "pro",
    duration_days: int = 365,
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db),
):
    """
    手动升级用户订阅（客服后台操作，需要管理员权限）。

    参数：
        username: 要升级的用户名
        tier: 目标等级 (pro / enterprise)
        duration_days: 有效天数
    """
    # 检查是否是管理员（简单实现：检查当前用户是否在管理员列表中）
    admin_ids = ["admin"]  # 后续可改为数据库字段
    current_user = db.query(User).filter(User.id == user_id).first()
    if not current_user or current_user.username not in admin_ids:
        raise HTTPException(status_code=403, detail="需要管理员权限")

    target_user = db.query(User).filter(User.username == username).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    from datetime import datetime, timedelta
    target_user.subscription_tier = tier
    target_user.subscription_expires_at = datetime.utcnow() + timedelta(days=duration_days)
    target_user.max_trial_interviews = 999
    db.commit()

    return {"message": f"用户 {username} 已升级为 {tier}，有效期 {duration_days} 天"}
