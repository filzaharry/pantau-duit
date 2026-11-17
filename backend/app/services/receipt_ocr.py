"""
Reusable Receipt OCR & Information Extraction Service.
100% Free & Open-Source (Uses local Tesseract OCR & Pillow).
Zero Paid AI / Zero API Tokens required.

Can be reused across:
- Telegram Bot (@pd_exavolt_bot) for instant photo receipt logging
- Web App Reimbursement Claim Receipts
- Web App Direct Transaction Photo Uploads
- Dedicated REST API Endpoints
"""

import io
import os
import re
import shutil
import logging
import subprocess
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Tuple
from PIL import Image, ImageOps, ImageFilter

logger = logging.getLogger("receipt_ocr")


class ReceiptOCRService:
    """
    Modular, reusable OCR engine and Indonesian receipt parser.
    Runs entirely on-premise / local CPU using Tesseract OCR.
    """

    def __init__(self, tesseract_cmd: Optional[str] = None):
        self.tesseract_cmd = tesseract_cmd or shutil.which("tesseract") or "/usr/bin/tesseract"
        self._is_available = os.path.exists(self.tesseract_cmd) if self.tesseract_cmd else False

    @property
    def is_available(self) -> bool:
        """Check if Tesseract OCR is installed and available on the system."""
        if not self._is_available:
            cmd = shutil.which("tesseract") or "/usr/bin/tesseract"
            self._is_available = os.path.exists(cmd) if cmd else False
            if self._is_available:
                self.tesseract_cmd = cmd
        return self._is_available

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Normalize image for OCR.
        Preserves original scale unless image is tiny (< 400px width).
        Avoids interpolation blur on stylized bold headers.
        """
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        # Only scale up if extremely small (< 400px)
        w, h = image.size
        if w < 400:
            scale = 800 / float(w)
            new_w = 800
            new_h = int(float(h) * scale)
            image = image.resize((new_w, new_h), Image.Resampling.BILINEAR)

        return image

    def extract_text(
        self,
        image_input: Union[bytes, str, Path, Image.Image],
        lang: str = "ind+eng"
    ) -> str:
        """
        Extract raw text from an image using Tesseract OCR.
        Accepts raw image bytes, a file path, or a PIL Image object.
        Uses a two-pass approach:
        - Pass 1: Clean normalized image
        - Pass 2: Grayscale with auto-contrast (fallback if Pass 1 is too short)
        """
        if not self.is_available:
            raise RuntimeError(
                "Tesseract OCR is not installed on this system. "
                "Install it via: sudo apt install -y tesseract-ocr tesseract-ocr-ind"
            )

        if isinstance(image_input, (str, Path)):
            img = Image.open(str(image_input))
        elif isinstance(image_input, bytes):
            img = Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, Image.Image):
            img = image_input
        else:
            raise ValueError("Unsupported image input type. Provide bytes, filepath, or PIL.Image.")

        # Pass 1: Clean normalized image
        processed = self.preprocess_image(img)
        text = self._run_tesseract_cli(processed, lang=lang)

        # Pass 2: If Pass 1 yielded little text, try gentle autocontrast grayscale
        if len(text.strip()) < 25:
            try:
                gray = ImageOps.autocontrast(img.convert("L"))
                text_pass2 = self._run_tesseract_cli(gray, lang=lang)
                if len(text_pass2.strip()) > len(text.strip()):
                    text = text_pass2
            except Exception:
                pass

        return text

    def _run_tesseract_cli(self, image: Image.Image, lang: str = "ind+eng") -> str:
        """Internal runner using pytesseract or subprocess with graceful fallback."""
        try:
            import pytesseract
            try:
                return pytesseract.image_to_string(image, lang=lang)
            except Exception:
                return pytesseract.image_to_string(image, lang="eng")
        except ImportError:
            pass

        # Subprocess fallback
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
            image.save(tmp_path, format="PNG")

        try:
            cmd = [self.tesseract_cmd, tmp_path, "stdout", "-l", lang]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if res.returncode != 0:
                cmd = [self.tesseract_cmd, tmp_path, "stdout", "-l", "eng"]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            return res.stdout or ""
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def parse_receipt_text(self, raw_text: str) -> Dict[str, Any]:
        """
        Extract structured receipt entities from raw Indonesian OCR text:
        - Merchant name
        - Total amount (Rupiah)
        - Subtotal / Tax
        - Transaction date & time
        - Category suggestion
        - Line items
        """
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        total_amount: Optional[Decimal] = None
        subtotal_amount: Optional[Decimal] = None
        tax_amount: Optional[Decimal] = None
        parsed_date: Optional[datetime] = None
        merchant_name: str = "Struk Pembelian"
        category_hint: str = "Shopping"
        items: List[Dict[str, Any]] = []

        # Lines that contain non-monetary reference/ID data
        reference_line_keywords = [
            "no :", "no.", "nomor", "ref", "trx", "invoice", "order",
            "pax", "kasir", "npwp", "telp", "phone", "antrian", "id:"
        ]

        # Helper to clean Rupiah number string into Decimal
        def clean_idr_number(num_str: str) -> Optional[Decimal]:
            clean = re.sub(r"[^\d.,]", "", num_str)
            if "," in clean and "." in clean:
                clean = clean.replace(".", "").replace(",", ".")
            elif "." in clean:
                parts = clean.split(".")
                if len(parts[-1]) in (2, 3) or len(parts) > 2:
                    clean = clean.replace(".", "")
            elif "," in clean:
                parts = clean.split(",")
                if len(parts[-1]) in (2, 3) or len(parts) > 2:
                    clean = clean.replace(",", "")
            try:
                val = int(float(clean))
                # Sanity limit for retail consumer receipts: Rp 500 up to Rp 100.000.000
                if 500 <= val <= 100_000_000:
                    return Decimal(str(val))
            except Exception:
                pass
            return None

        def extract_numbers_from_line(line: str) -> List[Decimal]:
            # Handles spaced dots/commas e.g. "69. 020" or "69, 020" or "69,000"
            raw_matches = re.findall(r"(\d+(?:\s*[.,]\s*\d+)+|\d{3,})", line)
            nums = []
            for rm in raw_matches:
                norm = re.sub(r"\s*([.,])\s*", r"\1", rm)
                val = clean_idr_number(norm)
                if val is not None:
                    nums.append(val)
            return nums

        # 1. Merchant Name Extraction
        known_merchants = {
            "Indomaret": "Shopping",
            "Alfamart": "Shopping",
            "Alfamidi": "Shopping",
            "Superindo": "Shopping",
            "Hypermart": "Shopping",
            "Transmart": "Shopping",
            "Toko Kopi Manusia": "Food & Beverage",
            "Tokokopimanusia": "Food & Beverage",
            "SPBU Pertamina": "Transportation",
            "Pertamina": "Transportation",
            "Shell": "Transportation",
            "BP-AKR": "Transportation",
            "Starbucks": "Food & Beverage",
            "Kopi Kenangan": "Food & Beverage",
            "Janji Jiwa": "Food & Beverage",
            "Point Coffee": "Food & Beverage",
            "McDonald's": "Food & Beverage",
            "KFC": "Food & Beverage",
            "Hokben": "Food & Beverage",
            "Pizza Hut": "Food & Beverage",
            "Burger King": "Food & Beverage",
            "Bakso": "Food & Beverage",
            "Soto": "Food & Beverage",
            "Mie Gacoan": "Food & Beverage",
            "Apotek K-24": "Health",
            "Kimia Farma": "Health",
            "Guardian": "Health",
            "Watson": "Health",
            "Century": "Health",
            "Gramedia": "Shopping"
        }

        full_lower = raw_text.lower()
        for k_merch, cat in known_merchants.items():
            if k_merch.lower().replace(" ", "") in full_lower.replace(" ", "") or k_merch.lower() in full_lower:
                merchant_name = k_merch
                category_hint = cat
                break

        # Handle OCR typo on Toko Kopi Manusia (e.g. TOKOKDPIMANUSIA)
        if "kopimanusia" in full_lower.replace("d", "o") or "tokokopi" in full_lower.replace("d", "o"):
            merchant_name = "Toko Kopi Manusia"
            category_hint = "Food & Beverage"

        # If not known, use first clean header line
        junk_headers = [
            "selamat datang", "terima kasih", "struk", "nota", "faktur",
            "kasir", "jl.", "jalan", "telp", "no.", "npwp", "tax", "pos"
        ]
        if merchant_name == "Struk Pembelian" and lines:
            for line in lines[:5]:
                l_low = line.lower()
                if len(line) >= 3 and not any(j in l_low for j in (junk_headers + reference_line_keywords)):
                    clean_name = re.sub(r"[^a-zA-Z0-9\s&.-]", "", line).strip()
                    if len(clean_name) >= 3:
                        merchant_name = clean_name.title()
                        break

        # 2. Extract Transaction Date & Time
        date_match = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b", raw_text)
        time_match = re.search(r"\b(\d{1,2}):(\d{2})(?::(\d{2}))?\b", raw_text)

        hour, minute, second = 12, 0, 0
        if time_match:
            try:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                second = int(time_match.group(3)) if time_match.group(3) else 0
            except Exception:
                pass

        if date_match:
            try:
                d = int(date_match.group(1))
                m = int(date_match.group(2))
                y = int(date_match.group(3))
                if y < 100:
                    y += 2000
                parsed_date = datetime(y, m, d, hour, minute, second, tzinfo=timezone.utc)
            except Exception:
                pass

        # 3. Extract Amounts & Line Items
        header_patterns = [
            r"\b(?:tanggal|date|waktu|time|jam)\b",
            r"\b(?:no|nomor|order|invoice|inv|trx|kasir|cashier|pax|table|meja|antrian)\s*[:.]?",
            r"\b(?:dine\s*in|take\s*away|takeaway|info|mode)\b",
            r"\b(?:jl\.|jalan|telp|phone|npwp|selamat\s+datang|terima\s+kasih)\b"
        ]

        summary_patterns = [
            r"\b(?:bayar|total|subtotal|sub\s*total|grand\s*total|total\s*belanja|total\s*akhir|total\s*bayar|total\s*tagihan|harga\s*jual|tagihan)\b",
            r"\b(?:tunai|cash|kembalian|kembali|change)\b",
            r"\b(?:edc|bca|mandiri|bri|bni|qris|debit|kredit|gopay|ovo|dana|shopeepay)\b",
            r"\b\d+\s*item\b"
        ]

        tax_keywords = [
            "pb1", "pb 1", "ppn", "pajak", "tax", "service", "sc", "service charge"
        ]

        discount_keywords = [
            "diskon", "discount", "potongan", "hemat"
        ]

        taxes: List[Dict[str, Any]] = []
        discounts: List[Dict[str, Any]] = []

        # 3.1 Extract Line Items, Taxes, and Discounts
        i = 0
        n = len(lines)
        while i < n:
            line = lines[i]
            l_low = line.lower()
            norm_line = re.sub(r"\s*([.,])\s*", r"\1", line)

            # Check for taxes/fees
            is_tax = False
            for tkw in tax_keywords:
                if re.search(r"\b" + re.escape(tkw) + r"\b", l_low):
                    nums = extract_numbers_from_line(line)
                    if nums:
                        tax_name = line.split(":")[0].strip() if ":" in line else line.strip(" -:*•")
                        taxes.append({
                            "name": tax_name,
                            "amount": nums[-1]
                        })
                        is_tax = True
                        break
            if is_tax:
                i += 1
                continue

            # Check for discounts
            is_disc = False
            for dkw in discount_keywords:
                if re.search(r"\b" + re.escape(dkw) + r"\b", l_low):
                    nums = extract_numbers_from_line(line)
                    if nums:
                        disc_name = line.split(":")[0].strip() if ":" in line else line.strip(" -:*•")
                        discounts.append({
                            "name": disc_name,
                            "amount": nums[-1]
                        })
                        is_disc = True
                        break
            if is_disc:
                i += 1
                continue

            # Skip headers
            if any(re.search(hp, l_low) for hp in header_patterns):
                i += 1
                continue

            # Skip summary lines
            if any(re.search(sp, l_low) for sp in summary_patterns):
                i += 1
                continue

            # Case 1: Two-line item:
            # line i: Item name (e.g. "AMERICANO. ICE")
            # line i+1: "1x @38.570 38.570" or "1x 038.570 38.570" or "3 x 15.000 45.000"
            if i + 1 < n:
                next_line = lines[i + 1]
                next_norm = re.sub(r"\s*([.,])\s*", r"\1", next_line)
                m_qty_price = re.match(
                    r"^(\d+)\s*x\s*(?:[@oO0]?\s*(\d+(?:[.,]\d+)*))?\s*=?\s*(\d+(?:[.,]\d+)*)$",
                    next_norm,
                    re.IGNORECASE
                )
                if m_qty_price:
                    qty_val = max(1, int(m_qty_price.group(1)))
                    unit_raw = m_qty_price.group(2)
                    tot_raw = m_qty_price.group(3)
                    tot_num = clean_idr_number(tot_raw)
                    unit_cleaned = re.sub(r"^0+(?=\d)", "", unit_raw) if unit_raw else None
                    unit_num = clean_idr_number(unit_cleaned) if unit_cleaned else (tot_num / qty_val if tot_num else None)
                    if tot_num and len(line) >= 2:
                        items.append({
                            "name": line.strip(" -:*•"),
                            "qty": qty_val,
                            "unit_price": unit_num or (tot_num / qty_val),
                            "total_price": tot_num
                        })
                        i += 2
                        continue

            # Case 2: Inline item with qty and total: "Soto Sapi Bungkus 3 x 15.000 45.000"
            m_inline_qty = re.search(
                r"^(.*?)\s+(\d+)\s*x\s*(?:[@oO0]?\s*(\d+(?:[.,]\d+)*))?\s*=?\s*(\d+(?:[.,]\d+)*)$",
                norm_line,
                re.IGNORECASE
            )
            if m_inline_qty:
                item_name = m_inline_qty.group(1).strip(" -:*•")
                qty_val = max(1, int(m_inline_qty.group(2)))
                unit_raw = m_inline_qty.group(3)
                tot_raw = m_inline_qty.group(4)
                tot_num = clean_idr_number(tot_raw)
                unit_cleaned = re.sub(r"^0+(?=\d)", "", unit_raw) if unit_raw else None
                unit_num = clean_idr_number(unit_cleaned) if unit_cleaned else (tot_num / qty_val if tot_num else None)
                if tot_num and len(item_name) >= 2 and not any(re.search(sp, item_name.lower()) for sp in summary_patterns):
                    items.append({
                        "name": item_name,
                        "qty": qty_val,
                        "unit_price": unit_num or (tot_num / qty_val),
                        "total_price": tot_num
                    })
                    i += 1
                    continue

            # Case 3: Prefix qty: "2x SOTO MIE BOGOR 40.000"
            m_prefix_qty = re.match(
                r"^(\d+)\s*x\s+(.*?)\s+(\d+(?:[.,]\d+)+)$",
                norm_line,
                re.IGNORECASE
            )
            if m_prefix_qty:
                qty_val = max(1, int(m_prefix_qty.group(1)))
                item_name = m_prefix_qty.group(2).strip(" -:*•")
                tot_raw = m_prefix_qty.group(3)
                tot_num = clean_idr_number(tot_raw)
                if tot_num and len(item_name) >= 2 and not any(re.search(sp, item_name.lower()) for sp in summary_patterns):
                    items.append({
                        "name": item_name,
                        "qty": qty_val,
                        "unit_price": tot_num / qty_val,
                        "total_price": tot_num
                    })
                    i += 1
                    continue

            # Case 4: Retail minimarket format: "ULTRA MILK COKLAT 250ML 1 7.200"
            m_retail = re.search(r"^(.*?)\s+(\d{1,2})\s+(\d+(?:[.,]\d+)+)$", norm_line)
            if m_retail:
                item_name = m_retail.group(1).strip(" -:*•")
                qty_val = max(1, int(m_retail.group(2)))
                tot_raw = m_retail.group(3)
                tot_num = clean_idr_number(tot_raw)
                if tot_num and len(item_name) >= 2 and not any(re.search(sp, item_name.lower()) for sp in summary_patterns):
                    items.append({
                        "name": item_name,
                        "qty": qty_val,
                        "unit_price": tot_num / qty_val,
                        "total_price": tot_num
                    })
                    i += 1
                    continue

            # Case 5: Simple item line: "Item Name 25.000"
            m_simple = re.search(r"^(.*?)\s+(\d+(?:[.,]\d+)+)$", norm_line)
            if m_simple:
                item_name = m_simple.group(1).strip(" -:*•")
                tot_raw = m_simple.group(2)
                tot_num = clean_idr_number(tot_raw)
                if (
                    tot_num
                    and len(item_name) >= 3
                    and not any(re.search(sp, item_name.lower()) for sp in summary_patterns)
                    and not any(re.search(hp, item_name.lower()) for hp in header_patterns)
                ):
                    items.append({
                        "name": item_name,
                        "qty": 1,
                        "unit_price": tot_num,
                        "total_price": tot_num
                    })
                    i += 1
                    continue

            i += 1

        # 3.2 Extract Grand Totals (Scan backwards from bottom lines)
        total_keywords = [
            "grand total", "total belanja", "total bayar", "total akhir",
            "harga total", "jml total", "jumlah total", "total tagihan",
            "total", "tagihan"
        ]
        payment_keywords = ["edc", "qris", "tunai", "cash", "debit", "gopay", "ovo", "shopeepay", "bca", "mandiri", "bri"]
        subtotal_keywords = ["subtotal", "sub total", "jumlah belanja", "jumlah harga"]

        detected_amounts: List[Tuple[str, Decimal]] = []

        # Check explicitly labelled Total lines
        for line in reversed(lines):
            l_low = line.lower()
            if any(r in l_low for r in reference_line_keywords):
                continue
            if any(re.search(r"\b" + re.escape(t_kw) + r"\b", l_low) for t_kw in total_keywords):
                nums = extract_numbers_from_line(line)
                if nums:
                    detected_amounts.append(("TOTAL_LINE", nums[-1]))
                    break

        # Check Payment line (EDC / BCA / QRIS / Cash / Tunai)
        for line in reversed(lines):
            l_low = line.lower()
            if any(r in l_low for r in reference_line_keywords):
                continue
            if any(re.search(r"\b" + re.escape(p_kw) + r"\b", l_low) for p_kw in payment_keywords):
                nums = extract_numbers_from_line(line)
                if nums:
                    detected_amounts.append(("PAYMENT_LINE", nums[-1]))
                    break

        # Check Subtotal line
        for line in reversed(lines):
            l_low = line.lower()
            if any(r in l_low for r in reference_line_keywords):
                continue
            if any(re.search(r"\b" + re.escape(s_kw) + r"\b", l_low) for s_kw in subtotal_keywords):
                nums = extract_numbers_from_line(line)
                if nums:
                    subtotal_amount = nums[-1]
                    detected_amounts.append(("SUBTOTAL_LINE", nums[-1]))
                    break

        # Reconcile detected amounts
        edc_val = next((val for label, val in detected_amounts if label == "PAYMENT_LINE"), None)
        total_val = next((val for label, val in detected_amounts if label == "TOTAL_LINE"), None)
        sub_val = next((val for label, val in detected_amounts if label == "SUBTOTAL_LINE"), None)

        if edc_val and sub_val and edc_val == sub_val:
            total_amount = edc_val
        elif total_val and edc_val and abs(total_val - edc_val) <= 100:
            total_amount = edc_val
        elif total_val:
            total_amount = total_val
        elif edc_val:
            total_amount = edc_val
        elif sub_val:
            total_amount = sub_val

        # Fallback: Scan lines from bottom for first valid amount not on a reference line
        if total_amount is None:
            for line in reversed(lines):
                l_low = line.lower()
                if any(r in l_low for r in reference_line_keywords):
                    continue
                nums = extract_numbers_from_line(line)
                if nums:
                    total_amount = nums[-1]
                    break

        # Reconcile subtotal & taxes
        if taxes and tax_amount is None:
            tax_amount = sum(t["amount"] for t in taxes)

        if subtotal_amount is None and items:
            subtotal_amount = sum(it["total_price"] for it in items)

        if total_amount is None and subtotal_amount:
            total_amount = subtotal_amount + (tax_amount or Decimal("0")) - sum(d["amount"] for d in discounts)

        # 4. Infer Category
        if any(k in full_lower for k in ["kopi", "coffee", "americano", "latte", "goreng", "resto", "makan", "soto", "mie", "bakso"]):
            category_hint = "Food & Beverage"
        elif any(k in full_lower for k in ["bensin", "spbu", "pertamax", "pertalite", "shell", "solar"]):
            category_hint = "Transportation"
        elif any(k in full_lower for k in ["obat", "apotek", "farmasi", "vitamin", "klinik", "dokter"]):
            category_hint = "Health"
        elif any(k in full_lower for k in ["listrik", "pln", "pdam", "air", "pulsa", "kuota"]):
            category_hint = "Utilities & Bills"

        return {
            "merchant_name": merchant_name,
            "total_amount": total_amount,
            "subtotal_amount": subtotal_amount,
            "tax_amount": tax_amount,
            "taxes": taxes,
            "discounts": discounts,
            "transaction_date": parsed_date or datetime.now(timezone.utc),
            "category_hint": category_hint,
            "items": items,
            "raw_text": raw_text
        }

    def save_receipt_file(
        self,
        image_bytes: bytes,
        destination_dir: Union[str, Path],
        filename_prefix: str = "receipt"
    ) -> Tuple[str, Path]:
        """
        Save receipt image to server disk.
        Returns:
            (relative_url_path, absolute_file_path)
        """
        dest_path = Path(destination_dir)
        dest_path.mkdir(parents=True, exist_ok=True)

        unique_id = uuid.uuid4().hex[:12]
        filename = f"{filename_prefix}_{unique_id}.jpg"
        full_path = dest_path / filename

        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(full_path, format="JPEG", quality=85)
        except Exception:
            with open(full_path, "wb") as f:
                f.write(image_bytes)

        return filename, full_path

    def process_receipt(
        self,
        image_input: Union[bytes, str, Path, Image.Image],
        save_dir: Optional[Union[str, Path]] = None,
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete end-to-end receipt processing pipeline:
        1. Saves receipt image to local directory (if save_dir provided)
        2. Executes local Tesseract OCR
        3. Parses structured receipt information
        4. Returns consolidated result dictionary
        """
        file_path_saved: Optional[Path] = None
        receipt_url: Optional[str] = None
        raw_bytes: Optional[bytes] = None

        if isinstance(image_input, bytes):
            raw_bytes = image_input
        elif isinstance(image_input, (str, Path)) and os.path.exists(image_input):
            with open(image_input, "rb") as f:
                raw_bytes = f.read()

        if save_dir and raw_bytes:
            filename, file_path_saved = self.save_receipt_file(raw_bytes, save_dir)
            if base_url:
                clean_base = base_url.rstrip("/")
                receipt_url = f"{clean_base}/{filename}"
            else:
                receipt_url = f"/uploads/receipts/{filename}"

        try:
            raw_text = self.extract_text(image_input)
            ocr_success = bool(raw_text.strip())
        except Exception as e:
            logger.error(f"Receipt OCR extraction failed: {e}")
            raw_text = ""
            ocr_success = False

        parsed = self.parse_receipt_text(raw_text)

        return {
            "success": ocr_success and (parsed["total_amount"] is not None),
            "ocr_success": ocr_success,
            "merchant_name": parsed["merchant_name"],
            "total_amount": parsed["total_amount"],
            "subtotal_amount": parsed["subtotal_amount"],
            "tax_amount": parsed["tax_amount"],
            "taxes": parsed.get("taxes", []),
            "discounts": parsed.get("discounts", []),
            "transaction_date": parsed["transaction_date"],
            "category_hint": parsed["category_hint"],
            "items": parsed["items"],
            "receipt_url": receipt_url,
            "file_path": str(file_path_saved) if file_path_saved else None,
            "raw_text": raw_text
        }


# Global singleton instance for easy import across any module
receipt_ocr_service = ReceiptOCRService()
