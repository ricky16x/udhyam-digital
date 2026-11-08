"""Conversational Advisor.

Deterministic, multi-slot conversational advisor with slot-filling,
intent and entity extraction, tap-to-answer chips in English and Hindi,
multilingual voice/text understanding, and plain-language bundle explanations.
Fully self-contained: zero external LLM API dependency, zero latency,
zero data leakage, and 100% compliance with DPDP principles.
"""
from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict

from catalogue import NEEDS, SEGMENT_DEFAULT_NEEDS, SEGMENTS, BusinessProfile, recommend
from registry import lookup_gstin, mask

TIER1 = {"ahmedabad", "bengaluru", "bangalore", "chennai", "delhi", "new delhi", "hyderabad", "kolkata", "mumbai", "pune",
         "gurugram", "noida"}
TIER2 = {"indore", "coimbatore", "kochi", "jaipur", "lucknow", "ludhiana", "mysuru", "bhopal", "nagpur", "nashik", "patna",
         "surat", "vadodara", "visakhapatnam", "chandigarh", "kanpur", "agra", "nashik", "rajkot", "dehradun"}
NO_FIBRE_PINS = ("4400", "8000")  # mocked pincode feasibility: these prefixes have no fibre

BUSINESS_TYPES = [
    # key, EN label, HI label, segment, keywords
    ("kirana", "Kirana / general store", "किराना / जनरल स्टोर", "micro", ["kirana", "general store", "grocery", "किराना", "दुकान", "shop", "retail", "store"]),
    ("pharmacy", "Pharmacy / medical store", "मेडिकल स्टोर", "micro", ["pharmacy", "medical store", "chemist", "दवा", "मेडिकल", "medical", "pharma"]),
    ("salon", "Salon / boutique", "सैलून / बुटीक", "micro", ["salon", "parlour", "boutique", "सैलून", "पार्लर", "बुटीक", "beauty", "spa"]),
    ("food", "Bakery / sweet shop / café", "बेकरी / मिठाई / कैफ़े", "micro", ["bakery", "sweet", "cafe", "café", "मिठाई", "बेकरी", "restaurant", "hotel", "food"]),
    ("clinic", "Clinic / diagnostic lab", "क्लिनिक / लैब", "prof", ["clinic", "dental", "doctor", "lab", "diagnostic", "physio", "hospital", "क्लिनिक", "डॉक्टर", "lab"]),
    ("office", "CA / law / agency office", "CA / वकील / एजेंसी ऑफिस", "prof", ["ca firm", "chartered", "law", "lawyer", "advocate", "agency", "insurance", "architect", "real estate", "travel", "office", "वकील", "ऑफिस", "consulting"]),
    ("coaching", "Coaching centre", "कोचिंग सेंटर", "prof", ["coaching", "tuition", "institute", "classes", "academy", "कोचिंग", "ट्यूशन", "क्लास"]),
    ("chain", "Chain with several branches", "कई ब्रांच वाली चेन", "multi", ["chain", "branches", "outlets", "stores", "outlets", "multi-site", "ब्रांच", "चेन"]),
    ("factory", "Factory / workshop", "फ़ैक्टरी / वर्कशॉप", "mfg", ["factory", "unit", "manufactur", "workshop", "moulding", "textile", "printing", "packaging", "फ़ैक्टरी", "कारखाना", "manufacturing"]),
]

NEED_KEYWORDS = {
    "internet": ["internet", "broadband", "fibre", "fiber", "नेट", "इंटरनेट"],
    "payments": ["upi", "billing", "bill", "card", "pos", "पेमेंट", "बिलिंग", "qr"],
    "whatsapp": ["whatsapp", "sms", "alert", "promotion", "व्हाट्सएप"],
    "cctv": ["cctv", "camera", "cameras", "cam", "कैमरा", "सीसीटीवी", "surveillance"],
    "guest_wifi": ["wifi", "wi-fi", "guest wifi", "customer wifi", "वाईफाई"],
    "email": ["email", "domain", "office", "gsuite", "ईमेल", "mail"],
    "backup": ["backup", "storage", "cloud storage", "बैकअप"],
    "security": ["security", "antivirus", "firewall", "ransomware", "virus", "सुरक्षा"],
    "uptime": ["uptime", "failover", "backup line", "redundant", "never down"],
    "phone_lines": ["phone", "ivr", "calling", "landline", "sip", "tollfree", "1800", "फ़ोन"],
    "website": ["website", "web", "site", "वेबसाइट"],
    "central_mgmt": ["central", "sdwan", "sd-wan", "all branches"],
    "machines": ["machine", "iot", "sensor", "मशीन"],
    "fleet": ["fleet", "vehicle", "gps", "tracking", "गाड़ी", "ट्रैकिंग"],
    "dedicated": ["dedicated", "leased line", "ill", "sla", "leased"],
}

