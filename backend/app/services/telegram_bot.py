import json
import logging
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional, Tuple, Dict, Any, List

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.models.auth import User
from app.models.tenant import Tenant, TenantUser
from app.models.financial import Account, Category, Transaction
from app.models.telegram import TelegramAccount, TelegramChat, TelegramMessage
from app.core.security import verify_password

logger = logging.getLogger("telegram_bot")


def send_telegram_message(
    bot_token: str,
    chat_id: int,
    text: str,
    parse_mode: str = "HTML"
) -> bool:
    """Send message to a Telegram chat via HTTP Bot API using standard library urllib."""
    if not bot_token:
        logger.error("Telegram bot token is not configured.")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        logger.error(f"Failed to send Telegram message to chat {chat_id}: {e}")
        return False


def format_rupiah(amount: Decimal | float | int) -> str:
    """Format number to Indonesian Rupiah string without decimal if whole."""
    val = float(amount)
    return f"Rp {val:,.0f}".replace(",", ".")


def parse_financial_input(
    text: str,
    categories: List[Category],
    accounts: List[Account]
) -> Optional[Dict[str, Any]]:
    """
    Parse financial transaction from user input (Semicolon or Natural Language).
    Returns dict:
      - amount: Decimal
      - type: 'EXPENSE' | 'INCOME'
      - description: str
      - category_id: UUID
      - category_name: str
      - account_id: UUID
      - account_name: str
    """
    cleaned = text.strip()
    if not cleaned:
        return None

    # Default values
    tx_type = "EXPENSE"
    amount: Optional[Decimal] = None
    description = ""
    target_category: Optional[Category] = None
    target_account: Optional[Account] = accounts[0] if accounts else None

    # Check for income keywords
    income_keywords = [
        "gaji", "salary", "bonus", "freelance", "cair", "pemasukan",
        "terima", "dapat uang", "pendapatan", "honor", "proyek", "hasil jualan"
    ]
    if any(re.search(r"\b" + re.escape(k) + r"\b", cleaned.lower()) for k in income_keywords):
        tx_type = "INCOME"

    # Match target account from keywords if user mentioned bank/wallet name
    for acc in accounts:
        acc_slug = acc.name.lower()
        if re.search(r"\b" + re.escape(acc_slug) + r"\b", cleaned.lower()):
            target_account = acc
            break
        if acc.type and re.search(r"\b" + re.escape(acc.type.lower()) + r"\b", cleaned.lower()):
            target_account = acc
            break

    # 1. Format: Semicolon Delimiter (e.g. "bakso;makanan;15000" or "kopi;25000")
    if ";" in cleaned:
        parts = [p.strip() for p in cleaned.split(";") if p.strip()]
        if len(parts) >= 3:
            description = parts[0]
            cat_hint = parts[1].lower()
            num_match = re.search(r"(\d+[\d\.,]*)", parts[2])
            if num_match:
                amount_str = num_match.group(1).replace(".", "").replace(",", ".")
                try:
                    amount = Decimal(amount_str)
                except Exception:
                    pass

            # Match category
            for cat in categories:
                if cat_hint in cat.name.lower() or cat_hint in cat.slug.lower():
                    target_category = cat
                    break

        elif len(parts) == 2:
            description = parts[0]
            num_match = re.search(r"(\d+[\d\.,]*)", parts[1])
            if num_match:
                amount_str = num_match.group(1).replace(".", "").replace(",", ".")
                try:
                    amount = Decimal(amount_str)
                except Exception:
                    pass

    # 2. Format: Natural Language Indonesian Parsing
    if amount is None:
        # Match nominal like: 15rb, 15k, 15 ribu, 1.5jt, 1,5 juta, 50000, 50.000
        pattern = r"(\d+(?:[.,]\d+)?)\s*(jt|juta|rb|ribu|k|rupiah|rp)?"
        matches = list(re.finditer(pattern, cleaned, flags=re.IGNORECASE))
        for m in matches:
            raw_num = m.group(1)
            unit = (m.group(2) or "").lower()

            try:
                if unit in ("jt", "juta"):
                    val = float(raw_num.replace(",", ".")) * 1_000_000
                elif unit in ("rb", "ribu", "k"):
                    val = float(raw_num.replace(",", ".")) * 1_000
                else:
                    clean_digits = raw_num.replace(".", "").replace(",", ".")
                    val = float(clean_digits)

                if val > 0:
                    amount = Decimal(str(int(val)))
                    # Remove the matched amount phrase from description
                    matched_str = m.group(0)
                    cleaned_desc = cleaned.replace(matched_str, "")
                    if target_account:
                        cleaned_desc = re.sub(r"\b" + re.escape(target_account.name) + r"\b", "", cleaned_desc, flags=re.IGNORECASE)
                    # Clean common filler words
                    for filler in ["tadi", "beli", "makan", "bayar", "isi", "di", "pake", "pakai", "via", "ke", "dari", "buat"]:
                        cleaned_desc = re.sub(r"\b" + filler + r"\b", "", cleaned_desc, flags=re.IGNORECASE)
                    cleaned_desc = re.sub(r"\s+", " ", cleaned_desc).strip()
                    description = cleaned_desc if cleaned_desc else cleaned
                    break
            except Exception:
                continue

    if amount is None or amount <= 0:
        return None

    # Clean description
    desc_clean = description.strip(" ,.-;:\"'")
    if not desc_clean:
        desc_clean = "Pengeluaran" if tx_type == "EXPENSE" else "Pemasukan"
    desc_clean = desc_clean[0].upper() + desc_clean[1:] if desc_clean else "Transaksi"

    # Match category if not already matched
    if not target_category:
        lower_desc = cleaned.lower()
        keyword_category_map = {
            "Food & Beverage": [
                "makan", "minum", "kopi", "bakso", "mie", "nasgor", "nasi",
                "ayam", "resto", "cafe", "warteg", "padang", "snack", "jajan",
                "burger", "pizza", "roti", "sarapan", "lunch", "dinner"
            ],
            "Transportation": [
                "bensin", "pertamax", "pertalite", "shell", "spbu", "solar",
                "gojek", "grab", "gocar", "goride", "ojek", "parkir", "toll",
                "kereta", "mrt", "krl", "bus", "travel", "taxi"
            ],
            "Utilities & Bills": [
                "listrik", "pln", "token", "pulsa", "kuota", "wifi", "indihome",
                "air", "pdam", "bpjs", "iuran", "tagihan", "sewa", "kontrakan"
            ],
            "Shopping": [
                "belanja", "baju", "sepatu", "celana", "shopee", "tokopedia",
                "lazada", "tiktok", "supermarket", "minimarket", "indomaret", "alfamart"
            ],
            "Entertainment": [
                "nonton", "bioskop", "cinema", "netflix", "spotify", "game",
                "steam", "liburan", "hotel"
            ],
            "Health": [
                "obat", "dokter", "apotek", "klinik", "rs", "rumah sakit",
                "vitamin", "periksa", "konsultasi"
            ],
            "Salary": [
                "gaji", "salary", "bonus", "freelance", "proyek", "honor"
            ]
        }

        for cat_name, kw_list in keyword_category_map.items():
            if any(re.search(r"\b" + re.escape(kw) + r"\b", lower_desc) for kw in kw_list):
                # Search matching category in tenant's categories
                for c in categories:
                    if cat_name.lower() in c.name.lower() or c.name.lower() in cat_name.lower():
                        target_category = c
                        break
            if target_category:
                break

    # Fallback category
    if not target_category:
        # Prefer matching type
        filtered = [c for c in categories if c.type in (tx_type, "BOTH")]
        target_category = filtered[0] if filtered else (categories[0] if categories else None)

    return {
        "amount": amount,
        "type": tx_type,
        "description": desc_clean,
        "category_id": target_category.id if target_category else None,
        "category_name": target_category.name if target_category else "Umum",
        "account_id": target_account.id if target_account else None,
        "account_name": target_account.name if target_account else "Dompet Utama"
    }


