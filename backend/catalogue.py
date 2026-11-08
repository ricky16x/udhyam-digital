"""Bundle engine: needs -> products, eligibility rules, dependencies, transparent price.

The GenAI advisor never prices anything itself. It collects a BusinessProfile
and calls `recommend()`; every product, quantity and rupee shown to the owner
comes from this deterministic, testable module and product_catalogue.csv.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field, asdict
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

SEGMENTS = {
    "micro": "Micro retail & services",
    "prof": "Professional offices",
    "multi": "Small multi-site businesses",
    "mfg": "Small manufacturers",
}

# Plain-language needs the advisor asks about (EN / HI labels used by the UI)
NEEDS = {
    "internet": ("Reliable internet", "भरोसेमंद इंटरनेट"),
    "payments": ("Billing & UPI/card payments", "बिलिंग और UPI/कार्ड पेमेंट"),
    "whatsapp": ("Reach customers on WhatsApp/SMS", "WhatsApp/SMS से ग्राहकों तक पहुँच"),
    "cctv": ("CCTV you can watch on your phone", "फ़ोन पर देख सकें ऐसा CCTV"),
    "guest_wifi": ("Wi-Fi for customers", "ग्राहकों के लिए Wi-Fi"),
    "email": ("Business email & documents", "बिज़नेस ईमेल और डॉक्यूमेंट"),
    "backup": ("Data backup", "डेटा बैकअप"),
    "security": ("Protection from viruses/ransomware", "वायरस/रैनसमवेयर से सुरक्षा"),
    "uptime": ("Never go offline (backup link)", "इंटरनेट कभी बंद न हो (बैकअप)"),
    "phone_lines": ("Business phone lines / IVR", "बिज़नेस फ़ोन लाइन / IVR"),
    "website": ("Website", "वेबसाइट"),
    "central_mgmt": ("Manage all branches centrally", "सभी ब्रांच एक जगह से संभालें"),
    "machines": ("Monitor machines", "मशीनों की निगरानी"),
    "fleet": ("Track vehicles", "गाड़ियों की ट्रैकिंग"),
    "dedicated": ("Dedicated high-speed line", "डेडिकेटेड हाई-स्पीड लाइन"),
}

# Defaults per segment = products most often bought by activated, retained
# customers in smb_leads.csv (see analysis/segment_bundles.py)
SEGMENT_DEFAULT_NEEDS = {
    "micro": ["internet", "payments"],
    "prof": ["internet", "email", "security", "backup"],
    "multi": ["internet", "uptime", "payments", "cctv", "central_mgmt"],
    "mfg": ["dedicated", "email", "security", "cctv"],
}


@dataclass
class BusinessProfile:
    segment: str = "micro"              # micro | prof | multi | mfg
    business_type: str = ""
    employees: int = 2
    sites: int = 1
    city_tier: int = 1
    has_gstin: bool = False
    gstin_active: bool = False          # set after GSTIN lookup
    fibre_available: bool = True        # from pincode feasibility (mocked)
    current_spend: int = 0              # monthly telecom spend today, INR
    needs: list[str] = field(default_factory=list)
    mobile_lines: int | None = None
    users: int | None = None            # PCs / email users
    cameras: int | None = None
    counters: int | None = None
    vehicles: int = 0
    machines: int = 0
    contract_months: int = 12
    language: str = "en"


@lru_cache(maxsize=1)
def catalogue() -> dict[str, dict]:
    out = {}
    with open(DATA / "product_catalogue.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            for k in ("price_min_inr_per_month", "price_max_inr_per_month", "one_time_setup_inr",
                      "min_contract_months", "min_employees", "min_sites", "typical_install_days"):
                r[k] = int(r[k])
            r["tiers"] = {int(t) for t in r["available_city_tiers"].split(";")}
            r["deps"] = [d for d in r["requires_one_of"].split("|") if d] if r["requires_one_of"] else []
            r["segments"] = r["target_segments"].split(";")
            out[r["product_id"]] = r
    return out


def eligible(pid: str, p: BusinessProfile) -> tuple[bool, str | None]:
    c = catalogue()[pid]
    if p.city_tier not in c["tiers"]:
        return False, f"{c['product_name']} is not yet available in tier-{p.city_tier} cities"
    if p.employees < c["min_employees"]:
        return False, f"{c['product_name']} is for businesses with {c['min_employees']}+ employees"
    if p.sites < c["min_sites"]:
        return False, f"{c['product_name']} needs {c['min_sites']}+ sites"
    if c["requires_gstin"] == "Y" and not (p.has_gstin and p.gstin_active):
        return False, f"{c['product_name']} needs an active GSTIN"
    return True, None


def _connectivity(p: BusinessProfile, notes: list[str]) -> str:
    """Pick the primary internet product per site."""
    cat = catalogue()
    if "dedicated" in p.needs or p.segment == "mfg":
        for pid in ("P06", "P05") if p.employees >= 25 else ("P05",):
            if eligible(pid, p)[0]:
                return pid
        notes.append("A leased line needs an active GSTIN and 10+ employees, so we suggest business fibre instead")
    if p.segment in ("prof", "mfg") and p.employees >= 15 and eligible("P03", p)[0] and p.fibre_available:
        return "P03"
    if not p.fibre_available:
        notes.append("Fibre is not available at your pincode yet, so we use 5G AirFiber (installs in 2 days)")
        return "P04"
    if p.segment == "prof" or (p.segment == "multi" and p.employees / max(p.sites, 1) >= 8):
        return "P02"
    return "P01"


def recommend(p: BusinessProfile) -> dict:
    cat = catalogue()
    needs = list(dict.fromkeys((p.needs or []) + SEGMENT_DEFAULT_NEEDS.get(p.segment, [])))
    p.needs = needs
    notes: list[str] = []
    excluded: list[dict] = []
    lines: dict[str, dict] = {}
    sites = max(1, p.sites)

    def add(pid: str, qty: int, why: str, optional: bool = False):
        ok, reason = eligible(pid, p)
        if not ok:
            excluded.append({"product_id": pid, "name": cat[pid]["product_name"], "reason": reason})
            return False
        if pid in lines:
            lines[pid]["qty"] = max(lines[pid]["qty"], qty)
        else:
            lines[pid] = {"product_id": pid, "qty": max(1, qty), "why": why, "optional": optional}
        return True

    primary = _connectivity(p, notes)
    add(primary, sites, "Main internet for {} site{}".format(sites, "s" if sites > 1 else ""))

    lines_default = p.mobile_lines or (1 if (p.segment == "micro" and (p.employees <= 2 or (p.current_spend and p.current_spend <= 800))) else (2 if p.segment == "micro" else max(2, min(p.employees // 4, 6))))
    add("P08" if p.segment != "micro" else "P07", lines_default,
        "Business mobile lines with GST invoice - replaces personal SIMs")
    users = p.users or max(1, min(p.employees, 15 if p.segment == "prof" else 12))

    if "payments" in needs:
        add("P19", p.counters or sites, "GST-ready billing with UPI/card acceptance on a tablet",
            optional=(p.segment == "micro" and bool(p.current_spend and p.current_spend < 1000)))
    if "whatsapp" in needs:
        if not add("P15", 1, "Verified WhatsApp channel with your catalogue", optional=p.segment == "micro"):
            notes.append("WhatsApp Business API needs an active GSTIN - you can add it later once GST is registered")
        add("P14", 1, "10,000 SMS/month for offers and reminders", optional=True)
    if "cctv" in needs:
        add("P23", p.cameras or (2 if p.segment == "micro" else 2 * sites), "HD cameras with 30-day cloud recording, view on phone")
    if "guest_wifi" in needs:
        add("P22", sites, "Separate customer Wi-Fi keeps your billing network safe", optional=p.segment == "micro")
    if "email" in needs:
        add("P16", users, "Email on your own domain + documents + video meetings")
    if "backup" in needs:
        add("P17", 1, "Automatic 1 TB backup of PCs and phones", optional=p.segment != "prof")
    if "security" in needs:
        add("P20", users, "Antivirus and ransomware protection per device")
        if p.employees >= 10:
            add("P21", sites, "Managed firewall watched by our security team", optional=True)
    if "uptime" in needs:
        add("P09", sites, "Automatic 4G/5G failover when the main line is down")
    if "phone_lines" in needs:
        add("P12", max(2, min(users // 3, 6)), "Cloud phone lines with IVR and call recording")
        add("P13", 1, "1800 toll-free number for customers", optional=True)
    if "website" in needs:
        add("P18", 1, "Domain, 5-page website and hosting", optional=True)
    if "central_mgmt" in needs and sites >= 3:
        add("P10", sites, "Manage all branch links centrally with app priority")
    if "machines" in needs or p.machines:
        add("P24", max(p.machines, 4), "Sensors for machine uptime and energy use")
    if "fleet" in needs or p.vehicles:
        add("P25", max(p.vehicles, 1), "GPS tracking with live dashboard")
    if p.segment in ("prof", "mfg") and eligible("P11", p)[0] and ("cctv" in needs or p.segment == "mfg"):
        add("P11", 1, "Static IP for remote CCTV/server access", optional=True)

    # dependency resolution: every product with requires_one_of must have a base link
    for pid in list(lines):
        deps = cat[pid]["deps"]
        if deps and not any(d in lines for d in deps):
            if primary in deps:
                continue
            if lines[pid]["optional"]:
                excluded.append({"product_id": pid, "name": cat[pid]["product_name"],
                                 "reason": f"Works only with {', '.join(cat[d]['product_name'] for d in deps[:3])}"})
                lines.pop(pid)
                continue
            fallback = next((d for d in deps if eligible(d, p)[0]), None)
            if fallback:
                add(fallback, sites, f"Needed for {cat[pid]['product_name']}")
            else:
                excluded.append({"product_id": pid, "name": cat[pid]["product_name"], "reason": "Needs a supported internet line"})
                lines.pop(pid)

    contract = max(p.contract_months, max(cat[pid]["min_contract_months"] for pid in lines if not lines[pid]["optional"]))
    bundle = {"profile": asdict(p), "lines": list(lines.values()), "excluded": excluded, "notes": notes,
              "contract_months": 24 if contract > 12 else 12}
    q = price(bundle)
    # Affordability guardrail for micro businesses: in smb_leads.csv micro bundles
    # above Rs 3,000/month churned at 36% within 6 months vs 7% at Rs 2,500-3,000.
    # For micro merchants spending <= Rs 800, enforce an affordable starter cap (~Rs 1,500).
    if p.segment == "micro":
        cap = max(1500 if (p.current_spend and p.current_spend <= 800) else 2999, int(p.current_spend * 2.5)) if p.current_spend else 2999
        for ln in sorted([l for l in bundle["lines"] if not l["optional"]], key=lambda l: -q["by_id"][l["product_id"]]["monthly"]):
            if q["monthly_total"] <= cap:
                break
            if ln["product_id"] in (primary, "P07"):
                continue
            ln["optional"] = True
            q = price(bundle)
        if q["monthly_total"] > cap and lines.get("P07", {}).get("qty", 1) > 1:
            lines["P07"]["qty"] = 1
            q = price(bundle)
        bundle["affordability_cap"] = cap
        if p.current_spend and p.current_spend <= 800:
            notes.append(f"Starter pack right-sized for your current ₹{p.current_spend:,}/mo spend: reliable business fiber replaces mobile hotspot drop-offs; extra billing software is kept as an optional add-on.")
    bundle["quote"] = q
    bundle["install_days"] = install_days(bundle)
    return bundle


def unit_price(pid: str, contract_months: int, n_products: int) -> int:
    """Transparent rule: bundle of 3+ products on 24 months = floor of range,
    3+ products on 12 months = 25% into the range, else mid-point."""
    c = catalogue()[pid]
    lo, hi = c["price_min_inr_per_month"], c["price_max_inr_per_month"]
    t = 0.0 if (n_products >= 3 and contract_months >= 24) else (0.25 if n_products >= 3 else 0.5)
    v = lo + t * (hi - lo)
    r = int(round(v / 10.0) * 10 - 1)  # Rs 1,349-style price points
    return r if lo <= r <= hi else int(round(v))


def price(bundle: dict, selected: set[str] | None = None) -> dict:
    """Price the bundle. `selected` = product ids the owner toggled on (all
    non-optional lines are on by default)."""
    cat = catalogue()
    active = [l for l in bundle["lines"] if (selected is None and not l["optional"]) or (selected is not None and l["product_id"] in selected)]
    n = len(active)
    cm = bundle.get("contract_months", 12)
    by_id, monthly, setup, standalone = {}, 0, 0, 0
    for l in bundle["lines"]:
        c = cat[l["product_id"]]
        up = unit_price(l["product_id"], cm, n)
        mid = unit_price(l["product_id"], 12, 1)
        row = {"product_id": l["product_id"], "name": c["product_name"], "category": c["category"], "unit": c["unit"],
               "qty": l["qty"], "unit_price": up, "monthly": up * l["qty"], "setup": c["one_time_setup_inr"] * l["qty"],
               "why": l["why"], "optional": l["optional"], "on": l in active, "install_days": c["typical_install_days"]}
        by_id[l["product_id"]] = row
        if l in active:
            monthly += row["monthly"]
            setup += row["setup"]
            standalone += mid * l["qty"]
    setup_waived = setup if (cm >= 24 and setup <= 5000) else 0
    return {"items": list(by_id.values()), "by_id": by_id, "monthly_total": monthly,
            "gst_18": round(monthly * 0.18), "monthly_with_gst": round(monthly * 1.18),
            "one_time_setup": setup - setup_waived, "setup_waived": setup_waived,
            "savings_vs_standalone": max(0, standalone - monthly), "contract_months": cm,
            "setup_emi_12m": math.ceil((setup - setup_waived) / 12),
            "price_rule": "3+ products: 25% into each product's price range (12 months) or the floor (24 months). Fewer: mid-point."}


def install_days(bundle: dict) -> int:
    cat = catalogue()
    on = [l for l in bundle["lines"] if not l["optional"]]
    return max((cat[l["product_id"]]["typical_install_days"] for l in on), default=1)