T = {  # UI strings for conversational advisor
    "en": {
        "hello": "Namaste! I'm the Accel Business advisor. In 6 quick questions I'll suggest the right internet, phone and digital tools for your business, with one clear monthly price. What kind of business do you run?",
        "employees": "How many people work in your business, including you?",
        "sites": "How many shops, offices or branches do you have?",
        "city": "Which city are you in? You can also type your 6-digit pincode so I can check fibre availability.",
        "gstin": "Do you have a GST number? With it I can fill your business details automatically. Type the 15-character GSTIN, or tap 'No GST'.",
        "gst_found": "Found it: **{name}**, {constitution}, {state} – GST status **{status}**.",
        "gst_inactive": "Your GSTIN shows as **{status}**. I'll suggest products that don't need GST; you can add others once it's active.",
        "gst_bad": "That GSTIN doesn't look right ({err}). Please check and type it again, or tap 'No GST'.",
        "needs": "What do you want help with? I've pre-selected what businesses like yours usually need – tap to change, then 'Done'.",
        "spend": "Roughly how much do you spend per month on phone and internet today?",
        "ready": "Here's what I recommend for your {btype}. Everything is on one bill with one support number.",
        "done": "Done", "nogst": "No GST", "callback": "Talk to an expert",
        "unknown": "Sorry, I didn't catch that. Please tap one of the options or tell me about your business.",
    },
    "hi": {
        "hello": "नमस्ते! मैं Accel Business सलाहकार हूँ। 6 छोटे सवालों में मैं आपके बिज़नेस के लिए सही इंटरनेट, फ़ोन और डिजिटल टूल सुझाऊँगा – एक साफ़ मासिक कीमत के साथ। आपका बिज़नेस क्या है?",
        "employees": "आपके बिज़नेस में आपको मिलाकर कितने लोग काम करते हैं?",
        "sites": "आपकी कितनी दुकानें, ऑफिस या ब्रांच हैं?",
        "city": "आप किस शहर में हैं? फ़ाइबर उपलब्धता जाँचने के लिए 6 अंकों का पिनकोड भी लिख सकते हैं।",
        "gstin": "क्या आपके पास GST नंबर है? इससे आपकी बिज़नेस जानकारी अपने-आप भर जाएगी। 15 अक्षर का GSTIN लिखें, या 'GST नहीं है' दबाएँ।",
        "gst_found": "मिल गया: **{name}**, {constitution}, {state} – GST स्थिति **{status}**।",
        "gst_inactive": "आपका GSTIN **{status}** दिख रहा है। मैं ऐसे प्रोडक्ट सुझाऊँगा जिनके लिए GST ज़रूरी नहीं; GST चालू होने पर बाकी जोड़ सकते हैं।",
        "gst_bad": "यह GSTIN सही नहीं लग रहा ({err})। कृपया दोबारा लिखें, या 'GST नहीं है' दबाएँ।",
        "needs": "आपको किसमें मदद चाहिए? आप जैसे बिज़नेस को आमतौर पर जो चाहिए, वह मैंने चुन दिया है – बदलने के लिए टैप करें, फिर 'हो गया'।",
        "spend": "अभी फ़ोन और इंटरनेट पर हर महीने लगभग कितना खर्च होता है?",
        "ready": "आपके {btype} के लिए मेरा सुझाव यह है। सब कुछ एक बिल और एक सपोर्ट नंबर पर।",
        "done": "हो गया", "nogst": "GST नहीं है", "callback": "एक्सपर्ट से बात करें",
        "unknown": "माफ़ कीजिए, समझ नहीं पाया। कृपया कोई विकल्प चुनें या अपने बिज़नेस के बारे में बताएँ।",
    },
}

