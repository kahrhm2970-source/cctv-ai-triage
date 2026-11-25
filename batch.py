"""Classify synthetic CSV tickets locally and export Arabic HTML."""
import argparse
import csv
import html
import json
import re
from pathlib import Path
from triage import Model

LABELS={'connectivity':'اتصال','recording':'تسجيل','image':'جودة الصورة','human_review':'معلومات غير كافية أو ملتبسة'}

def classify(path):
    if Path(path).stat().st_size > 1_000_000: raise ValueError('Input exceeds 1 MB')
    with open(path,encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=['ticket_id','description']: raise ValueError('Expected ticket_id,description columns')
        rows=list(reader)
    if not 1<=len(rows)<=1000: raise ValueError('Expected 1–1000 rows')
    seen=set(); results=[]; model=Model()
    for r in rows:
        if None in r or any(v is None for v in r.values()): raise ValueError('Invalid row width')
        if not re.fullmatch(r'LAB-[0-9]{3,6}',r['ticket_id']) or r['ticket_id'] in seen: raise ValueError('Use unique LAB-001 style IDs')
        seen.add(r['ticket_id'])
        result=model.predict(r['description'])
        results.append({'ticket_id':r['ticket_id'],**result})
    return results

def report(rows):
    # Raw input descriptions are deliberately omitted from exported reports.
    cells=''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in [r['ticket_id'],LABELS[r['category']],r['model_score'],'مراجعة بشرية مطلوبة',' / '.join(r['steps'])])+'</tr>' for r in rows)
    return '''<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CCTV AI Batch</title><style>body{font:18px system-ui;margin:4%;color:#16324f;background:#eef3f8}header{padding:24px;background:#16324f;color:white;border-radius:12px}table{background:white;border-collapse:collapse;width:100%}td,th{padding:12px;border:1px solid #cbd5e1}section{overflow:auto}</style><header><h1>CCTV AI Triage | فرز البلاغات</h1><p>بيانات تدريبية افتراضية • تعلم آلة محلي</p></header><p>عدد البلاغات: '''+str(len(rows))+'''</p><p>درجة النموذج غير معايرة ولا تمثل احتمال صحة التشخيص. جميع النتائج تتطلب مراجعة بشرية. المقترحات ثابتة حسب الفئة ولا تنفذ أي إجراء.</p><section><table><tr><th>البلاغ</th><th>التصنيف المقترح</th><th>درجة النموذج</th><th>المراجعة</th><th>خطوات أولية</th></tr>'''+cells+'</table></section></html>'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('csv_file');p.add_argument('--out',default='reports');a=p.parse_args()
    try:
        rows=classify(a.csv_file); out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
        (out/'report.html').write_text(report(rows),encoding='utf-8')
        # Exclude matched words as well as descriptions from saved JSON.
        safe=[{k:v for k,v in r.items() if k!='matched_tokens'} for r in rows]
        (out/'results.json').write_text(json.dumps(safe,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'Exported {len(rows)} tickets; human review required for all.')
    except (ValueError,OSError,UnicodeError,csv.Error) as e:p.exit(2,str(e)+'\n')
if __name__=='__main__':main()
