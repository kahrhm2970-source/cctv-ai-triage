import threading
import unittest
from http.client import HTTPConnection
from http.server import HTTPServer
from urllib.parse import urlencode
from web_app import Handler
class WebTests(unittest.TestCase):
    def setUp(self):
        self.server=HTTPServer(('127.0.0.1',0),Handler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join()
    def request(self,method,path,body=None,headers=None):
        c=HTTPConnection('127.0.0.1',self.server.server_port,timeout=3)
        c.request(method,path,body,headers or {});r=c.getresponse();data=r.read().decode();code=r.status;c.close();return code,data
    def test_home(self):
        code,data=self.request('GET','/');self.assertEqual(code,200);self.assertIn('textarea',data)
    def test_prediction(self):
        code,data=self.request('POST','/classify',urlencode({'text':'فشل استرجاع التسجيلات القرص ممتلئ'}),{'Content-Type':'application/x-www-form-urlencoded'})
        self.assertEqual(code,200);self.assertIn('<h2>تسجيل</h2>',data);self.assertIn('مراجعة بشرية',data)
    def test_empty_and_oversize(self):
        for text in ['', 'x'*1001]:
            code,_=self.request('POST','/classify',urlencode({'text':text}),{'Content-Type':'application/x-www-form-urlencoded'});self.assertEqual(code,400)
    def test_cross_origin(self):
        code,_=self.request('POST','/classify','text=x',{'Origin':'https://example.org','Content-Type':'application/x-www-form-urlencoded'});self.assertEqual(code,403)
    def test_no_input_reflection(self):
        code,data=self.request('POST','/classify',urlencode({'text':'<script>alert(1)</script>'}),{'Content-Type':'application/x-www-form-urlencoded'})
        self.assertEqual(code,200);self.assertNotIn('<script>',data)
if __name__=='__main__':unittest.main()
