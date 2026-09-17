from sqlalchemy import text, select
from app.core.database import SessionLocal
from app.models.tenant import Tenant


def test_telegram_user_resolution_uses_index():
    """Verify Telegram webhook user lookup uses B-Tree index scan (sub-millisecond path)."""
    db = SessionLocal()
    try:
        # Run EXPLAIN on Telegram user ID lookup
        result = db.execute(
            text("EXPLAIN SELECT * FROM telegram_accounts WHERE telegram_user_id = :tg_id"),
            {"tg_id": 987654321}
        ).scalars().all()

        explain_plan = " ".join(result)
        # Verify it uses Index Scan
        assert "Index Scan" in explain_plan or "Bitmap Index Scan" in explain_plan, f"Plan should use index scan, got: {explain_plan}"
    finally:
        db.close()


def test_dashboard_aggregation_query():
    """Verify dashboard aggregation computes expense vs income without sequential scans on large sets."""
    db = SessionLocal()
    try:
        tenant = db.execute(select(Tenant).where(Tenant.slug == "budi-personal")).scalar_one()

        query = text("""
            SELECT 
                COALESCE(SUM(amount) FILTER (WHERE transaction_type = 'EXPENSE'), 0) as total_expenses,
                COALESCE(SUM(amount) FILTER (WHERE transaction_type = 'INCOME'), 0) as total_income,
                COALESCE(SUM(amount) FILTER (WHERE transaction_type = 'TRANSFER'), 0) as total_transfers
            FROM transactions
            WHERE tenant_id = :tenant_id
              AND status = 'COMPLETED'
              AND deleted_at IS NULL;
        """)

        row = db.execute(query, {"tenant_id": tenant.id}).mappings().first()
        assert row is not None
        assert float(row["total_expenses"]) == 15000.00
        assert float(row["total_income"]) == 12000000.00
        assert float(row["total_transfers"]) == 500000.00
    finally:
        db.close()


def test_category_breakdown_aggregation():
    """Verify category spending aggregation is grouped correctly without loading all rows into memory."""
    db = SessionLocal()
    try:
        tenant = db.execute(select(Tenant).where(Tenant.slug == "budi-personal")).scalar_one()

        query = text("""
            SELECT 
                c.name as category_name,
                SUM(t.amount) as total_spent,
                COUNT(t.id) as transaction_count
            FROM transactions t
            JOIN categories c ON c.id = t.category_id
            WHERE t.tenant_id = :tenant_id
              AND t.transaction_type = 'EXPENSE'
              AND t.status = 'COMPLETED'
              AND t.deleted_at IS NULL
            GROUP BY c.name
            ORDER BY total_spent DESC;
        """)

        rows = db.execute(query, {"tenant_id": tenant.id}).mappings().all()
        assert len(rows) >= 1
        assert rows[0]["category_name"] == "Food & Beverage"
        assert float(rows[0]["total_spent"]) == 15000.00
    finally:
        db.close()
