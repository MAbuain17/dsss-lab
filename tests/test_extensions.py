import unittest
import numpy as np
from dsss_lab.core import *
class ExtensionTests(unittest.TestCase):
    def test_pulse_shaping(self):
        b=payload(n=300);c=spreading_code(31)
        for beta in [.2,.35,.7]:
            h=rrc_taps(beta);self.assertAlmostEqual(float(h@h),1)
            x=spread(b,c);z=matched_pulse(pulse_shape(x,h,4),h,4,len(x));d,_=despread(z,c);np.testing.assert_array_equal(d,b)
    def test_full_burst_receiver(self):
        c=spreading_code();p=spread(payload(n=16,seed=133),c);b=frame_bytes(b'Hello')
        x=np.r_[p,spread(b,c)];r=np.pad(oscillator(x,.0002,.8),(29,64))
        d,_,est=receive_burst(r,p,len(b),c,64,[-.0002,0,.0002]);self.assertEqual(est['delay'],29);self.assertEqual(unframe_bits(d),(b'Hello',True))
    def test_gold_cross_correlation(self):
        a=spreading_code();g=a*a[(3*np.arange(127))%127]
        cross=np.fft.ifft(np.fft.fft(a)*np.conj(np.fft.fft(g))).real
        self.assertTrue(set(np.rint(cross).astype(int)).issubset({-17,-1,15,17,1,-15}))
