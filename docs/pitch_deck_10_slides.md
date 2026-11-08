# Project Udyam Digital · 10-Slide Winning Pitch Deck
### Airtel SYNC 2026 Hackathon · Enterprise Track A
**Fictional Operator: Accel Business (Telecom Enterprise Division)**

---

## Slide 1: Title & Executive Summary
- **Title:** Project Udyam Digital: Making India's MSMEs Go Digital in One Sitting
- **Subtitle:** Digital-First Acquisition, Smart KYC, and Transparent Bundling for 6 Crore+ Small Businesses
- **Presenter / Team:** Team Udyam Digital
- **The Core Thesis:** Transform SMB onboarding from a slow, 17.6-day field sales ordeal into a self-serve, 5-minute digital journey on a smartphone in the owner's language.
- **Top Impact:**
  - Lead-to-Activation conversion: **7.4% → 15.5% (+110% lift)**
  - Time to activate: **17.6 days → 5.0 days (-72%)**
  - Blended Cost of Acquisition (CAC): **₹15,000 → ₹5,200 (-65%)**
  - Churn guardrail: micro-bundle affordability capped at ₹2,999/mo (dropping 6-month churn from 36% to 7%).

---

## Slide 2: The MSME Opportunity & The Broken Funnel
- **Market Size:** India has 6.3 Crore MSMEs; Accel Business dominates large enterprise accounts but has <8% SMB share.
- **The Diagnosis (Synthetic Dataset of 5,000 Leads):**
  - 5,000 leads generated → 368 activations (**7.4% conversion**).
  - Steepest drop-off: **Needs Assessed (1,974) → Quote Accepted (861) = 56% lost!**
  - Paperwork friction: 32% drop during KYC due to missing documents, long delays, and name mismatches.
  - Churn & Dissatisfaction: 3+ status follow-up calls per customer; ₹15,000 blended CAC against ₹6,900/mo median bundle.
- **Why Competitors Win:** Digital-first players offer instant sign-up for single products. Accel must offer full bundles with zero human friction.

---

## Slide 3: Target Segmentation & Right-Sized Bundles
| Segment | % Base | Typical Business | Core Problem | Winning Bundle | Price Point |
|---|---|---|---|---|---|
| **Micro Retail & Services** | 55% | Kirana, salon, chemist | Owner's phone + hotspot, UPI QR drops | **Starter:** Biz Fibre 100 + 1 SIM (replaces personal hotspot); optional Cloud POS / UPI tablet | **₹1,448–₹2,499/mo** (Affordability Cap: ₹1,500–₹2,999) |
| **Professional Offices** | 25% | Clinic, CA firm, coaching | Home broadband, personal Gmail, data leaks | Biz Fibre 300 + Cloud Email + Endpoint Security + Backup | ₹4,999–₹7,999/mo |
| **Multi-Site Chains** | 15% | Restaurant chain, retail (3–10 stores) | Mixed ISPs, no central IT, downtime | Multi-Fibre + SD-WAN + Cloud CCTV + 4G Failover | ₹12,999–₹24,999/mo |
| **Small Manufacturers** | 5% | Auto parts, textile, packaging | Need dedicated uptime, machine data | Internet Leased Line (ILL) + IoT Machine Sensors + Firewall | ₹25,000–₹45,000/mo |

- **Affordability Guardrail:** Data proves micro businesses billed >₹3,000/mo churned at 36% vs 7% when kept under ₹3,000. For low-spend solo merchants (spending ≤₹800/mo on mobile), our engine enforces a ₹1,500 starter ceiling with optional toggles, eliminating sticker shock and churn.

---

## Slide 4: Solution Architecture & Conversational Advisor
- **Conversational Advisor (Chat & Voice, EN & HI):**
  - Multi-slot natural language entity and intent extraction.
  - Takes 6 quick inputs (Business Type, Staff, Sites, City/Pincode, GSTIN, Needs).
  - Zero external LLM dependency: deterministic, ultra-fast (<5ms), zero hallucination, 100% compliant with privacy regulations.
  - Transparent bundle generation: automatically validates product catalogue rules, dependency chains, and city-tier availability.

---

## Slide 5: Instant Smart KYC & 1-Click DigiLocker
- **The Frictionless Flow:**
  1. **DPDP Notice & Consent:** Separate, itemised consent for KYC vs optional WhatsApp marketing; instant 1-tap withdrawal/erasure.
  2. **DigiLocker Integration:** Instant pull of authentic GST & Udyam registrations without camera uploads.
  3. **Computer Vision OCR Pipeline:** Auto-deskew (±12°), watermark removal, Laplacian blur rescue, confusable character repair (O/0, I/J).
  4. **Registry Cross-Verification:** Real checksum validator + mock GSTIN/Udyam registries catching cancelled GSTINs, tampered numbers, and altered legal names.
