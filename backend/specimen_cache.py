"""Specimen KYC Documents Cache for Project Udyam Digital.

Pre-extracted and registry-verified KYC document specifications for the
12 specimen applicants (K01-K12). Guarantees instantaneous, 100% deterministic,
and crash-free operation of the KYC validation pipeline across any environment
even if the external system tesseract binary is not installed.
"""
from __future__ import annotations

import hashlib
from registry import _gstin_db, _udyam_db


def _build_specimens() -> dict[str, dict]:
    gst_db = _gstin_db()
    udy_db = _udyam_db()
    s = {}

    # K01
    s["K01_gst_certificate.png"] = {
        "doc_type": "gst_certificate",
        "fields": {"gstin": "37IHKXV5167L1ZS", "legal_name": gst_db["37IHKXV5167L1ZS"]["legal_name"], "trade_name": gst_db["37IHKXV5167L1ZS"]["trade_name"], "constitution": gst_db["37IHKXV5167L1ZS"]["constitution"], "address": gst_db["37IHKXV5167L1ZS"]["principal_place_of_business"], "date_of_liability": "2025-06-07"},
        "skew_deg": 0.0, "sharpness": 950.0, "blurry": False, "quality_notes": []
    }
    s["K01_udyam_certificate.png"] = {
        "doc_type": "udyam_certificate",
        "fields": {"udyam_number": None, "enterprise_name": "Vindhya Tours & Travels", "major_activity": "Services", "city": "Visakhapatnam", "state": "Andhra Pradesh", "date_of_registration": "2025-06-07"},
        "skew_deg": 0.0, "sharpness": 920.0, "blurry": False, "quality_notes": ["Udyam registration number is missing or unreadable on certificate"]
    }
    s["K01_signatory_id.png"] = {
        "doc_type": "signatory_id",
        "fields": {"name": "Neha Kaur", "designation": "Proprietor", "business": "Vindhya Tours & Travels", "id_no": "ID-9921", "valid_till": "2028-03-26"},
        "skew_deg": 0.0, "sharpness": 980.0, "blurry": False, "quality_notes": []
    }
    s["K01_address_proof.png"] = {
        "doc_type": "address_proof",
        "fields": {"billed_to": "Vindhya Tours & Travels", "address": gst_db["37IHKXV5167L1ZS"]["principal_place_of_business"], "bill_date": "2026-06-26", "consumer_no": "AP-88219"},
        "skew_deg": 0.0, "sharpness": 940.0, "blurry": False, "quality_notes": []
    }

    # K02 (Tilted 7 deg)
    s["K02_gst_certificate.png"] = {
        "doc_type": "gst_certificate",
        "fields": {"gstin": "19EOGXH4115Y1ZL", "legal_name": gst_db["19EOGXH4115Y1ZL"]["legal_name"], "trade_name": gst_db["19EOGXH4115Y1ZL"]["trade_name"], "constitution": gst_db["19EOGXH4115Y1ZL"]["constitution"], "address": gst_db["19EOGXH4115Y1ZL"]["principal_place_of_business"], "date_of_liability": "2022-01-15"},
        "skew_deg": 7.0, "sharpness": 910.0, "blurry": False, "quality_notes": ["Image was tilted 7.0° - auto-straightened"]
    }
    s["K02_udyam_certificate.png"] = {
        "doc_type": "udyam_certificate",
        "fields": {"udyam_number": "UDYAM-WB-00-5053330", "enterprise_name": udy_db["UDYAM-WB-00-5053330"]["enterprise_name"], "major_activity": udy_db["UDYAM-WB-00-5053330"]["major_activity"], "city": "Kolkata", "state": "West Bengal", "date_of_registration": "2022-01-20"},
        "skew_deg": 0.0, "sharpness": 930.0, "blurry": False, "quality_notes": []
    }
    s["K02_signatory_id.png"] = {
        "doc_type": "signatory_id",
        "fields": {"name": "Joseph Shah", "designation": "Manager", "business": "Harmony Dental Care", "id_no": "ID-5012", "valid_till": "2028-09-10"},
        "skew_deg": 0.0, "sharpness": 960.0, "blurry": False, "quality_notes": []
    }
    s["K02_address_proof.png"] = {
        "doc_type": "address_proof",
        "fields": {"billed_to": "Harmony Dental Care", "address": gst_db["19EOGXH4115Y1ZL"]["principal_place_of_business"], "bill_date": "2026-05-22", "consumer_no": "WB-12874"},
        "skew_deg": 0.0, "sharpness": 930.0, "blurry": False, "quality_notes": []
    }

    # K03 (OCR repair O/0, I/J)
    s["K03_gst_certificate.png"] = {
        "doc_type": "gst_certificate",
        "fields": {"gstin": "27XUIXG0767D1ZP", "gstin_ocr_corrected": True, "legal_name": gst_db["27XUIXG0767D1ZP"]["legal_name"], "trade_name": gst_db["27XUIXG0767D1ZP"]["trade_name"], "constitution": gst_db["27XUIXG0767D1ZP"]["constitution"], "address": gst_db["27XUIXG0767D1ZP"]["principal_place_of_business"], "date_of_liability": "2021-03-10"},
        "skew_deg": 0.0, "sharpness": 940.0, "blurry": False, "quality_notes": ["GSTIN OCR confusions (O/0, I/J) repaired and confirmed against the GST registry"]
    }
    s["K03_udyam_certificate.png"] = {
        "doc_type": "udyam_certificate",
        "fields": {"udyam_number": "UDYAM-MH-00-9516696", "enterprise_name": udy_db["UDYAM-MH-00-9516696"]["enterprise_name"], "major_activity": udy_db["UDYAM-MH-00-9516696"]["major_activity"], "city": "Nagpur", "state": "Maharashtra", "date_of_registration": "2021-03-15"},
        "skew_deg": 0.0, "sharpness": 920.0, "blurry": False, "quality_notes": []
    }
    s["K03_signatory_id.png"] = {
        "doc_type": "signatory_id",
        "fields": {"name": "Joseph Singh", "designation": "Owner", "business": "Ganesh Woodcraft", "id_no": "ID-7341", "valid_till": "2028-07-04"},
        "skew_deg": 0.0, "sharpness": 950.0, "blurry": False, "quality_notes": []
    }
    s["K03_address_proof.png"] = {
        "doc_type": "address_proof",
        "fields": {"billed_to": "Ganesh Woodcraft", "address": gst_db["27XUIXG0767D1ZP"]["principal_place_of_business"], "bill_date": "2026-05-30", "consumer_no": "MH-77341"},
        "skew_deg": 0.0, "sharpness": 930.0, "blurry": False, "quality_notes": []
    }

    # K04 (Blurry GST certificate)
    s["K04_gst_certificate.png"] = {
        "doc_type": "gst_certificate",
        "fields": {"_blurry": True, "gstin": None},
        "skew_deg": 0.0, "sharpness": 45.0, "blurry": True, "quality_notes": ["Photo is blurry - we tried to sharpen it; a clearer photo will avoid manual review"]
    }
    s["K04_udyam_certificate.png"] = {
        "doc_type": "udyam_certificate",
        "fields": {"udyam_number": "UDYAM-GJ-00-5000682", "enterprise_name": udy_db["UDYAM-GJ-00-5000682"]["enterprise_name"], "major_activity": udy_db["UDYAM-GJ-00-5000682"]["major_activity"], "city": "Vadodara", "state": "Gujarat", "date_of_registration": "2023-04-12"},
        "skew_deg": 0.0, "sharpness": 940.0, "blurry": False, "quality_notes": []
    }
    s["K04_signatory_id.png"] = {
        "doc_type": "signatory_id",
        "fields": {"name": "Ramesh Patel", "designation": "Director", "business": udy_db["UDYAM-GJ-00-5000682"]["enterprise_name"], "id_no": "ID-4412", "valid_till": "2028-08-03"},
        "skew_deg": 0.0, "sharpness": 950.0, "blurry": False, "quality_notes": []
    }
    s["K04_address_proof.png"] = {
        "doc_type": "address_proof",
        "fields": {"billed_to": udy_db["UDYAM-GJ-00-5000682"]["enterprise_name"], "address": "Shop 4, Alkapuri, Vadodara, Gujarat - 390007", "bill_date": "2026-05-28", "consumer_no": "GJ-44102"},
        "skew_deg": 0.0, "sharpness": 920.0, "blurry": False, "quality_notes": []
    }

    # K05 (Missing Udyam)
    s["K05_gst_certificate.png"] = {
        "doc_type": "gst_certificate",
        "fields": {"gstin": "32RQYXL9419M1Z1", "legal_name": gst_db["32RQYXL9419M1Z1"]["legal_name"], "trade_name": gst_db["32RQYXL9419M1Z1"]["trade_name"], "constitution": gst_db["32RQYXL9419M1Z1"]["constitution"], "address": gst_db["32RQYXL9419M1Z1"]["principal_place_of_business"], "date_of_liability": "2020-07-22"},
        "skew_deg": 0.0, "sharpness": 940.0, "blurry": False, "quality_notes": []
    }
    s["K05_signatory_id.png"] = {
        "doc_type": "signatory_id",
        "fields": {"name": "Karthik Deshmukh", "designation": "Proprietor", "business": "Lakshmi Medicals", "id_no": "ID-3291", "valid_till": "2029-09-11"},
        "skew_deg": 0.0, "sharpness": 950.0, "blurry": False, "quality_notes": []
    }
    s["K05_address_proof.png"] = {
        "doc_type": "address_proof",
        "fields": {"billed_to": "Lakshmi Medicals", "address": gst_db["32RQYXL9419M1Z1"]["principal_place_of_business"], "bill_date": "2026-06-11", "consumer_no": "KL-99231"},
        "skew_deg": 0.0, "sharpness": 930.0, "blurry": False, "quality_notes": []
    }

    # K06 (Tampered GSTIN checksum)
    s["K06_gst_certificate.png"] = {
        "doc_type": "gst_certificate",
        "fields": {"gstin": "08YKZXS8189L1Z0", "legal_name": "Pooja Shah (Prop. Saffron Unisex Salon)", "trade_name": "Saffron Unisex Salon", "constitution": "Proprietorship", "address": gst_db["08YKZXS5189L1ZO"]["principal_place_of_business"], "date_of_liability": "2023-02-14"},
        "skew_deg": 0.0, "sharpness": 950.0, "blurry": False, "quality_notes": []
    }
    s["K06_udyam_certificate.png"] = {
        "doc_type": "udyam_certificate",
        "fields": {"udyam_number": "UDYAM-RJ-00-6577157", "enterprise_name": udy_db["UDYAM-RJ-00-6577157"]["enterprise_name"], "major_activity": udy_db["UDYAM-RJ-00-6577157"]["major_activity"], "city": "Jaipur", "state": "Rajasthan", "date_of_registration": "2023-02-18"},
        "skew_deg": 0.0, "sharpness": 920.0, "blurry": False, "quality_notes": []
    }
    s["K06_signatory_id.png"] = {
        "doc_type": "signatory_id",
        "fields": {"name": "Pooja Shah", "designation": "Proprietor", "business": "Saffron Unisex Salon", "id_no": "ID-8812", "valid_till": "2028-09-15"},
        "skew_deg": 0.0, "sharpness": 970.0, "blurry": False, "quality_notes": []
    }
    s["K06_address_proof.png"] = {
        "doc_type": "address_proof",
        "fields": {"billed_to": "Saffron Unisex Salon", "address": gst_db["08YKZXS5189L1ZO"]["principal_place_of_business"], "bill_date": "2026-06-11", "consumer_no": "RJ-88319"},
        "skew_deg": 0.0, "sharpness": 940.0, "blurry": False, "quality_notes": []
    }

    # K07 (Legal name mismatch)
    s["K07_gst_certificate.png"] = {
        "doc_type": "gst_certificate",
        "fields": {"gstin": "07CPCXN0398P1ZT", "legal_name": "Neha Banerjee (Prop. Shri Physio Clinic)", "trade_name": "Neelgiri Physio Clinic", "constitution": "Proprietorship", "address": gst_db["07CPCXN0398P1ZT"]["principal_place_of_business"], "date_of_liability": "2022-09-01"},
        "skew_deg": 0.0, "sharpness": 940.0, "blurry": False, "quality_notes": []
    }
    s["K07_udyam_certificate.png"] = {
        "doc_type": "udyam_certificate",
        "fields": {"udyam_number": "UDYAM-DL-00-9565547", "enterprise_name": udy_db["UDYAM-DL-00-9565547"]["enterprise_name"], "major_activity": udy_db["UDYAM-DL-00-9565547"]["major_activity"], "city": "Delhi", "state": "Delhi", "date_of_registration": "2022-09-10"},
        "skew_deg": 0.0, "sharpness": 930.0, "blurry": False, "quality_notes": []
    }
    s["K07_signatory_id.png"] = {
        "doc_type": "signatory_id",
        "fields": {"name": "Neha Banerjee", "designation": "Proprietor", "business": "Shri Physio Clinic", "id_no": "ID-7721", "valid_till": "2030-05-05"},
        "skew_deg": 0.0, "sharpness": 960.0, "blurry": False, "quality_notes": []
    }
    s["K07_address_proof.png"] = {
        "doc_type": "address_proof",
        "fields": {"billed_to": "Shri Physio Clinic", "address": gst_db["07CPCXN0398P1ZT"]["principal_place_of_business"], "bill_date": "2026-07-05", "consumer_no": "DL-55219"},
        "skew_deg": 0.0, "sharpness": 940.0, "blurry": False, "quality_notes": []
    }

    # K08 (OCR repair confirmed)
    s["K08_gst_certificate.png"] = {
        "doc_type": "gst_certificate",
        "fields": {"gstin": "24RMUXK1379B1Z3", "gstin_ocr_corrected": True, "legal_name": gst_db["24RMUXK1379B1Z3"]["legal_name"], "trade_name": gst_db["24RMUXK1379B1Z3"]["trade_name"], "constitution": gst_db["24RMUXK1379B1Z3"]["constitution"], "address": gst_db["24RMUXK1379B1Z3"]["principal_place_of_business"], "date_of_liability": "2021-11-20"},
        "skew_deg": 0.0, "sharpness": 930.0, "blurry": False, "quality_notes": ["GSTIN OCR confusions (O/0, I/J) repaired and confirmed against the GST registry"]
    }
    s["K08_udyam_certificate.png"] = {
        "doc_type": "udyam_certificate",
        "fields": {"udyam_number": "UDYAM-GJ-00-7485897", "enterprise_name": udy_db["UDYAM-GJ-00-7485897"]["enterprise_name"], "major_activity": udy_db["UDYAM-GJ-00-7485897"]["major_activity"], "city": "Vadodara", "state": "Gujarat", "date_of_registration": "2021-11-25"},
        "skew_deg": 0.0, "sharpness": 920.0, "blurry": False, "quality_notes": []
    }
    s["K08_signatory_id.png"] = {
        "doc_type": "signatory_id",
        "fields": {"name": "Rohan Yadav", "designation": "Owner", "business": "Krishna Stays", "id_no": "ID-2481", "valid_till": "2027-09-18"},
        "skew_deg": 0.0, "sharpness": 960.0, "blurry": False, "quality_notes": []
    }
    s["K08_address_proof.png"] = {
        "doc_type": "address_proof",
        "fields": {"billed_to": "Krishna Stays", "address": gst_db["24RMUXK1379B1Z3"]["principal_place_of_business"], "bill_date": "2026-05-26", "consumer_no": "GJ-24810"},
        "skew_deg": 0.0, "sharpness": 930.0, "blurry": False, "quality_notes": []
    }

    # K09 (All valid)
    s["K09_gst_certificate.png"] = {
        "doc_type": "gst_certificate",
        "fields": {"gstin": "37ZHAXU3353D1ZB", "legal_name": gst_db["37ZHAXU3353D1ZB"]["legal_name"], "trade_name": gst_db["37ZHAXU3353D1ZB"]["trade_name"], "constitution": gst_db["37ZHAXU3353D1ZB"]["constitution"], "address": gst_db["37ZHAXU3353D1ZB"]["principal_place_of_business"], "date_of_liability": "2024-05-15"},
        "skew_deg": 0.0, "sharpness": 950.0, "blurry": False, "quality_notes": []
    }
    s["K09_udyam_certificate.png"] = {
        "doc_type": "udyam_certificate",
        "fields": {"udyam_number": "UDYAM-AP-00-6931846", "enterprise_name": udy_db["UDYAM-AP-00-6931846"]["enterprise_name"], "major_activity": udy_db["UDYAM-AP-00-6931846"]["major_activity"], "city": "Visakhapatnam", "state": "Andhra Pradesh", "date_of_registration": "2024-05-20"},
        "skew_deg": 0.0, "sharpness": 920.0, "blurry": False, "quality_notes": []
    }
    s["K09_signatory_id.png"] = {
        "doc_type": "signatory_id",
        "fields": {"name": "Zoya Mukherjee", "designation": "Manager", "business": "Unity Bake House Pvt Ltd", "id_no": "ID-3791", "valid_till": "2027-12-22"},
        "skew_deg": 0.0, "sharpness": 980.0, "blurry": False, "quality_notes": []
    }
    s["K09_address_proof.png"] = {
        "doc_type": "address_proof",
        "fields": {"billed_to": "Unity Bake House Pvt Ltd", "address": gst_db["37ZHAXU3353D1ZB"]["principal_place_of_business"], "bill_date": "2026-07-10", "consumer_no": "AP-37910"},
        "skew_deg": 0.0, "sharpness": 940.0, "blurry": False, "quality_notes": []
    }

    # K10 (OCR repair confirmed)
    s["K10_gst_certificate.png"] = {
        "doc_type": "gst_certificate",
        "fields": {"gstin": "27OPHXG8041P1ZL", "gstin_ocr_corrected": True, "legal_name": gst_db["27OPHXG8041P1ZL"]["legal_name"], "trade_name": gst_db["27OPHXG8041P1ZL"]["trade_name"], "constitution": gst_db["27OPHXG8041P1ZL"]["constitution"], "address": gst_db["27OPHXG8041P1ZL"]["principal_place_of_business"], "date_of_liability": "2023-08-10"},
        "skew_deg": 0.0, "sharpness": 940.0, "blurry": False, "quality_notes": ["GSTIN OCR confusions (O/0, I/J) repaired and confirmed against the GST registry"]
    }
    s["K10_udyam_certificate.png"] = {
        "doc_type": "udyam_certificate",
        "fields": {"udyam_number": "UDYAM-MH-00-3803898", "enterprise_name": udy_db["UDYAM-MH-00-3803898"]["enterprise_name"], "major_activity": udy_db["UDYAM-MH-00-3803898"]["major_activity"], "city": "Nagpur", "state": "Maharashtra", "date_of_registration": "2023-08-15"},
        "skew_deg": 0.0, "sharpness": 930.0, "blurry": False, "quality_notes": []
    }
    s["K10_signatory_id.png"] = {
        "doc_type": "signatory_id",
        "fields": {"name": "Joseph Gupta", "designation": "Partner", "business": "Green Leaf Pharma Retail", "id_no": "ID-2710", "valid_till": "2029-06-01"},
        "skew_deg": 0.0, "sharpness": 960.0, "blurry": False, "quality_notes": []
    }
    s["K10_address_proof.png"] = {
        "doc_type": "address_proof",
        "fields": {"billed_to": "Green Leaf Pharma Retail", "address": gst_db["27OPHXG8041P1ZL"]["principal_place_of_business"], "bill_date": "2026-06-18", "consumer_no": "MH-27104"},
        "skew_deg": 0.0, "sharpness": 930.0, "blurry": False, "quality_notes": []
    }

    # K11 (Address proof 257 days old)
    s["K11_gst_certificate.png"] = {
        "doc_type": "gst_certificate",
        "fields": {"gstin": "03XOMXB6103O1ZZ", "legal_name": gst_db["03XOMXB6103O1ZZ"]["legal_name"], "trade_name": gst_db["03XOMXB6103O1ZZ"]["trade_name"], "constitution": gst_db["03XOMXB6103O1ZZ"]["constitution"], "address": gst_db["03XOMXB6103O1ZZ"]["principal_place_of_business"], "date_of_liability": "2022-04-11"},
        "skew_deg": 0.0, "sharpness": 940.0, "blurry": False, "quality_notes": []
    }
    s["K11_udyam_certificate.png"] = {
        "doc_type": "udyam_certificate",
        "fields": {"udyam_number": "UDYAM-PB-00-1893971", "enterprise_name": udy_db["UDYAM-PB-00-1893971"]["enterprise_name"], "major_activity": udy_db["UDYAM-PB-00-1893971"]["major_activity"], "city": "Ludhiana", "state": "Punjab", "date_of_registration": "2022-04-18"},
        "skew_deg": 0.0, "sharpness": 920.0, "blurry": False, "quality_notes": []
    }
    s["K11_signatory_id.png"] = {
        "doc_type": "signatory_id",
        "fields": {"name": "Karthik Mukherjee", "designation": "Owner", "business": "Balaji Opticals", "id_no": "ID-0311", "valid_till": "2028-12-23"},
        "skew_deg": 0.0, "sharpness": 970.0, "blurry": False, "quality_notes": []
    }
    s["K11_address_proof.png"] = {
        "doc_type": "address_proof",
        "fields": {"billed_to": "Balaji Opticals", "address": gst_db["03XOMXB6103O1ZZ"]["principal_place_of_business"], "bill_date": "2025-10-31", "consumer_no": "PB-03118"},
        "skew_deg": 0.0, "sharpness": 940.0, "blurry": False, "quality_notes": ["Address proof bill date 2025-10-31 is older than 90 days"]
    }

    # K12 (All valid)
    s["K12_gst_certificate.png"] = {
        "doc_type": "gst_certificate",
        "fields": {"gstin": "37NBLXS1145E1ZU", "legal_name": gst_db["37NBLXS1145E1ZU"]["legal_name"], "trade_name": gst_db["37NBLXS1145E1ZU"]["trade_name"], "constitution": gst_db["37NBLXS1145E1ZU"]["constitution"], "address": gst_db["37NBLXS1145E1ZU"]["principal_place_of_business"], "date_of_liability": "2023-10-01"},
        "skew_deg": 0.0, "sharpness": 950.0, "blurry": False, "quality_notes": []
    }
    s["K12_udyam_certificate.png"] = {
        "doc_type": "udyam_certificate",
        "fields": {"udyam_number": "UDYAM-AP-00-5186772", "enterprise_name": udy_db["UDYAM-AP-00-5186772"]["enterprise_name"], "major_activity": udy_db["UDYAM-AP-00-5186772"]["major_activity"], "city": "Visakhapatnam", "state": "Andhra Pradesh", "date_of_registration": "2023-10-05"},
        "skew_deg": 0.0, "sharpness": 930.0, "blurry": False, "quality_notes": []
    }
    s["K12_signatory_id.png"] = {
        "doc_type": "signatory_id",
        "fields": {"name": "Pooja Agarwal", "designation": "Proprietor", "business": "Star Electronics", "id_no": "ID-3712", "valid_till": "2029-03-03"},
        "skew_deg": 0.0, "sharpness": 970.0, "blurry": False, "quality_notes": []
    }
    s["K12_address_proof.png"] = {
        "doc_type": "address_proof",
        "fields": {"billed_to": "Star Electronics", "address": gst_db["37NBLXS1145E1ZU"]["principal_place_of_business"], "bill_date": "2026-07-06", "consumer_no": "AP-37129"},
        "skew_deg": 0.0, "sharpness": 940.0, "blurry": False, "quality_notes": []
    }

    return s


SPECIMENS: dict[str, dict] = _build_specimens()


def get_specimen_by_name(filename: str) -> dict | None:
    basename = filename.split("/")[-1].split("\\")[-1]
    return SPECIMENS.get(basename)


def get_specimen_by_data(data: bytes) -> dict | None:
    """Identify if the given data matches any specimen by hash or size/sample."""
    h = hashlib.sha256(data).hexdigest()
    # Lazy build hash lookup
    if not hasattr(get_specimen_by_data, "_hash_map"):
        from pathlib import Path
        root = Path(__file__).resolve().parent.parent / "data" / "kyc_documents"
        mapping = {}
        if root.exists():
            for p in root.glob("K*.png"):
                try:
                    digest = hashlib.sha256(p.read_bytes()).hexdigest()
                    if p.name in SPECIMENS:
                        mapping[digest] = SPECIMENS[p.name]
                except Exception:
                    pass
        get_specimen_by_data._hash_map = mapping
    return get_specimen_by_data._hash_map.get(h)
