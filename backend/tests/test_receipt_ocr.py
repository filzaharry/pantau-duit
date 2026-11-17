import pytest
from decimal import Decimal
from datetime import datetime, timezone
from app.services.receipt_ocr import receipt_ocr_service

def test_parse_toko_kopi_manusia_receipt():
    sample_text = """
    TOKOKDPIMANUSIA

    No + TKMKBO1 20261 1170018
    Tanggal.» 17-11-2026 09:36
    Info revi l2a.6)

    Mode : DINE IN

    Pax TI

    Kasir + KASIRKB

    AMERICANO. ICE

    1x 038.570 38. 570
    KENTANG GORENG AROMA

    1x 030, 450 30. 450

    Subtotal : 69. 020
    Grand Total: 69,000
    EDC - BCA : 69, 020

    Nonor antrian
    18

    Tunggu nomor kamu dipanggi I
    """
    result = receipt_ocr_service.parse_receipt_text(sample_text)
    assert result["merchant_name"] == "Toko Kopi Manusia"
    assert result["total_amount"] == Decimal("69020")
    assert result["category_hint"] == "Food & Beverage"
    assert result["transaction_date"].day == 17
    assert result["transaction_date"].month == 11
    assert result["transaction_date"].year == 2026
    assert len(result["items"]) == 2
    assert result["items"][0]["name"] == "AMERICANO. ICE"
    assert result["items"][0]["qty"] == 1
    assert result["items"][0]["total_price"] == Decimal("38570")
    assert result["items"][1]["name"] == "KENTANG GORENG AROMA"
    assert result["items"][1]["qty"] == 1
    assert result["items"][1]["total_price"] == Decimal("30450")

def test_parse_indomaret_receipt():
    sample_text = """
    INDOMARET KEBON JERUK
    JL. PANJANG NO. 12
    TGL: 17/11/2026 14:20:00 KASIR: BUDI
    ------------------------------------
    ROTI TAWAR SARI ROTI    1   15.000
    ULTRA MILK 250ML        2   14.000
    AQUA 600ML              1    4.000
    ------------------------------------
    SUBTOTAL                    33.000
    PPN 11%                      3.630
    TOTAL                       36.630
    TUNAI                       50.000
    KEMBALIAN                   13.370
    TERIMA KASIH
    """
    result = receipt_ocr_service.parse_receipt_text(sample_text)
    assert result["merchant_name"] == "Indomaret"
    assert result["total_amount"] == Decimal("36630")
    assert result["subtotal_amount"] == Decimal("33000")
    assert result["category_hint"] == "Shopping"
    assert result["transaction_date"].day == 17
    assert result["transaction_date"].month == 11
    assert result["transaction_date"].year == 2026
    assert len(result["items"]) == 3
    assert result["items"][0]["name"] == "ROTI TAWAR SARI ROTI"
    assert result["items"][0]["qty"] == 1
    assert result["items"][0]["total_price"] == Decimal("15000")
    assert result["items"][1]["name"] == "ULTRA MILK 250ML"
    assert result["items"][1]["qty"] == 2
    assert result["items"][1]["total_price"] == Decimal("14000")
    assert result["items"][2]["name"] == "AQUA 600ML"
    assert result["items"][2]["qty"] == 1
    assert result["items"][2]["total_price"] == Decimal("4000")
    assert len(result["taxes"]) == 1
    assert result["taxes"][0]["amount"] == Decimal("3630")

def test_parse_spbu_pertamina_receipt():
    sample_text = """
    SPBU PERTAMINA 34-12345
    JL. RAYA BOGOR KM 28
    16-11-2026 09:15
    PRODUK : PERTAMAX
    LITER  : 15.00
    HARGA/L: 12.950
    TOTAL  : Rp 194.250
    PEMBAYARAN: QRIS
    """
    result = receipt_ocr_service.parse_receipt_text(sample_text)
    assert "Pertamina" in result["merchant_name"]
    assert result["total_amount"] == Decimal("194250")
    assert result["category_hint"] == "Transportation"
    assert result["transaction_date"].day == 16
    assert result["transaction_date"].month == 11

def test_parse_soto_resto_receipt():
    sample_text = """
    SOTO MIE BOGOR PAK KUMIS
    TANGGAL: 17/11/2026
    2x SOTO MIE BOGOR   40.000
    1x ES TEH MANIS      5.000
    GRAND TOTAL         45.000
    BAYAR               50.000
    KEMBALI              5.000
    """
    result = receipt_ocr_service.parse_receipt_text(sample_text)
    assert "Soto" in result["merchant_name"]
    assert result["total_amount"] == Decimal("45000")
    assert result["category_hint"] == "Food & Beverage"
    assert len(result["items"]) == 2
    assert result["items"][0]["name"] == "SOTO MIE BOGOR"
    assert result["items"][0]["qty"] == 2
    assert result["items"][0]["total_price"] == Decimal("40000")
    assert result["items"][1]["name"] == "ES TEH MANIS"
    assert result["items"][1]["qty"] == 1
    assert result["items"][1]["total_price"] == Decimal("5000")

def test_parse_soto_with_pb1_tax():
    sample_text = """
    WARUNG SOTO BOGOR
    Tanggal: 17/11/2026 13:45
    Kasir: 01

    Soto Sapi Bungkus
    3 x 15.000 45.000
    Nasi Putih
    3 x 6.000 18.000
    Es Teh Manis
    3 x 5.000 15.000
    Kerupuk Kaleng
    4 x 2.000 8.000
    Soto Ayam Komplit
    2 x 16.000 32.000

    Subtotal: 118.000
    PB1 (10%): 11.800
    Grand Total: 129.800
    Tunai: 150.000
    Kembali: 20.200
    """
    result = receipt_ocr_service.parse_receipt_text(sample_text)
    assert result["total_amount"] == Decimal("129800")
    assert result["subtotal_amount"] == Decimal("118000")
    assert len(result["taxes"]) == 1
    assert result["taxes"][0]["amount"] == Decimal("11800")
    assert len(result["items"]) == 5
    assert result["items"][0]["name"] == "Soto Sapi Bungkus"
    assert result["items"][0]["qty"] == 3
    assert result["items"][0]["total_price"] == Decimal("45000")
    assert result["items"][1]["name"] == "Nasi Putih"
    assert result["items"][1]["qty"] == 3
    assert result["items"][1]["total_price"] == Decimal("18000")

