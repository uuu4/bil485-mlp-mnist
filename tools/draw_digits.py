"""Okul numarasının her hanesini trackpad/fare ile çizip my_digits/NN.png olarak kaydeden yerel çizim tahtası.

Kullanım:  python3 tools/draw_digits.py 23120205056
Sonra tarayıcıda http://127.0.0.1:8791 açılır, her rakam elle çizilir. Dosyalar yalnızca bu makinede,
my_digits/ klasörüne yazılır (sunucu 127.0.0.1'e bağlıdır, dışarıdan erişilemez).
"""
import base64, pathlib, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

NUM = sys.argv[1] if len(sys.argv) > 1 else ""
OUT = pathlib.Path(__file__).resolve().parent.parent / "my_digits"
PORT = 8791
assert NUM.isdigit(), "Kullanım: python3 tools/draw_digits.py <okul numarası>"

PAGE = """<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rakam çizim tahtası</title>
<style>
 :root{--bg:#fafaf7;--fg:#1d1d1b;--mut:#6b6b66;--card:#fff;--line:#dcdcd4;--acc:#1f5fd6}
 @media(prefers-color-scheme:dark){:root{--bg:#161615;--fg:#eeeeea;--mut:#9a9a93;--card:#202020;--line:#383836;--acc:#6ea2ff}}
 body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.45 system-ui,sans-serif;display:flex;justify-content:center}
 main{width:100%;max-width:460px;padding:20px 16px 40px;box-sizing:border-box}
 h1{font-size:20px;margin:0 0 4px} p{margin:4px 0;color:var(--mut)}
 #target{font-size:64px;font-weight:700;line-height:1;margin:10px 0 2px}
 canvas{width:100%;max-width:360px;aspect-ratio:1;background:#000;border-radius:10px;touch-action:none;cursor:crosshair;display:block;margin:10px 0;border:1px solid var(--line)}
 .row{display:flex;gap:8px;flex-wrap:wrap}
 button{font:inherit;padding:10px 14px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--fg);cursor:pointer}
 button.p{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:600}
 #strip{display:flex;gap:6px;flex-wrap:wrap;margin-top:18px}
 #strip div{width:44px;text-align:center;font-size:11px;color:var(--mut)} #strip img{width:44px;height:44px;border-radius:6px;display:block;border:1px solid var(--line)}
 #msg{min-height:1.4em;color:var(--acc)}
</style>
<main>
 <h1>Okul numarası: <span id="num"></span></h1>
 <p>Trackpad'e basılı tutarak (tıkla-sürükle) çiz. Rakamı tuvalin ortasına, büyük ve kalın çiz.</p>
 <div id="target"></div><p id="pos"></p>
 <canvas id="c" width="280" height="280"></canvas>
 <div class="row"><button id="clr">Temizle</button><button id="back">Önceki hane</button><button id="save" class="p">Kaydet ve sonraki</button></div>
 <p id="msg"></p><div id="strip"></div>
</main>
<script>
const NUM="__NUM__", N=NUM.length;
const c=document.getElementById('c'), ctx=c.getContext('2d');
let idx=0, drawing=false, last=null, dirty=false;
const saved={};
function blank(){ctx.fillStyle='#000';ctx.fillRect(0,0,280,280);dirty=false;}
ctx.lineWidth=22;ctx.lineCap='round';ctx.lineJoin='round';ctx.strokeStyle='#fff';ctx.fillStyle='#fff';
function pt(e){const r=c.getBoundingClientRect();return [(e.clientX-r.left)*280/r.width,(e.clientY-r.top)*280/r.height];}
c.addEventListener('pointerdown',e=>{c.setPointerCapture(e.pointerId);drawing=true;last=pt(e);
  ctx.beginPath();ctx.arc(last[0],last[1],11,0,7);ctx.fill();dirty=true;});
c.addEventListener('pointermove',e=>{if(!drawing)return;const p=pt(e);ctx.beginPath();ctx.moveTo(last[0],last[1]);ctx.lineTo(p[0],p[1]);ctx.stroke();last=p;});
['pointerup','pointercancel'].forEach(t=>c.addEventListener(t,()=>{drawing=false;}));
function show(){
  document.getElementById('num').textContent=NUM;
  document.getElementById('target').textContent=idx<N?NUM[idx]:'✓';
  document.getElementById('pos').textContent=idx<N?('Hane '+(idx+1)+' / '+N):'Hepsi kaydedildi';
  document.getElementById('save').disabled=idx>=N;
  const s=document.getElementById('strip');s.innerHTML='';
  for(let i=0;i<N;i++){const d=document.createElement('div');
    d.innerHTML=(saved[i]?'<img src="'+saved[i]+'">':'<img alt="">')+(i+1)+': '+NUM[i];s.appendChild(d);}
  blank();
}
document.getElementById('clr').onclick=()=>{blank();};
document.getElementById('back').onclick=()=>{if(idx>0){idx--;show();}};
document.getElementById('save').onclick=async()=>{
  const m=document.getElementById('msg');
  if(!dirty){m.textContent='Önce rakamı çiz.';return;}
  const url=c.toDataURL('image/png');
  const r=await fetch('/save?i='+(idx+1),{method:'POST',body:url});
  if(!r.ok){m.textContent='Kaydedilemedi: '+r.status;return;}
  saved[idx]=url;m.textContent='Kaydedildi: my_digits/'+String(idx+1).padStart(2,'0')+'.png';
  idx++;show();
};
show();
</script></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if urlparse(self.path).path != "/":
            self.send_error(404); return
        body = PAGE.replace("__NUM__", NUM).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def do_POST(self):
        u = urlparse(self.path)
        try:
            i = int(parse_qs(u.query)["i"][0])
            assert u.path == "/save" and 1 <= i <= len(NUM)
            raw = self.rfile.read(int(self.headers["Content-Length"])).decode()
            head, b64 = raw.split(",", 1)
            assert head == "data:image/png;base64"
            png = base64.b64decode(b64)
            assert png[:8] == b"\x89PNG\r\n\x1a\n" and len(png) < 2_000_000
        except Exception:
            self.send_error(400); return
        OUT.mkdir(exist_ok=True)
        (OUT / f"{i:02d}.png").write_bytes(png)
        self.send_response(204); self.end_headers()


if __name__ == "__main__":
    print(f"Çizim tahtası: http://127.0.0.1:{PORT}  (numara {NUM}, kayıt: {OUT})")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
