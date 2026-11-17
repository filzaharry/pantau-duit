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
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger("receipt_ocr")


class ReceiptOCRService:
    """
    Modular, reusable OCR engine and Indonesian receipt parser.
    Runs entirely on-premise / local CPU using Tesseract OCR.
    """

    def __init__(self, tesseract_cmd: Optional[str] = None):
        # Locate tesseract binary (default to PATH or common system locations)
        self.tesseract_cmd = tesseract_cmd or shutil.which("tesseract") or "/usr/bin/tesseract"
        self._is_available = os.path.exists(self.tesseract_cmd) if self.tesseract_cmd else False
        if not self._is_available:
            logger.warning("Tesseract binary not found. OCR features will be disabled until installed.")

    @property
    def is_available(self) -> bool:
        """Check if Tesseract OCR is installed and available on the system."""
        if not self._is_available:
            # Recheck in case it was installed dynamically
            cmd = shutil.which("tesseract") or "/usr/bin/tesseract"
            self._is_available = os.path.exists(cmd) if cmd else False
            if self._is_available:
                self.tesseract_cmd = cmd
        return self._is_available

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Enhance image quality specifically for thermal paper receipt OCR:
        - Scale up low resolution receipts
        - Grayscale conversion
        - Contrast enhancement
        - Unsharp mask sharpening
        - Binarization thresholding
        """
        # Convert to RGB if palette/RGBA
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        # Resize if width < 1200px to ensure crisp dot-matrix receipt fonts
        w, h = image.size
        if w < 1200:
            scale = 1200 / float(w)
            new_w = 1200
            new_h = int(float(h) * scale)
            image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Grayscale
        gray = image.convert("L")

        # Increase contrast
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(1.8)

        # Slight sharpening
        sharpened = enhanced.filter(ImageFilter.SHARPEN)

        # Binarization / High-contrast threshold (black text on pure white)
        # Thermal receipt papers often have grayish backgrounds
        threshold = 145
        table = [0 if i < threshold else 255 for i in range(256)]
        binarized = sharpened.point(table, "1")

        return binarized

    def extract_text(
        self,
        image_input: Union[bytes, str, Path, Image.Image],
        lang: str = "ind+eng"
    ) -> str:
        """
        Extract raw text from an image using Tesseract OCR.
        Accepts raw image bytes, a file path, or a PIL Image object.
        """
        if not self.is_available:
            raise RuntimeError(
                "Tesseract OCR is not installed on this system. "
                "Install it via: sudo apt install -y tesseract-ocr tesseract-ocr-ind"
            )

        # Load into PIL Image
        if isinstance(image_input, (str, Path)):
            img = Image.open(str(image_input))
        elif isinstance(image_input, bytes):
            img = Image.open(io.BytesIO(image_input))
        elif isinstance(image_input, Image.Image):
            img = image_input
        else:
            raise ValueError("Unsupported image input type. Provide bytes, filepath, or PIL.Image.")

        # Try with preprocessing first
        processed = self.preprocess_image(img)

        # Run OCR via pytesseract if available, else standard subprocess
        text = self._run_tesseract_cli(processed, lang=lang)

        # If preprocessing produced very little text, fallback to raw grayscale
        if len(text.strip()) < 10:
            fallback_img = img.convert("L")
            text = self._run_tesseract_cli(fallback_img, lang=lang)

        return text

    def _run_tesseract_cli(self, image: Image.Image, lang: str = "ind+eng") -> str:
        """Internal runner using pytesseract or subprocess with graceful fallback."""
        try:
            import pytesseract
            # Test if ind is available, fallback to eng if needed
            try:
                return pytesseract.image_to_string(image, lang=lang, config="--psm 6")
            except Exception:
                return pytesseract.image_to_string(image, lang="eng", config="--psm 6")
        except ImportError:
            pass

        # Subprocess fallback
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
            image.save(tmp_path, format="PNG")

        try:
            # Try ind+eng first
            cmd = [self.tesseract_cmd, tmp_path, "stdout", "-l", lang, "--psm", "6"]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            if res.returncode != 0:
                # Fallback to English only
                cmd = [self.tesseract_cmd, tmp_path, "stdout", "-l", "eng", "--psm", "6"]
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
        - Line items (if clearly detected)
        """
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

        total_amount: Optional[Decimal] = None
        subtotal_amount: Optional[Decimal] = None
        tax_amount: Optional[Decimal] = None
        parsed_date: Optional[datetime] = None
        merchant_name: str = "Struk Pembelian"
        category_hint: str = "Shopping"
        items: List[Dict[str, Any]] = []

        # 1. Extract Merchant Name (usually in lines 0 to 4)
        junk_headers = [
            "selamat datang", "terima kasih", "struk", "nota", "faktur",
            "kasir", "jl.", "jalan", "telp", "no.", "npwp", "tax", "pos"
        ]
        known_merchants = {
            "Indomaret": "Shopping",
            "Alfamart": "Shopping",
            "Alfamidi": "Shopping",
            "Superindo": "Shopping",
            "Hypermart": "Shopping",
            "Transmart": "Shopping",
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
            "Gramedia": "Shopping",
            "Ace Hardware": "Shopping",
            "Mitra10": "Shopping"
        }

        # Check known merchants across whole text first
        full_lower = raw_text.lower()
        for k_merch, cat in known_merchants.items():
            if re.search(r"\b" + re.escape(k_merch.lower()) + r"\b", full_lower):
                merchant_name = k_merch
                category_hint = cat
                break

        # If not a known brand, use first clean header line
        if merchant_name == "Struk Pembelian" and lines:
            for line in lines[:5]:
                l_low = line.lower()
                if len(line) >= 3 and not any(j in l_low for j in junk_headers):
                    clean_name = re.sub(r"[^a-zA-Z0-9\s&.-]", "", line).strip()
                    if len(clean_name) >= 3:
                        merchant_name = clean_name.title()
                        break

        # 2. Extract Transaction Date & Time
        # Pattern 1: dd/mm/yyyy or dd-mm-yyyy or yyyy-mm-dd
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

        # 3. Extract Amounts (Scan backwards from bottom lines where totals reside)
        def clean_number(num_str: str) -> Optional[Decimal]:
            try:
                # Remove spaces and currency symbols
                clean = re.sub(r"[^\d.,]", "", num_str)
                # Indonesian receipts often use dots for thousands: 45.000 or commas 45.000,00
                if "," in clean and "." in clean:
                    # 45.000,00
                    clean = clean.replace(".", "").replace(",", ".")
                elif "." in clean:
                    # Check if dot is thousands: 45.000 or decimal 45.50
                    parts = clean.split(".")
                    if len(parts[-1]) == 3 or len(parts) > 2:
                        clean = clean.replace(".", "")
                    else:
                        clean = clean.replace(".", "")
                elif "," in clean:
                    clean = clean.replace(",", "")
                val = int(float(clean))
                return Decimal(str(val)) if val > 0 else None
            except Exception:
                return None

        # Priority 1: Lines explicitly stating Total / Grand Total / Tagihan / Bayar
        total_keywords = [
            "grand total", "total belanja", "total bayar", "total akhir",
            "harga total", "jml total", "jumlah total", "total tagihan",
            "total", "tagihan"
        ]
        payment_keywords = ["tunai", "cash", "debit", "qris", "gopay", "ovo", "shopeepay", "bca", "mandiri", "bri"]
        subtotal_keywords = ["subtotal", "sub total", "jumlah belanja", "jumlah harga"]

        # Search from bottom to top
        for line in reversed(lines):
            l_low = line.lower()

            # Check Total line
            if total_amount is None:
                for t_kw in total_keywords:
                    if re.search(r"\b" + re.escape(t_kw) + r"\b", l_low):
                        # Find all numbers in this line
                        num_matches = re.findall(r"(\d+[\d.,]*)", line)
                        if num_matches:
                            val = clean_number(num_matches[-1])
                            if val and val > 100:
                                total_amount = val
                                break

            # Check Subtotal line
            if subtotal_amount is None:
                for s_kw in subtotal_keywords:
                    if re.search(r"\b" + re.escape(s_kw) + r"\b", l_low):
                        num_matches = re.findall(r"(\d+[\d.,]*)", line)
                        if num_matches:
                            val = clean_number(num_matches[-1])
                            if val and val > 100:
                                subtotal_amount = val
                                break

            # Check Tax / PPN line
            if tax_amount is None and ("ppn" in l_low or "pajak" in l_low or "tax" in l_low):
                num_matches = re.findall(r"(\d+[\d.,]*)", line)
                if num_matches:
                    val = clean_number(num_matches[-1])
                    if val:
                        tax_amount = val

        # Fallback 1: If total not found, check payment line (Tunai / QRIS / Cash)
        if total_amount is None:
            for line in reversed(lines):
                l_low = line.lower()
                for p_kw in payment_keywords:
                    if re.search(r"\b" + re.escape(p_kw) + r"\b", l_low):
                        num_matches = re.findall(r"(\d+[\d.,]*)", line)
                        if num_matches:
                            val = clean_number(num_matches[-1])
                            if val and val > 100:
                                total_amount = val
                                break
                if total_amount:
                    break

        # Fallback 2: Subtotal as total
        if total_amount is None and subtotal_amount is not None:
            total_amount = subtotal_amount

        # Fallback 3: Largest number in the entire receipt >= 1000
        if total_amount is None:
            all_numbers = re.findall(r"\b(\d{1,3}(?:\.\d{3})+|\d{4,})\b", raw_text)
            candidates = []
            for num in all_numbers:
                val = clean_number(num)
                if val and val >= 1000:
                    candidates.append(val)
            if candidates:
                # Typically the total is the maximum number or close to it
                total_amount = max(candidates)

        # 4. Infer Category if not matched by merchant
        if category_hint == "Shopping":
            food_words = ["makan", "minum", "kopi", "cafe", "mie", "soto", "bakso", "nasi", "ayam", "snack", "resto"]
            transport_words = ["bensin", "spbu", "pertamax", "pertalite", "shell", "solar", "parkir", "tol"]
            health_words = ["obat", "apotek", "farmasi", "vitamin", "klinik", "dokter", "resep"]
            bills_words = ["listrik", "pln", "pdam", "air", "pulsa", "kuota", "wifi", "indihome"]

            if any(w in full_lower for w in food_words):
                category_hint = "Food & Beverage"
            elif any(w in full_lower for w in transport_words):
                category_hint = "Transportation"
            elif any(w in full_lower for w in health_words):
                category_hint = "Health"
            elif any(w in full_lower for w in bills_words):
                category_hint = "Utilities & Bills"

        return {
            "merchant_name": merchant_name,
            "total_amount": total_amount,
            "subtotal_amount": subtotal_amount,
            "tax_amount": tax_amount,
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

        # Optimize & save as JPEG using Pillow
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(full_path, format="JPEG", quality=85)
        except Exception:
            # Direct binary write fallback
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

        # Extract bytes if needed for saving
        if isinstance(image_input, bytes):
            raw_bytes = image_input
        elif isinstance(image_input, (str, Path)) and os.path.exists(image_input):
            with open(image_input, "rb") as f:
                raw_bytes = f.read()

        # Save to disk if requested
        if save_dir and raw_bytes:
            filename, file_path_saved = self.save_receipt_file(raw_bytes, save_dir)
            if base_url:
                clean_base = base_url.rstrip("/")
                receipt_url = f"{clean_base}/{filename}"
            else:
                receipt_url = f"/uploads/receipts/{filename}"

        # Run OCR
        try:
            raw_text = self.extract_text(image_input)
            ocr_success = bool(raw_text.strip())
        except Exception as e:
            logger.error(f"Receipt OCR extraction failed: {e}")
            raw_text = ""
            ocr_success = False

        # Parse Entities
        parsed = self.parse_receipt_text(raw_text)

        return {
            "success": ocr_success and (parsed["total_amount"] is not None),
            "ocr_success": ocr_success,
            "merchant_name": parsed["merchant_name"],
            "total_amount": parsed["total_amount"],
            "subtotal_amount": parsed["subtotal_amount"],
            "tax_amount": parsed["tax_amount"],
            "transaction_date": parsed["transaction_date"],
            "category_hint": parsed["category_hint"],
            "items": parsed["items"],
            "receipt_url": receipt_url,
            "file_path": str(file_path_saved) if file_path_saved else None,
            "raw_text": raw_text
        }


# Global singleton instance for easy import across any module
receipt_ocr_service = ReceiptOCRService()
