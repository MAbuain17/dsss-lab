"""An unknown-delay, unknown-phase framed text link with grid-search CFO recovery."""
import numpy as np
from dsss_lab.core import *

def demo():
    code=spreading_code();preamble=spread(payload(n=16,seed=133),code)
    message=b'DSSS: Tripoli to Edinburgh';frame=frame_bytes(message)
    tx=np.r_[preamble,spread(frame,code)]
    rng=np.random.default_rng(7)
    rx=awgn(np.pad(oscillator(tx,.0002,.83),(29,64)),12,rng)
    decoded,_,est=receive_burst(rx,preamble,len(frame),code,64,[-.0002,0,.0002])
    recovered,crc_ok=unframe_bits(decoded)
    assert crc_ok and recovered==message
    print('Recovered:',recovered.decode());print('CRC valid:',crc_ok);print('Acquisition:',est)
    return est

if __name__=='__main__':demo()
