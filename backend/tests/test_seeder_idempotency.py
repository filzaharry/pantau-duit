from sqlalchemy import select, func
from app.core.database import SessionLocal
from app.models.rbac import Role, Permission, RolePermission
from app.models.billing import Plan, PlanFeature
from app.models.financial import Category
from app.seeds.runner import run_all_seeders


def test_seeder_idempotency():
    """Verify running seeders repeatedly produces identical state with no duplicates."""
    db = SessionLocal()
    try:
        # Get baseline counts
        count_perms_1 = db.scalar(select(func.count(Permission.id)))
        count_roles_1 = db.scalar(select(func.count(Role.id)))
        count_plans_1 = db.scalar(select(func.count(Plan.id)))
        count_categories_1 = db.scalar(select(func.count(Category.id)))
    finally:
        db.close()

    # Re-run all seeders
    run_all_seeders()

    db2 = SessionLocal()
    try:
        count_perms_2 = db2.scalar(select(func.count(Permission.id)))
        count_roles_2 = db2.scalar(select(func.count(Role.id)))
        count_plans_2 = db2.scalar(select(func.count(Plan.id)))
        count_categories_2 = db2.scalar(select(func.count(Category.id)))

        assert count_perms_1 == count_perms_2, "Permissions count must not change on duplicate seed"
        assert count_roles_1 == count_roles_2, "Roles count must not change on duplicate seed"
        assert count_plans_1 == count_plans_2, "Plans count must not change on duplicate seed"
        assert count_categories_1 == count_categories_2, "Categories count must not change on duplicate seed"
    finally:
        db2.close()
