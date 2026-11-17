import pytest
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from app.services.telegram_bot import parse_financial_input, format_rupiah
from app.models.financial import Category, Account
import uuid

@pytest.fixture
def dummy_categories():
    food_cat = Category(
        id=uuid.uuid4(),
        name="Food & Beverage",
        slug="food-beverage",
        type="EXPENSE"
    )
    transport_cat = Category(
        id=uuid.uuid4(),
        name="Transportation",
        slug="transportation",
        type="EXPENSE"
    )
    salary_cat = Category(
        id=uuid.uuid4(),
        name="Salary",
        slug="salary",
        type="INCOME"
    )
    utilities_cat = Category(
        id=uuid.uuid4(),
        name="Utilities & Bills",
        slug="utilities-bills",
        type="EXPENSE"
    )
    return [food_cat, transport_cat, salary_cat, utilities_cat]

@pytest.fixture
def dummy_accounts():
    cash_acc = Account(
        id=uuid.uuid4(),
        name="Dompet Tunai",
        type="CASH",
        current_balance=Decimal("100000.00")
    )
    bca_acc = Account(
        id=uuid.uuid4(),
        name="BCA",
        type="BANK",
        current_balance=Decimal("500000.00")
    )
    return [cash_acc, bca_acc]

def test_user_reported_case(dummy_categories, dummy_accounts):
    """Test user exact case: 'Hari ini beli soto mi bogor 2 totalnya 40 ribu'"""
    text = "Hari ini beli soto mi bogor 2 totalnya 40 ribu"
    result = parse_financial_input(text, dummy_categories, dummy_accounts)
    
    assert result is not None
    assert result["amount"] == Decimal("40000")
    assert result["qty"] == 2
    assert result["unit_price"] == Decimal("20000")
    assert "Soto Mi Bogor" in result["description"]
    assert result["category_name"] == "Food & Beverage"
    assert result["type"] == "EXPENSE"
    assert result["transaction_date"].date() == datetime.now(timezone.utc).date()

def test_yesterday_with_porsi(dummy_categories, dummy_accounts):
    """Test 'kemarin makan soto ayam 2 porsi total 35rb'"""
    text = "kemarin makan soto ayam 2 porsi total 35rb"
    result = parse_financial_input(text, dummy_categories, dummy_accounts)
    
    assert result is not None
    assert result["amount"] == Decimal("35000")
    assert result["qty"] == 2
    assert result["unit_price"] == Decimal("17500")
    assert "Soto Ayam" in result["description"]
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date()
    assert result["transaction_date"].date() == yesterday

def test_qty_before_item(dummy_categories, dummy_accounts):
    """Test 'beli 2 kopi susu 36k'"""
    text = "beli 2 kopi susu 36k"
    result = parse_financial_input(text, dummy_categories, dummy_accounts)
    
    assert result is not None
    assert result["amount"] == Decimal("36000")
    assert result["qty"] == 2
    assert result["unit_price"] == Decimal("18000")
    assert "Kopi Susu" in result["description"]
    assert result["category_name"] == "Food & Beverage"

def test_single_item(dummy_categories, dummy_accounts):
    """Test 'makan bakso 25rb'"""
    text = "makan bakso 25rb"
    result = parse_financial_input(text, dummy_categories, dummy_accounts)
    
    assert result is not None
    assert result["amount"] == Decimal("25000")
    assert result["qty"] == 1
    assert result["unit_price"] == Decimal("25000")
    assert "Bakso" in result["description"]

def test_account_matching(dummy_categories, dummy_accounts):
    """Test 'bensin shell 50.000 pake bca'"""
    text = "bensin shell 50.000 pake bca"
    result = parse_financial_input(text, dummy_categories, dummy_accounts)
    
    assert result is not None
    assert result["amount"] == Decimal("50000")
    assert result["account_name"] == "BCA"
    assert result["category_name"] == "Transportation"

def test_income(dummy_categories, dummy_accounts):
    """Test 'gaji freelance 2.5jt'"""
    text = "gaji freelance 2.5jt"
    result = parse_financial_input(text, dummy_categories, dummy_accounts)
    
    assert result is not None
    assert result["type"] == "INCOME"
    assert result["amount"] == Decimal("2500000")
    assert result["category_name"] == "Salary"

def test_semicolon_format(dummy_categories, dummy_accounts):
    """Test semicolon formats"""
    res1 = parse_financial_input("soto mi bogor;2;40000", dummy_categories, dummy_accounts)
    assert res1["amount"] == Decimal("40000")
    assert res1["qty"] == 2
    assert res1["unit_price"] == Decimal("20000")

    res2 = parse_financial_input("kopi;20000", dummy_categories, dummy_accounts)
    assert res2["amount"] == Decimal("20000")
    assert res2["qty"] == 1

def test_format_rupiah():
    assert format_rupiah(40000) == "Rp 40.000"
    assert format_rupiah(2500000) == "Rp 2.500.000"
