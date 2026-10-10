import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('viewer',ROOT/'tools/render_predictions.py')
viewer=importlib.util.module_from_spec(spec)
spec.loader.exec_module(viewer)

class GeometryTests(unittest.TestCase):
    def test_projection_and_near_plane(self):
        p=[[100,0,50,0],[0,100,50,0],[0,0,1,0]]
        self.assertEqual(viewer.project((2,1,10),p),(70,60))
        self.assertIsNone(viewer.project((0,0,-1),p))

    def test_kitti_dimensions_and_bottom_center(self):
        boxes=viewer.read_predictions(ROOT/'examples/synthetic_predictions.txt')
        b=boxes[0]
        self.assertEqual(b['score'],0.92)
        c=viewer.corners(b)
        self.assertAlmostEqual(max(v[1] for v in c),b['y'])
        self.assertAlmostEqual(min(v[1] for v in c),b['y']-b['h'])
        self.assertAlmostEqual(sum(v[0] for v in c)/8,b['x'])
        self.assertAlmostEqual(sum(v[2] for v in c)/8,b['z'])

    def test_invalid_predictions_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'bad.txt'
            path.write_text('Car 0 0 0 0 0 0 0 1 1 1 0 0 nan 0 0.5')
            with self.assertRaises(ValueError): viewer.read_predictions(path)

    def test_html_escapes_labels_and_marks_demo(self):
        boxes=viewer.read_predictions(ROOT/'examples/synthetic_predictions.txt')
        boxes[0]['label']='<script>alert(1)</script>'
        page=viewer.render(boxes,viewer.read_projection(ROOT/'examples/synthetic_calib.txt'),1242,375,synthetic=True)
        self.assertNotIn('<script>alert(1)</script>',page)
        self.assertIn('Synthetic geometry demo',page)
        self.assertEqual(page.count('<svg '),2)

if __name__=='__main__': unittest.main()
