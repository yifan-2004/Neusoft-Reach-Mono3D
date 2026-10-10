#!/usr/bin/env python3
"""Render saved KITTI camera-coordinate predictions to an offline HTML report.

This utility performs geometry only. It never downloads or runs a model.
"""
import argparse
import base64
import html
import json
import math
import mimetypes
from pathlib import Path

EDGES = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]


def read_predictions(path):
    boxes = []
    for number, line in enumerate(Path(path).read_text().splitlines(), 1):
        fields = line.split()
        if not fields or fields[0] == 'DontCare':
            continue
        if len(fields) not in (15, 16):
            raise ValueError(f'Line {number}: expected 15 or 16 KITTI fields')
        values = list(map(float, fields[1:]))
        if not all(math.isfinite(v) for v in values):
            raise ValueError(f'Line {number}: values must be finite')
        h, w, length, x, y, z, yaw = values[7:14]
        if min(h, w, length) <= 0:
            raise ValueError(f'Line {number}: dimensions must be positive')
        boxes.append(dict(label=fields[0], h=h, w=w, length=length,
                          x=x, y=y, z=z, yaw=yaw,
                          score=values[14] if len(values) == 15 else None))
    return boxes


def read_projection(path):
    for line in Path(path).read_text().splitlines():
        key, sep, value = line.partition(':')
        if sep and key.strip() == 'P2':
            values = list(map(float, value.split()))
            if len(values) != 12 or not all(math.isfinite(v) for v in values):
                raise ValueError('P2 must contain 12 finite values')
            return [values[i:i+4] for i in (0,4,8)]
    raise ValueError('Calibration file needs a P2 projection matrix')


def corners(box):
    h, w, length = box['h'], box['w'], box['length']
    c, s = math.cos(box['yaw']), math.sin(box['yaw'])
    local = [(length/2,0,w/2),(length/2,0,-w/2),(-length/2,0,-w/2),(-length/2,0,w/2),
             (length/2,-h,w/2),(length/2,-h,-w/2),(-length/2,-h,-w/2),(-length/2,-h,w/2)]
    return [(c*x+s*z+box['x'], y+box['y'], -s*x+c*z+box['z']) for x,y,z in local]


def project(point, projection):
    p = (*point, 1.0)
    q = [sum(a*b for a,b in zip(row,p)) for row in projection]
    return None if q[2] <= 0.1 else (q[0]/q[2],q[1]/q[2])


