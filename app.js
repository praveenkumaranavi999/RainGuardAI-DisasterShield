const API="http://127.0.0.1:8010";
let map,marks=[];
function init()
{
    map=L.map("map").setView([11.127,78.657],7.5);L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {attribution:"&copy; OpenStreetMap"}).addTo(map)}
    async function get(p){let c=new AbortController(),t=setTimeout(()=>c.abort(),1800);
        try{let r=await fetch(API+p,{signal:c.signal,cache:"no-store"});
        if(!r.ok)throw Error(r.status);
        return r.json()}finally{clearTimeout(t)}}function ic(r){let c=r==="HIGH"?"#ff6477":r==="MODERATE"?"#f3c34f":"#35d68a";
        return L.divIcon({className:"",html:`<div style="width:15px;height:15px;border-radius:50%;background:${c};
            border:2px solid #07111c"></div>`,iconSize:[15,15],
        iconAnchor:[7,7]})}async function load(){try{let[w,p,r,d,s]=await Promise
            .all(["/weather","/predict","/risk","/districts","/summary"].map(get));
        r1.textContent=w.rainfall_1h_mm;r6.textContent=w.forecast_next_6h_mm;rr.textContent=p.prediction;
        rc.textContent=`Confidence ${p.confidence}%`;fr.textContent=r.inundation_risk;fc.textContent=`Confidence ${r.inundation_confidence}%`;
        warning.innerHTML=`<b>${r.inundation_risk==="HIGH"?"🚨 HIGH PRIORITY WARNING":
            r.inundation_risk==="MODERATE"?"⚠ MODERATE WATCH":"✓ LOW RISK MONITORING"}</b><p>${r.warning}</p>`;
        dc.textContent=s.districts_monitored;hc.textContent=s.high_risk;mc.textContent=s.moderate_risk;lc.textContent=s.low_risk;
        marks.forEach(x=>x.remove());marks=[];
        d.districts.forEach(x=>{let m=L.marker([x.lat,x.lon],{icon:ic(x.risk)}).addTo(map);
        m.bindPopup(`<b>RainGuard AI</b><br>${x.district}<br>Risk: <b>${x.risk}</b><br>Rainfall: 
        ${x.rainfall_mm} mm<br>Confidence: ${x.confidence}%<br>Lead: ${x.lead_time_hours} h<br><small>Synthetic demo input</small>`);marks.push(m)});
        rows.innerHTML=[...d.districts].sort((a,b)=>({HIGH:0,MODERATE:1,LOW:2}[a.risk]-({HIGH:0,MODERATE:1,LOW:2}[b.risk])))
        .slice(0,15).map(x=>`<tr><td><b>${x.district}</b></td><td class="${x.risk.toLowerCase()}">${x.risk}</td><td>${x.rainfall_mm} 
        mm</td><td>${x.confidence}%</td><td>${x.lead_time_hours} h</td><td>${x.status}</td></tr>`).join("");
        updated.textContent="AI updated "+new Date().toLocaleTimeString()}
        catch(e){warning.innerHTML="<b>Backend offline</b><p>Start FastAPI on port 8010.</p>"}}
        refresh.onclick=async()=>{refresh.textContent="⟳ Refreshing...";await load();refresh.textContent="↻ Refresh Intelligence";};init();load();setInterval(load,30000);