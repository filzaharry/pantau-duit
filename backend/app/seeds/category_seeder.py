from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.financial import Category

SYSTEM_CATEGORIES = [
    # Expenses
    ("Food & Beverage", "food-and-beverage", "EXPENSE", "utensils", "#EF4444"),
    ("Transportation", "transportation", "EXPENSE", "car", "#F97316"),
    ("Housing & Rent", "housing-and-rent", "EXPENSE", "home", "#F59E0B"),
    ("Utilities & Bills", "utilities-and-bills", "EXPENSE", "bolt", "#EAB308"),
    ("Groceries", "groceries", "EXPENSE", "shopping-cart", "#84CC16"),
    ("Shopping", "shopping", "EXPENSE", "bag-shopping", "#10B981"),
    ("Entertainment", "entertainment", "EXPENSE", "film", "#06B6D4"),
    ("Health & Medical", "health-and-medical", "EXPENSE", "heart-pulse", "#3B82F6"),
    ("Education", "education", "EXPENSE", "graduation-cap", "#6366F1"),
    ("Personal Care", "personal-care", "EXPENSE", "spa", "#8B5CF6"),
    ("Gifts & Donations", "gifts-and-donations", "EXPENSE", "gift", "#D946EF"),
    ("Fees & Charges", "fees-and-charges", "EXPENSE", "receipt", "#EC4899"),
    ("Other Expense", "other-expense", "EXPENSE", "ellipsis", "#6B7280"),
    # Incomes
    ("Salary", "salary", "INCOME", "money-bill-wave", "#10B981"),
    ("Business Revenue", "business-revenue", "INCOME", "store", "#059669"),
    ("Freelance & Side Gig", "freelance-side-gig", "INCOME", "laptop-code", "#34D399"),
    ("Investment Return", "investment-return", "INCOME", "chart-line", "#22C55E"),
    ("Dividend", "dividend", "INCOME", "coins", "#16A34A"),
    ("Bonus & Commission", "bonus-commission", "INCOME", "trophy", "#15803D"),
    ("Refund & Cashback", "refund-cashback", "INCOME", "rotate-left", "#4ADE80"),
    ("Other Income", "other-income", "INCOME", "wallet", "#86EFAC"),
    # Investment
    ("Stocks", "stocks", "INVESTMENT", "arrow-trend-up", "#2563EB"),
    ("Cryptocurrency", "cryptocurrency", "INVESTMENT", "bitcoin-sign", "#F7931A"),
    ("Mutual Funds", "mutual-funds", "INVESTMENT", "chart-pie", "#7C3AED"),
    ("Bonds & Sukuk", "bonds-sukuk", "INVESTMENT", "file-contract", "#0284C7"),
    ("Precious Metals", "precious-metals", "INVESTMENT", "gem", "#D97706"),
]


def seed_categories(db: Session) -> dict[str, int]:
    """Idempotently seed standard system categories."""
    created_count = 0

    for name, slug, cat_type, icon, color in SYSTEM_CATEGORIES:
        existing = db.execute(
            select(Category).where(
                Category.tenant_id.is_(None),
                func.lower(Category.name) == name.lower(),
                Category.type == cat_type,
            )
        ).scalar_one_or_none()

        if not existing:
            category = Category(
                tenant_id=None,
                parent_id=None,
                name=name,
                slug=slug,
                type=cat_type,
                icon=icon,
                color=color,
                is_system=True,
            )
            db.add(category)
            created_count += 1

    db.commit()
    return {"system_categories": created_count}
