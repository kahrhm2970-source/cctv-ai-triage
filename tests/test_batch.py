import tempfile
import unittest
from pathlib import Path
from batch import classify, report
class BatchTests(unittest.TestCase):
    def test_demo(self):
        rows=classify('examples/tickets.csv')
        self.assertEqual([r['category'] for r in rows],['connectivity','recording','image','human_review'])
        self.assertTrue(all(r['review_required'] for r in rows))
    def test_bad_csv(self):
        for data in ['wrong\n','ticket_id,description\n','ticket_id,description\nLAB-001,\n','ticket_id,description\nreal,hello\n','ticket_id,description\nLAB-001,hello\nLAB-001,hello\n','ticket_id,description\nLAB-001,hello,extra\n']:
            with self.subTest(data=data),tempfile.TemporaryDirectory() as d:
                p=Path(d)/'x.csv';p.write_text(data,encoding='utf-8')
                with self.assertRaises(ValueError):classify(p)
    def test_escape(self):
        rows=classify('examples/tickets.csv');rows[0]['steps']=['<script>bad</script>']
        text=report(rows);self.assertNotIn('<script>',text);self.assertIn('&lt;script&gt;',text)
    def test_no_description_export(self):
        self.assertNotIn('انقطاع الشبكة الاتصال متقطع',report(classify('examples/tickets.csv')))

