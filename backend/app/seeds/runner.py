import sys
from app.core.database import SessionLocal
from app.seeds.rbac_seeder import seed_rbac
from app.seeds.plan_seeder import seed_plans
from app.seeds.category_seeder import seed_categories
from app.seeds.demo_seeder import seed_demo_tenant
from app.seeds.company_seeder import seed_company


def run_all_seeders():
    """Execute all seeders in strictly controlled, idempotent transaction sequence."""
    db = SessionLocal()
    print("=" * 60)
    print("🌱 Starting Pantau-Duit Database Seeders (Idempotent)")
    print("=" * 60)
    try:
        # 1. RBAC
        print("▶ Seeding RBAC permissions and system roles...")
        rbac_res = seed_rbac(db)
        print(f"  ✓ RBAC seeded: {rbac_res}")

        # 2. Plans & Features
        print("▶ Seeding subscription plans and entitlements...")
        plan_res = seed_plans(db)
        print(f"  ✓ Plans seeded: {plan_res}")

        # 3. Categories
        print("▶ Seeding system transaction categories...")
        cat_res = seed_categories(db)
        print(f"  ✓ Categories seeded: {cat_res}")

        # 4. Demo Tenant & Domain Relationships
        print("▶ Seeding demo tenant, accounts, transactions & Telegram link...")
        demo_res = seed_demo_tenant(db)
        print(f"  ✓ Demo tenant seeded: {demo_res}")

        # 5. Company HR & Payroll
        print("▶ Seeding Company business tenant, employees, departments & payroll...")
        company_res = seed_company(db)
        print(f"  ✓ Company seeded: {company_res}")

        print("=" * 60)
        print("✨ All seeders executed successfully without error!")
        print("=" * 60)
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed with error: {e}", file=sys.stderr)
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    run_all_seeders()