- **100% Catch Rate on Case Specimens (K01–K12):** Catches cancelled GSTIN (K01), tilted image (K02), OCR confusions (K03, K08, K10), blur (K04), missing Udyam (K05), tampered checksum (K06), name mismatch (K07), old bill (K11).

---

## Slide 6: Transparent Quote & Automated Order Tracker
- **No More 5-Page PDF Code Confusion:**
  - One transparent monthly price with toggles for optional add-ons.
  - 12-month vs 24-month contract pricing (24 months waives up to ₹5,000 one-time setup fee).
  - Clear itemised savings vs standalone purchases.
- **Automated Order Tracker (Zero Status Chase Calls):**
  - Real-time milestone tracker: Order Placed → KYC Verified → Site Check → Engineer Assigned → Live.
  - Named field engineer details + arrival slot.
  - Proactive WhatsApp alerts eliminate customer follow-up calls (dropping from 3.0 to <0.2).

---

## Slide 7: Field Force & Channel Partner Symbiosis
- **Digital Adds to the Field Force, Does Not Compete:**
  - **In-Store Partner Portal:** Local resellers and field reps use the digital journey for instant in-person onboarding, earning commissions instantly.
  - **Live Warm Handoffs:** When a customer asks for a human or KYC requires document clarification, the session automatically syncs to the Back Office with pre-filled profile details. Reps call within 2 hours without asking repetitive questions.
  - **Propensity-Driven Lead Scoring:**
    - ML model (Logistic Regression, 5-fold CV AUC 0.71) scores dropped leads using leakage-free initial attributes.
    - Top 30% of leads hold 68% of potential activations.
    - High-value leads routed to Field/Partner visits; low-value leads nudged via automated WhatsApp templates.

---

## Slide 8: Data Privacy & Security (DPDP Act 2023)
- **Consent (s.6):** Itemized, affirmative, in regional languages, with 1-tap delete & withdraw (`DELETE /api/kyc/consent`).
- **Data Minimisation & Purpose Limitation (s.4, s.8):** No PAN or Aadhaar numbers collected. Images discarded immediately after OCR extraction (only SHA-256 fingerprint kept).
- **Masking Everywhere:** GSTIN `37**********1ZS`, IDs masked in UI, back office, audit log, and APIs.
- **Retention & Localization:** 30-day retention post-activation; encrypted rest/transit, India data residency.

---

## Slide 9: Business Impact & Unit Economics
| Metric | Baseline (smb_leads.csv) | Udyam Digital Target | Impact Mechanism |
|---|---|---|---|
| **Lead-to-Active Conversion** | 7.4% (368 / 5,000) | **15.5% (774 / 5,000)** | +110% lift; removes drop-offs across quote & KYC |
| **Onboarding Cycle Time** | 17.6 days | **5.0 days (median)** | Instant quote & KYC; installation scheduled on checkout |
| **Blended CAC** | ₹15,000 | **₹5,200** | 65% reduction; digital self-serve + propensity routing |
| **Status Chases** | 3.0 calls/customer | **0.2 calls/customer** | WhatsApp proactive updates & live visual tracker |
| **6-Month Churn (Micro)** | 36% | **7%** | Strict ₹2,999 affordability cap & right-sized bundles |
| **Quarterly Revenue Added** | Baseline: ₹2.54 Cr | **Projected: ₹5.34 Cr** | **+₹2.80 Cr incremental ARR per 5,000 leads** |

---

## Slide 10: Rollout Roadmap & Risk Mitigation
- **Phased Rollout:**
  - **Phase 1 (Months 1–2):** Deploy Tier-1 metro digital portal for Micro Retail & Professional segments; integrate DigiLocker.
  - **Phase 2 (Months 3–4):** Expand to Tier-2 cities with 5G AirFiber fallback; roll out Partner Assisted App.
  - **Phase 3 (Months 5–6):** Scale WhatsApp bot flow, regional languages (Tamil, Telugu, Marathi, Gujarati), and automated field dispatch.
- **Risk Mitigation:**
  - *Risk: Fibre infeasibility at shop location* → *Fix: Auto-switch to 5G AirFiber FWA within 48 hours.*
  - *Risk: Partner pushback* → *Fix: Channel partner attribution & commission tracking on digital links.*
  - *Risk: Document fraud* → *Fix: Automated GST/Udyam registry validation and mismatch alerts.*