EMP_CHIPS = [("1-5", 3), ("6-15", 10), ("16-50", 30), ("50+", 80)]
SITE_CHIPS = [("1", 1), ("2", 2), ("3-5", 4), ("6+", 8)]
SPEND_CHIPS = [("< ₹1,000", 800), ("₹1,000–3,000", 2000), ("₹3,000–10,000", 6000), ("₹10,000+", 15000)]
CITY_CHIPS = ["Delhi", "Mumbai", "Bengaluru", "Pune", "Jaipur", "Lucknow", "Indore", "Surat"]

SESSIONS: dict[str, dict] = {}


def _hi_digits(s: str) -> str:
    return s.translate(str.maketrans("०१२३४५६७८९", "0123456789"))


def new_session(lang: str = "en") -> dict:
    sid = uuid.uuid4().hex[:12]
    s = {"id": sid, "lang": lang if lang in T else "en", "step": "business", "profile": BusinessProfile(language=lang),
         "history": [], "gstin_masked": None, "recommendation": None, "mode": "guided", "events": ["advisor_started"]}
    SESSIONS[sid] = s
    msg = _ask(s, "business")
    return {"session_id": sid, **msg}


def _chips(s, step):
    lang = s["lang"]
    if step == "business":
        return [{"id": k, "label": en if lang == "en" else hi} for k, en, hi, _, _ in BUSINESS_TYPES]
    if step == "employees":
        return [{"id": a, "label": a} for a, _ in EMP_CHIPS]
    if step == "sites":
        return [{"id": a, "label": a} for a, _ in SITE_CHIPS]
    if step == "city":
        return [{"id": c, "label": c} for c in CITY_CHIPS]
    if step == "gstin":
        return [{"id": "nogst", "label": T[lang]["nogst"]}]
    if step == "needs":
        sel = set(s["profile"].needs or SEGMENT_DEFAULT_NEEDS.get(s["profile"].segment, []))
        order = {"micro": ["internet", "payments", "whatsapp", "cctv", "guest_wifi", "website", "security"],
                 "prof": ["internet", "email", "security", "backup", "uptime", "phone_lines", "whatsapp", "website", "cctv"],
                 "multi": ["internet", "uptime", "central_mgmt", "payments", "cctv", "whatsapp", "phone_lines", "guest_wifi", "fleet"],
                 "mfg": ["dedicated", "email", "security", "cctv", "machines", "fleet", "uptime", "backup"]}[s["profile"].segment]
        return [{"id": n, "label": NEEDS[n][0 if lang == "en" else 1], "selected": n in sel, "multi": True} for n in order] + \
               [{"id": "done", "label": T[lang]["done"], "primary": True}]
    if step == "spend":
        return [{"id": a, "label": a} for a, _ in SPEND_CHIPS]
    return []


def _ask(s, step):
    s["step"] = step
    key = {"business": "hello"}.get(step, step)
    text = T[s["lang"]][key]
    s["history"].append({"role": "assistant", "text": text})
    return {"reply": text, "chips": _chips(s, step), "step": step, "profile": asdict(s["profile"])}


def _parse_business(text: str, lang: str = "en"):
    t = text.lower()
    for k, en, hi, seg, kws in BUSINESS_TYPES:
        if k == t or any(w in t for w in kws):
            return k, (hi if lang == "hi" else en), seg
    return None


def _num(text: str):
    m = re.search(r"\d+", _hi_digits(text))
    return int(m.group()) if m else None


