import os
import json
import logging
import re
import uuid
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List

from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.models.auth import User
from app.models.tenant import Tenant, TenantUser
from app.models.financial import Account, Category, Transaction
from app.models.telegram import TelegramAccount, TelegramChat, TelegramMessage
from app.core.security import verify_password
from app.services.receipt_ocr import receipt_ocr_service

logger = logging.getLogger("telegram_bot")


def send_telegram_message(
    bot_token: str,
    chat_id: int,
    text: str,
    parse_mode: str = "HTML",
    reply_markup: Optional[Dict[str, Any]] = None
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
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

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


def answer_callback_query(
    bot_token: str,
    callback_query_id: str,
    text: Optional[str] = None,
    show_alert: bool = False
) -> bool:
    """Acknowledge Telegram callback query from inline buttons."""
    if not bot_token or not callback_query_id:
        return False

    url = f"https://api.telegram.org/bot{bot_token}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
        payload["show_alert"] = show_alert

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
        logger.error(f"Failed to answer callback query {callback_query_id}: {e}")
        return False


def build_wallet_inline_keyboard(accounts: List[Account]) -> Dict[str, Any]:
    """Generate Telegram inline keyboard for wallet selection."""
    inline_keyboard = []
    for acc in accounts:
        bal = acc.current_balance or Decimal("0")
        bal_str = format_rupiah(bal)
        icon = "💵" if acc.type == "CASH" else ("📱" if acc.type == "E_WALLET" else "🏦")
        button_text = f"{icon} {acc.name} ({bal_str})"
        inline_keyboard.append([
            {"text": button_text, "callback_data": f"select_wallet:{acc.id}"}
        ])
    inline_keyboard.append([
        {"text": "❌ Batalkan", "callback_data": "cancel_receipt"}
    ])
    return {"inline_keyboard": inline_keyboard}


def format_receipt_breakdown_html(
    merchant_name: str,
    total_amount: Decimal,
    items: List[Dict[str, Any]],
    subtotal_amount: Optional[Decimal] = None,
    taxes: Optional[List[Dict[str, Any]]] = None,
    discounts: Optional[List[Dict[str, Any]]] = None,
    category_name: str = "Shopping",
    transaction_date: Optional[datetime] = None
) -> str:
    """Format structured receipt breakdown for Telegram user confirmation."""
    lines = ["🧾 <b>Detail Struk Belanja Terdeteksi:</b>\n"]
    lines.append(f"🏪 Toko/Merchant: <b>{merchant_name}</b>")
    if transaction_date:
        lines.append(f"📅 Tanggal: <b>{transaction_date.strftime('%d/%m/%Y %H:%M')}</b>")
    lines.append(f"🏷️ Kategori: <b>{category_name}</b>\n")

    if items:
        lines.append("📋 <b>Rincian Item:</b>")
        for it in items:
            name = it.get("name", "Item")
            qty = it.get("qty", 1)
            unit_price = it.get("unit_price")
            total_price = it.get("total_price")
            if qty > 1 and unit_price:
                lines.append(f"• {name} (<b>{qty}x</b> @ {format_rupiah(unit_price)}) = <b>{format_rupiah(total_price)}</b>")
            else:
                lines.append(f"• {name} = <b>{format_rupiah(total_price or unit_price or 0)}</b>")
    else:
        lines.append(f"📋 <b>Rincian:</b> Belanja di {merchant_name}")

    lines.append("━━━━━━━━━━━━━━━━━━━━")
    if subtotal_amount and (taxes or discounts or (subtotal_amount != total_amount)):
        lines.append(f"Subtotal: <code>{format_rupiah(subtotal_amount)}</code>")
    if taxes:
        for t in taxes:
            t_name = t.get("name", "Pajak")
            lines.append(f"{t_name}: <code>{format_rupiah(t.get('amount', 0))}</code>")
    if discounts:
        for d in discounts:
            d_name = d.get("name", "Diskon")
            lines.append(f"{d_name}: <code>-{format_rupiah(d.get('amount', 0))}</code>")

    lines.append(f"💰 <b>Total Tagihan: {format_rupiah(total_amount)}</b>\n")
    lines.append("❓ <b>Apakah detail data di atas sudah benar?</b>")
    lines.append("Silakan pilih, <b>masuk ke dompet mana saldo dipotong?</b>")
    return "\n".join(lines)


def format_rupiah(amount: Decimal | float | int) -> str:
    """Format number to Indonesian Rupiah string without decimal if whole."""
    val = float(amount)
    return f"Rp {val:,.0f}".replace(",", ".")


def download_telegram_file(bot_token: str, file_id: str) -> Optional[bytes]:
    """Download a file (photo or document) from Telegram using Bot API."""
    if not bot_token or not file_id:
        return None

    try:
        url_info = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
        req = urllib.request.Request(url_info)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if not data.get("ok"):
                logger.error(f"Telegram getFile returned not ok: {data}")
                return None
            file_path = data.get("result", {}).get("file_path")
            if not file_path:
                return None

        # Download raw bytes
        url_file = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        req_file = urllib.request.Request(url_file)
        with urllib.request.urlopen(req_file, timeout=20) as resp_file:
            return resp_file.read()
    except Exception as e:
        logger.error(f"Failed to download Telegram file {file_id}: {e}")
        return None


def parse_financial_input(
    text: str,
    categories: List[Category],
    accounts: List[Account]
) -> Optional[Dict[str, Any]]:
    """
    Parse financial transaction from user input (Semicolon or Natural Language).
    Extracts:
      - amount: Decimal (Total transaction amount)
      - type: 'EXPENSE' | 'INCOME'
      - description: str (Title/item name)
      - item_name: str (Clean item name without qty/price)
      - qty: int (Quantity / items count)
      - unit_price: Decimal (Price per unit)
      - transaction_date: datetime (Parsed or current date)
      - category_id: UUID
      - category_name: str
      - account_id: UUID
      - account_name: str
    """
    cleaned = text.strip()
    if not cleaned:
        return None

    now = datetime.now(timezone.utc)
    tx_date = now

    # Default values
    tx_type = "EXPENSE"
    amount: Optional[Decimal] = None
    qty: int = 1
    unit_price: Optional[Decimal] = None
    item_name: str = ""
    description: str = ""
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

    # 1. Date extraction from text
    date_patterns = [
        (r"\b(hari ini|tadi (?:pagi|siang|sore|malam)|tadi)\b", 0),
        (r"\b(kemarin|kemaren)\b", -1),
        (r"\b(lusa|2 hari lalu|dua hari lalu)\b", -2),
        (r"\b(3 hari lalu|tiga hari lalu)\b", -3),
    ]
    for pat, day_offset in date_patterns:
        m = re.search(pat, cleaned, re.IGNORECASE)
        if m:
            tx_date = now + timedelta(days=day_offset)
            cleaned = re.sub(pat, " ", cleaned, flags=re.IGNORECASE).strip()
            break

    # Specific date format dd/mm/yyyy or dd-mm-yyyy
    dm_match = re.search(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b", cleaned)
    if dm_match:
        d = int(dm_match.group(1))
        m_val = int(dm_match.group(2))
        y = int(dm_match.group(3)) if dm_match.group(3) else now.year
        if y < 100:
            y += 2000
        try:
            tx_date = datetime(y, m_val, d, now.hour, now.minute, now.second, tzinfo=timezone.utc)
            cleaned = cleaned.replace(dm_match.group(0), " ").strip()
        except Exception:
            pass

    # Helper function to convert raw number and unit string to integer/decimal
    def num_unit_to_val(raw_num: str, unit: Optional[str]) -> int:
        u = (unit or "").lower()
        if u in ("jt", "juta"):
            return int(float(raw_num.replace(",", ".")) * 1_000_000)
        elif u in ("rb", "ribu", "k"):
            return int(float(raw_num.replace(",", ".")) * 1_000)
        else:
            clean = raw_num.replace(".", "").replace(",", ".")
            return int(float(clean))

    # 2. Format: Semicolon Delimiter (e.g. "bakso;makanan;15000" or "soto;2;40000" or "kopi;25000")
    if ";" in cleaned:
        parts = [p.strip() for p in cleaned.split(";") if p.strip()]
        if len(parts) >= 3:
            description = parts[0]
            # Check if parts[1] is a quantity
            if parts[1].isdigit():
                qty = max(1, int(parts[1]))
            else:
                cat_hint = parts[1].lower()
                for cat in categories:
                    if cat_hint in cat.name.lower() or cat_hint in cat.slug.lower():
                        target_category = cat
                        break
            num_match = re.search(r"(\d+[\d\.,]*)", parts[2])
            if num_match:
                amount_str = num_match.group(1).replace(".", "").replace(",", ".")
                try:
                    amount = Decimal(amount_str)
                except Exception:
                    pass

        elif len(parts) == 2:
            description = parts[0]
            num_match = re.search(r"(\d+[\d\.,]*)", parts[1])
            if num_match:
                amount_str = num_match.group(1).replace(".", "").replace(",", ".")
                try:
                    amount = Decimal(amount_str)
                except Exception:
                    pass

        item_name = description

    # 3. Format: Natural Language Indonesian Parsing
    if amount is None:
        working_text = cleaned

        # 3.1 Check for @ unit price pattern: e.g. "@ 20rb" or "masing-masing 15k" or "satuan 20.000"
        at_pattern = r"(?:@|masing[- ]masing|satuan(?:nya)?)\s*(?:rp\.?|rupiah)?\s*(\d+(?:[.,]\d+)?)\s*(jt|juta|rb|ribu|k|rupiah|rp)?\b"
        m_at = re.search(at_pattern, working_text, flags=re.IGNORECASE)
        at_unit_price: Optional[Decimal] = None
        if m_at:
            val = num_unit_to_val(m_at.group(1), m_at.group(2))
            if val > 0:
                at_unit_price = Decimal(str(val))
                working_text = working_text[:m_at.span()[0]] + " " + working_text[m_at.span()[1]:]

        total_amount: Optional[Decimal] = None
        matched_amount_span: Optional[Tuple[int, int]] = None

        # Priority A: Numbers preceded by total / seharga / habis / sebesar / senilai / bayar
        kw_pattern = r"\b(?:total(?:nya)?|semua(?:nya)?|habis|seharga|senilai|sebesar|bayar)\s*(?:rp\.?|rupiah)?\s*(\d+(?:[.,]\d+)?)\s*(jt|juta|rb|ribu|k|rupiah|rp)?\b"
        m_kw = re.search(kw_pattern, working_text, flags=re.IGNORECASE)
        if m_kw:
            val = num_unit_to_val(m_kw.group(1), m_kw.group(2))
            if val > 0:
                total_amount = Decimal(str(val))
                matched_amount_span = m_kw.span()

        # Priority B: Numbers with explicit currency units (jt, juta, rb, ribu, k, rupiah) or Rp prefix
        if total_amount is None:
            curr_pattern = r"(?:rp\.?\s*(\d+(?:[.,]\d+)?)\s*(jt|juta|rb|ribu|k|rupiah)?|(\d+(?:[.,]\d+)?)\s*(jt|juta|rb|ribu|k|rupiah))\b"
            matches = list(re.finditer(curr_pattern, working_text, flags=re.IGNORECASE))
            if matches:
                m_curr = matches[-1]
                raw_num = m_curr.group(1) or m_curr.group(3)
                unit = m_curr.group(2) or m_curr.group(4)
                val = num_unit_to_val(raw_num, unit)
                if val > 0:
                    total_amount = Decimal(str(val))
                    matched_amount_span = m_curr.span()

        # Priority C: Large standalone numbers (>= 500) or numbers with dots like 40.000
        if total_amount is None:
            large_pattern = r"\b(\d{1,3}(?:\.\d{3})+|\d{4,})\b"
            m_large = re.search(large_pattern, working_text)
            if m_large:
                val = int(m_large.group(1).replace(".", ""))
                if val > 0:
                    total_amount = Decimal(str(val))
                    matched_amount_span = m_large.span()

        # Isolate remaining text without amount
        text_without_amount = working_text
        if matched_amount_span:
            text_without_amount = working_text[:matched_amount_span[0]] + " " + working_text[matched_amount_span[1]:]

        # 3.2 Extract Quantity
        # Pattern 1: With unit (porsi, bungkus, pcs, x, etc.)
        qty_unit_pattern = r"\b(\d+)\s*(?:x|porsi|bungkus|buah|biji|mangkok|piring|gelas|cup|botol|item|pcs|box|kotak|pack|paket|lembar|butir|ekor)\b"
        m_qty = re.search(qty_unit_pattern, text_without_amount, flags=re.IGNORECASE)
        if m_qty:
            qty = max(1, int(m_qty.group(1)))
            text_without_amount = re.sub(qty_unit_pattern, " ", text_without_amount, count=1, flags=re.IGNORECASE)
        else:
            # Pattern 2: Standalone small number (1-99) left in text (e.g. "soto mi bogor 2")
            m_small = re.search(r"\b([1-9]\d?)\b", text_without_amount)
            if m_small:
                qty = max(1, int(m_small.group(1)))
                text_without_amount = re.sub(r"\b" + m_small.group(1) + r"\b", " ", text_without_amount, count=1)

        # If user provided @ unit price and no total amount, calculate total
        if at_unit_price and total_amount is None:
            total_amount = at_unit_price * qty

        # Priority D: Fallback to any number left if total_amount is still None
        if total_amount is None:
            any_num = re.search(r"\b(\d+)\b", text_without_amount)
            if any_num:
                val = int(any_num.group(1))
                if val > 0:
                    total_amount = Decimal(str(val))
                    text_without_amount = re.sub(r"\b" + any_num.group(1) + r"\b", " ", text_without_amount, count=1)

        amount = total_amount

        # 3.3 Clean description and extract item name
        cleaned_desc = text_without_amount
        if target_account:
            cleaned_desc = re.sub(r"\b" + re.escape(target_account.name) + r"\b", " ", cleaned_desc, flags=re.IGNORECASE)

        filler_words = [
            "tadi", "beli", "makan", "bayar", "isi", "di", "pake", "pakai",
            "via", "ke", "dari", "buat", "untuk", "dan", "sama", "jajan",
            "ongkir", "total", "totalnya", "seharga", "senilai", "sebesar", "habis"
        ]
        for fw in filler_words:
            cleaned_desc = re.sub(r"\b" + fw + r"\b", " ", cleaned_desc, flags=re.IGNORECASE)

        cleaned_desc = re.sub(r"\s+", " ", cleaned_desc).strip(" ,.-;:\"'")
        item_name = cleaned_desc.title() if cleaned_desc else ("Pengeluaran" if tx_type == "EXPENSE" else "Pemasukan")
        description = item_name

    if amount is None or amount <= 0:
        return None

    # Calculate unit price
    unit_price = (amount / qty) if (amount and qty > 0) else amount

    # Clean description fallback
    desc_clean = description.strip(" ,.-;:\"'")
    if not desc_clean:
        desc_clean = "Pengeluaran" if tx_type == "EXPENSE" else "Pemasukan"
    desc_clean = desc_clean[0].upper() + desc_clean[1:] if desc_clean else "Transaksi"

    # Match category if not already matched
    if not target_category:
        lower_desc = (cleaned + " " + item_name).lower()
        keyword_category_map = {
            "Food & Beverage": [
                "makan", "minum", "kopi", "bakso", "mie", "nasgor", "nasi",
                "ayam", "resto", "cafe", "warteg", "padang", "snack", "jajan",
                "burger", "pizza", "roti", "sarapan", "lunch", "dinner",
                "soto", "sate", "bebek", "rawon", "gudeg", "pecel", "seafood",
                "ikan", "teh", "jus", "boba", "martabak", "gorengan", "siomay",
                "batagor", "bubur", "donat", "kue", "cemilan", "es", "esteh"
            ],
            "Transportation": [
                "bensin", "pertamax", "pertalite", "shell", "spbu", "solar",
                "gojek", "grab", "gocar", "goride", "ojek", "parkir", "toll",
                "kereta", "mrt", "krl", "bus", "travel", "taxi",
                "tol", "angkot", "maxim", "indrive", "cuci motor", "cuci mobil", "servis", "service", "oli"
            ],
            "Utilities & Bills": [
                "listrik", "pln", "token", "pulsa", "kuota", "wifi", "indihome",
                "air", "pdam", "bpjs", "iuran", "tagihan", "sewa", "kontrakan",
                "gas", "lpg", "galon", "ipl"
            ],
            "Shopping": [
                "belanja", "baju", "sepatu", "celana", "shopee", "tokopedia",
                "lazada", "tiktok", "supermarket", "minimarket", "indomaret", "alfamart"
            ],
            "Entertainment": [
                "nonton", "bioskop", "cinema", "netflix", "spotify", "game",
                "steam", "liburan", "hotel", "karaoke", "konser", "tiket"
            ],
            "Health": [
                "obat", "dokter", "apotek", "klinik", "rs", "rumah sakit",
                "vitamin", "periksa", "konsultasi", "lab", "vaksin", "kacamata"
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
        "item_name": item_name,
        "qty": qty,
        "unit_price": unit_price,
        "transaction_date": tx_date,
        "category_id": target_category.id if target_category else None,
        "category_name": target_category.name if target_category else "Umum",
        "account_id": target_account.id if target_account else None,
        "account_name": target_account.name if target_account else "Dompet Utama"
    }


def match_item_to_category(
    item_name: str,
    categories: List[Category],
    default_category_id: Optional[uuid.UUID] = None
) -> Optional[uuid.UUID]:
    """Helper to auto-match individual receipt items to tenant categories based on keywords."""
    if not item_name or not categories:
        return default_category_id

    lower = item_name.lower()
    keyword_map = {
        "Food & Beverage": [
            "soto", "mie", "mi ", "bakso", "nasi", "ayam", "bebek", "ikan",
            "kopi", "coffee", "latte", "tea", "teh", "susu", "milk", "jus",
            "juice", "roti", "bread", "cake", "snack", "chiki", "biskuit",
            "wafer", "cokelat", "chocolate", "gorengan", "martabak", "pizza",
            "burger", "resto", "cafe", "warung", "dapur", "kuliner", "makan",
            "minum", "mcd", "kfc", "indomie", "pop mie"
        ],
        "Transportation": [
            "bensin", "pertalite", "pertamax", "solar", "shell", "spbu",
            "toll", "tol", "parkir", "parking", "grab", "gojek", "goride",
            "gocar", "maxim", "taxi", "taksi", "kereta", "krl", "mrt",
            "busway", "transjakarta", "flight", "pesawat"
        ],
        "Shopping": [
            "sabun", "shampoo", "sampo", "odol", "pasta gigi", "tissue",
            "tisu", "deterjen", "rinso", "molto", "minyak", "beras",
            "telur", "gula", "garam", "bumbu", "baju", "celana", "sepatu",
            "sandal", "kaos", "tas", "alfamart", "indomaret", "superindo",
            "hypermart", "transmart", "tokopedia", "shopee"
        ],
        "Utilities & Bills": [
            "listrik", "pln", "air", "pdam", "wifi", "internet", "indihome",
            "biznet", "pulsa", "paket data", "bpjs", "asuransi", "iuran"
        ],
        "Health & Medical": [
            "obat", "apotek", "farmasi", "vitamin", "panadol", "paracetamol",
            "dokter", "klinik", "rumah sakit", "laboratorium"
        ]
    }

    for target_cat_name, kws in keyword_map.items():
        if any(re.search(r"\b" + re.escape(kw) + r"\b", lower) for kw in kws):
            for c in categories:
                if target_cat_name.lower() in c.name.lower() or c.name.lower() in target_cat_name.lower():
                    return c.id

    for c in categories:
        if c.name.lower() in lower or lower in c.name.lower():
            return c.id

    return default_category_id


def execute_wallet_selection(
    db: Session,
    bot_token: str,
    chat_id: int,
    tg_account: TelegramAccount,
    tg_chat: TelegramChat,
    target_account: Account,
    pending: Dict[str, Any],
    tg_username: str,
    tg_user_id: int
) -> dict:
    """Check wallet balance, deduct funds, and record receipt transactions one-by-one per item."""
    total_amount = Decimal(str(pending["total_amount"]))
    acc_balance = target_account.current_balance or Decimal("0")

    # 1. Check if balance is sufficient
    if acc_balance < total_amount:
        shortage = total_amount - acc_balance
        warn_msg = (
            f"⚠️ <b>Maaf, saldo di {target_account.name} kurang!</b>\n\n"
            f"💳 Dompet: <b>{target_account.name}</b>\n"
            f"💵 Sisa Saldo: <b>{format_rupiah(acc_balance)}</b>\n"
            f"💸 Total Belanja: <b>{format_rupiah(total_amount)}</b>\n"
            f"<i>(Kurang {format_rupiah(shortage)})</i>\n\n"
            f"Silakan pilih dompet lain yang saldonya mencukupi, atau klik batalkan:"
        )
        all_accounts = db.execute(
            select(Account).where(
                Account.tenant_id == tg_chat.tenant_id,
                Account.deleted_at.is_(None),
                Account.status == "ACTIVE"
            ).order_by(desc(Account.current_balance))
        ).scalars().all()
        keyboard = build_wallet_inline_keyboard(all_accounts)
        send_telegram_message(bot_token, chat_id, warn_msg, reply_markup=keyboard)
        return {"status": "insufficient_wallet_balance"}

    # 2. Balance is sufficient: Deduct wallet balance
    target_account.current_balance -= total_amount

    # Fetch available categories for auto-matching item categories
    tenant_categories = db.execute(
        select(Category).where(
            Category.tenant_id == tg_chat.tenant_id,
            Category.deleted_at.is_(None)
        )
    ).scalars().all()

    default_cat_id = None
    if pending.get("category_id"):
        try:
            default_cat_id = uuid.UUID(pending["category_id"])
        except Exception:
            pass

    tx_date_raw = pending.get("transaction_date")
    try:
        tx_date = datetime.fromisoformat(tx_date_raw) if tx_date_raw else datetime.now(timezone.utc)
    except Exception:
        tx_date = datetime.now(timezone.utc)

    merchant_name = pending.get("merchant_name") or "Struk Belanja"
    receipt_url = pending.get("receipt_url")

    items = pending.get("items") or []
    taxes = pending.get("taxes") or []
    created_txs: List[Transaction] = []

    if items:
        # User requested: create transaction one by one per item, NOT just grand total!
        total_items_recorded = Decimal("0")

        for it in items:
            raw_name = (it.get("name") or "Item Belanja").strip()
            qty = max(1, int(it.get("qty", 1)))
            unit_price_raw = it.get("unit_price")
            total_price_raw = it.get("total_price")

            if total_price_raw is not None and Decimal(str(total_price_raw)) > 0:
                item_amt = Decimal(str(total_price_raw))
                unit_amt = Decimal(str(unit_price_raw)) if unit_price_raw else (item_amt / qty)
            elif unit_price_raw is not None and Decimal(str(unit_price_raw)) > 0:
                unit_amt = Decimal(str(unit_price_raw))
                item_amt = unit_amt * qty
            else:
                continue

            item_cat_id = match_item_to_category(raw_name, tenant_categories, default_cat_id)
            desc = f"{raw_name} ({qty}x)" if qty > 1 else raw_name
            item_notes = (
                f"Item dari struk {merchant_name} (Qty: {qty} @ {format_rupiah(unit_amt)}) | "
                f"Dicatat via Telegram OCR (@{tg_username or tg_user_id})"
                if qty > 1 else
                f"Item dari struk {merchant_name} | Dicatat via Telegram OCR (@{tg_username or tg_user_id})"
            )

            tx_item = Transaction(
                tenant_id=tg_chat.tenant_id,
                account_id=target_account.id,
                category_id=item_cat_id,
                amount=item_amt,
                transaction_type="EXPENSE",
                transaction_date=tx_date,
                source="TELEGRAM",
                status="COMPLETED",
                description=desc,
                receipt_url=receipt_url,
                notes=item_notes,
                metadata_json={
                    "telegram_chat_id": chat_id,
                    "telegram_user_id": tg_user_id,
                    "telegram_username": tg_username,
                    "ocr_engine": "tesseract_local",
                    "merchant": merchant_name,
                    "item_name": raw_name,
                    "qty": qty,
                    "unit_price": float(unit_amt),
                    "is_receipt_item": True,
                    "receipt_url": receipt_url
                },
                created_by=tg_account.user_id
            )
            db.add(tx_item)
            created_txs.append(tx_item)
            total_items_recorded += item_amt

        # Add taxes / service charges if any
        for tx_item in taxes:
            tax_name = tx_item.get("name") or "Pajak / PB1"
            tax_amt = Decimal(str(tx_item.get("amount") or 0))
            if tax_amt > 0:
                tax_cat_id = match_item_to_category("pajak", tenant_categories, default_cat_id)
                tax_tx = Transaction(
                    tenant_id=tg_chat.tenant_id,
                    account_id=target_account.id,
                    category_id=tax_cat_id,
                    amount=tax_amt,
                    transaction_type="EXPENSE",
                    transaction_date=tx_date,
                    source="TELEGRAM",
                    status="COMPLETED",
                    description=f"{tax_name} ({merchant_name})",
                    receipt_url=receipt_url,
                    notes=f"{tax_name} dari struk {merchant_name} | Dicatat via Telegram OCR (@{tg_username or tg_user_id})",
                    metadata_json={
                        "telegram_chat_id": chat_id,
                        "merchant": merchant_name,
                        "is_receipt_tax": True,
                        "receipt_url": receipt_url
                    },
                    created_by=tg_account.user_id
                )
                db.add(tax_tx)
                created_txs.append(tax_tx)
                total_items_recorded += tax_amt

        # If there's an unallocated positive difference between total_amount and recorded items
        diff = total_amount - total_items_recorded
        if diff > Decimal("0"):
            diff_tx = Transaction(
                tenant_id=tg_chat.tenant_id,
                account_id=target_account.id,
                category_id=default_cat_id,
                amount=diff,
                transaction_type="EXPENSE",
                transaction_date=tx_date,
                source="TELEGRAM",
                status="COMPLETED",
                description=f"Biaya Lainnya / Pembulatan ({merchant_name})",
                receipt_url=receipt_url,
                notes=f"Penyesuaian selisih struk {merchant_name} dengan total kasir | Telegram OCR",
                metadata_json={
                    "telegram_chat_id": chat_id,
                    "merchant": merchant_name,
                    "is_receipt_rounding": True
                },
                created_by=tg_account.user_id
            )
            db.add(diff_tx)
            created_txs.append(diff_tx)

    # Fallback if no items could be parsed individually from receipt
    if not created_txs:
        single_tx = Transaction(
            tenant_id=tg_chat.tenant_id,
            account_id=target_account.id,
            category_id=default_cat_id,
            amount=total_amount,
            transaction_type="EXPENSE",
            transaction_date=tx_date,
            source="TELEGRAM",
            status="COMPLETED",
            description=merchant_name,
            receipt_url=receipt_url,
            notes=f"Struk dipindai otomatis via Telegram OCR (@{tg_username or tg_user_id})",
            metadata_json={
                "telegram_chat_id": chat_id,
                "merchant": merchant_name,
                "ocr_engine": "tesseract_local",
                "receipt_url": receipt_url
            },
            created_by=tg_account.user_id
        )
        db.add(single_tx)
        created_txs.append(single_tx)

    # Reset chat state back to IDLE
    tg_chat.current_state = "IDLE"
    tg_chat.state_context = {}
    tg_chat.last_active_at = datetime.now(timezone.utc)

    db.commit()

    # Format detailed confirmation message
    item_rows = []
    for tx in created_txs:
        item_rows.append(f"• {tx.description}: <b>{format_rupiah(tx.amount)}</b>")
    items_summary_text = "\n".join(item_rows)

    success_msg = (
        f"✅ <b>Struk Berhasil Dicatat ({len(created_txs)} Transaksi)!</b>\n\n"
        f"🏪 Toko/Merchant: <b>{merchant_name}</b>\n"
        f"💳 Dompet: <b>{target_account.name}</b>\n\n"
        f"📋 <b>Rincian per Item:</b>\n"
        f"{items_summary_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💸 <b>Total Terpotong:</b> <b>{format_rupiah(total_amount)}</b> (Pengeluaran 🔴)\n"
        f"💰 <b>Sisa Saldo {target_account.name}:</b> <b>{format_rupiah(target_account.current_balance)}</b>\n\n"
        f"📎 <i>Foto struk tersimpan aman di setiap transaksi web!</i>"
    )
    send_telegram_message(bot_token, chat_id, success_msg)
    return {
        "status": "receipt_confirmed_and_recorded",
        "tx_count": len(created_txs),
        "tx_ids": [str(tx.id) for tx in created_txs],
        "account_id": str(target_account.id),
        "total_amount": float(total_amount)
    }


def handle_telegram_update(update_data: dict, db: Session, bot_token: str) -> dict:
    """Main Telegram webhook controller: handles pairing, commands, button callbacks, and transaction logging."""
    callback_query = update_data.get("callback_query")
    message = update_data.get("message") or update_data.get("edited_message")

    # -------------------------------------------------------------------------
    # CALLBACK QUERY (Inline Keyboard Button Clicks)
    # -------------------------------------------------------------------------
    if callback_query:
        callback_id = callback_query.get("id")
        cb_from = callback_query.get("from", {})
        tg_user_id = cb_from.get("id")
        cb_msg = callback_query.get("message", {})
        chat_id = cb_msg.get("chat", {}).get("id") or tg_user_id
        cb_data = callback_query.get("data", "")

        tg_username = cb_from.get("username") or ""

        # Acknowledge callback immediately so button spinner stops
        answer_callback_query(bot_token, callback_id)

        # Lookup linked Telegram account
        tg_account = db.execute(
            select(TelegramAccount).where(TelegramAccount.telegram_user_id == tg_user_id)
        ).scalar_one_or_none()

        if not tg_account:
            send_telegram_message(
                bot_token, chat_id,
                "⚠️ Akun Telegram Anda belum terhubung. Ketik <code>/pair email_anda</code> untuk menghubungkan."
            )
            return {"status": "callback_not_paired"}

        # Lookup chat
        tg_chat = db.execute(
            select(TelegramChat).where(
                TelegramChat.telegram_account_id == tg_account.id,
                TelegramChat.chat_id == chat_id
            )
        ).scalar_one_or_none()

        if not tg_chat or tg_chat.current_state != "AWAITING_WALLET_SELECTION":
            send_telegram_message(
                bot_token, chat_id,
                "ℹ️ Sesi pemilihan dompet ini sudah selesai atau kedaluwarsa. Silakan kirim foto struk kembali jika ingin mencatat."
            )
            return {"status": "callback_state_expired"}

        pending = (tg_chat.state_context or {}).get("pending_receipt")
        if not pending:
            tg_chat.current_state = "IDLE"
            tg_chat.state_context = {}
            db.commit()
            send_telegram_message(
                bot_token, chat_id,
                "ℹ️ Data struk tidak ditemukan. Silakan kirim ulang foto struk Anda."
            )
            return {"status": "pending_missing"}

        # Button: Cancel Receipt
        if cb_data == "cancel_receipt":
            tg_chat.current_state = "IDLE"
            tg_chat.state_context = {}
            tg_chat.last_active_at = datetime.now(timezone.utc)
            db.commit()
            send_telegram_message(
                bot_token, chat_id,
                "❌ <b>Pencatatan struk dibatalkan.</b>\nTidak ada saldo dompet yang terpotong."
            )
            return {"status": "receipt_cancelled"}

        # Button: Select Wallet
        if cb_data.startswith("select_wallet:"):
            selected_acc_id_str = cb_data.split(":", 1)[1]
            try:
                selected_acc_uuid = uuid.UUID(selected_acc_id_str)
            except Exception:
                selected_acc_uuid = None

            target_account = db.execute(
                select(Account).where(Account.id == selected_acc_uuid, Account.deleted_at.is_(None))
            ).scalar_one_or_none() if selected_acc_uuid else None

            if not target_account:
                send_telegram_message(
                    bot_token, chat_id,
                    "⚠️ Dompet yang dipilih tidak ditemukan atau telah dihapus."
                )
                return {"status": "wallet_not_found"}

            return execute_wallet_selection(
                db=db,
                bot_token=bot_token,
                chat_id=chat_id,
                tg_account=tg_account,
                tg_chat=tg_chat,
                target_account=target_account,
                pending=pending,
                tg_username=tg_username,
                tg_user_id=tg_user_id
            )

        return {"status": "callback_ignored"}

    if not message:
        return {"status": "ignored_no_message"}

    chat = message.get("chat", {})
    from_user = message.get("from", {})
    chat_id = chat.get("id")
    tg_user_id = from_user.get("id")

    # Check for photo or document image
    photos = message.get("photo")
    doc = message.get("document")
    is_image = False
    file_id = None
    if photos and isinstance(photos, list):
        is_image = True
        file_id = photos[-1].get("file_id")
    elif doc and (doc.get("mime_type") or "").startswith("image/"):
        is_image = True
        file_id = doc.get("file_id")

    raw_text = (message.get("text") or message.get("caption") or "").strip()

    if not chat_id or not tg_user_id or (not raw_text and not is_image):
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

        # 2. Match by Pairing Code (e.g. PD-994812 -> default user with accounts or admin)
        elif pairing_key.upper().startswith("PD-") or pairing_key == "PD-994812":
            # Link to active user with accounts (prefer real user like filzaharry / budi)
            target_user = db.execute(
                select(User).where(User.email == "harryfilza@gmail.com")
            ).scalar_one_or_none()
            if not target_user:
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

        # Find user's active tenant (prioritize one with active accounts)
        tu_list = db.execute(
            select(TenantUser).where(TenantUser.user_id == target_user.id, TenantUser.status == "ACTIVE")
        ).scalars().all()
        tenant = None
        for item in tu_list:
            t = db.execute(select(Tenant).where(Tenant.id == item.tenant_id)).scalar_one_or_none()
            if t:
                has_acc = db.execute(
                    select(Account).where(Account.tenant_id == t.id, Account.deleted_at.is_(None))
                ).first()
                if has_acc:
                    tenant = t
                    break
                if not tenant:
                    tenant = t

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

    # Find tenant - prioritize tenant with accounts
    tu_list = db.execute(
        select(TenantUser).where(TenantUser.user_id == user.id, TenantUser.status == "ACTIVE")
    ).scalars().all()
    tenant = None
    for tu_item in tu_list:
        t_cand = db.execute(select(Tenant).where(Tenant.id == tu_item.tenant_id)).scalar_one_or_none()
        if t_cand:
            has_acc = db.execute(
                select(Account).where(Account.tenant_id == t_cand.id, Account.deleted_at.is_(None))
            ).first()
            if has_acc:
                tenant = t_cand
                break
            if not tenant:
                tenant = t_cand

    if not tenant:
        tenant = db.execute(select(Tenant)).scalars().first()

    tenant_id = tenant.id

    # Lookup chat record
    tg_chat = db.execute(
        select(TelegramChat).where(
            TelegramChat.telegram_account_id == tg_account.id,
            TelegramChat.chat_id == chat_id
        )
    ).scalar_one_or_none()

    # -------------------------------------------------------------------------
    # STATE: AWAITING_WALLET_SELECTION (Interactive receipt confirmation)
    # -------------------------------------------------------------------------
    if tg_chat and tg_chat.current_state == "AWAITING_WALLET_SELECTION":
        pending = (tg_chat.state_context or {}).get("pending_receipt")
        if not pending:
            tg_chat.current_state = "IDLE"
            tg_chat.state_context = {}
            db.commit()
        else:
            # Check if user wants to cancel
            if raw_text.lower() in ("batal", "cancel", "/cancel", "batalin", "gak jadi", "batal struk"):
                tg_chat.current_state = "IDLE"
                tg_chat.state_context = {}
                tg_chat.last_active_at = datetime.now(timezone.utc)
                db.commit()
                send_telegram_message(
                    bot_token, chat_id,
                    "❌ <b>Pencatatan struk dibatalkan.</b>\nTidak ada saldo dompet yang terpotong."
                )
                return {"status": "receipt_cancelled"}

            # If user sent a new image or a slash command, clear state and let it proceed
            if is_image or raw_text.startswith(("/start", "/saldo", "/transaksi", "/reset", "/unpair", "/logout", "/pair", "/login")):
                tg_chat.current_state = "IDLE"
                tg_chat.state_context = {}
                db.flush()
            else:
                # User typed a wallet name or number (e.g. "BCA", "Tabungan", "1")
                tenant_accs = db.execute(
                    select(Account).where(
                        Account.tenant_id == tg_chat.tenant_id,
                        Account.deleted_at.is_(None),
                        Account.status == "ACTIVE"
                    ).order_by(desc(Account.current_balance))
                ).scalars().all()

                selected_account = None
                if raw_text.isdigit():
                    idx = int(raw_text) - 1
                    if 0 <= idx < len(tenant_accs):
                        selected_account = tenant_accs[idx]

                if not selected_account:
                    for acc in tenant_accs:
                        if acc.name.lower() in raw_text.lower() or raw_text.lower() in acc.name.lower():
                            selected_account = acc
                            break

                if selected_account:
                    return execute_wallet_selection(
                        db=db,
                        bot_token=bot_token,
                        chat_id=chat_id,
                        tg_account=tg_account,
                        tg_chat=tg_chat,
                        target_account=selected_account,
                        pending=pending,
                        tg_username=tg_username,
                        tg_user_id=tg_user_id
                    )
                else:
                    merch = pending.get("merchant_name") or "Struk Belanja"
                    tot = Decimal(str(pending.get("total_amount", 0)))
                    keyboard = build_wallet_inline_keyboard(tenant_accs)
                    send_telegram_message(
                        bot_token, chat_id,
                        f"ℹ️ Anda sedang dalam proses konfirmasi struk <b>{merch}</b> (Total: <b>{format_rupiah(tot)}</b>).\n\n"
                        f"Silakan pilih salah satu dompet di tombol bawah ini, atau ketik <b>batal</b>:",
                        reply_markup=keyboard
                    )
                    return {"status": "awaiting_wallet_choice"}

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
        # Auto-provision a default cash wallet so user can transact immediately
        default_acc = Account(
            tenant_id=tenant_id,
            name="Dompet Tunai",
            type="CASH",
            currency="IDR",
            opening_balance=Decimal("0.00"),
            current_balance=Decimal("0.00"),
            status="ACTIVE",
            icon="/wallets/cash.svg",
            color="#10B981"
        )
        db.add(default_acc)
        db.flush()
        accounts = [default_acc]

    categories = db.execute(
        select(Category).where(
            Category.tenant_id.in_([tenant_id, None])
        )
    ).scalars().all()

    # -------------------------------------------------------------------------
    # PHOTO RECEIPT OCR SCANNING (Local Tesseract Engine)
    # -------------------------------------------------------------------------
    if is_image and file_id:
        img_bytes = download_telegram_file(bot_token, file_id)
        if not img_bytes:
            send_telegram_message(
                bot_token, chat_id,
                "⚠️ Gagal mengunduh foto struk dari Telegram. Silakan coba kirim ulang."
            )
            return {"status": "failed_download_photo"}

        # Define receipt upload directory
        base_uploads = Path("/vol/pantau-duit/backend/uploads") if os.path.exists("/vol/pantau-duit/backend/uploads") else Path("uploads")
        receipts_save_dir = base_uploads / "receipts"
        receipts_save_dir.mkdir(parents=True, exist_ok=True)

        ocr_result = receipt_ocr_service.process_receipt(
            img_bytes,
            save_dir=receipts_save_dir,
            base_url="https://pantau-duit.exavolt.net/uploads/receipts"
        )

        total_amount = ocr_result.get("total_amount")

        if total_amount and total_amount > 0:
            merchant_name = ocr_result.get("merchant_name") or "Struk Belanja"
            cat_hint = ocr_result.get("category_hint") or "Shopping"
            target_category = None
            for c in categories:
                if cat_hint.lower() in c.name.lower() or c.name.lower() in cat_hint.lower():
                    target_category = c
                    break
            if not target_category:
                filtered = [c for c in categories if c.type in ("EXPENSE", "BOTH")]
                target_category = filtered[0] if filtered else (categories[0] if categories else None)

            tx_date = ocr_result.get("transaction_date") or datetime.now(timezone.utc)
            items = ocr_result.get("items") or []
            taxes = ocr_result.get("taxes") or []
            discounts = ocr_result.get("discounts") or []
            subtotal_amount = ocr_result.get("subtotal_amount")

            # Save pending receipt in chat state context
            pending_data = {
                "merchant_name": merchant_name,
                "total_amount": str(total_amount),
                "subtotal_amount": str(subtotal_amount or total_amount),
                "tax_amount": str(ocr_result.get("tax_amount") or 0),
                "taxes": taxes,
                "discounts": discounts,
                "items": items,
                "category_id": str(target_category.id) if target_category else None,
                "category_name": target_category.name if target_category else "Shopping",
                "transaction_date": tx_date.isoformat(),
                "receipt_url": ocr_result.get("receipt_url")
            }

            if tg_chat:
                tg_chat.current_state = "AWAITING_WALLET_SELECTION"
                tg_chat.state_context = {"pending_receipt": pending_data}
                tg_chat.last_active_at = datetime.now(timezone.utc)

                msg_record = TelegramMessage(
                    telegram_chat_id=tg_chat.id,
                    telegram_message_id=message.get("message_id", 0),
                    direction="INCOMING",
                    raw_text=raw_text or "[FOTO STRUK]",
                    parsed_intent="SCAN_RECEIPT_OCR",
                    status="PROCESSED"
                )
                db.add(msg_record)

            db.commit()

            # Format detailed item breakdown HTML & send inline keyboard buttons
            breakdown_text = format_receipt_breakdown_html(
                merchant_name=merchant_name,
                total_amount=total_amount,
                items=items,
                subtotal_amount=subtotal_amount,
                taxes=taxes,
                discounts=discounts,
                category_name=target_category.name if target_category else "Shopping",
                transaction_date=tx_date
            )
            keyboard = build_wallet_inline_keyboard(accounts)
            send_telegram_message(bot_token, chat_id, breakdown_text, reply_markup=keyboard)

            return {
                "status": "awaiting_wallet_selection",
                "merchant": merchant_name,
                "total": float(total_amount),
                "items_count": len(items)
            }
        else:
            raw_preview = (ocr_result.get("raw_text") or "").strip()[:150]
            preview_msg = f"\n\n<i>Teks terbaca sebagian:</i>\n<code>{raw_preview}...</code>" if raw_preview else ""
            reply_text = (
                f"📸 <b>Foto Struk Diterima!</b>{preview_msg}\n\n"
                f"⚠️ Nominal total belum terdeteksi otomatis.\n"
                f"💡 <b>Tips:</b> Silakan balas pesan ini dengan mengetik nominalnya, misalnya: <code>{ocr_result.get('merchant_name', 'struk')} 45rb</code>"
            )
            send_telegram_message(bot_token, chat_id, reply_text)
            return {"status": "receipt_unclear_total"}

    # Check for multi-line transaction entry (e.g. user typed multiple items separated by newlines)
    text_lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
    if len(text_lines) > 1:
        parsed_batch = []
        for line in text_lines:
            p = parse_financial_input(line, categories, accounts)
            if p and p.get("amount"):
                parsed_batch.append((line, p))

        if len(parsed_batch) > 1:
            batch_txs = []
            total_batch_amount = Decimal("0")
            primary_account = None

            for line_str, p in parsed_batch:
                tgt_acc = db.execute(select(Account).where(Account.id == p["account_id"])).scalar_one_or_none() or accounts[0]
                primary_account = tgt_acc
                amt = p["amount"]
                if p["type"] == "INCOME":
                    tgt_acc.current_balance += amt
                else:
                    tgt_acc.current_balance -= amt
                    total_batch_amount += amt

                it_title = p.get("item_name") or p["description"]
                it_qty = p.get("qty", 1)
                it_desc = p["description"]
                if it_qty > 1 and f"({it_qty}x)" not in it_desc:
                    it_desc = f"{it_desc} ({it_qty}x)"

                tx_row = Transaction(
                    tenant_id=tenant_id,
                    account_id=tgt_acc.id,
                    category_id=p["category_id"],
                    amount=amt,
                    transaction_type=p["type"],
                    transaction_date=p.get("transaction_date") or datetime.now(timezone.utc),
                    source="TELEGRAM",
                    status="COMPLETED",
                    description=it_desc,
                    notes=f"Dicatat via Telegram (@{tg_username or tg_user_id}): \"{line_str}\"",
                    metadata_json={
                        "telegram_chat_id": chat_id,
                        "telegram_user_id": tg_user_id,
                        "raw_input": line_str,
                        "parsed_by": "telegram_smart_parser_multiline"
                    },
                    created_by=user.id
                )
                db.add(tx_row)
                batch_txs.append(tx_row)

            # Save chat log & commit
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
                    parsed_intent="RECORD_MULTIPLE_EXPENSE",
                    status="PROCESSED"
                )
                db.add(msg_record)

            db.commit()

            summary_lines = [f"• {t.description}: <b>{format_rupiah(t.amount)}</b>" for t in batch_txs]
            acc_name = primary_account.name if primary_account else "Dompet"
            acc_bal = format_rupiah(primary_account.current_balance) if primary_account else ""

            reply_text = (
                f"✅ <b>{len(batch_txs)} Transaksi Berhasil Dicatat!</b>\n\n"
                f"📋 <b>Rincian per Item:</b>\n" + "\n".join(summary_lines) + "\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"💸 <b>Total Terpotong:</b> <b>{format_rupiah(total_batch_amount)}</b> (Pengeluaran 🔴)\n"
                f"💳 Dompet: <b>{acc_name}</b>\n"
                f"💰 Sisa Saldo: <b>{acc_bal}</b>\n\n"
                f"<i>Cek di: https://pantau-duit.exavolt.net/transactions</i>"
            )
            send_telegram_message(bot_token, chat_id, reply_text)
            return {"status": "multiple_transactions_recorded", "count": len(batch_txs)}

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

    tx_date = parsed.get("transaction_date") or datetime.now(timezone.utc)
    item_title = parsed.get("item_name") or parsed["description"]
    qty = parsed.get("qty", 1)
    unit_price = parsed.get("unit_price") or parsed["amount"]

    # Format description: if qty > 1, e.g. "Soto Mi Bogor (2x)"
    desc_to_save = parsed["description"]
    if qty > 1 and f"({qty}x)" not in desc_to_save:
        desc_to_save = f"{desc_to_save} ({qty}x)"

    # Clean, structured notes
    notes_parts = []
    if qty > 1:
        notes_parts.append(f"Qty: {qty} item @ {format_rupiah(unit_price)}")
        notes_parts.append(f"Total: {format_rupiah(parsed['amount'])}")
    notes_parts.append(f"Dicatat via Telegram (@{tg_username or tg_user_id}): \"{raw_text}\"")
    notes_to_save = " | ".join(notes_parts)

    metadata_dict = {
        "telegram_chat_id": chat_id,
        "telegram_user_id": tg_user_id,
        "telegram_username": tg_username,
        "raw_input": raw_text,
        "parsed_by": "telegram_smart_parser",
        "item_name": item_title,
        "qty": qty,
        "unit_price": float(unit_price),
        "total_amount": float(parsed["amount"]),
        "date_parsed": tx_date.strftime("%Y-%m-%d")
    }

    # Create Transaction record in DB
    new_tx = Transaction(
        tenant_id=tenant_id,
        account_id=target_account.id,
        category_id=parsed["category_id"],
        amount=parsed["amount"],
        transaction_type=parsed["type"],
        transaction_date=tx_date,
        source="TELEGRAM",
        status="COMPLETED",
        description=desc_to_save,
        notes=notes_to_save,
        metadata_json=metadata_dict,
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
    date_formatted = tx_date.strftime("%d/%m/%Y")

    if qty > 1:
        unit_formatted = format_rupiah(unit_price)
        reply_text = (
            f"✅ <b>Transaksi Berhasil Dicatat!</b>\n\n"
            f"📅 Tanggal: <b>{date_formatted}</b>\n"
            f"🍲 Item: <b>{item_title}</b>\n"
            f"🔢 Jumlah: <b>{qty} porsi/item</b> (@ {unit_formatted})\n"
            f"💸 Total: <b>{nominal_formatted}</b> ({type_label})\n"
            f"🏷️ Kategori: <b>{parsed['category_name']}</b>\n"
            f"💳 Dompet: <b>{target_account.name}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Sisa Saldo <b>{target_account.name}</b>: <b>{new_bal_formatted}</b>\n\n"
            f"<i>Cek di: https://pantau-duit.exavolt.net/transactions</i>"
        )
    else:
        reply_text = (
            f"✅ <b>Transaksi Berhasil Dicatat!</b>\n\n"
            f"📅 Tanggal: <b>{date_formatted}</b>\n"
            f"📝 Item: <b>{parsed['description']}</b>\n"
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
