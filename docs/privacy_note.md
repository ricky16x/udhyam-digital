# Udyam Digital: data privacy and security note (1 page)

**Law it is built for:** Digital Personal Data Protection Act, 2023 (DPDP), plus telecom KYC rules for business connections. The design treats the synthetic data as if it were real customer data.

## 1. Consent before any document (DPDP s.6)
- A dedicated consent screen appears **before** the first upload, in the owner's language (English or Hindi today; more languages come from the same strings file). It states **what** we collect, **why**, **how long** we keep it, and **the owner's rights**.
- Purposes are separate and itemised. *KYC verification* and *service activation* are required. *WhatsApp offers* is optional and unticked by default, so the owner can still buy without agreeing to it.
- Each consent is stored with an ID, the purposes, a version (`2026-10-v1`), a timestamp and the language. Uploads are refused (HTTP 403) until consent exists.
- **Withdraw and erase** takes one tap on the KYC screen (`DELETE /api/kyc/consent/{session}`). It deletes the consent and every extracted KYC field for that session.

## 2. Purpose limitation and data minimisation (s.4, s.8)
- The advisor asks **only** about the business: type, size, sites, city or pincode, needs and spend. It never asks for Aadhaar, PAN, bank or card details. The advisor engine strictly restricts data collection to business eligibility requirements.
- KYC collects the four documents the activation process needs, and nothing more. The signatory ID is the synthetic ID card, not an Aadhaar number. E-sign uses Aadhaar **OTP** through a licensed e-sign provider, so Accel never sees or stores the Aadhaar number.
- **Images are discarded as soon as OCR finishes.** Only the extracted fields and a SHA-256 fingerprint (kept for audit and tamper evidence) are stored.
- GSTIN lookup returns only the fields needed to prefill the form and decide eligibility (trade name, constitution, state, status). Full registry records stay on the server.

## 3. Masking everywhere outside the verification step
- GSTIN `37**********1ZS`, Udyam `UDYAM-**********772`, ID and consumer numbers show only their last 4 characters. This applies in the UI, the back office, API responses and logs (`registry.mask`).
- The audit log keeps event, time, a truncated session ID and the document hash. It never holds raw identifiers or document text.

## 4. Retention
| Data | Kept for | Then |
|---|---|---|
| Document images | Seconds (in memory during OCR) | Deleted, never written to disk |
| Extracted KYC fields | 30 days after activation, or as long as licence/KYC rules require | Deleted or archived encrypted under the licence-mandated retention |
| Abandoned journeys (no order) | 30 days | Deleted |
| Advisor chat transcript | 30 days, for quality only | Deleted |
| Consent records and audit log | Life of the relationship + 3 years | Kept as evidence of consent |

## 5. Accuracy and fairness (s.8(3))
- Every automated decision is explained in plain language ("Bill is 257 days old – limit 90"). Each failed check says how to fix it, and a borderline case goes to **human review**, not auto-rejection.
- OCR repairs (O→0, I→J) are accepted only when the GST **registry** confirms the result, so a tampered GSTIN can never be "repaired" into a valid one.
- The lead propensity score decides **who gets a call first**. It never decides who gets service. It uses no protected attributes, and language is used only to route the lead to a matching-language agent.

## 6. Security controls (production design)
- TLS 1.3 in transit. Field-level AES-256 encryption at rest for KYC fields, with keys in a cloud KMS. Data stays in India-region hosting.
- Role-based access: field and partner users see masked identifiers and the leads assigned to them. Only the KYC operations team can unmask, and every unmask is logged.
- Upload hardening: 8 MB limit, image types only, decoding with OpenCV in an isolated worker, and no file is ever executed or served back.
- **Zero 3rd-party AI exposure:** The conversational advisor runs locally / on-premises with deterministic intent and entity extraction. No customer input, transcript, or identifier is ever shared with external LLM providers or cloud APIs.
- **Breach response:** notify the Data Protection Board and affected users as DPDP requires. A grievance officer contact is shown on the consent screen.