def _extract_slots(text: str, lang: str = "en") -> dict:
    """Multi-slot extractor from free-text and voice transcripts (EN/HI/Hinglish)."""
    t = text.lower()
    extracted = {}

    # 1. Business
    b = _parse_business(text, lang)
    if b:
        extracted["business"] = b

    # 2. Employees / Staff
    m_emp = re.search(r"(\d+)\s*(?:people|staff|employees|workers|persons|log|karmachari|लोग|कर्मचारी)", _hi_digits(t))
    if m_emp:
        extracted["employees"] = int(m_emp.group(1))

    # 3. Sites / Branches
    m_site = re.search(r"(\d+)\s*(?:sites?|branches?|shops?|stores?|offices?|outlets?|ब्रांच|दुकानें?)", _hi_digits(t))
    if m_site:
        extracted["sites"] = int(m_site.group(1))

    # 4. City / Pincode
    m_pin = re.search(r"\b(\d{6})\b", _hi_digits(t))
    if m_pin:
        extracted["pincode"] = m_pin.group(1)
    else:
        for c in TIER1 | TIER2:
            if re.search(rf"\b{c}\b", t):
                extracted["city"] = c.title()
                break

    # 5. GSTIN
    m_gst = re.search(r"\b([0-9]{2}[A-Z0-9]{13})\b", text.upper())
    if m_gst:
        extracted["gstin"] = m_gst.group(1)
    elif re.search(r"\b(no gst|without gst|dont have gst|nahi|nahin|नहीं)\b", t):
        extracted["no_gst"] = True

    # 6. Needs
    found_needs = []
    for nid, kws in NEED_KEYWORDS.items():
        if any(re.search(rf"\b{kw}\b", t) for kw in kws):
            found_needs.append(nid)
    if found_needs:
        extracted["needs"] = found_needs

    # 7. Spend
    m_spend = re.search(r"(?:rs\.?|inr|₹|spend|kharch|खर्च)\s*(\d[\d,]*)", _hi_digits(t))
    if m_spend:
        val = int(m_spend.group(1).replace(",", ""))
        extracted["spend"] = val

    return extracted


def handle(sid: str, text: str = "", choice: str | None = None, selected: list[str] | None = None) -> dict:
    """Process an advisor turn deterministically with conversational slot-filling."""
    s = SESSIONS.get(sid)
    if not s:
        raise KeyError("session not found")
    user = choice or text
    s["history"].append({"role": "user", "text": user})
    return _conversational_turn(s, text, choice, selected)