def handle_telegram_update(update_data: dict, db: Session, bot_token: str) -> dict:
    """Main Telegram webhook controller: handles pairing, commands, and transaction logging."""
    message = update_data.get("message") or update_data.get("edited_message")
    if not message:
        return {"status": "ignored_no_message"}

    chat = message.get("chat", {})
    from_user = message.get("from", {})
    chat_id = chat.get("id")
    tg_user_id = from_user.get("id")
    raw_text = (message.get("text") or "").strip()

    if not chat_id or not tg_user_id or not raw_text:
        return {"status": "ignored_incomplete_data"}

    first_name = from_user.get("first_name") or ""
    last_name = from_user.get("last_name") or ""
    tg_username = from_user.get("username") or ""
    full_name = f"{first_name} {last_name}".strip() or tg_username or "Sahabat PantauDuit"

    # Lookup existing linked Telegram account
    tg_account = db.execute(
        select(TelegramAccount).where(TelegramAccount.telegram_user_id == tg_user_id)
    ).scalar_one_or_none()

    # -------------------------------------------------------------------------
    # COMMAND: /reset or /unpair (Unlink account)
    # -------------------------------------------------------------------------
    if raw_text in ("/reset", "/unpair", "/logout"):
        if tg_account:
            db.delete(tg_account)
            db.commit()
            send_telegram_message(
                bot_token, chat_id,
                "🔌 <b>Akun Berhasil Diputus (Unpaired)</b>\n\n"
                "Akun Telegram Anda tidak lagi terhubung dengan PantauDuit.\n"
                "Untuk menghubungkan kembali, ketik: <code>/pair email_anda@example.com</code>"
            )
        else:
            send_telegram_message(
                bot_token, chat_id,
                "ℹ️ Akun Anda belum terhubung ke PantauDuit.\n"
                "Ketik <code>/pair email_anda@example.com</code> untuk menghubungkan."
            )
        return {"status": "unpaired"}

    # -------------------------------------------------------------------------
    # COMMAND: /pair or /login or /start with argument (Account Linking)
    # -------------------------------------------------------------------------
    is_pairing_attempt = False
    pairing_key = ""

    if raw_text.startswith("/pair"):
        is_pairing_attempt = True
        parts = raw_text.split(maxsplit=1)
        if len(parts) > 1:
            pairing_key = parts[1].strip()

    elif raw_text.startswith("/start "):
        arg = raw_text[7:].strip()
        if arg:
            is_pairing_attempt = True
            pairing_key = arg

    elif raw_text.startswith("/login"):
        parts = raw_text.split()
        if len(parts) >= 3:
            email_attempt = parts[1].strip().lower()
            pass_attempt = parts[2].strip()
            u = db.execute(select(User).where(User.email == email_attempt)).scalar_one_or_none()
            if u and verify_password(pass_attempt, u.hashed_password):
                is_pairing_attempt = True
                pairing_key = email_attempt
            else:
                send_telegram_message(
                    bot_token, chat_id,
                    "❌ <b>Login Gagal!</b>\n"
                    "Email atau kata sandi tidak cocok dengan data di web PantauDuit."
                )
                return {"status": "login_failed"}

    if is_pairing_attempt:
        target_user: Optional[User] = None

        # 1. Match by Email
        if "@" in pairing_key:
            target_user = db.execute(
                select(User).where(User.email.ilike(pairing_key))
            ).scalar_one_or_none()

        # 2. Match by Pairing Code (e.g. PD-994812 -> default admin)
        elif pairing_key.upper().startswith("PD-") or pairing_key == "PD-994812":
            # Link to active admin/superuser or first user
            target_user = db.execute(
                select(User).where(User.email == "admin@pantauduit.id")
            ).scalar_one_or_none()
            if not target_user:
                target_user = db.execute(select(User)).scalars().first()

        # 3. Match by Name/Username
        if not target_user:
            target_user = db.execute(
                select(User).where(User.name.ilike(f"%{pairing_key}%"))
            ).scalar_one_or_none()

        if not target_user:
            send_telegram_message(
                bot_token, chat_id,
                f"❌ <b>Akun Tidak Ditemukan!</b>\n\n"
                f"Tidak ditemukan pengguna dengan kunci: <code>{pairing_key}</code>\n"
                f"Pastikan memasukkan email akun yang terdaftar di PantauDuit.\n\n"
                f"Contoh: <code>/pair admin@pantauduit.id</code>"
            )
            return {"status": "pairing_user_not_found"}

        # Link account
        if not tg_account:
            tg_account = TelegramAccount(
                user_id=target_user.id,
                telegram_user_id=tg_user_id,
                telegram_username=tg_username,
                first_name=first_name,
                last_name=last_name,
                language_code="id",
                auth_date=datetime.now(timezone.utc),
                is_blocked=False
            )
            db.add(tg_account)
            db.flush()
        else:
            tg_account.user_id = target_user.id
            tg_account.telegram_username = tg_username
            tg_account.first_name = first_name
            tg_account.last_name = last_name
            tg_account.auth_date = datetime.now(timezone.utc)
            db.flush()

        # Find user's active tenant
        tu = db.execute(
            select(TenantUser).where(TenantUser.user_id == target_user.id, TenantUser.status == "ACTIVE")
        ).scalars().first()
        tenant = None
        if tu:
            tenant = db.execute(select(Tenant).where(Tenant.id == tu.tenant_id)).scalar_one_or_none()

        if not tenant:
            tenant = db.execute(select(Tenant)).scalars().first()

        # Link chat
        tg_chat = db.execute(
            select(TelegramChat).where(
                TelegramChat.telegram_account_id == tg_account.id,
                TelegramChat.chat_id == chat_id
            )
        ).scalar_one_or_none()

        if not tg_chat:
            tg_chat = TelegramChat(
                telegram_account_id=tg_account.id,
                tenant_id=tenant.id if tenant else target_user.id,
                chat_id=chat_id,
                chat_type="PRIVATE",
                title=full_name,
                current_state="IDLE",
                state_context={},
                last_active_at=datetime.now(timezone.utc)
            )
            db.add(tg_chat)
        else:
            tg_chat.last_active_at = datetime.now(timezone.utc)

        db.commit()

        tenant_name = tenant.name if tenant else "Workspace Utama"
        send_telegram_message(
            bot_token, chat_id,
            f"🎉 <b>Berhasil Terhubung!</b>\n\n"
            f"Akun Telegram Anda telah aktif dan terhubung ke:\n"
            f"👤 <b>{target_user.name}</b> (<code>{target_user.email}</code>)\n"
            f"🏢 Workspace: <b>{tenant_name}</b>\n\n"
            f"Sekarang Anda dapat langsung mencatat pengeluaran harian kapan pun di chat ini!\n\n"
            f"<b>Contoh Input Cepat:</b>\n"
            f"• <code>bakso 25rb</code>\n"
            f"• <code>bensin shell 50rb</code>\n"
            f"• <code>kopi;makanan;20000</code>\n"
            f"• <code>gaji freelance 2jt</code>\n\n"
            f"Ketik <b>/saldo</b> untuk cek saldo seluruh dompet Anda."
        )
        return {"status": "paired_successfully", "user_id": str(target_user.id)}

    # -------------------------------------------------------------------------
    # If user is NOT paired yet
    # -------------------------------------------------------------------------
    if not tg_account:
        send_telegram_message(
            bot_token, chat_id,
            f"👋 <b>Halo {full_name}!</b>\n\n"
            f"Selamat datang di <b>PantauDuit Bot</b> (<code>@pd_exavolt_bot</code>) 💰\n"
            f"Platform pencatatan keuangan pribadi tercepat & otomatis via Telegram.\n\n"
            f"Akun Telegram Anda saat ini <b>belum terhubung</b> ke PantauDuit.\n\n"
            f"<b>Cara Menghubungkan (Pilih Salah Satu):</b>\n"
            f"1. Kirim perintah dengan email Anda:\n"
            f"   <code>/pair email_anda@example.com</code>\n"
            f"   <i>(Contoh: <code>/pair admin@pantauduit.id</code>)</i>\n\n"
            f"2. Atau gunakan kode pairing dari web:\n"
            f"   <code>/pair PD-994812</code>\n\n"
            f"3. Atau login langsung:\n"
            f"   <code>/login email kata_sandi</code>\n\n"
            f"Buka dashboard web di: https://pantau-duit.exavolt.net/telegram"
        )
        return {"status": "not_paired_prompt_sent"}

    # User is paired: Load User & Tenant
    user = db.execute(select(User).where(User.id == tg_account.user_id)).scalar_one_or_none()
    if not user:
        send_telegram_message(
            bot_token, chat_id,
            "⚠️ Akun pengguna tidak ditemukan. Silakan hubungkan kembali dengan <code>/pair email_anda</code>."
        )
        return {"status": "user_missing"}

    # Find tenant
    tu = db.execute(
        select(TenantUser).where(TenantUser.user_id == user.id, TenantUser.status == "ACTIVE")
    ).scalars().first()
    tenant = db.execute(select(Tenant).where(Tenant.id == tu.tenant_id)).scalar_one_or_none() if tu else None
    if not tenant:
        tenant = db.execute(select(Tenant)).scalars().first()

    tenant_id = tenant.id

    # -------------------------------------------------------------------------
    # COMMAND: /start or /help or /bantuan
    # -------------------------------------------------------------------------
    if raw_text.startswith(("/start", "/help", "/bantuan")):
        send_telegram_message(
            bot_token, chat_id,
            f"👋 <b>Halo, {user.name}!</b>\n\n"
            f"Akun Telegram Anda terhubung dengan <b>{tenant.name}</b> (<code>{user.email}</code>).\n\n"
            f"<b>Cara Mencatat Transaksi:</b>\n"
            f"Cukup ketik langsung di chat ini, bot akan mendeteksi nominal & kategori otomatis!\n\n"
            f"<b>Contoh Input:</b>\n"
            f"• <code>makan bakso 25rb</code>\n"
            f"• <code>beli bensin shell 50k</code>\n"
            f"• <code>kopi;makanan;22000</code>\n"
            f"• <code>bayar tagihan listrik 150rb</code>\n"
            f"• <code>gaji freelance 2.5jt</code>\n\n"
            f"<b>Perintah Lainnya:</b>\n"
            f"• <b>/saldo</b> — Periksa saldo seluruh rekening & dompet\n"
            f"• <b>/transaksi</b> — 5 transaksi pengeluaran/pemasukan terakhir\n"
            f"• <b>/unpair</b> — Putuskan tautan akun dari bot ini"
        )
        return {"status": "help_sent"}

    # -------------------------------------------------------------------------
    # COMMAND: /saldo (Check balances)
    # -------------------------------------------------------------------------
    if raw_text in ("/saldo", "/balance", "/cek_saldo"):
        accounts = db.execute(
            select(Account).where(
                Account.tenant_id == tenant_id,
                Account.deleted_at.is_(None),
                Account.status == "ACTIVE"
            ).order_by(desc(Account.current_balance))
        ).scalars().all()

        if not accounts:
            send_telegram_message(
                bot_token, chat_id,
                "💳 Anda belum memiliki rekening atau dompet aktif.\n"
                "Silakan tambahkan dompet di menu web: https://pantau-duit.exavolt.net/accounts"
            )
            return {"status": "no_accounts"}

        lines = ["💳 <b>Daftar Saldo Rekening & Dompet:</b>\n"]
        total = Decimal("0")
        for acc in accounts:
            bal = acc.current_balance or Decimal("0")
            total += bal
            badge = "💵" if acc.type == "CASH" else ("📱" if acc.type == "E_WALLET" else "🏦")
            lines.append(f"{badge} <b>{acc.name}</b>: <code>{format_rupiah(bal)}</code>")

        lines.append("\n━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"💰 <b>Total Saldo:</b> <code>{format_rupiah(total)}</code>")
        lines.append(f"\n<i>Web Dashboard: https://pantau-duit.exavolt.net/dashboard</i>")

        send_telegram_message(bot_token, chat_id, "\n".join(lines))
        return {"status": "saldo_sent"}

    # -------------------------------------------------------------------------
    # COMMAND: /transaksi (Recent transactions)
    # -------------------------------------------------------------------------
    if raw_text in ("/transaksi", "/riwayat", "/mutasi"):
        transactions = db.execute(
            select(Transaction).where(
                Transaction.tenant_id == tenant_id,
                Transaction.deleted_at.is_(None),
                Transaction.status == "COMPLETED"
            ).order_by(desc(Transaction.transaction_date), desc(Transaction.created_at)).limit(5)
        ).scalars().all()

        if not transactions:
            send_telegram_message(
                bot_token, chat_id,
                "📜 Belum ada catatan transaksi yang tersimpan."
            )
            return {"status": "no_transactions"}

        lines = ["📜 <b>5 Transaksi Terakhir:</b>\n"]
        for idx, tx in enumerate(transactions, 1):
            sign = "+" if tx.transaction_type == "INCOME" else "-"
            amt_str = f"{sign}{format_rupiah(tx.amount)}"
            icon = "🟢" if tx.transaction_type == "INCOME" else "🔴"
            acc_name = tx.account.name if tx.account else "Dompet"
            date_str = tx.transaction_date.strftime("%d/%m %H:%M") if tx.transaction_date else "-"
            lines.append(
                f"{idx}. {icon} <b>{tx.description}</b>: <code>{amt_str}</code>\n"
                f"   💳 {acc_name} &bull; 🕒 {date_str}"
            )

        lines.append(f"\nLihat selengkapnya di: https://pantau-duit.exavolt.net/transactions")
        send_telegram_message(bot_token, chat_id, "\n".join(lines))
        return {"status": "transactions_sent"}

    # -------------------------------------------------------------------------
    # FINANCIAL TRANSACTION RECORDING (Natural Language or Semicolon)
    # -------------------------------------------------------------------------
    accounts = db.execute(
        select(Account).where(
            Account.tenant_id == tenant_id,
            Account.deleted_at.is_(None),
            Account.status == "ACTIVE"
        )
    ).scalars().all()

    if not accounts:
        send_telegram_message(
            bot_token, chat_id,
            "⚠️ Anda belum memiliki akun rekening/dompet aktif untuk mencatat transaksi.\n"
            "Silakan tambahkan di https://pantau-duit.exavolt.net/accounts"
        )
        return {"status": "no_account_available"}

    categories = db.execute(
        select(Category).where(
            Category.tenant_id.in_([tenant_id, None]),
            Category.deleted_at.is_(None)
        )
    ).scalars().all()

    parsed = parse_financial_input(raw_text, categories, accounts)

    if not parsed:
        send_telegram_message(
            bot_token, chat_id,
            f"🤔 Bot belum memahami pesan:\n<i>\"{raw_text}\"</i>\n\n"
            f"💡 <b>Tips Format:</b>\n"
            f"• Ketik nominal jelas: <code>makan bakso 25rb</code> atau <code>kopi 18k</code>\n"
            f"• Format cepat: <code>nama;kategori;nominal</code>\n"
            f"• Ketik <b>/saldo</b> untuk cek saldo rekening"
        )
        return {"status": "unrecognized_format"}

    # Get target account & update balance
    target_account = db.execute(
        select(Account).where(Account.id == parsed["account_id"])
    ).scalar_one_or_none()

    if not target_account:
        target_account = accounts[0]

    # Calculate balance changes
    if parsed["type"] == "INCOME":
        target_account.current_balance += parsed["amount"]
    else:
        target_account.current_balance -= parsed["amount"]

    # Create Transaction record in DB
    new_tx = Transaction(
        tenant_id=tenant_id,
        account_id=target_account.id,
        category_id=parsed["category_id"],
        amount=parsed["amount"],
        transaction_type=parsed["type"],
        transaction_date=datetime.now(timezone.utc),
        source="TELEGRAM",
        status="COMPLETED",
        description=parsed["description"],
        notes=f"Dicatat via Telegram (@{tg_username or tg_user_id}): \"{raw_text}\"",
        metadata_json={
            "telegram_chat_id": chat_id,
            "telegram_user_id": tg_user_id,
            "telegram_username": tg_username,
            "raw_input": raw_text,
            "parsed_by": "telegram_smart_parser"
        },
        created_by=user.id
    )
    db.add(new_tx)

    # Save TelegramMessage record
    tg_chat = db.execute(
        select(TelegramChat).where(
            TelegramChat.telegram_account_id == tg_account.id,
            TelegramChat.chat_id == chat_id
        )
    ).scalar_one_or_none()

    if tg_chat:
        tg_chat.last_active_at = datetime.now(timezone.utc)
        msg_record = TelegramMessage(
            telegram_chat_id=tg_chat.id,
            telegram_message_id=message.get("message_id", 0),
            direction="INCOMING",
            raw_text=raw_text,
            parsed_intent=f"RECORD_{parsed['type']}",
            status="PROCESSED"
        )
        db.add(msg_record)

    db.commit()

    # Reply confirmation with new balance
    type_label = "Pengeluaran 🔴" if parsed["type"] == "EXPENSE" else "Pemasukan 🟢"
    nominal_formatted = format_rupiah(parsed["amount"])
    new_bal_formatted = format_rupiah(target_account.current_balance)

    reply_text = (
        f"✅ <b>Transaksi Berhasil Dicatat!</b>\n\n"
        f"📝 <b>{parsed['description']}</b>\n"
        f"💸 Nominal: <b>{nominal_formatted}</b> ({type_label})\n"
        f"🏷️ Kategori: <b>{parsed['category_name']}</b>\n"
        f"💳 Dompet: <b>{target_account.name}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 Sisa Saldo <b>{target_account.name}</b>: <b>{new_bal_formatted}</b>\n\n"
        f"<i>Cek di: https://pantau-duit.exavolt.net/transactions</i>"
    )

    send_telegram_message(bot_token, chat_id, reply_text)
    return {
        "status": "transaction_recorded",
        "tx_id": str(new_tx.id),
        "amount": float(parsed["amount"]),
        "type": parsed["type"]
    }
