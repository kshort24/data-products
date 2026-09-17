"""Self-contained interactive command dashboard for UC #45. No external code, no CDN (house rule).
Every value is either computed in the browser from the embedded pitch log receipt or read from payload receipts."""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent; OUT = HERE / 'out'; TPL = HERE / 'tpl'
DEST = HERE / 'dp_uc45_command_dashboard.html'
pay = json.loads((OUT / 'dp_uc45_payload.json').read_text())
blob = json.dumps(pay, separators=(',', ':')).replace('</', '<\\/')
html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sánchez Command Dashboard · uc-pps-031</title>
<style>{(TPL / 'style.css').read_text()}</style></head><body>
{(TPL / 'body.html').read_text()}
<script>window.__UC45__ = {blob};</script>
<script>{(TPL / 'app.js').read_text()}</script>
</body></html>"""
DEST.write_text(html, encoding='utf-8')
print(f'dashboard -> {DEST.name}  ({DEST.stat().st_size / 1024:.0f} KB)')