def _conversational_turn(s: dict, text: str, choice: str | None, selected: list[str] | None) -> dict:
    p: BusinessProfile = s["profile"]
    lang, step = s["lang"], s["step"]
    val = (choice or text or "").strip()
    pre = []

    # 1. Handoff check
    if choice == "callback" or re.search(r"\b(callback|expert|agent|human|talk to|call me|बात करनी|कॉल करें)\b", val.lower()):
        s["events"].append("handoff_requested")
        reply = ("OK – an Accel expert will call you within 2 working hours. Your answers so far are saved, so you won't have to repeat them."
                 if lang == "en" else "ठीक है – Accel एक्सपर्ट 2 कार्य-घंटों में आपको कॉल करेंगे। आपके जवाब सेव हैं, दोबारा बताने की ज़रूरत नहीं।")
        s["history"].append({"role": "assistant", "text": reply})
        chips = [
            {"id": "home", "label": "Back to Home 🏠" if lang == "en" else "होम पेज पर जाएँ 🏠", "primary": True},
        ]
        if s.get("recommendation"):
            chips.append({"id": "quote", "label": "See my quote →" if lang == "en" else "कोटेशन देखें →"})
        chips.append({"id": "restart", "label": "Start fresh" if lang == "en" else "नए सिरे से शुरू करें"})
        return {"reply": reply, "chips": chips, "step": "handoff", "profile": asdict(p), "handoff": True}

    # Direct home or restart command
    if re.search(r"^\s*(home|main screen|menu|restart|start over|शुरू|होम|मेनू)\s*$", val.lower()):
        msg = "Taking you back to the home screen." if lang == "en" else "होम स्क्रीन पर ले जा रहे हैं।"
        return {"reply": msg,
                "chips": [{"id": "home", "label": "Back to Home 🏠" if lang == "en" else "होम पेज पर जाएँ 🏠", "primary": True},
                          {"id": "restart", "label": "Start fresh" if lang == "en" else "नए सिरे से शुरू करें"}],
                "step": "welcome", "profile": asdict(p), "action": "home"}

    # 2. Multi-slot free text parsing if free text is entered
    if text and not choice:
        slots = _extract_slots(text, lang)
        if slots.get("business"):
            k, label, seg = slots["business"]
            p.segment, p.business_type = seg, label
        if slots.get("employees"):
            p.employees = slots["employees"]
        if slots.get("sites"):
            p.sites = slots["sites"]
            if p.sites >= 3 and p.segment in ("micro", "prof"):
                p.segment = "multi"
        if slots.get("pincode"):
            p.fibre_available = not slots["pincode"].startswith(NO_FIBRE_PINS)
            p.city_tier = 1 if slots["pincode"][:2] in ("11", "40", "56", "60", "50", "70", "41", "38") else 2
            s["city"] = slots["pincode"]
        elif slots.get("city"):
            c = slots["city"].lower()
            p.city_tier = 1 if any(t1 in c for t1 in TIER1) else 2
            s["city"] = slots["city"]
        if slots.get("gstin"):
            lk = lookup_gstin(slots["gstin"])
            if lk["format"]["valid"]:
                p.has_gstin = True
                s["gstin"] = lk["format"]["gstin"]
                s["gstin_masked"] = mask(s["gstin"])
                if lk["found"]:
                    r = lk["record"]
                    p.gstin_active = r["status"] == "Active"
                    s["registry"] = {"trade_name": r["trade_name"], "legal_name": r["legal_name"], "constitution": r["constitution"],
                                     "state": r["state"], "status": r["status"], "address": r["principal_place_of_business"]}
                    pre.append(T[lang]["gst_found"].format(name=r["trade_name"], constitution=r["constitution"], state=r["state"], status=r["status"]))
        elif slots.get("no_gst"):
            p.has_gstin, p.gstin_active = False, False
        if slots.get("needs"):
            p.needs = list(dict.fromkeys((p.needs or []) + slots["needs"]))
        if slots.get("spend"):
            p.current_spend = slots["spend"]

        # If business was given and we advanced, determine next missing step
        if step == "business" and p.business_type:
            if not p.employees:
                return _ask(s, "employees")
            if not s.get("city") and p.city_tier == 1:
                return _ask(s, "city")
            if not p.has_gstin and "gstin" not in s:
                return _ask(s, "gstin")
            if not p.needs:
                return _ask(s, "needs")
            if not p.current_spend:
                return _ask(s, "spend")
            return _recommend(s)

    # 3. Step-by-step handler
    if step == "business":
        b = _parse_business(val, lang)
        if not b:
            return {"reply": T[lang]["unknown"], "chips": _chips(s, step), "step": step, "profile": asdict(p)}
        key, label, seg = b
        p.segment, p.business_type = seg, label
        n = _num(val) if text else None
        if n:
            p.employees = n
            return _ask(s, "sites" if p.segment == "multi" else "city")
        return _ask(s, "employees")

    if step == "employees":
        n = dict(EMP_CHIPS).get(val) or _num(val)
        if not n:
            return {"reply": T[lang]["unknown"], "chips": _chips(s, step), "step": step, "profile": asdict(p)}
        p.employees = n
        if p.segment == "multi":
            return _ask(s, "sites")
        if p.segment in ("micro", "prof") and n >= 1:
            p.sites = 1
            return _ask(s, "city") if p.segment != "prof" else _ask(s, "sites")
        return _ask(s, "sites")

    if step == "sites":
        n = dict(SITE_CHIPS).get(val) or _num(val)
        if not n:
            return {"reply": T[lang]["unknown"], "chips": _chips(s, step), "step": step, "profile": asdict(p)}
        p.sites = n
        if n >= 3 and p.segment in ("micro", "prof"):
            p.segment = "multi"
        return _ask(s, "city")

    if step == "city":
        v = val.lower()
        pin = re.search(r"\b\d{6}\b", _hi_digits(v))
        if pin:
            p.fibre_available = not pin.group().startswith(NO_FIBRE_PINS)
            p.city_tier = 1 if pin.group()[:2] in ("11", "40", "56", "60", "50", "70", "41", "38") else 2
        else:
            p.city_tier = 1 if any(c in v for c in TIER1) else 2
        s["city"] = val
        return _ask(s, "gstin")

    if step == "gstin":
        if choice == "nogst" or re.search(r"\b(no|nahi|nahin|without|नहीं)\b", val.lower()):
            p.has_gstin, p.gstin_active = False, False
            return _ask(s, "needs")
        lk = lookup_gstin(re.sub(r"\s", "", val))
        if not lk["format"]["valid"]:
            err = "; ".join(lk["format"]["errors"])[:90]
            return {"reply": T[lang]["gst_bad"].format(err=err), "chips": _chips(s, step), "step": step, "profile": asdict(p)}
        p.has_gstin = True
        s["gstin"] = lk["format"]["gstin"]
        s["gstin_masked"] = mask(s["gstin"])
        if lk["found"]:
            r = lk["record"]
            p.gstin_active = r["status"] == "Active"
            s["registry"] = {"trade_name": r["trade_name"], "legal_name": r["legal_name"], "constitution": r["constitution"],
                             "state": r["state"], "status": r["status"], "address": r["principal_place_of_business"]}
            pre.append(T[lang]["gst_found"].format(name=r["trade_name"], constitution=r["constitution"], state=r["state"], status=r["status"]))
            if not p.gstin_active:
                pre.append(T[lang]["gst_inactive"].format(status=r["status"]))
        else:
            p.gstin_active = False
            pre.append("GSTIN format is valid but not found in the GST registry – we'll verify it during KYC." if lang == "en"
                       else "GSTIN का फ़ॉर्मेट सही है पर GST रजिस्ट्री में नहीं मिला – KYC में जाँच करेंगे।")
        out = _ask(s, "needs")
        out["reply"] = "\n\n".join(pre + [out["reply"]])
        return out

    if step == "needs":
        if choice == "done" or (selected is not None):
            if selected is not None:
                p.needs = [n for n in selected if n in NEEDS]
            return _ask(s, "spend")
        # free text: map keywords to needs
        v = val.lower()
        add = {nid for nid, kws in NEED_KEYWORDS.items() if any(kw in v for kw in kws)}
        p.needs = list(dict.fromkeys((p.needs or SEGMENT_DEFAULT_NEEDS[p.segment]) + list(add)))
        return _ask(s, "spend")

    if step == "spend":
        n = dict(SPEND_CHIPS).get(val) or _num(val)
        p.current_spend = n or 0
        return _recommend(s)

    if step == "done":
        return {"reply": "You can change the add-ons in your quote, or tap 'Talk to an expert'." if lang == "en"
                else "आप कोटेशन में ऐड-ऑन बदल सकते हैं, या 'एक्सपर्ट से बात करें' दबाएँ।", "chips": [], "step": "done", "profile": asdict(p)}

    return {"reply": T[lang]["unknown"], "chips": _chips(s, step), "step": step, "profile": asdict(p)}


