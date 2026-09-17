from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.billing import Plan, PlanFeature

PLANS_DATA = [
    {
        "code": "free",
        "name": "Free Starter",
        "description": "Essential financial tracking for individual personal use",
        "price": Decimal("0.00"),
        "currency": "IDR",
        "interval": "MONTHLY",
        "interval_count": 1,
        "trial_period_days": 0,
        "is_active": True,
        "sort_order": 1,
        "features": {
            "max_transactions_per_month": "100",
            "max_accounts": "3",
            "telegram_bot_access": "true",
            "nlp_parser_enabled": "false",
            "multi_user_limit": "1",
            "export_reports": "false",
            "recurring_transactions_limit": "3",
        },
    },
    {
        "code": "pro_monthly",
        "name": "Pro Monthly",
        "description": "Full power Telegram financial assistant with NLP parsing and unlimited transactions",
        "price": Decimal("49000.00"),
        "currency": "IDR",
        "interval": "MONTHLY",
        "interval_count": 1,
        "trial_period_days": 7,
        "is_active": True,
        "sort_order": 2,
        "features": {
            "max_transactions_per_month": "-1",  # -1 = unlimited
            "max_accounts": "10",
            "telegram_bot_access": "true",
            "nlp_parser_enabled": "true",
            "multi_user_limit": "2",  # supports couple/family sharing
            "export_reports": "true",
            "recurring_transactions_limit": "-1",
        },
    },
    {
        "code": "pro_yearly",
        "name": "Pro Yearly",
        "description": "Pro plan with 2 months free discount billed annually",
        "price": Decimal("490000.00"),
        "currency": "IDR",
        "interval": "YEARLY",
        "interval_count": 1,
        "trial_period_days": 14,
        "is_active": True,
        "sort_order": 3,
        "features": {
            "max_transactions_per_month": "-1",
            "max_accounts": "10",
            "telegram_bot_access": "true",
            "nlp_parser_enabled": "true",
            "multi_user_limit": "2",
            "export_reports": "true",
            "recurring_transactions_limit": "-1",
        },
    },
    {
        "code": "business_monthly",
        "name": "Business Team",
        "description": "Advanced multi-user workspace for teams, small businesses, and agencies",
        "price": Decimal("149000.00"),
        "currency": "IDR",
        "interval": "MONTHLY",
        "interval_count": 1,
        "trial_period_days": 14,
        "is_active": True,
        "sort_order": 4,
        "features": {
            "max_transactions_per_month": "-1",
            "max_accounts": "-1",
            "telegram_bot_access": "true",
            "nlp_parser_enabled": "true",
            "multi_user_limit": "10",
            "export_reports": "true",
            "recurring_transactions_limit": "-1",
        },
    },
]


def seed_plans(db: Session) -> dict[str, int]:
    """Idempotently seed subscription plans and features."""
    created_plans = 0
    created_features = 0

    for item in PLANS_DATA:
        existing_plan = db.execute(select(Plan).where(Plan.code == item["code"])).scalar_one_or_none()
        if not existing_plan:
            plan = Plan(
                code=item["code"],
                name=item["name"],
                description=item["description"],
                price=item["price"],
                currency=item["currency"],
                interval=item["interval"],
                interval_count=item["interval_count"],
                trial_period_days=item["trial_period_days"],
                is_active=item["is_active"],
                sort_order=item["sort_order"],
            )
            db.add(plan)
            db.flush()
            created_plans += 1
        else:
            plan = existing_plan

        # Seed plan features
        for feat_key, feat_val in item["features"].items():
            existing_feat = db.execute(
                select(PlanFeature).where(
                    PlanFeature.plan_id == plan.id,
                    PlanFeature.feature_key == feat_key,
                )
            ).scalar_one_or_none()

            if not existing_feat:
                feature = PlanFeature(
                    plan_id=plan.id,
                    feature_key=feat_key,
                    feature_value=feat_val,
                )
                db.add(feature)
                created_features += 1
            else:
                existing_feat.feature_value = feat_val

    db.commit()
    return {"plans": created_plans, "features": created_features}
