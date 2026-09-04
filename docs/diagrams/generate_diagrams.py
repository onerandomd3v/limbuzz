"""Generate lightweight SVG and Draw.io exports for the LIMBUZZ V1 diagrams."""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent
W, H = 1280, 760

COLORS = {
    "ink": "#263238", "muted": "#607d8b", "line": "#90a4ae",
    "blue": "#d9efff", "blue_line": "#1976d2", "orange": "#fff0d6",
    "orange_line": "#ef8b22", "green": "#def5e7", "green_line": "#2e8b57",
    "red": "#ffe1e1", "red_line": "#c62828", "paper": "#fbfdff",
}

def svg_start(title, subtitle=""):
    return [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(title)}">''',
            f'<rect width="{W}" height="{H}" fill="{COLORS["paper"]}"/>',
            f'<text x="56" y="62" font-family="Inter,Arial,sans-serif" font-size="30" font-weight="700" fill="{COLORS["ink"]}">{escape(title)}</text>',
            f'<text x="56" y="92" font-family="Inter,Arial,sans-serif" font-size="15" fill="{COLORS["muted"]}">{escape(subtitle)}</text>']

def defs(a):
    a.append(f'''<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{COLORS["line"]}"/></marker></defs>''')

def box(a, x, y, w, h, label, fill="blue", stroke=None, sub=None, radius=14):
    stroke = stroke or COLORS[fill + "_line"]
    a += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{COLORS[fill]}" stroke="{stroke}" stroke-width="2"/>',
          f'<text x="{x+w/2}" y="{y+h/2-5}" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="18" font-weight="600" fill="{COLORS["ink"]}">{escape(label)}</text>']
    if sub:
        a.append(f'<text x="{x+w/2}" y="{y+h/2+20}" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="13" fill="{COLORS["muted"]}">{escape(sub)}</text>')

