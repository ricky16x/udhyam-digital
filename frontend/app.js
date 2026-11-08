// Udyam Digital - customer journey (vanilla JS, no build step)
const S = { lang: localStorage.getItem("lang") || "en", step: "welcome", sid: null, chat: [], chips: [], rec: null,
  quote: null, selected: null, contract: 12, kyc: {}, kycResult: null, slot: null, order: null, listening: false };
const $ = (q) => document.querySelector(q);
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const md = (s) => esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>");
const inr = (n) => "₹" + Number(n || 0).toLocaleString("en-IN");
const L = (en, hi) => (S.lang === "hi" ? hi : en);

async function api(path, body, method) {
  const r = await fetch(path, { method: method || (body ? "POST" : "GET"), headers: body instanceof FormData ? {} : { "Content-Type": "application/json" },
    body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(j.detail || "Something went wrong");
  return j;
}
api("/api/kyc/applicants").then((r) => { if (r && r.applicants) S.applicants = r.applicants; }).catch(() => {});

const STEPS = [["advisor", "Advisor", "सलाह"], ["quote", "Quote", "कोटेशन"], ["kyc", "KYC", "KYC"], ["pay", "Pay", "भुगतान"], ["track", "Track", "ट्रैक"]];
function renderSteps() {
  const i = STEPS.findIndex((s) => s[0] === S.step);
  $("#steps").style.display = S.step === "welcome" ? "none" : "flex";
  $("#steps").innerHTML = STEPS.map((s, k) => {
    const isClickable = k <= i || (s[0] === "quote" && S.quote) || (s[0] === "advisor" && S.sid);
    const cls = k === i ? "on" : k < i ? "done" : "";
    return `<div class="${cls}" ${isClickable ? `onclick="go('${s[0]}')"` : ""} style="${isClickable ? "cursor:pointer" : ""}">${L(s[1], s[2])}</div>`;
  }).join("");
  $("#langBtn").textContent = S.lang === "en" ? "हिं" : "EN";
}
function go(step) { S.step = step; render(); window.scrollTo(0, 0); }
function toggleLang() { S.lang = S.lang === "en" ? "hi" : "en"; localStorage.setItem("lang", S.lang); render(); }
function render() { renderSteps(); ({ welcome, advisor, quote, kyc, pay, track })[S.step](); }

// ---------------------------------------------------------------- welcome
function welcome() {
  $("#view").innerHTML = `
  <div class="hero">
    <span class="pill">${L("For shops, clinics, offices & factories", "दुकान, क्लिनिक, ऑफिस और फ़ैक्टरी के लिए")}</span>
    <h1>${L("Internet, business SIMs and digital tools – sorted in one sitting", "इंटरनेट, बिज़नेस सिम और डिजिटल टूल – एक बार में तय")}</h1>
    <p class="mut">${L("Answer 6 quick questions. Get one clear monthly price, upload documents from your phone, and track installation – no visits, no calls.", "6 छोटे सवाल। एक साफ़ मासिक कीमत, फ़ोन से डॉक्यूमेंट अपलोड, और इंस्टॉलेशन ट्रैक – न विज़िट, न कॉल।")}</p>
  </div>
  <div class="grid3"><div><b>3 min</b>${L("to a quote", "में कोटेशन")}</div><div><b>5 min</b>${L("KYC on phone", "फ़ोन पर KYC")}</div><div><b>1 bill</b>${L("one support no.", "एक सपोर्ट नंबर")}</div></div>
  <div class="card"><p><b>${L("Choose your language", "अपनी भाषा चुनें")}</b></p>
    <div class="chips" style="margin-top:10px">
      <button class="chip ${S.lang === "en" ? "sel" : ""}" onclick="S.lang='en';render()">English</button>
      <button class="chip ${S.lang === "hi" ? "sel" : ""}" onclick="S.lang='hi';render()">हिंदी</button>
      <button class="chip" disabled title="Coming next">मराठी · தமிழ் · ಕನ್ನಡ · ગુજરાતી ${L("(next)", "(जल्द)")}</button>
    </div></div>
  <button class="btn" id="startBtn" onclick="startAdvisor()">${L("Start – find my bundle", "शुरू करें – मेरा बंडल खोजें")}</button>
  <button class="btn sec" onclick="trackPrompt()">${L("Track an existing order", "मौजूदा ऑर्डर ट्रैक करें")}</button>
  <p class="mut" style="text-align:center">${L("Prefer WhatsApp? Message 'Hi' to +91 90000 00000 – same advisor.", "WhatsApp पसंद है? +91 90000 00000 पर 'Hi' भेजें – वही सलाहकार।")}</p>`;
}
async function startAdvisor() {
  $("#startBtn").innerHTML = '<span class="spinner"></span>';
  const r = await api("/api/advisor/start", { lang: S.lang });
  S.sid = r.session_id; S.chat = [{ who: "bot", text: r.reply }]; S.chips = r.chips; go("advisor");
}
async function trackPrompt() {
  const id = prompt(L("Order ID (e.g. UD2611ABCDE)", "ऑर्डर ID"));
  if (!id) return;
  try { S.order = await api("/api/order/" + id.trim()); go("track"); } catch (e) { alert(e.message); }
}

// ---------------------------------------------------------------- advisor
function advisor() {
  const multi = S.chips.some((c) => c.multi);
  $("#view").innerHTML = `
  <div class="chat" id="chat">${S.chat.map((m) => `<div class="msg ${m.who}">${md(m.text)}</div>`).join("")}</div>
  <div class="chips" id="chips">${S.chips.map((c) => `<button class="chip ${c.selected ? "sel" : ""} ${c.primary ? "pri" : ""}" data-id="${esc(c.id)}">${esc(c.label)}</button>`).join("")}</div>
  <div class="input"><input id="txt" placeholder="${L("Type or speak your answer…", "लिखें या बोलें…")}" onkeydown="if(event.key==='Enter')sendText()">
    <button class="icon ${S.listening ? "rec" : ""}" title="Voice" onclick="voice()">🎤</button><button class="icon" onclick="sendText()">➤</button></div>`;
  document.querySelectorAll("#chips .chip").forEach((b) => b.onclick = () => {
    const c = S.chips.find((x) => x.id === b.dataset.id);
    if (!c) return;
    if (c.multi) { c.selected = !c.selected; b.classList.toggle("sel"); return; }
    if (c.id === "home") return go("welcome");
    if (c.id === "restart") return startAdvisor();
    if (c.id === "quote") return openQuote();
    if (c.id === "done" && multi) return send({ choice: "done", selected: S.chips.filter((x) => x.multi && x.selected).map((x) => x.id) }, L("Done", "हो गया"));
    send({ choice: c.id }, c.label);
  });
  window.scrollTo(0, document.body.scrollHeight);
}
function sendText() { const v = $("#txt").value.trim(); if (v) send({ text: v }, v); }
async function send(payload, label) {
  S.chat.push({ who: "me", text: label }); S.chips = []; advisor();
  S.chat.push({ who: "bot", text: "…" }); advisor();
  try {
    const r = await api("/api/advisor/message", { session_id: S.sid, ...payload });
    S.chat[S.chat.length - 1] = { who: "bot", text: r.reply }; S.chips = r.chips || [];
    if (r.recommendation) S.rec = r.recommendation;
    if (r.action === "home") setTimeout(() => go("welcome"), 800);
  } catch (e) { S.chat[S.chat.length - 1] = { who: "bot", text: e.message }; }
  advisor();
}
function voice() {  // Web Speech API: en-IN / hi-IN speech to text
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return alert(L("Voice input needs Chrome on Android/desktop.", "वॉइस के लिए Chrome चाहिए।"));
  const r = new SR(); r.lang = S.lang === "hi" ? "hi-IN" : "en-IN"; r.interimResults = false;
  S.listening = true; advisor();
  r.onresult = (e) => { const t = e.results[0][0].transcript; S.listening = false; send({ text: t }, t); };
  r.onend = () => { S.listening = false; advisor(); }; r.start();
}

// ---------------------------------------------------------------- quote
async function openQuote(sel) {
  S.selected = sel || S.selected;
  S.quote = await api("/api/quote", { session_id: S.sid, selected: S.selected, contract_months: S.contract });
  S.selected = S.quote.items.filter((i) => i.on).map((i) => i.product_id);
  go("quote");
}
function quote() {
  const q = S.quote, rec = S.rec;
  const items = q.items.map((i) => `
    <div class="item ${i.on ? "" : "off"}">
      <label class="tog"><input type="checkbox" ${i.on ? "checked" : ""} data-p="${i.product_id}"><span></span></label>
      <div><div class="nm">${esc(i.name)} <span class="mut">×${i.qty}</span></div><div class="why">${esc(i.why)}</div>
        ${i.optional ? `<div class="why" style="color:var(--red-d)">${L("Optional add-on", "वैकल्पिक ऐड-ऑन")}</div>` : ""}</div>
      <div class="pr">${inr(i.monthly)}<div class="mut" style="font-weight:400">${inr(i.unit_price)}/${esc(i.unit.replace("per ", ""))}</div></div>
    </div>`).join("");
  $("#view").innerHTML = `
  <div class="total">
    <div class="mut">${L("Your monthly price", "आपकी मासिक कीमत")}</div>
    <div class="big">${inr(q.monthly_total)}<small> /${L("month", "महीना")} + GST</small></div>
    <div class="mut">${inr(q.monthly_with_gst)} ${L("incl. 18% GST", "18% GST सहित")} · ${L("one-time setup", "एक-बार सेटअप")} ${inr(q.one_time_setup)}
      ${q.setup_waived ? ` (${inr(q.setup_waived)} ${L("waived", "माफ़")})` : ""}${q.one_time_setup > 0 ? ` · ${L("or", "या")} ${inr(q.setup_emi_12m)}/mo ×12` : ""}</div>
    ${q.savings_vs_standalone ? `<p class="ok" style="margin-top:6px;font-weight:600">${L("You save", "बचत")} ${inr(q.savings_vs_standalone)}/${L("month vs buying separately", "महीना, अलग-अलग खरीदने की तुलना में")}</p>` : ""}
    <p class="mut" style="margin-top:6px">${L("Installed in about", "इंस्टॉलेशन लगभग")} ${q.install_days} ${L("days", "दिन में")}</p>
  </div>
  <div class="seg"><button class="${S.contract === 12 ? "on" : ""}" onclick="S.contract=12;openQuote()">12 ${L("months", "महीने")}</button>
    <button class="${S.contract === 24 ? "on" : ""}" onclick="S.contract=24;openQuote()">24 ${L("months – lowest price", "महीने – सबसे कम कीमत")}</button></div>
  ${(q.warnings || []).map((w) => `<div class="note">${esc(w)}</div>`).join("")}
  ${(rec.notes || []).map((n) => `<div class="note">ℹ️ ${esc(n)}</div>`).join("")}
  <div class="card">${items}</div>
  ${rec.excluded.length ? `<details class="card"><summary class="mut">${L("Not included and why", "शामिल नहीं – क्यों")} (${rec.excluded.length})</summary>${rec.excluded.map((e) => `<p class="mut" style="margin-top:6px">• ${esc(e.reason)}</p>`).join("")}</details>` : ""}
  <p class="mut">${esc(q.price_rule)}</p>
  <button class="btn" onclick="go('kyc')" ${q.monthly_total > 0 ? "" : "disabled"}>${L("Looks good – continue", "ठीक है – आगे बढ़ें")}</button>
  ${q.monthly_total === 0 ? `<p class="mut" style="color:var(--red);text-align:center">${L("Please select at least one product", "कृपया कम से कम एक प्रोडक्ट चुनें")}</p>` : ""}
  <button class="btn sec" onclick="shareQuote()">${L("Share quote on WhatsApp", "WhatsApp पर कोटेशन भेजें")}</button>
  <button class="btn sec" onclick="go('advisor')">${L("Back to advisor", "सलाहकार पर वापस")}</button>
  <button class="btn sec" onclick="go('welcome')">${L("Back to Home 🏠", "होम पेज पर वापस 🏠")}</button>`;
  document.querySelectorAll(".tog input").forEach((t) => t.onchange = () => {
    const sel = new Set(S.selected); t.checked ? sel.add(t.dataset.p) : sel.delete(t.dataset.p); openQuote([...sel]);
  });
}
function shareQuote() {
  const q = S.quote, on = q.items.filter((i) => i.on).map((i) => `${i.name} x${i.qty}`).join(", ");
  window.open("https://wa.me/?text=" + encodeURIComponent(`Accel Business quote: ${inr(q.monthly_total)}/month + GST (${q.contract_months} months). ${on}`), "_blank");
}

// ---------------------------------------------------------------- KYC
const DOCS = [["gst_certificate", "GST certificate", "GST प्रमाणपत्र"], ["udyam_certificate", "Udyam certificate", "उद्यम प्रमाणपत्र"],
  ["signatory_id", "Signatory ID", "हस्ताक्षरकर्ता ID"], ["address_proof", "Address proof (bill < 90 days)", "पते का प्रमाण (90 दिन से नया बिल)"]];
function kyc() {
  if (!S.consent) return consentScreen();
  const lvl = { pass: ["✓", "ok"], warn: ["!", "warn"], fail: ["✕", "bad"] };
  const applList = S.applicants || Array.from({ length: 12 }, (_, i) => `K${String(i + 1).padStart(2, "0")}`);
  $("#view").innerHTML = `
  <h2>${L("Upload documents", "डॉक्यूमेंट अपलोड करें")}</h2>
  <p class="mut">${L("Take a photo or pick a file. We read it instantly, check it with GST and Udyam registries, and delete the image right after.", "फ़ोटो लें या फ़ाइल चुनें। हम तुरंत पढ़कर GST/उद्यम रजिस्ट्री से जाँचते हैं और फ़ोटो तुरंत हटा देते हैं।")}</p>
  <button class="btn sec" onclick="digilocker()">🔐 ${L("Fetch from DigiLocker instead", "DigiLocker से लाएँ")}</button>
  <div class="card"><div class="row sp"><b>${L("Demo: load a case applicant", "डेमो: केस आवेदक चुनें")}</b></div>
    <div class="row" style="margin-top:8px"><select id="appl">${applList.map(a => `<option>${a}</option>`).join("")}</select>
    <button class="btn sm" id="sampleBtn" onclick="loadSample()">${L("Load", "लोड")}</button></div></div>
  ${DOCS.map(([k, en, hi]) => { const d = S.kyc[k]; return `
    <div class="card"><div class="doc"><b>${L(en, hi)}</b><span class="st ${d ? "badge-ok" : ""}">${d ? L("Read", "पढ़ लिया") : L("Pending", "बाकी")}</span></div>
      ${d ? `<div class="kv" style="margin-top:8px">${Object.entries(d.fields).filter(([, v]) => v !== null && v !== false && v !== true).map(([a, v]) => `<b>${esc(a.replace(/_/g, " "))}</b><span>${esc(v)}</span>`).join("")}</div>
        ${(d.quality_notes || []).map((n) => `<p class="mut" style="margin-top:6px">⚙️ ${esc(n)}</p>`).join("")}` : ""}
      <input class="file" style="margin-top:8px" type="file" accept="image/*" capture="environment" onchange="upload('${k}', this.files[0])"></div>`; }).join("")}
  ${S.kycResult ? `<div class="card"><div class="row sp"><b>${L("Verification", "सत्यापन")}</b>
      <span class="st ${S.kycResult.status === "verified" ? "badge-ok" : S.kycResult.status === "review" ? "badge-warn" : "badge-bad"}" style="padding:4px 10px;border-radius:10px;font-size:12px;font-weight:700">
      ${{ verified: L("Verified", "सत्यापित"), review: L("Quick review", "जल्द समीक्षा"), rejected_fixable: L("Needs a fix", "सुधार चाहिए") }[S.kycResult.status]}</span></div>
      ${S.kycResult.checks.map((c) => `<div class="check"><i class="${lvl[c.level][1] === "ok" ? "ok" : ""}" style="color:var(--${lvl[c.level][1] === "ok" ? "ok" : lvl[c.level][1]})">${lvl[c.level][0]}</i><span>${esc(c.message)}</span></div>`).join("")}</div>` : ""}
  <button class="btn" onclick="verify()" ${Object.keys(S.kyc).length ? "" : "disabled"}>${L("Verify documents", "डॉक्यूमेंट जाँचें")}</button>
  ${S.kycResult && S.kycResult.status !== "rejected_fixable" ? `<button class="btn" onclick="go('pay')">${L("Continue to schedule & pay", "शेड्यूल और भुगतान")}</button>` : ""}
  <button class="btn sec" onclick="go('quote')">${L("Back to Quote", "कोटेशन पर वापस")}</button>
  <button class="btn sec" onclick="withdraw()">${L("Withdraw consent & delete my data", "सहमति वापस लें और डेटा हटाएँ")}</button>
  <button class="btn sec" onclick="go('welcome')">${L("Back to Home 🏠", "होम पेज पर वापस 🏠")}</button>`;
}
function consentScreen() {
  $("#view").innerHTML = `
  <div class="card consent"><h2>${L("Before we collect documents", "डॉक्यूमेंट लेने से पहले")}</h2>
  <ul>
    <li><b>${L("What", "क्या")}:</b> ${L("GST certificate, Udyam certificate, signatory ID and one address proof. Nothing else – no Aadhaar number, no bank details.", "GST, उद्यम, हस्ताक्षरकर्ता ID और एक पते का प्रमाण। इसके अलावा कुछ नहीं – न आधार नंबर, न बैंक विवरण।")}</li>
    <li><b>${L("Why", "क्यों")}:</b> ${L("Only to verify your business and activate the services you chose (legal requirement for business connections).", "केवल आपका बिज़नेस सत्यापित करने और चुनी सेवाएँ चालू करने के लिए (कनेक्शन के लिए कानूनी ज़रूरत)।")}</li>
    <li><b>${L("How long", "कब तक")}:</b> ${L("Photos are deleted right after we read them. Extracted details are kept for 30 days after activation (or as telecom licence rules require), then deleted.", "फ़ोटो पढ़ते ही हटा दी जाती हैं। जानकारी चालू होने के 30 दिन बाद (या लाइसेंस नियम अनुसार) हटा दी जाती है।")}</li>
    <li><b>${L("Your rights", "आपके अधिकार")}:</b> ${L("See, correct or erase your data and withdraw consent anytime from this screen or by WhatsApp. Grievance officer: privacy@accel.example.", "अपना डेटा देखें, सुधारें या हटाएँ, और कभी भी सहमति वापस लें। शिकायत अधिकारी: privacy@accel.example")}</li>
  </ul>
  <label><input type="checkbox" id="c1" checked disabled> ${L("Verify my business documents (required)", "मेरे बिज़नेस डॉक्यूमेंट की जाँच (ज़रूरी)")}</label>
  <label><input type="checkbox" id="c2" checked disabled> ${L("Use them to activate my order (required)", "ऑर्डर चालू करने में उपयोग (ज़रूरी)")}</label>
  <label><input type="checkbox" id="c3"> ${L("Send me offers on WhatsApp (optional – you can say no)", "WhatsApp पर ऑफ़र भेजें (वैकल्पिक)")}</label>
  </div>
  <button class="btn" onclick="giveConsent()">${L("I agree – continue", "मैं सहमत हूँ – आगे बढ़ें")}</button>
  <button class="btn sec" onclick="go('quote')">${L("Back to Quote", "कोटेशन पर वापस")}</button>
  <button class="btn sec" onclick="go('welcome')">${L("Back to Home 🏠", "होम पेज पर वापस 🏠")}</button>`;
}
async function giveConsent() {
  const p = ["kyc_verification", "service_activation"]; if ($("#c3").checked) p.push("marketing_whatsapp");
  S.consent = await api("/api/kyc/consent", { session_id: S.sid, purposes: p, lang: S.lang }); kyc();
}
async function upload(doc, file) {
  if (!file) return; const f = new FormData(); f.append("session_id", S.sid); f.append("doc_type", doc); f.append("file", file);
  try { S.kyc[doc] = await api("/api/kyc/upload", f); S.kycResult = null; kyc(); } catch (e) { alert(e.message); }
}
async function loadSample() {
  $("#sampleBtn").innerHTML = '<span class="spinner"></span>';
  const r = await api("/api/kyc/sample", { session_id: S.sid, applicant: $("#appl").value });
  S.kyc = r; S.kycResult = null; kyc();
}
async function digilocker() {
  if (!confirm(L("Fetch official Udyam & GST certificates directly from DigiLocker (MeitY)? No photo upload needed.", "क्या आप DigiLocker से सीधे Udyam और GST प्रमाणपत्र लाना चाहते हैं? फ़ोटो की ज़रूरत नहीं।"))) return;
  try {
    const r = await api("/api/kyc/digilocker", { session_id: S.sid });
    S.kyc = r;
    S.kycResult = null;
    kyc();
    await verify();
  } catch (e) {
    alert(e.message);
  }
}
async function verify() { S.kycResult = await api("/api/kyc/validate", { session_id: S.sid }); kyc(); }
async function withdraw() { await api("/api/kyc/consent/" + S.sid, null, "DELETE"); S.consent = null; S.kyc = {}; S.kycResult = null; alert(L("Done – your KYC data is deleted.", "हो गया – आपका KYC डेटा हटा दिया गया।")); go("quote"); }

// ---------------------------------------------------------------- pay
function pay() {
  const base = new Date("2026-07-15"); const days = [1, 2, 3].map((d) => { const x = new Date(base); x.setDate(x.getDate() + d); return x.toISOString().slice(0, 10); });
  const slots = days.flatMap((d) => [`${d} 10:00-13:00`, `${d} 14:00-18:00`]);
  $("#view").innerHTML = `
  <h2>${L("Pick an installation slot", "इंस्टॉलेशन का समय चुनें")}</h2>
  <div class="slots">${slots.map((s) => `<div class="slot ${S.slot === s ? "sel" : ""}" onclick="S.slot='${s}';pay()">${s.replace(" ", "<br>")}</div>`).join("")}</div>
  <div class="card"><div class="row sp"><b>${L("Monthly (UPI Autopay)", "मासिक (UPI ऑटोपे)")}</b><b>${inr(S.quote.monthly_with_gst)}</b></div>
    <div class="row sp mut" style="margin-top:6px"><span>${L("Setup today", "आज सेटअप")}</span><span>${inr(S.quote.one_time_setup)}</span></div>
    <p class="mut" style="margin-top:8px">${L("First bill starts only after activation. Signatory e-signs with Aadhaar OTP – they don't need to be present.", "पहला बिल चालू होने के बाद ही। हस्ताक्षरकर्ता आधार OTP से ई-साइन करें – मौजूद होना ज़रूरी नहीं।")}</p></div>
  <button class="btn" ${S.slot ? "" : "disabled"} onclick="placeOrder()" id="payBtn">${L("e-Sign & set up UPI Autopay", "ई-साइन और UPI ऑटोपे सेट करें")}</button>
  <button class="btn sec" onclick="go('kyc')">${L("Back to KYC", "KYC पर वापस")}</button>
  <button class="btn sec" onclick="go('welcome')">${L("Back to Home 🏠", "होम पेज पर वापस 🏠")}</button>`;
}
async function placeOrder() {
  $("#payBtn").innerHTML = '<span class="spinner"></span>';
  try { S.order = await api("/api/order", { session_id: S.sid, install_slot: S.slot }); go("track"); } catch (e) { alert(e.message); pay(); }
}

// ---------------------------------------------------------------- tracker
function track() {
  const o = S.order;
  $("#view").innerHTML = `
  <div class="total"><div class="mut">${L("Order", "ऑर्डर")} ${esc(o.order_id)}</div>
    <h2>${L("Expected live by", "चालू होने की तारीख")} ${o.stages[o.stages.length - 1].eta}</h2>
    <p class="mut">${o.items.map((i) => `${esc(i.name)} ×${i.qty}`).join(" · ")}</p></div>
  <div class="card tl">${o.stages.map((s) => `<div class="st ${s.done ? "done" : s.current ? "cur" : ""}"><b>${L(s.label, s.label_hi)}</b><div class="mut">${s.done ? "✓ " : L("by ", "")}${s.eta}</div></div>`).join("")}</div>
  ${o.engineer ? `<div class="card"><b>👷 ${esc(o.engineer.name)}</b><p class="mut">${esc(o.engineer.phone)} · ${esc(o.engineer.arrival)}</p></div>` : ""}
  <div class="card"><b>${L("Updates sent to WhatsApp", "WhatsApp पर भेजे गए अपडेट")}</b>${o.updates.map((u) => `<p class="mut" style="margin-top:6px">💬 ${esc(u.replace("WhatsApp: ", ""))}</p>`).join("")}</div>
  <p class="mut">${L("You'll get a WhatsApp message at every step – no need to call support.", "हर कदम पर WhatsApp संदेश मिलेगा – सपोर्ट को कॉल करने की ज़रूरत नहीं।")}</p>
  <button class="btn sec" onclick="advanceOrder()">${L("Demo: simulate next field update", "डेमो: अगला अपडेट")}</button>
  <button class="btn sec" onclick="go('welcome')">${L("Back to Home 🏠", "होम पेज पर वापस 🏠")}</button>`;
}
async function advanceOrder() { S.order = await api(`/api/order/${S.order.order_id}/advance`, {}); track(); }

render();
