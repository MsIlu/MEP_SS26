from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from appointments.simulator_catalog import PROVIDERS, SPECIALTY_LABELS
from fhir_mapper.hapi_client import HapiFhirClient, HapiFhirError, appointment_resource_to_result


router = APIRouter(prefix="/fhir-simulator", tags=["fhir-simulator"])


@router.get("", response_class=HTMLResponse, include_in_schema=False)
def simulator_dashboard() -> str:
    return _DASHBOARD_HTML


@router.get("/api/providers")
def simulator_providers() -> dict:
    return {
        "synthetic": True,
        "specialties": SPECIALTY_LABELS,
        "providers": [asdict(provider) for provider in PROVIDERS],
    }


@router.get("/api/appointments")
def simulator_appointments() -> dict:
    try:
        resources = HapiFhirClient().list_all_appointments()
    except HapiFhirError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    appointments = []
    for resource in resources:
        item = appointment_resource_to_result(resource)
        item["status"] = resource.get("status", "unknown")
        item["description"] = resource.get("description", "")
        appointments.append(item)
    appointments.sort(key=lambda item: (item["date"], item["time"], item["provider_name"]))
    return {"synthetic": True, "count": len(appointments), "appointments": appointments}


_DASHBOARD_HTML = r"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Careena 116117 FHIR-Simulator</title>
  <style>
    :root { color-scheme: light; --ink:#17343b; --teal:#087f83; --soft:#e9f6f5; --line:#c9dddc; --warn:#9a5b00; }
    * { box-sizing:border-box } body { margin:0; font:15px/1.45 system-ui,sans-serif; color:var(--ink); background:#f4f8f8 }
    header { padding:28px clamp(18px,5vw,64px); color:white; background:linear-gradient(120deg,#075f67,#0a9290) }
    h1 { margin:0 0 6px; font-size:clamp(24px,4vw,38px) } header p { margin:0; max-width:850px }
    main { max-width:1250px; margin:auto; padding:24px } .notice { padding:14px 16px; border:1px solid #efc36c; border-radius:12px; background:#fff8e8; color:#714500 }
    .stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin:18px 0 }
    .stat,.panel { border:1px solid var(--line); border-radius:16px; background:white; box-shadow:0 5px 20px #16434b0b }
    .stat { padding:16px } .stat strong { display:block; font-size:28px; color:var(--teal) }
    .toolbar { display:flex; flex-wrap:wrap; gap:10px; margin:18px 0 }
    input,select,button { min-height:42px; padding:8px 12px; border:1px solid var(--line); border-radius:10px; background:white; color:var(--ink) }
    input { flex:1; min-width:190px } button { cursor:pointer; color:white; border-color:var(--teal); background:var(--teal); font-weight:700 }
    .panel { overflow:hidden; margin:18px 0 } .panel h2 { margin:0; padding:17px 20px; border-bottom:1px solid var(--line); background:var(--soft) }
    .table-wrap { overflow:auto } table { width:100%; border-collapse:collapse } th,td { padding:12px 14px; border-bottom:1px solid #e7eeee; text-align:left; white-space:nowrap }
    th { font-size:12px; text-transform:uppercase; letter-spacing:.04em; color:#4f6d72 }
    .badge { display:inline-block; padding:4px 9px; border-radius:999px; background:#edf3f3; font-weight:700 }
    .booked { color:#075f67; background:#dff4ec }.proposed { color:#1d5c89; background:#e2f1ff}.cancelled { color:#8b3b3b; background:#ffe7e7 }
    .empty,.error { padding:24px; text-align:center }.error { color:#9b2c2c }
    @media(max-width:650px){ main{padding:14px} th,td{padding:10px} }
  </style>
</head>
<body>
  <header><h1>116117 FHIR-Simulator</h1><p>Lokale Entwicklungsoberfläche für synthetische Ärzte und FHIR-Termine. Keine echten Praxen, Verfügbarkeiten oder 116117-Daten.</p></header>
  <main>
    <div class="notice"><strong>Simulationsmodus:</strong> Termine entstehen bei einer Careena-Terminsuche und werden als FHIR-Appointment im lokalen HAPI-Server gespeichert.</div>
    <section class="stats">
      <div class="stat"><strong id="providerCount">–</strong>Testpraxen</div><div class="stat"><strong id="slotCount">–</strong>FHIR-Slots</div>
      <div class="stat"><strong id="freeCount">–</strong>verfügbar</div><div class="stat"><strong id="bookedCount">–</strong>gebucht</div>
    </section>
    <div class="toolbar">
      <input id="query" placeholder="Praxis, Fachrichtung, Adresse oder Datum">
      <select id="status"><option value="">Alle Status</option><option value="proposed">Verfügbar</option><option value="booked">Gebucht</option><option value="cancelled">Storniert</option></select>
      <button id="refresh">Aktualisieren</button>
    </div>
    <section class="panel"><h2>FHIR-Termine in HAPI</h2><div class="table-wrap" id="appointments">Lade…</div></section>
    <section class="panel"><h2>Synthetischer Arztkatalog</h2><div class="table-wrap" id="providers">Lade…</div></section>
  </main>
<script>
let slots=[], providers=[];
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function renderSlots(){const q=document.querySelector('#query').value.toLowerCase(),s=document.querySelector('#status').value;
 const rows=slots.filter(x=>(!s||x.status===s)&&JSON.stringify(x).toLowerCase().includes(q));
 document.querySelector('#appointments').innerHTML=rows.length?`<table><thead><tr><th>Status</th><th>Datum</th><th>Zeit</th><th>Praxis</th><th>Fachrichtung</th><th>Art</th><th>Adresse</th><th>Entfernung</th></tr></thead><tbody>${rows.map(x=>`<tr><td><span class="badge ${esc(x.status)}">${esc(x.status)}</span></td><td>${esc(x.date)}</td><td>${esc(x.time)}</td><td>${esc(x.provider_name)}</td><td>${esc(x.specialty)}</td><td>${esc(x.care_type)}</td><td>${esc(x.address)}</td><td>${esc(x.distance_km)} km</td></tr>`).join('')}</tbody></table>`:'<div class="empty">Keine passenden FHIR-Termine vorhanden.</div>'}
function renderProviders(){document.querySelector('#providers').innerHTML=`<table><thead><tr><th>Praxis</th><th>Fachrichtung</th><th>Ort</th><th>PLZ-Bereiche</th><th>Video</th></tr></thead><tbody>${providers.map(x=>`<tr><td>${esc(x.name)}</td><td>${esc(x.specialty)}</td><td>${esc(x.city)}</td><td>${esc(x.postal_prefixes.join(', '))}</td><td>${x.supports_video?'Ja':'Nein'}</td></tr>`).join('')}</tbody></table>`}
async function load(){try{const [p,a]=await Promise.all([fetch('/fhir-simulator/api/providers'),fetch('/fhir-simulator/api/appointments')]);if(!p.ok||!a.ok)throw new Error('HAPI-FHIR ist nicht erreichbar.');const pd=await p.json(),ad=await a.json();providers=pd.providers;slots=ad.appointments;
 providerCount.textContent=providers.length;slotCount.textContent=slots.length;freeCount.textContent=slots.filter(x=>x.status==='proposed').length;bookedCount.textContent=slots.filter(x=>x.status==='booked').length;renderProviders();renderSlots();}
 catch(e){document.querySelector('#appointments').innerHTML=`<div class="error">${esc(e.message)}</div>`}}
document.querySelector('#query').addEventListener('input',renderSlots);document.querySelector('#status').addEventListener('change',renderSlots);document.querySelector('#refresh').addEventListener('click',load);load();
</script></body></html>"""
