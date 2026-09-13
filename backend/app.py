from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime, timezone
import random, joblib

BASE=Path(__file__).resolve().parent.parent
app=FastAPI(title="RainGuard AI",version="2.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
RF=joblib.load(BASE/"models/rainfall_model.joblib")
IF=joblib.load(BASE/"models/inundation_model.joblib")

DISTRICTS=[("Ariyalur",11.1401,79.0786),("Chengalpattu",12.6819,79.9888),("Chennai",13.0827,80.2707),("Coimbatore",11.0168,76.9558),("Cuddalore",11.748,79.7714),("Dharmapuri",12.1211,78.1582),("Dindigul",10.3673,77.9803),("The Nilgiris",11.4102,76.6950),("Erode",11.341,77.7172),("Kallakurichi",11.7401,78.9597),("Kancheepuram",12.8342,79.7036),("Karur",10.9601,78.0766),("Krishnagiri",12.5186,78.2137),("Madurai",9.9252,78.1198),("Mayiladuthurai",11.1035,79.655),("Nagapattinam",10.7672,79.8449),("Kanniyakumari",8.0883,77.5385),("Namakkal",11.2194,78.1677),("Perambalur",11.2333,78.8833),("Pudukkottai",10.3797,78.8208),("Ramanathapuram",9.3639,78.8395),("Ranipet",12.9249,79.3333),("Salem",11.6643,78.146),("Sivaganga",9.8433,78.4809),("Tenkasi",8.959,77.3152),("Thanjavur",10.787,79.1378),("Theni",10.0104,77.4768),("Thoothukudi",8.7642,78.1348),("Tiruchirappalli",10.7905,78.7047),("Tirunelveli",8.7139,77.7567),("Tirupathur",12.4966,78.57),("Tiruppur",11.1085,77.3411),("Tiruvallur",13.1438,79.9082),("Tiruvannamalai",12.2253,79.0747),("Tiruvarur",10.7725,79.6368),("Vellore",12.9165,79.1325),("Viluppuram",11.9401,79.4861),("Virudhunagar",9.5851,77.9624)]

def ts(): return datetime.now(timezone.utc).isoformat()
def weather():
    rng=random.Random(int(datetime.now(timezone.utc).timestamp()//300))
    r1=round(rng.uniform(8,28),1); r3=round(r1+rng.uniform(12,35),1); r6=round(r3+rng.uniform(15,45),1)
    return {"location":"Coimbatore","temperature_c":round(rng.uniform(24,29),1),"humidity_percent":rng.randint(78,95),"rainfall_1h_mm":r1,"rainfall_3h_mm":r3,"rainfall_6h_mm":r6,"wind_speed_kmh":round(rng.uniform(12,28),1),"forecast_next_6h_mm":round(rng.uniform(35,90),1),"source":"Synthetic Demo Data","updated":ts()}
def rain_ai(w):
    x=[[w["rainfall_1h_mm"],w["humidity_percent"],w["temperature_c"],w["wind_speed_kmh"],max(0,w["rainfall_3h_mm"]-w["rainfall_1h_mm"])]]
    return str(RF.predict(x)[0]),round(float(max(RF.predict_proba(x)[0]))*100)
def flood_ai(w):
    x=[[w["rainfall_1h_mm"],w["rainfall_3h_mm"],w["rainfall_6h_mm"],w["humidity_percent"],w["temperature_c"],w["wind_speed_kmh"],18.0,.42]]
    return str(IF.predict(x)[0]),round(float(max(IF.predict_proba(x)[0]))*100)

@app.get("/")
def home(): return {"project":"RainGuard AI","status":"ONLINE","ai_ml":"ACTIVE","mode":"DEMO"}
@app.get("/health")
def health(): return {"status":"healthy","ai_engine":"READY","rainfall_model":"Random Forest LOADED","inundation_model":"Random Forest LOADED"}
@app.get("/weather")
def get_weather(): return weather()
@app.get("/predict")
def predict():
    w=weather(); p,c=rain_ai(w)
    return {"location":w["location"],"prediction":p,"confidence":c,"model":"Random Forest","model_status":"ONLINE","rainfall_1h_mm":w["rainfall_1h_mm"],"forecast_next_6h_mm":w["forecast_next_6h_mm"],"source":w["source"],"mode":"DEMO","updated":w["updated"]}
@app.get("/risk")
def risk():
    w=weather(); p,pc=rain_ai(w); f,fc=flood_ai(w)
    warning={"HIGH":"HIGH ALERT: Heavy rainfall and inundation risk detected. Review vulnerable zones immediately.","MODERATE":"MODERATE WATCH: Rainfall may cause localized waterlogging. Continue close monitoring.","LOW":"LOW RISK: No immediate inundation signal in the prototype assessment."}[f]
    return {"location":w["location"],"rainfall_prediction":p,"rainfall_confidence":pc,"inundation_risk":f,"inundation_confidence":fc,"risk_score":{"LOW":30,"MODERATE":65,"HIGH":90}[f],"next_6_hours_rainfall_mm":w["forecast_next_6h_mm"],"maximum_hourly_rainfall_mm":w["rainfall_1h_mm"],"warning":warning,"models":"Rainfall RF + Inundation RF","source":w["source"],"mode":"DEMO","status":"AI READY","updated":w["updated"]}
@app.get("/districts")
def districts():
    fixed={"Chennai":"HIGH","Cuddalore":"HIGH","Nagapattinam":"HIGH","Mayiladuthurai":"HIGH","Tiruvarur":"MODERATE","Thanjavur":"MODERATE","Coimbatore":"MODERATE","Tiruppur":"MODERATE","Madurai":"MODERATE","Tiruchirappalli":"MODERATE"}
    out=[]
    for i,(n,lat,lon) in enumerate(DISTRICTS):
        r=fixed.get(n,["LOW","LOW","MODERATE","LOW"][i%4]); q=random.Random(sum(map(ord,n)))
        rain=round({"LOW":q.uniform(4,18),"MODERATE":q.uniform(18,45),"HIGH":q.uniform(45,82)}[r],1)
        out.append({"district":n,"lat":lat,"lon":lon,"risk":r,"rainfall_mm":rain,"confidence":q.randint(82,97),"lead_time_hours":q.choice([2,3,4,6]),"status":"Warning" if r=="HIGH" else ("Watch" if r=="MODERATE" else "Monitoring")})
    return {"count":38,"districts":out,"mode":"DEMO","updated":ts()}
@app.get("/summary")
def summary():
    d = districts()["districts"]

    high = sum(1 for x in d if x["risk"] == "HIGH")
    moderate = sum(1 for x in d if x["risk"] == "MODERATE")
    low = sum(1 for x in d if x["risk"] == "LOW")

    return {
        "districts_monitored": len(d),
        "high_risk": high,
        "moderate_risk": moderate,
        "low_risk": low
    }