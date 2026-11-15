import unittest
import numpy as np
from render_sequence_video import corners, match

class GeometryTests(unittest.TestCase):
    def obj(self, z=10, typ='Car', box=None):
        return dict(t=typ, h=2., w=2., l=4., x=0., y=1., z=z, ry=0., box=box or [0, 0, 10, 10])

    def test_bottom_center_and_dimensions(self):
        c=corners(self.obj())
        np.testing.assert_allclose(c[:, :4].mean(axis=1), [0, 1, 10])
        np.testing.assert_allclose(c[:, 4:].mean(axis=1), [0, -1, 10])
        np.testing.assert_allclose(np.ptp(c, axis=1), [4, 2, 2])

    def test_gt_is_not_reused(self):
        pairs=match([self.obj(), self.obj()], [self.obj()])
        self.assertEqual(sum(g is not None for _,g in pairs),1)

    def test_large_depth_errors_are_not_hidden(self):
        self.assertIsNotNone(match([self.obj(z=90)], [self.obj(z=10)])[0][1])

    def test_class_and_overlap_are_required(self):
        self.assertIsNone(match([self.obj(typ='Truck')], [self.obj()])[0][1])
        self.assertIsNone(match([self.obj(box=[50,50,60,60])], [self.obj()])[0][1])

if __name__=='__main__':unittest.main()
