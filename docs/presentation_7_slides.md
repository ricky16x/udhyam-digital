# Project Udyam Digital · Official 7-Slide Presentation
### Airtel SYNC Hackathon 2026 · Enterprise Track A
**PowerPoint File:** [`Submission_Project_Udyam_Digital_TrackA.pptx`](../Submission_Project_Udyam_Digital_TrackA.pptx)  
*(Built strictly using the official template: `instructions/6ad9d4887d445_airtel_sync/Submission Template_Sync.pptx`)*

---

## Slide 1: Cover & Title
- **Headline:** PROJECT UDYAM DIGITAL
- **Subtitle:** Making India's MSMEs Go Digital in One Sitting
- **Context:** Airtel SYNC Hackathon 2026 · Enterprise Track A
- **Pillars:** Automated Needs Discovery | Smart KYC & DigiLocker | Transparent Bundling | Field Symbiosis
- **Thesis:** Transforming SMB acquisition from a 17.6-day field ordeal into a 5-minute self-serve digital journey on a smartphone in the owner's language.

---

## Slide 2: The MSME Problem: A Broken Acquisition Funnel
- **Core Challenge:** Accel Business leads corporate accounts but holds <8% share of India's 6.3 Crore MSMEs.
- **Empirical Funnel Analysis (from 5,000 historical leads):**
  - **7.4% Conversion:** Only 368 out of 5,000 leads activate.
  - **The Quote Cliff (56% Lost):** 1,974 leads assessed $\to$ only 861 accept quotes. Reps push jargon-filled enterprise PDFs with sticker shock.
  - **The KYC Barrier (32% Lost):** Paper-heavy document collection over email/visits leads to fatigue and abandonment.
  - **The Churn Cliff (36% Churn):** Micro merchants billed >₹3,000/mo churn at 36% within 6 months vs 7% under ₹3,000.
  - **17.6 Days & 3.0 Chase Calls:** Inordinate delay from lead to activation, resulting in ₹15,000 blended CAC.

---

## Slide 3: Target Customer Segmentation & Right-Sized Bundles
- **Priority 1: Professional Offices (Clinics, CA firms, Coaching centres):**
  - *Winning Bundle:* Biz Fibre 300 + Cloud Email + Endpoint Security + 1 TB Cloud Backup.
  - *Pricing:* **₹5,200 – ₹5,400/month** on 12-month contract.
  - *Strategic Rationale:* 90%+ GST compliance, high willingness to pay for data security and commercial SLA.
- **Priority 2: Micro Retail & Services (Kirana stores, Salons, Pharmacies):**
  - *Winning Bundle:* **Starter Pack: Biz Fibre 100 + 1 Business SIM** (replaces mobile hotspot) with optional Cloud POS billing tablet.
  - *Pricing:* **₹1,448 – ₹2,499/month** (Affordability ceiling $\le$ ₹1,500 for spend $\le$ ₹800).
  - *Strategic Rationale:* Eliminates peak-hour UPI dropouts while keeping costs accessible to prevent churn.
- **Priority 3: Multi-Site Retail Chains (3–10 outlets):**
  - *Winning Bundle:* Multi-site Fibre + Managed SD-WAN + Cloud CCTV + 4G Failover (₹21,000 – ₹33,000/mo).
- **Priority 4: Small Manufacturers:**
  - *Winning Bundle:* Internet Leased Line (ILL) + Machine Monitoring IoT + Fleet GPS (₹32,000 – ₹58,000/mo).

---

## Slide 4: Our Approach: The 4 Pillars of Udyam Digital
1. **Conversational Advisor (EN / HI / Voice):**
   - Deterministic multi-slot entity parsing in <5ms.
   - Zero external LLM calls $\to$ zero API failure, zero hallucination, 100% DPDP privacy.
   - Plain-language explanation of bundle value.
2. **Dynamic Bundle Engine:**
   - Evaluates 25 catalogue products, eligibility criteria, and dependency trees mathematically.
   - Enforces micro-spend affordability caps and transparent bundle discounts.
