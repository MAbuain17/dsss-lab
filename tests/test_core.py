import unittest
import numpy as np
from scipy import signal
from dsss_lab.core import *

class CoreTests(unittest.TestCase):
    def test_hardware_period_and_table(self):
        bits,states=hardware_pn(128)
        self.assertEqual(states[:8].tolist(),[0,64,32,80,40,84,42,85])
        self.assertEqual(len(set(states[:127].tolist())),127)
        self.assertEqual(int(states[-1]),0)
        self.assertNotIn(127,states);self.assertEqual(int(bits[:127].sum()),63)
    def test_acf(self):
        ac=periodic_acf(spreading_code());self.assertAlmostEqual(ac[0],1)
        np.testing.assert_allclose(ac[1:],-1/127,atol=1e-12)
    def test_energy_and_roundtrip(self):
        b=payload(n=101)
        for sf in [1,7,31,127]:
            for sps in [1,4]:
                x=spread(b,spreading_code(sf),sps);self.assertAlmostEqual(float(x@x),len(b),places=8)
                d,s=despread(x,spreading_code(sf),sps);np.testing.assert_array_equal(d,b);np.testing.assert_allclose(s,bipolar(b))
    def test_awgn_theory_and_noise(self):
        rng=np.random.default_rng(11);b=payload(n=60000);x=spread(b,spreading_code(7));y=awgn(x,2,rng)
        self.assertAlmostEqual(float(np.mean(abs(y-x)**2)),10**(-.2),delta=.005)
        d,_=despread(y,spreading_code(7));p=error_metrics(b,d)['ber'];theory=float(theoretical_bpsk(2));self.assertLess(abs(p-theory),5*np.sqrt(theory*(1-theory)/len(b)))
    def test_payload_and_crc(self):
        data='Tripoli → Edinburgh'.encode();b=frame_bytes(data);self.assertEqual(unframe_bits(b),(data,True));b[20]^=1;self.assertFalse(unframe_bits(b)[1])
        pcm=payload('pcm8',samples=np.array([-1,0,1]));np.testing.assert_allclose(pcm8_decode(pcm),[-1,0,1],atol=1/127.5)
    def test_hardware_recovery(self):
        t=hardware_trace([0,1,0,1]);np.testing.assert_array_equal(t['data'],t['recovered'])
    def test_acquisition(self):
        p=spread(payload(n=12),spreading_code(31));r=np.pad(oscillator(p,.002,.7),(17,23));a=acquire(r,p,40,[-.002,0,.002]);self.assertEqual(a['delay'],17);self.assertEqual(a['cfo'],.002);self.assertAlmostEqual(a['phase'],.7)
    def test_matched_channel_alignment(self):
        x=spread(payload(n=20),spreading_code(31));h=channel_impulse([3],[1j]);r=signal.fftconvolve(x,h);np.testing.assert_allclose(matched_channel(r,h,len(x)),x,atol=1e-12)
    def test_jammer_power(self):
        for kind in ['tone','chirp','noise','burst']:
            j=interference(10000,10,.01,np.random.default_rng(3),kind);self.assertAlmostEqual(float(np.mean(abs(j)**2)),.1)
    def test_repetition_energy(self):
        b=payload(n=33);enc=repetition_encode(b);x=spread(enc,spreading_code())/np.sqrt(3);self.assertAlmostEqual(float(x@x),len(b));_,s=despread(x,spreading_code());np.testing.assert_array_equal(repetition_decode(s),b)
    def test_impairment_identity(self):
        x=np.array([1+2j,3+4j]);np.testing.assert_allclose(oscillator(x),x);np.testing.assert_allclose(fractional_delay(x,0),x);np.testing.assert_allclose(iq_imbalance(x),x)
    def test_wilson_zero_errors(self):
        m=error_metrics(np.zeros(100),np.zeros(100));self.assertEqual(m['ber'],0);self.assertGreater(m['ci95_high'],0)
    def test_invalid_input(self):
        with self.assertRaises(ValueError):hardware_pn(seed=127)
        with self.assertRaises(ValueError):binary([0,2])
        with self.assertRaises(ValueError):despread([1,2],spreading_code())
        with self.assertRaises(ValueError):hardware_trace([0],sps=3)
    def test_parseval_psd(self):
        x=spread(payload(n=2000),spreading_code());f,p,bw=spectrum(x,2e6)
        self.assertAlmostEqual(float(np.sum(p)*(f[1]-f[0])),float(np.mean(x*x)),delta=.001)
        self.assertGreater(bw,0)

if __name__=='__main__':unittest.main()
