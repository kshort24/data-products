"""Self-contained interactive scouting card. No external code, no CDN — house rule."""
import json
from pathlib import Path
import pandas as pd, numpy as np
import dp_uc44_kernel as K

HERE = Path(__file__).parent; OUT = HERE/'out'; TPL = HERE/'tpl'
DEST = HERE/'dp_uc44_painter_scouting_card.html'
pay = json.loads((OUT/'dp_uc44_payload.json').read_text())

loc = pd.read_csv(OUT/'dp_uc44_pitch_locations_post.csv')
ap = K.load_phils((2026,), role='pitching'); ap = ap[ap.pitcher == K.SUBJECT_ID].copy()
ap['window'] = np.where(ap.game_date >= K.OPTION_RETURN_DATE, 'Post-Option', 'Pre-Option')
L = []
for w in ['Pre-Option','Post-Option']:
    d = ap[ap.window==w].dropna(subset=['plate_x','plate_z'])
    L.append(d[['window','stand','pitch_type','plate_x','plate_z']])
full = ap.dropna(subset=['plate_x','plate_z']).copy(); full['window']='Full 2026'
L.append(full[['window','stand','pitch_type','plate_x','plate_z']])
locs = pd.concat(L, ignore_index=True).round(3)

post = ap[ap.window=='Post-Option']
DATA = dict(
    pitch_colors={r.pitch_type: K.PITCH_COLORS.get(r.pitch_name, '#999')
                  for r in ap.drop_duplicates('pitch_type').itertuples()},
    pitch_order=['FF','SI','FC','SL','ST','CU','CH','FS'],
    zone=dict(top=round(float(post.sz_top.mean()),3), bot=round(float(post.sz_bot.mean()),3)),
    locations=locs.to_dict('records'),
    grades=pay['grades'],
    grades_pre=pd.read_csv(OUT/'dp_uc44_grades_pre_option.csv').replace({np.nan:None}).to_dict('records'),
    mix_by_stand=pay['mix_by_stand'],
    platoon=pay['platoon'],
    start_log=pay['start_log'],
    atl_lineup=pay['atl_lineup'],
    h2h=pd.read_csv(OUT/'dp_uc44_h2h_atl.csv').replace({np.nan:None}).to_dict('records'),
    reconciliation=pay['reconciliation'],
    dq=pay['dq'],
    arsenal=pay['arsenal_grade'],
)
# 'Full 2026' rows for platoon/mix are already present in the receipts under that label
blob = json.dumps(DATA, separators=(',',':'), default=str)
html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Andrew Painter — Scouting Card · uc-pps-030</title>
<style>{(TPL/'style.css').read_text()}</style></head><body>
{(TPL/'body.html').read_text()}
<script>window.__UC44__ = {blob};</script>
<script>
(function(){{
  const a = window.__UC44__.arsenal;
  const el = document.getElementById('arsGrade');
  el.textContent = 'ARSENAL ' + a.value.toFixed(0);
  el.style.color = a.value>=60?'#1a7f37':a.value>=55?'#5FA052':a.value>=45?'#8A8A8A':a.value>=40?'#D08C2E':'#E81828';
  document.getElementById('arsLab').textContent =
    '20-80 scale · post-option window · covers ' + Math.round(a.covered_usage*100) + '% of usage';
}})();
</script>
<script>{(TPL/'app.js').read_text()}</script>
</body></html>"""
DEST.write_text(html, encoding='utf-8')
print(f'dashboard -> {DEST.name}  ({DEST.stat().st_size/1024:.0f} KB)')
