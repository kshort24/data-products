"""Assemble the self-contained dashboard. No external script/style hosts except Google Fonts."""
import json
from pathlib import Path
HERE = Path(__file__).parent; OUT = HERE/'out'; TPL = HERE/'tpl'
pay = json.loads((OUT/'dp_uc43_payload.json').read_text(encoding='utf-8'))
slim = {k: pay[k] for k in ['meta','coverage','anchor','availability_d1','availability_d2','mip',
                            'coverage_rows','holman_mix','holman_wc','holman_count','holman_pitches',
                            'holman_sz','atl_order','opp_games','opp_drift','dq','defects','pitch_colors','max_bf','capacity_modes','revised']}
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Oswald:wght@400;600;700&family=Public+Sans:wght@400;600&'
         'family=IBM+Plex+Mono:wght@400;500&display=swap">')
TITLE = 'Game 2 Bullpen Control Room'
head = (f'<title>{TITLE}</title>{FONTS}<style>\n' + (TPL/'style.css').read_text(encoding='utf-8') + '\n</style>')
body = (TPL/'body.html').read_text(encoding='utf-8')
tail = ('<script id="uc43-data" type="application/json">' + json.dumps(slim, ensure_ascii=False).replace('</', '<\\/') + '</script>'
        '<script>window.__UC43__=JSON.parse(document.getElementById("uc43-data").textContent);</script>'
        '<script>\n' + (TPL/'app.js').read_text(encoding='utf-8') + '\n</script>')
# repo copy: full standalone document
(HERE/'dp_uc43_bullpen_control_room.html').write_text(
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1">' + head + '</head><body>' + body + tail +
    '</body></html>', encoding='utf-8')
# artifact copy: no skeleton — the Artifact tool supplies <!doctype>/<head>/<body>
(HERE/'dp_uc43_artifact.html').write_text(head + body + tail, encoding='utf-8')
for f in ['dp_uc43_bullpen_control_room.html','dp_uc43_artifact.html']:
    print(f'{f}  {(HERE/f).stat().st_size/1024:.0f} KB')
