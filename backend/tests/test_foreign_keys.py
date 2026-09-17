import pytest
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.core.database import SessionLocal
from app.models.tenant import Tenant
from app.models.financial import Account, Transaction, Category


def test_restrict_delete_account_with_transactions():
    """Verify ON DELETE RESTRICT prevents deleting accounts that have transactions."""
    db = SessionLocal()
    try:
        # Fetch an account with transactions
        tx = db.execute(select(Transaction)).first()
        assert tx is not None, "Transaction must exist"
        account_id = tx[0].account_id

        account = db.execute(select(Account).where(Account.id == account_id)).scalar_one()

        # Attempting to delete this account must fail with Foreign Key IntegrityError
        with pytest.raises(IntegrityError) as excinfo:
            db.delete(account)
            db.commit()

        assert "foreign key" in str(excinfo.value).lower() or "violates" in str(excinfo.value).lower()
        db.rollback()
    finally:
        db.close()


def test_check_constraint_transaction_amount_positive():
    """Verify CHECK constraint rejects non-positive amounts (amount <= 0)."""
    db = SessionLocal()
    try:
        tenant = db.execute(select(Tenant)).first()[0]
        account = db.execute(select(Account).where(Account.tenant_id == tenant.id)).first()[0]

        # Attempt to insert transaction with 0 amount
        zero_tx = Transaction(
            tenant_id=tenant.id,
            account_id=account.id,
            amount=Decimal("0.00"),
            transaction_type="EXPENSE",
            transaction_date=datetime.now(timezone.utc),
            source="DASHBOARD",
            status="COMPLETED",
            description="Illegal Zero Amount Transaction",
        )

        with pytest.raises(IntegrityError) as excinfo:
            db.add(zero_tx)
            db.commit()

        assert "chk_transactions_amount" in str(excinfo.value).lower() or "check constraint" in str(excinfo.value).lower()
        db.rollback()

        # Attempt to insert negative amount
        neg_tx = Transaction(
            tenant_id=tenant.id,
            account_id=account.id,
            amount=Decimal("-5000.00"),
            transaction_type="EXPENSE",
            transaction_date=datetime.now(timezone.utc),
            source="DASHBOARD",
            status="COMPLETED",
            description="Illegal Negative Amount Transaction",
        )

        with pytest.raises(IntegrityError) as excinfo:
            db.add(neg_tx)
            db.commit()

        assert "chk_transactions_amount" in str(excinfo.value).lower() or "check constraint" in str(excinfo.value).lower()
        db.rollback()
    finally:
        db.close()


def test_check_constraint_transaction_type_whitelist():
    """Verify CHECK constraint rejects invalid transaction types."""
    db = SessionLocal()
    try:
        tenant = db.execute(select(Tenant)).first()[0]
        account = db.execute(select(Account).where(Account.tenant_id == tenant.id)).first()[0]

        invalid_tx = Transaction(
            tenant_id=tenant.id,
            account_id=account.id,
            amount=Decimal("50000.00"),
            transaction_type="GAMBLING",  # Invalid type not in whitelist
            transaction_date=datetime.now(timezone.utc),
            source="DASHBOARD",
            status="COMPLETED",
            description="Illegal Transaction Type",
        )

        with pytest.raises(IntegrityError) as excinfo:
            db.add(invalid_tx)
            db.commit()

        assert "chk_transactions_type" in str(excinfo.value).lower() or "check constraint" in str(excinfo.value).lower()
        db.rollback()
    finally:
        db.close()