def line(a, x1, y1, x2, y2, label=None, dashed=False):
    dash = ' stroke-dasharray="7 6"' if dashed else ''
    a.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{COLORS["line"]}" stroke-width="2" marker-end="url(#arrow)"{dash}/>')
    if label:
        a.append(f'<text x="{(x1+x2)/2}" y="{(y1+y2)/2-8}" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="13" fill="{COLORS["muted"]}">{escape(label)}</text>')

def finish(a):
    a.append('</svg>')
    return '\n'.join(a)

def context():
    a = svg_start('LIMBUZZ V1 — System Context', 'Offline-first Android safety app · device-side emergency transport')
    defs(a)
    box(a, 60, 300, 150, 70, 'User', 'orange')
    box(a, 1080, 210, 150, 70, 'Contacts', 'green')
    box(a, 1080, 470, 150, 70, 'Map provider', 'green', sub='recipient opens link')
    box(a, 430, 150, 250, 105, 'LIMBUZZ Flutter app', 'blue', sub='screens · orchestration · SOS state')
    box(a, 430, 350, 250, 105, 'Native Android adapters', 'blue', sub='SMS · call · location · audio')
    box(a, 430, 550, 250, 105, 'Local persistence', 'green', sub='contacts · sessions · recordings')
    box(a, 800, 150, 180, 80, 'Foreground service', 'orange', sub='survives background limits')
    box(a, 800, 350, 180, 80, 'Cellular network', 'red', sub='SMS + voice')
    box(a, 800, 550, 180, 80, 'Firebase Auth', 'orange', sub='optional only', stroke=COLORS['orange_line'])
    line(a, 210, 335, 430, 205)
    line(a, 555, 255, 555, 350)
    line(a, 555, 455, 555, 550)
    line(a, 680, 400, 800, 390, 'SMS / call')
    line(a, 890, 230, 890, 350, 'emergency transport')
    line(a, 980, 390, 1080, 245)
    line(a, 1155, 280, 1155, 470, 'location URL')
    line(a, 680, 205, 800, 190, 'active session')
    line(a, 680, 205, 800, 590, 'optional sign-in', dashed=True)
    return finish(a)

def sequence():
    a = svg_start('LIMBUZZ V1 — SOS Emergency Sequence', 'SMS dispatch is independent of location timing and internet connectivity')
    defs(a)
    lanes = [('User', 120), ('Flutter UI', 350), ('Foreground service', 590), ('Native SMS / call', 840), ('Contacts', 1100)]
    for name, x in lanes:
        a.append(f'<text x="{x}" y="145" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="16" font-weight="600" fill="{COLORS["ink"]}">{escape(name)}</text>')
        a.append(f'<path d="M{x} 165 L{x} 690" stroke="{COLORS["line"]}" stroke-width="1.5" stroke-dasharray="5 7"/>')
    events = [(195,120,350,'hold SOS 3s'),(255,350,590,'start session'),(315,590,840,'send SMS to all'),(375,840,1100,'deliver emergency SMS'),(435,590,350,'show per-contact status'),(495,590,840,'call primary contact'),(555,840,1100,'deliver voice call'),(615,120,350,'cancel'),(655,350,590,'stop + all-clear')]
    for y,x1,x2,label in events:
        line(a,x1,y,x2,y,label)
    a.append(f'<rect x="700" y="205" width="280" height="74" rx="12" fill="{COLORS["green"]}" stroke="{COLORS["green_line"]}" stroke-width="2"/>')
    a.append(f'<text x="840" y="232" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="15" font-weight="600" fill="{COLORS["ink"]}">Parallel</text><text x="840" y="255" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="13" fill="{COLORS["muted"]}">location waits max 10s · audio starts</text>')
    return finish(a)

def model():
    a = svg_start('LIMBUZZ V1 — Local Data Model', 'Guest-safe persistence with optional identity linking')
    defs(a)
    box(a, 70, 170, 240, 150, 'USER_PROFILE', 'blue', sub='optional Google identity')
    box(a, 390, 120, 270, 190, 'EMERGENCY_CONTACT', 'orange', sub='1–5 local contacts · primary flag')
    box(a, 390, 430, 270, 190, 'EMERGENCY_SESSION', 'red', sub='ACTIVE / CLOSED · location snapshot')
    box(a, 760, 170, 270, 190, 'SESSION_ACTION', 'green', sub='SMS · CALL · LOCATION · AUDIO')
    box(a, 760, 480, 270, 150, 'AUDIO_RECORDING', 'orange', sub='private local path · share/delete')
    line(a, 310, 245, 390, 215, 'owns')
    line(a, 310, 275, 390, 510, 'starts')
    line(a, 660, 220, 760, 240, 'receives')
    line(a, 660, 525, 760, 270, 'records')
    line(a, 660, 560, 760, 550, 'contains')
    a.append(f'<text x="70" y="700" font-family="Inter,Arial,sans-serif" font-size="14" fill="{COLORS["muted"]}">Nullable user_profile_id keeps guest mode first-class; the database is the recovery source of truth.</text>')
    return finish(a)

def boundary():
    a = svg_start('LIMBUZZ V1 — Build Boundary', 'What ships in the controlled pilot versus explicitly deferred infrastructure')
    defs(a)
    a.append(f'<rect x="70" y="135" width="500" height="520" rx="18" fill="{COLORS["blue"]}" stroke="{COLORS["blue_line"]}" stroke-width="2"/><rect x="710" y="135" width="500" height="520" rx="18" fill="{COLORS["orange"]}" stroke="{COLORS["orange_line"]}" stroke-width="2"/>')
    a.append(f'<text x="320" y="180" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="22" font-weight="700" fill="{COLORS["ink"]}">V1 — Build now</text><text x="960" y="180" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="22" font-weight="700" fill="{COLORS["ink"]}">Later phases</text>')
    left = ['Flutter screens + SOS state machine','Local database + contacts','Foreground service + recovery','Device SMS + primary call','Local audio + permissions','Optional Firebase sign-in']
    right = ['Application backend','Gateway SMS + OTP','FCM push + history','Cloud backup / media','Usernames + social discovery','Real-time tracking']
    for i, t in enumerate(left): box(a, 115, 210+i*65, 410, 42, t, 'paper', stroke=COLORS['blue_line'], radius=9)
    for i, t in enumerate(right): box(a, 755, 210+i*65, 410, 42, t, 'paper', stroke=COLORS['orange_line'], radius=9)
    return finish(a)

def drawio(name, title, items):
    cells = ['<mxfile host="app.diagrams.net" version="24.7.17"><diagram name="'+escape(title)+'"><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>']
    cells.append(f'<mxCell id="title" value="{escape(title)}" style="text;html=1;fontSize=22;fontStyle=1;align=left;verticalAlign=middle;" vertex="1" parent="1"><mxGeometry x="40" y="30" width="700" height="40" as="geometry"/></mxCell>')
    for i,(label,x,y,color) in enumerate(items,2):
        cells.append(f'<mxCell id="n{i}" value="{escape(label)}" style="rounded=1;whiteSpace=wrap;html=1;fillColor={color};strokeColor=#607D8B;fontSize=16;spacing=10;" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="220" height="70" as="geometry"/></mxCell>')
    for i in range(2, 1+len(items)):
        if i < 1+len(items): cells.append(f'<mxCell id="e{i}" edge="1" parent="1" source="n{i}" target="n{i+1}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=block;html=1;"><mxGeometry relative="1" as="geometry"/></mxCell>')
    cells.append('</root></mxGraphModel></diagram></mxfile>')
    (OUT / (name+'.drawio')).write_text(''.join(cells), encoding='utf-8')

if __name__ == '__main__':
    outputs = {'system-context':context(),'sos-sequence':sequence(),'local-data-model':model(),'v1-boundary':boundary()}
    for name, content in outputs.items(): (OUT/(name+'.svg')).write_text(content, encoding='utf-8')
    drawio('system-context','LIMBUZZ V1 — System Context',[('User',80,150,'#FFF0D6'),('Flutter app',360,150,'#D9EFFF'),('Android adapters',640,150,'#D9EFFF'),('Cellular SMS + voice',920,150,'#FFE1E1'),('Emergency contacts',920,300,'#DEF5E7')])
    drawio('sos-sequence','LIMBUZZ V1 — SOS Sequence',[('Hold SOS 3 seconds',80,150,'#FFF0D6'),('Start persisted session',360,150,'#D9EFFF'),('Send SMS to all contacts',640,150,'#FFE1E1'),('Call primary contact',920,150,'#DEF5E7'),('Cancel → all-clear',640,300,'#DEF5E7')])
    drawio('local-data-model','LIMBUZZ V1 — Local Data Model',[('User profile',80,150,'#D9EFFF'),('Emergency contacts',360,150,'#FFF0D6'),('Emergency session',640,150,'#FFE1E1'),('Session actions',920,150,'#DEF5E7'),('Audio recording',640,300,'#FFF0D6')])
    drawio('v1-boundary','LIMBUZZ V1 — Build Boundary',[('V1: local emergency flow',80,150,'#D9EFFF'),('V1: foreground service',360,150,'#D9EFFF'),('Later: backend + gateway',640,150,'#FFF0D6'),('Later: push + social',920,150,'#FFF0D6')])
