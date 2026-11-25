"""Educational Arabic CCTV text classifier; no device connections."""
import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path

DATA = {
 'connectivity': ['انقطاع اتصال الشبكه الكاميرا غير متصله', 'فقدان الاتصال بالسويتش وانقطاع الشبكه', 'network offline disconnected link', 'الكاميرا خارج الشبكه الاتصال متقطع'],
 'recording': ['التسجيل متوقف لا توجد تسجيلات للاسترجاع', 'فشل استرجاع التسجيلات من القرص', 'recording playback disk storage failure', 'التسجيلات مفقوده ومساحه القرص ممتلئه'],
 'image': ['الصوره ضبابيه العدسه متسخه', 'جوده الصوره ضعيفه والاضاءه مظلمه', 'blurry image lens focus dark', 'تشويش الصوره وانعكاس الاضاءه علي العدسه']
}
STEPS = {
 'connectivity': ['وثق رسالة الحالة ووقت ظهورها.', 'اطلب من الفني المخول مراجعة حالة الرابط والطاقة وفق إجراءات الموقع.'],
 'recording': ['تحقق من اختيار الوقت والقناة الصحيحين في بيئة التدريب.', 'ارفع للفني المخول نتيجة الفحص ورسالة التخزين دون حذف التسجيلات.'],
 'image': ['وثق نوع ضعف الصورة دون مشاركة لقطات حساسة.', 'اطلب مراجعة العدسة والإضاءة من المختص وفق إجراءات الموقع.']
}

def tokens(text):
    text = re.sub('[ًٌٍَُِّْـ]', '', text.lower())
    text = re.sub('[أإآ]', 'ا', text).replace('ة','ه').replace('ى','ي')
    return re.findall(r'[a-z\u0621-\u064a]+', text)

class Model:
    def __init__(self, data=DATA):
        self.counts = {k: Counter(w for s in v for w in tokens(s)) for k,v in data.items()}
        self.vocab = set().union(*(set(c) for c in self.counts.values()))
        self.docs = {k:len(v) for k,v in data.items()}
    def predict(self, text):
        if not isinstance(text,str) or not 1 <= len(text.strip()) <= 1000:
            raise ValueError('Enter 1–1000 characters')
        words = set(tokens(text)) & self.vocab
        scores = {k: math.log(self.docs[k]/sum(self.docs.values())) + sum(math.log((c[w]+1)/(sum(c.values())+len(self.vocab))) for w in words) for k,c in self.counts.items()}
        top = max(scores.values())
        weights = {k:math.exp(v-top) for k,v in scores.items()}
        total = sum(weights.values())
        ranked = sorted(((k,v/total) for k,v in weights.items()), key=lambda x:x[1], reverse=True)
        label, score = ranked[0]
        abstain = len(words)<2 or score<0.60 or score-ranked[1][1]<0.20
        return {'category':'human_review' if abstain else label, 'model_score':round(score,4), 'matched_tokens':sorted(words), 'review_required':True, 'steps': ['الوصف غير كاف أو ملتبس؛ اطلب تفاصيل إضافية ومراجعة مختص.'] if abstain else STEPS[label]}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('text', nargs='?')
    args=p.parse_args()
    try:
        # Interactive input avoids shell history for descriptions; use fictional data only.
        print(json.dumps(Model().predict(args.text if args.text is not None else input('وصف تدريبي: ')),ensure_ascii=False,indent=2))
    except ValueError as exc: p.exit(2,str(exc)+'\n')

