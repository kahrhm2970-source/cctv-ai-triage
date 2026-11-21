"""Small synthetic holdout, not a production benchmark."""
import json
from triage import Model
CASES=[('انقطاع الشبكة الاتصال متقطع','connectivity'),('فشل استرجاع التسجيلات القرص ممتلئ','recording'),('الصورة ضبابية العدسة متسخة','image'),('مرحبا صباح الخير','human_review'),('الاتصال','human_review'),('','invalid')]
def evaluate():
    model=Model(); results=[]
    for text,expected in CASES:
        try: actual=model.predict(text)['category']
        except ValueError: actual='invalid'
        results.append(dict(text=text,expected=expected,actual=actual,passed=expected==actual))
    return {'note':'Synthetic smoke evaluation only; no real-world accuracy claim','passed':sum(r['passed'] for r in results),'total':len(results),'cases':results}
if __name__=='__main__': print(json.dumps(evaluate(),ensure_ascii=False,indent=2))
