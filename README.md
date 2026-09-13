# RainGuard AI v2
SIH 2026 prototype with actual Random Forest ML integration.

Run backend:
`python -m pip install -r requirements.txt`
`python -m uvicorn backend.app:app --reload --port 8010`

Run frontend in another terminal:
`python -m http.server 5501 --directory frontend`

Open: http://127.0.0.1:5501/

The prototype uses synthetic data. Rainfall and inundation predictions are produced by separate trained Random Forest models. Real IMD, satellite, radar, NWP, terrain and observed-flood data can replace the demo ingestion layer later.