3. **Instant Smart KYC (DPDP 2023 Compliant):**
   - 1-click DigiLocker retrieval for authentic Udyam and GST certificates.
   - Computer vision OCR pipeline with auto-deskew ($\pm 12^\circ$), blur rescue, and confusable character repair.
   - 1-tap data withdrawal and erasure button (`DELETE /api/kyc/consent`).
4. **Proactive Order Tracker:**
   - Real-time milestone tracker with named technicians and SLA countdown.
   - Proactive WhatsApp updates eliminate customer chase calls.

---

## Slide 5: Detailed Competitive Analysis: Accel's Unfair Advantage

| Evaluation Dimension | Accel Udyam Digital | Legacy Telcos (Jio/Vi) | SaaS Point Tools (Khatabook/Zoho) | Local Unorganized Resellers |
| :--- | :--- | :--- | :--- | :--- |
| **Onboarding Journey** | **5-Min Digital Self-Serve** (Phone, DigiLocker, Voice) | 14–20 Days Field Visits (Paper forms & physical reps) | Instant App Download (Self-serve, card payment) | Fragmented Manual (Cash / unorganised) |
| **Product Offering** | **Unified Bundle** (Broadband + SIMs + Cloud + POS) | Siloed Products (SIM separate from fiber) | Single Point Tool (Accounting OR POS only) | Single piece (Dongle or local ISP) |
| **Billing & Support** | **1 Consolidated Bill** with single enterprise support no. | Multiple Separate Bills with confusing account codes | Multiple Subscriptions across 3-4 vendors | No formal contract; zero SLA or GST credit |
| **Network SLA & Reliability** | **Commercial 99% SLA** with 4-hr local fiber restoration | Best-effort consumer SLA for retail SMBs | Dependent on 3rd-party internet connectivity | Consumer prepaid with frequent evening lag |

---

## Slide 6: Field Force & Channel Partner Symbiosis
*Digital empowers local partners and sales reps rather than cannibalizing them:*
1. **Assisted In-Store Portal:** Local computer shops and retail partners use the same mobile web journey to onboard walk-in kirana owners in 5 minutes, earning instant digital commission attribution.
2. **Warm Live Handoffs:** When an SMB asks for a human or KYC encounters a legal variance, chat context, declared needs, and GST details sync directly to the Back Office. Reps call within 2 hours fully prepared.
3. **ML Propensity Scoring (AUC 0.76):** Trained on 5,000 historical leads. Scores dropped leads as `HIGH`, `MEDIUM`, or `LOW`. Top 30% of leads capture 68% of potential activations.
4. **Optimised Dispatch:** High-value leads get dispatched for physical field visits; low-value micro leads receive automated WhatsApp recovery nudges, slashing blended CAC from ₹15,000 to ₹5,200.

---

## Slide 7: Business Impact, Unit Economics & 12-Month Rollout
- **Quantified Impact Metrics:**
  - **Lead-to-Activation Conversion:** **7.4% $\to$ 15.5% (+110% lift)** by eliminating quote & KYC drop-offs.
  - **Time to Activate:** **17.6 days $\to$ 5.0 days (-72%)** via instant DigiLocker KYC and online scheduling.
  - **Blended CAC:** **₹15,000 $\to$ ₹5,200 (-65%)** via digital self-serve and propensity routing.
  - **Customer Chase Calls:** **3.0 calls $\to$ 0.2 calls** via real-time milestone tracker and WhatsApp alerts.
  - **Micro Churn:** **36% $\to$ <7%** via right-sized starter pricing.
- **12-Month Phased Rollout Roadmap:**
  - **Months 1–3 (Pilot Launch):** Deploy in Delhi NCR & Pune across Professional Offices & Kirana segments. Validate DigiLocker & UPI Autopay.
  - **Months 4–6 (Partner Enablement):** Integrate 500+ local channel partners with the assisted onboarding portal and live commission tracking.
  - **Months 7–9 (Regional Scale):** Expand vernacular support to Tamil, Telugu, Marathi, and Bengali. Scale back-office ML lead recovery.
  - **Months 10–12 (Pan-India Expansion):** Full nationwide rollout across 100+ cities. Target: 50,000 active MSME bundles activated.
