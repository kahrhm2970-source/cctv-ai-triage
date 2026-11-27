"""Local-only educational Arabic UI. No external calls or persistence."""
import html
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from triage import Model
from batch import LABELS

PAGE='''<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>CCTV AI Triage</title><style>body{font:18px system-ui;background:#edf3f8;color:#14324d;max-width:850px;margin:40px auto;padding:20px}header,article,form{background:white;border-radius:16px;padding:24px;margin:20px 0}textarea{width:95%;font:inherit;padding:12px;border:1px solid #8da4ba;border-radius:8px}button{font:inherit;background:#14324d;color:white;padding:12px 28px;border:0;border-radius:8px}small{display:block;margin:12px 0}</style><header><h1>CCTV AI Triage</h1><p>مساعد فرز أوصاف الأعطال • نموذج تدريبي محلي</p><p>تصنيف نصي بتعلم الآلة، دون تحليل فيديو أو اتصال بالكاميرات. استخدم بيانات افتراضية فقط.</p></header><form method="post" action="/classify"><label for="text">وصف العطل الافتراضي</label><p>مثال: فشل استرجاع التسجيلات القرص ممتلئ</p><textarea id="text" name="text" rows="4" required maxlength="1000" placeholder="اكتب وصفًا تدريبيًا هنا"></textarea><small>لا تدخل مواقع العمل أو أسماء أو عناوين IP أو معلومات سرية.</small><button type="submit">اقتراح التصنيف</button></form>'''

def result_html(text):
    r=Model().predict(text)
    steps=''.join('<li>'+html.escape(s)+'</li>' for s in r['steps'])
    return '<article><h2>'+LABELS[r['category']]+'</h2><p>مراجعة بشرية مطلوبة دائمًا</p><p>درجة النموذج: '+str(r['model_score'])+'</p><p>هذه الدرجة ليست احتمال صحة التشخيص. النموذج قد يخطئ مع النفي واللهجات والأعطال المختلطة.</p><ul>'+steps+'</ul><p>الخطوات نصوص ثابتة حسب الفئة، وليست تعليمات مولدة.</p></article>'

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def respond(self,code,body):
        raw=(PAGE+body+'</html>').encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers();self.wfile.write(raw)
    def trusted(self):
        allowed={f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'}
        host=self.headers.get('Host','')
        origin=self.headers.get('Origin')
        return host in allowed and (origin is None or origin in {'http://'+h for h in allowed}) and self.headers.get('Sec-Fetch-Site') not in {'cross-site'}
    def do_GET(self):
        if not self.trusted():return self.respond(403,'طلب غير مسموح')
        self.respond(200 if self.path=='/' else 404,'' if self.path=='/' else 'صفحة غير موجودة')
    def do_POST(self):
        if not self.trusted():return self.respond(403,'طلب غير مسموح')
        if self.path!='/classify':return self.respond(404,'صفحة غير موجودة')
        try:
            if self.headers.get('Content-Type','').split(';')[0]!='application/x-www-form-urlencoded':raise ValueError()
            n=int(self.headers.get('Content-Length','0'))
            if not 1<=n<=16000:raise ValueError()
            fields=parse_qs(self.rfile.read(n).decode('utf-8'),strict_parsing=True,max_num_fields=1)
            if set(fields)!={'text'} or len(fields['text'])!=1:raise ValueError()
            body=result_html(fields['text'][0])
        except (ValueError,UnicodeError):return self.respond(400,'أدخل وصفًا افتراضيًا صالحًا من 1 إلى 1000 حرف.')
        self.respond(200,body)

if __name__=='__main__':
    print('Open http://127.0.0.1:8765 — Ctrl+C to stop. Local training only.')
    HTTPServer(('127.0.0.1',8765),Handler).serve_forever()
