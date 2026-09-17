from datetime import datetime, timezone, timedelta, date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.security import hash_password
from app.models.auth import User
from app.models.tenant import Tenant, TenantUser
from app.models.rbac import Role, TenantUserRole
from app.models.billing import Plan, Subscription, Payment
from app.models.financial import Account, Category, Transaction, Budget, FinancialGoal, GoalContribution, RecurringTransaction
from app.models.telegram import TelegramAccount, TelegramChat


def seed_demo_tenant(db: Session) -> dict[str, str]:
    """Idempotently seed a complete, realistic demo tenant illustrating all domain relationships."""
    now = datetime.now(timezone.utc)
    today = now.date()

    # 1. Superadmin User
    superadmin = db.execute(select(User).where(User.email == "superadmin@pantauduit.id")).scalar_one_or_none()
    if not superadmin:
        superadmin = User(
            email="superadmin@pantauduit.id",
            password_hash=hash_password("SuperAdminSecure123!"),
            name="Platform Superadmin",
            status="ACTIVE",
            is_superadmin=True,
            email_verified_at=now,
        )
        db.add(superadmin)
        db.flush()

    # 2. Demo User (Budi)
    user_budi = db.execute(select(User).where(User.email == "budi@pantauduit.id")).scalar_one_or_none()
    if not user_budi:
        user_budi = User(
            email="budi@pantauduit.id",
            password_hash=hash_password("BudiPassword123!"),
            name="Budi Santoso",
            status="ACTIVE",
            is_superadmin=False,
            email_verified_at=now,
        )
        db.add(user_budi)
        db.flush()

    # 3. Personal Workspace for Budi
    tenant_slug = "budi-personal"
    tenant = db.execute(select(Tenant).where(Tenant.slug == tenant_slug)).scalar_one_or_none()
    if not tenant:
        tenant = Tenant(
            name="Personal Workspace Budi",
            slug=tenant_slug,
            type="PERSONAL",
            currency="IDR",
            timezone="Asia/Jakarta",
        )
        db.add(tenant)
        db.flush()

    # 4. Workspace Membership (Budi -> Personal Workspace)
    membership = db.execute(
        select(TenantUser).where(TenantUser.tenant_id == tenant.id, TenantUser.user_id == user_budi.id)
    ).scalar_one_or_none()
    if not membership:
        membership = TenantUser(
            tenant_id=tenant.id,
            user_id=user_budi.id,
            status="ACTIVE",
            joined_at=now,
        )
        db.add(membership)
        db.flush()

        # Assign 'owner' role
        owner_role = db.execute(
            select(Role).where(Role.tenant_id.is_(None), Role.slug == "owner")
        ).scalar_one()
        db.add(TenantUserRole(tenant_user_id=membership.id, role_id=owner_role.id))
        db.flush()

    # 5. Pro Subscription
    pro_plan = db.execute(select(Plan).where(Plan.code == "pro_monthly")).scalar_one()
    subscription = db.execute(
        select(Subscription).where(Subscription.tenant_id == tenant.id)
    ).scalar_one_or_none()

    if not subscription:
        sub_start = now - timedelta(days=5)
        sub_end = sub_start + timedelta(days=30)
        subscription = Subscription(
            tenant_id=tenant.id,
            plan_id=pro_plan.id,
            status="ACTIVE",
            started_at=sub_start,
            current_period_start=sub_start,
            current_period_end=sub_end,
            grace_period_end=sub_end + timedelta(days=3),
            cancel_at_period_end=False,
            metadata_json={"gateway": "midtrans", "channel": "qris"},
        )
        db.add(subscription)
        db.flush()

        # Add matching Payment record
        payment = Payment(
            tenant_id=tenant.id,
            subscription_id=subscription.id,
            invoice_number="INV-202609-0001",
            external_payment_id="midtrans-pay-001",
            amount=pro_plan.price,
            currency="IDR",
            payment_method="QRIS",
            payment_channel="GOPAY_QRIS",
            status="PAID",
            paid_at=sub_start,
            expires_at=sub_start + timedelta(hours=24),
            metadata_json={"transaction_status": "settlement"},
        )
        db.add(payment)
        db.flush()

    # 6. Accounts (BCA, GoPay, Cash)
    acc_bca = db.execute(
        select(Account).where(Account.tenant_id == tenant.id, Account.name == "BCA Tabungan")
    ).scalar_one_or_none()
    if not acc_bca:
        acc_bca = Account(
            tenant_id=tenant.id,
            name="BCA Tabungan",
            type="BANK",
            account_number="1234567890",
            currency="IDR",
            opening_balance=Decimal("10000000.00"),
            current_balance=Decimal("21485000.00"),  # Opening + Salary (12M) - Bakso (15k) - Transfer (500k)
            status="ACTIVE",
            color="#00529C",
            icon="building-columns",
        )
        db.add(acc_bca)
        db.flush()

    acc_gopay = db.execute(
        select(Account).where(Account.tenant_id == tenant.id, Account.name == "GoPay Wallet")
    ).scalar_one_or_none()
    if not acc_gopay:
        acc_gopay = Account(
            tenant_id=tenant.id,
            name="GoPay Wallet",
            type="E_WALLET",
            account_number="08123456789",
            currency="IDR",
            opening_balance=Decimal("500000.00"),
            current_balance=Decimal("1000000.00"),  # Opening + Transfer In (500k)
            status="ACTIVE",
            color="#00AED6",
            icon="wallet",
        )
        db.add(acc_gopay)
        db.flush()

    # 7. Categories Lookup
    cat_food = db.execute(select(Category).where(Category.slug == "food-and-beverage")).scalar_one()
    cat_salary = db.execute(select(Category).where(Category.slug == "salary")).scalar_one()

    # 8. Transactions (Income, Telegram Expense, Transfer)
    existing_tx = db.execute(select(Transaction).where(Transaction.tenant_id == tenant.id)).first()
    if not existing_tx:
        # Salary Income
        tx_salary = Transaction(
            tenant_id=tenant.id,
            account_id=acc_bca.id,
            category_id=cat_salary.id,
            amount=Decimal("12000000.00"),
            transaction_type="INCOME",
            transaction_date=now - timedelta(days=2),
            source="DASHBOARD",
            status="COMPLETED",
            description="Gaji Bulanan PT Maju Jaya",
            created_by=user_budi.id,
        )
        db.add(tx_salary)

        # Telegram Food Expense: "bakso;makanan;15000"
        tx_food = Transaction(
            tenant_id=tenant.id,
            account_id=acc_bca.id,
            category_id=cat_food.id,
            amount=Decimal("15000.00"),
            transaction_type="EXPENSE",
            transaction_date=now - timedelta(hours=3),
            source="TELEGRAM",
            status="COMPLETED",
            description="Bakso Urat Pak Kumis",
            notes="Input otomatis via Telegram",
            metadata_json={
                "raw_input": "bakso;makanan;15000",
                "nlp_confidence": 0.98,
                "parsed_by": "telegram_fast_parser",
            },
            created_by=user_budi.id,
        )
        db.add(tx_food)

        # Transfer: BCA -> GoPay (Single record, no expense pollution!)
        tx_transfer = Transaction(
            tenant_id=tenant.id,
            account_id=acc_bca.id,
            destination_account_id=acc_gopay.id,
            category_id=None,
            amount=Decimal("500000.00"),
            transaction_type="TRANSFER",
            transaction_date=now - timedelta(hours=1),
            source="DASHBOARD",
            status="COMPLETED",
            description="Top up GoPay dari BCA",
            created_by=user_budi.id,
        )
        db.add(tx_transfer)
        db.flush()

    # 9. Telegram Account & Chat Mapping
    tg_account = db.execute(
        select(TelegramAccount).where(TelegramAccount.telegram_user_id == 987654321)
    ).scalar_one_or_none()
    if not tg_account:
        tg_account = TelegramAccount(
            user_id=user_budi.id,
            telegram_user_id=987654321,
            telegram_username="budisantoso",
            first_name="Budi",
            last_name="Santoso",
            language_code="id",
            auth_date=now - timedelta(days=4),
        )
        db.add(tg_account)
        db.flush()

        tg_chat = TelegramChat(
            telegram_account_id=tg_account.id,
            tenant_id=tenant.id,
            chat_id=987654321,
            chat_type="PRIVATE",
            title="Budi Santoso",
            current_state="IDLE",
            state_context={},
            last_active_at=now,
        )
        db.add(tg_chat)
        db.flush()

    # 10. Budget (Monthly Food Budget)
    existing_budget = db.execute(
        select(Budget).where(Budget.tenant_id == tenant.id, Budget.category_id == cat_food.id)
    ).scalar_one_or_none()
    if not existing_budget:
        budget = Budget(
            tenant_id=tenant.id,
            category_id=cat_food.id,
            name="Budget Makan & Minum",
            amount=Decimal("2000000.00"),
            period="MONTHLY",
            start_date=today.replace(day=1),
            end_date=(today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1),
            alert_threshold_percent=80,
            is_active=True,
        )
        db.add(budget)

    # 11. Financial Goal (Emergency Fund)
    existing_goal = db.execute(
        select(FinancialGoal).where(FinancialGoal.tenant_id == tenant.id, FinancialGoal.name == "Dana Darurat")
    ).scalar_one_or_none()
    if not existing_goal:
        goal = FinancialGoal(
            tenant_id=tenant.id,
            name="Dana Darurat",
            target_amount=Decimal("50000000.00"),
            current_amount=Decimal("5000000.00"),
            target_date=today + timedelta(days=365),
            status="IN_PROGRESS",
            color="#10B981",
            icon="shield-halved",
        )
        db.add(goal)
        db.flush()

        db.add(GoalContribution(
            goal_id=goal.id,
            transaction_id=None,
            amount=Decimal("5000000.00"),
            contribution_date=now - timedelta(days=3),
            notes="Setoran awal dana darurat",
        ))

    # 12. Recurring Transaction (Internet WiFi)
    cat_bills = db.execute(select(Category).where(Category.slug == "utilities-and-bills")).scalar_one()
    existing_recurring = db.execute(
        select(RecurringTransaction).where(RecurringTransaction.tenant_id == tenant.id)
    ).scalar_one_or_none()
    if not existing_recurring:
        db.add(RecurringTransaction(
            tenant_id=tenant.id,
            account_id=acc_bca.id,
            category_id=cat_bills.id,
            amount=Decimal("350000.00"),
            transaction_type="EXPENSE",
            description="Tagihan Internet Indihome Bulanan",
            frequency="MONTHLY",
            start_date=today,
            next_execution_date=today + timedelta(days=15),
            status="ACTIVE",
        ))

    db.commit()
    return {"demo_tenant": tenant.name, "user": user_budi.email}
