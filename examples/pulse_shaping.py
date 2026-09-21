"""RRC pulse shaping, matched filtering and occupied bandwidth comparisons."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from dsss_lab.core import *
from dsss_lab.experiments import save_csv

def run(out='results'):
    out=Path(out);(out/'figures').mkdir(parents=True,exist_ok=True)
    b=payload(n=4000,seed=99);code=spreading_code();chips=spread(b,code);rng=np.random.default_rng(99)
    rows=[];fig,ax=plt.subplots(figsize=(7,4))
    for beta in [.2,.35,.7]:
        h=rrc_taps(beta,10,4);x=pulse_shape(chips,h,4)
        y=awgn(x,8,rng);z=matched_pulse(y,h,4,len(chips));d,_=despread(z,code)
        f,p,bw=spectrum(x,8e6);rows.append(dict(rolloff=beta,span_chips=10,obw99_hz=bw,ebn0_db=8,**error_metrics(b,d)))
        ax.plot(f/1e6,10*np.log10(np.maximum(p,1e-30)),label=f'RRC beta={beta}')
    ax.set(xlabel='Baseband frequency (MHz)',ylabel='PSD (dB / Hz)',title='Pulse shaping at 2 Mchip/s');ax.legend();fig.tight_layout();fig.savefig(out/'figures/pulse_shaping.png');plt.close(fig)
    save_csv(out/'pulse_shaping.csv',rows)

if __name__=='__main__':run()