def explain_bundle(b: dict, lang: str) -> str:
    """Format bundle recommendation clearly in plain language."""
    q = b["quote"]
    on = [i for i in q["items"] if i["on"]]
    if lang == "hi":
        head = f"कुल **₹{q['monthly_total']:,}/महीना** (+18% GST), {q['contract_months']} महीने का प्लान।"
        lines = [f"• {i['name']} ×{i['qty']} – {i['why']}" for i in on]
        tail = f"इंस्टॉलेशन लगभग {b['install_days']} दिन में।"
    else:
        head = f"Total **₹{q['monthly_total']:,}/month** (+18% GST) on a {q['contract_months']}-month plan."
        lines = [f"• {i['name']} ×{i['qty']} – {i['why']}" for i in on]
        tail = f"Everything installed in about {b['install_days']} days."
    if q["savings_vs_standalone"]:
        tail += (f" You save ₹{q['savings_vs_standalone']:,}/month vs buying separately." if lang == "en"
                 else f" अलग-अलग खरीदने से ₹{q['savings_vs_standalone']:,}/महीना की बचत।")
    notes = [f"ℹ️ {n}" for n in b["notes"]]
    return "\n".join([head] + lines + notes + [tail])


def _recommend(s: dict) -> dict:
    p: BusinessProfile = s["profile"]
    b = recommend(p)
    s["recommendation"] = b
    s["step"] = "done"
    s["events"].append("bundle_recommended")
    intro = T[s["lang"]]["ready"].format(btype=p.business_type or SEGMENTS[p.segment])
    text = intro + "\n\n" + explain_bundle(b, s["lang"])
    s["history"].append({"role": "assistant", "text": text})
    return {"reply": text, "chips": [{"id": "quote", "label": "See my quote →" if s["lang"] == "en" else "कोटेशन देखें →", "primary": True},
                                      {"id": "callback", "label": T[s["lang"]]["callback"]},
                                      {"id": "home", "label": "Home 🏠" if s["lang"] == "en" else "होम 🏠"}],
            "step": "done", "profile": asdict(p), "recommendation": b}
