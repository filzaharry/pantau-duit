import uuid
from decimal import Decimal
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.services.telegram_bot import (
    format_receipt_breakdown_html,
    build_wallet_inline_keyboard,
    execute_wallet_selection,
    format_rupiah
)
from app.models.financial import Account
from app.models.telegram import TelegramAccount, TelegramChat


def test_format_receipt_breakdown_html_with_taxes():
    items = [
        {"name": "Soto Sapi Bungkus", "qty": 3, "unit_price": Decimal("15000"), "total_price": Decimal("45000")},
        {"name": "Nasi Putih", "qty": 3, "unit_price": Decimal("6000"), "total_price": Decimal("18000")},
    ]
    taxes = [
        {"name": "PB1 (10%)", "amount": Decimal("6300")}
    ]
    html = format_receipt_breakdown_html(
        merchant_name="Warung Soto Bogor",
        total_amount=Decimal("69300"),
        items=items,
        subtotal_amount=Decimal("63000"),
        taxes=taxes,
        category_name="Food & Beverage",
        transaction_date=datetime(2026, 11, 17, 12, 30, tzinfo=timezone.utc)
    )
    assert "Warung Soto Bogor" in html
    assert "Soto Sapi Bungkus (<b>3x</b> @ Rp 15.000) = <b>Rp 45.000</b>" in html
    assert "PB1 (10%): <code>Rp 6.300</code>" in html
    assert "Total Tagihan: Rp 69.300" in html
    assert "masuk ke dompet mana saldo dipotong?" in html


def test_build_wallet_inline_keyboard():
    acc1 = Account(
        id=uuid.uuid4(),
        name="Dompet Tunai",
        type="CASH",
        current_balance=Decimal("50000")
    )
    acc2 = Account(
        id=uuid.uuid4(),
        name="BCA Harry",
        type="BANK",
        current_balance=Decimal("1500000")
    )
    keyboard = build_wallet_inline_keyboard([acc1, acc2])
    buttons = keyboard["inline_keyboard"]
    assert len(buttons) == 3  # 2 accounts + 1 cancel button
    assert f"select_wallet:{acc1.id}" == buttons[0][0]["callback_data"]
    assert "Dompet Tunai (Rp 50.000)" in buttons[0][0]["text"]
    assert f"select_wallet:{acc2.id}" == buttons[1][0]["callback_data"]
    assert "cancel_receipt" == buttons[2][0]["callback_data"]


def test_execute_wallet_selection_insufficient_balance():
    db = MagicMock()
    bot_token = "dummy_token"
    chat_id = 12345
    tg_account = MagicMock(spec=TelegramAccount)
    tg_account.user_id = uuid.uuid4()
    tg_chat = MagicMock(spec=TelegramChat)
    tg_chat.tenant_id = uuid.uuid4()

    acc = Account(
        id=uuid.uuid4(),
        name="Dompet Pas-pasan",
        type="CASH",
        current_balance=Decimal("20000")  # Less than total 50,000
    )

    pending = {
        "merchant_name": "Soto Mie Bogor",
        "total_amount": "50000",
        "items": []
    }

    with patch("app.services.telegram_bot.send_telegram_message") as mock_send:
        res = execute_wallet_selection(
            db=db,
            bot_token=bot_token,
            chat_id=chat_id,
            tg_account=tg_account,
            tg_chat=tg_chat,
            target_account=acc,
            pending=pending,
            tg_username="harry",
            tg_user_id=12345
        )
        assert res["status"] == "insufficient_wallet_balance"
        # Balance must NOT be deducted
        assert acc.current_balance == Decimal("20000")
        # Check that warning message was sent
        mock_send.assert_called_once()
        sent_text = mock_send.call_args[0][2]
        assert "saldo di Dompet Pas-pasan kurang" in sent_text
        assert "Dibutuhkan" not in sent_text or "Total Belanja" in sent_text


def test_execute_wallet_selection_sufficient_balance():
    db = MagicMock()
    bot_token = "dummy_token"
    chat_id = 12345
    tg_account = MagicMock(spec=TelegramAccount)
    tg_account.user_id = uuid.uuid4()
    tg_chat = MagicMock(spec=TelegramChat)
    tg_chat.tenant_id = uuid.uuid4()

    acc = Account(
        id=uuid.uuid4(),
        name="BCA Harry",
        type="BANK",
        current_balance=Decimal("100000")
    )

    pending = {
        "merchant_name": "Toko Kopi Manusia",
        "total_amount": "69020",
        "items": [
            {"name": "AMERICANO. ICE", "qty": 1, "unit_price": Decimal("38570"), "total_price": Decimal("38570")},
            {"name": "KENTANG GORENG AROMA", "qty": 1, "unit_price": Decimal("30450"), "total_price": Decimal("30450")}
        ],
        "category_id": None,
        "receipt_url": "https://pantau-duit.exavolt.net/uploads/receipts/test.jpg"
    }

    with patch("app.services.telegram_bot.send_telegram_message") as mock_send:
        res = execute_wallet_selection(
            db=db,
            bot_token=bot_token,
            chat_id=chat_id,
            tg_account=tg_account,
            tg_chat=tg_chat,
            target_account=acc,
            pending=pending,
            tg_username="harry",
            tg_user_id=12345
        )
        assert res["status"] == "receipt_confirmed_and_recorded"
        # Balance deducted: 100,000 - 69,020 = 30,980
        assert acc.current_balance == Decimal("30980")
        assert tg_chat.current_state == "IDLE"
        assert tg_chat.state_context == {}
        # Transaction added to db
        db.add.assert_called_once()
        db.commit.assert_called_once()
        mock_send.assert_called_once()
        sent_text = mock_send.call_args[0][2]
        assert "Transaksi Berhasil Dicatat" in sent_text
        assert "Rp 30.980" in sent_text
