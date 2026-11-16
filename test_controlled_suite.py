import unittest
from evaluate_controlled_suite import bev_iou,assign

class EvaluationTests(unittest.TestCase):
    def obj(self,x=0,z=10,ry=0,box=None):return dict(t='Car',x=x,y=1.5,z=z,h=1.5,w=2,l=4,ry=ry,box=box or [0,0,10,10])
    def test_bev_geometry(self):
        self.assertAlmostEqual(bev_iou(self.obj(),self.obj()),1)
        self.assertEqual(bev_iou(self.obj(),self.obj(x=10)),0)
        self.assertAlmostEqual(bev_iou(self.obj(),self.obj(x=2)),1/3,places=6)
        self.assertAlmostEqual(bev_iou(self.obj(),self.obj(ry=1.5707963267948966)),1/3,places=6)
    def test_matching_excludes_depth_filter(self):
        self.assertEqual(len(assign([self.obj(z=100)],[self.obj(z=10)])),1)
        self.assertEqual(len(assign([self.obj(),self.obj()],[self.obj()])),1)
        p=self.obj();p['t']='Pedestrian';self.assertEqual(assign([p],[self.obj()]),[])
if __name__=='__main__':unittest.main()