def render(boxes, projection, width, height, image=None, synthetic=False):
    colors = ['#53e0c4','#ffcb77','#aeb6ff','#ff83ad']
    svg = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Projected 3D bounding boxes">',
           f'<rect width="{width}" height="{height}" fill="#111e33"/>']
    if image:
        mime = mimetypes.guess_type(str(image))[0]
        if mime not in ('image/png','image/jpeg','image/webp'):
            raise ValueError('Background image must be PNG, JPEG or WebP')
        data = base64.b64encode(Path(image).read_bytes()).decode()
        svg.append(f'<image width="{width}" height="{height}" preserveAspectRatio="none" href="data:{mime};base64,{data}"/>')
    elif synthetic:
        svg.append(f'<path d="M 0 {height} L {width*.38} {height*.42} L {width*.62} {height*.42} L {width} {height}" fill="#1b2e47"/>')
        svg.append(f'<path d="M {width*.5} {height*.48} L {width*.5} {height}" stroke="#647893" stroke-dasharray="18 22" stroke-width="3"/>')
    bev = ['<svg viewBox="0 0 500 500" role="img" aria-label="Bird eye view, camera coordinates">',
           '<rect width="500" height="500" fill="#111e33"/>']
    for z in range(0,51,10):
        v = 460-z*8
        bev.append(f'<path d="M 40 {v} H 460" stroke="#273b52"/><text x="7" y="{v}" fill="#98abc1" font-size="12">{z}m</text>')
    bev.append('<path d="M 250 50 V 460" stroke="#647893" stroke-dasharray="4 8"/><text x="230" y="484" fill="#98abc1">camera</text>')
    rows=[]
    for i, box in enumerate(boxes):
        color=colors[i%len(colors)]
        points=corners(box)
        projected=[project(p,projection) for p in points]
        for a,b in EDGES:
            if projected[a] is not None and projected[b] is not None:
                x1,y1=projected[a]; x2,y2=projected[b]
                svg.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="2.5"/>')
        label=html.escape(box['label'])
        if projected[4]:
            x,y=20,30+i*26
            svg.append(f'<text x="{x:.2f}" y="{y:.2f}" fill="{color}" font-size="17">{label} · {box["z"]:.1f}m</text>')
        poly=' '.join(f'{250+x*8:.2f},{460-z*8:.2f}' for x,y,z in points[:4])
        bev.append(f'<polygon points="{poly}" stroke="{color}" fill="{color}" fill-opacity=".15" stroke-width="2"/>')
        score='—' if box['score'] is None else f'{box["score"]:.3f}'
        rows.append(f'<tr><td>{label}</td><td>{score}</td><td>{box["z"]:.1f} m</td><td>{box["h"]:.2f} × {box["w"]:.2f} × {box["length"]:.2f}</td></tr>')
    svg.append('</svg>'); bev.append('</svg>')
    status='Synthetic geometry demo · not model predictions' if synthetic else 'Saved predictions · no inference performed by this viewer'
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Neusoft Reach Mono3D · Prediction Viewer</title><style>
*{box-sizing:border-box}body{margin:0;background:#081321;color:#e8f0fc;font:16px system-ui,sans-serif}main{max-width:1240px;margin:auto;padding:40px 24px}header{display:flex;justify-content:space-between;gap:24px;align-items:center}h1{font-size:38px;margin:8px 0}p{color:#a6b9d0;line-height:1.7}.tag{color:#53e0c4;letter-spacing:2px;font-size:12px}.notice{padding:12px 18px;background:#172a40;border-left:3px solid #ffcb77;border-radius:5px;color:#ffcb77}.grid{display:grid;grid-template-columns:2fr 1fr;gap:20px;margin:28px 0}.panel{background:#101f32;border:1px solid #25374f;border-radius:16px;overflow:hidden}.panel h2{font-size:14px;margin:0;padding:16px;color:#a6b9d0}svg{display:block;width:100%}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:14px;border-bottom:1px solid #25374f}th{color:#a6b9d0;font-size:13px}footer{color:#a6b9d0;font-size:13px;margin-top:24px}@media(max-width:760px){.grid{grid-template-columns:1fr}header{display:block}h1{font-size:28px}.panel{overflow:auto}}
</style><main><header><div><span class="tag">NEUSOFT REACH / MONO3D</span><h1>See the scene in 3D.</h1><p>Camera projection, bird-eye view and object attributes in one offline report.</p></div></header>'''+f'<div class="notice">{status}</div><div class="grid"><section class="panel"><h2>CAMERA VIEW</h2>{"".join(svg)}</section><section class="panel"><h2>BIRD-EYE VIEW · ±25 m / 0–50 m</h2>{"".join(bev)}</section></div><section class="panel"><h2>OBJECT ATTRIBUTES · KITTI CAMERA COORDINATES</h2><table><thead><tr><th>Class</th><th>Score</th><th>Forward depth</th><th>H × W × L (m)</th></tr></thead><tbody>{"".join(rows)}</tbody></table></section><footer>Boxes use KITTI bottom-center locations, rotation around camera Y, and P2 projection. The bird-eye view is derived from the same camera-coordinate boxes; no point-cloud sensor is used.</footer></main></html>'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predictions',required=True)
    parser.add_argument('--calibration',required=True)
    parser.add_argument('--image')
    parser.add_argument('--width',type=int,default=1242)
    parser.add_argument('--height',type=int,default=375)
    parser.add_argument('--output',required=True)
    parser.add_argument('--synthetic',action='store_true',help='Explicitly label illustrative non-model data')
    args=parser.parse_args()
    if args.width<=0 or args.height<=0:
        parser.error('Image dimensions must be positive and match the supplied image')
    boxes=read_predictions(args.predictions)
    projection=read_projection(args.calibration)
    output=Path(args.output); output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(render(boxes,projection,args.width,args.height,args.image,args.synthetic))
    print(f'Wrote {output} with {len(boxes)} boxes; no inference performed.')


if __name__=='__main__':
    main()
