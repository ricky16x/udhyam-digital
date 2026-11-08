"""Mock government registries (GSTIN, Udyam) and identifier validators.

The case data uses real-format GSTINs with valid checksums, except that the
4th PAN character is always 'X'. We accept 'X' as an entity type so the
synthetic data validates, as the data README asks.
"""
from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

GST_STATE_CODES = {
    "01": "Jammu and Kashmir", "02": "Himachal Pradesh", "03": "Punjab", "04": "Chandigarh",
    "05": "Uttarakhand", "06": "Haryana", "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
    "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh", "13": "Nagaland", "14": "Manipur",
    "15": "Mizoram", "16": "Tripura", "17": "Meghalaya", "18": "Assam", "19": "West Bengal",
    "20": "Jharkhand", "21": "Odisha", "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "26": "Dadra and Nagar Haveli and Daman and Diu", "27": "Maharashtra", "29": "Karnataka",
    "30": "Goa", "31": "Lakshadweep", "32": "Kerala", "33": "Tamil Nadu", "34": "Puducherry",
    "35": "Andaman and Nicobar Islands", "36": "Telangana", "37": "Andhra Pradesh", "38": "Ladakh",
}
UDYAM_STATE_CODES = {
    "JK": "Jammu and Kashmir", "HP": "Himachal Pradesh", "PB": "Punjab", "CH": "Chandigarh",
    "UK": "Uttarakhand", "HR": "Haryana", "DL": "Delhi", "RJ": "Rajasthan", "UP": "Uttar Pradesh",
    "BR": "Bihar", "WB": "West Bengal", "JH": "Jharkhand", "OD": "Odisha", "CG": "Chhattisgarh",
    "MP": "Madhya Pradesh", "GJ": "Gujarat", "MH": "Maharashtra", "KR": "Karnataka", "KA": "Karnataka",
    "GA": "Goa", "KL": "Kerala", "TN": "Tamil Nadu", "PY": "Puducherry", "TS": "Telangana",
    "TG": "Telangana", "AP": "Andhra Pradesh", "AS": "Assam",
}
_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GSTIN_RE = re.compile(r"^(\d{2})([A-Z]{5}\d{4}[A-Z])([1-9A-Z])Z([0-9A-Z])$")
PAN_ENTITY = set("CPHFATBLJGX")  # X accepted for synthetic data
UDYAM_RE = re.compile(r"^UDYAM-([A-Z]{2})-(\d{2})-(\d{7})$")


def gstin_checksum(first14: str) -> str:
    total = 0
    for i, ch in enumerate(first14):
        prod = _CHARS.index(ch) * (2 if i % 2 else 1)
        total += prod // 36 + prod % 36
    return _CHARS[(36 - total % 36) % 36]


def validate_gstin_format(gstin: str) -> dict:
    g = (gstin or "").strip().upper()
    out = {"gstin": g, "valid": False, "errors": []}
    m = GSTIN_RE.match(g)
    if not m:
        out["errors"].append("GSTIN must be 15 characters: 2-digit state code, 10-char PAN, entity no., 'Z', checksum")
        return out
    state, pan = m.group(1), m.group(2)
    if state not in GST_STATE_CODES:
        out["errors"].append(f"Unknown GST state code {state}")
    if pan[3] not in PAN_ENTITY:
        out["errors"].append(f"PAN entity type '{pan[3]}' is not valid")
    if gstin_checksum(g[:14]) != g[14]:
        out["errors"].append("Checksum digit does not match - likely a typo or a tampered number")
    out["state"] = GST_STATE_CODES.get(state)
    out["pan"] = pan
    out["valid"] = not out["errors"]
    return out


def validate_udyam_format(num: str) -> dict:
    u = (num or "").strip().upper()
    m = UDYAM_RE.match(u)
    out = {"udyam_number": u, "valid": bool(m), "errors": []}
    if not m:
        out["errors"].append("Udyam number must look like UDYAM-XX-00-0000000")
    else:
        out["state"] = UDYAM_STATE_CODES.get(m.group(1))
    return out


@lru_cache(maxsize=1)
def _gstin_db() -> dict:
    with open(DATA / "mock_gstin_registry.csv", newline="", encoding="utf-8") as f:
        return {r["gstin"]: r for r in csv.DictReader(f)}


@lru_cache(maxsize=1)
def _udyam_db() -> dict:
    with open(DATA / "mock_udyam_registry.csv", newline="", encoding="utf-8") as f:
        return {r["udyam_number"]: r for r in csv.DictReader(f)}


def lookup_gstin(gstin: str) -> dict:
    fmt = validate_gstin_format(gstin)
    if not fmt["valid"]:
        return {"found": False, "format": fmt}
    rec = _gstin_db().get(fmt["gstin"])
    return {"found": rec is not None, "format": fmt, "record": rec}


def lookup_udyam(num: str) -> dict:
    fmt = validate_udyam_format(num)
    if not fmt["valid"]:
        return {"found": False, "format": fmt}
    rec = _udyam_db().get(fmt["udyam_number"])
    return {"found": rec is not None, "format": fmt, "record": rec}


def mask(value: str | None, keep_start: int = 2, keep_end: int = 3) -> str:
    """Mask identifiers for logs and UI (DPDP data minimisation)."""
    if not value:
        return ""
    v = str(value)
    if len(v) <= keep_start + keep_end:
        return "*" * len(v)
    return v[:keep_start] + "*" * (len(v) - keep_start - keep_end) + v[-keep_end:]
