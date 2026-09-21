"""Deterministic experiment runner; writes CSV, JSON and figures with Agg backend."""
from pathlib import Path
import argparse, csv, json, platform, sys
import numpy as np
import scipy
from scipy import signal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .core import *

plt.rcParams.update({'figure.dpi':140,'savefig.dpi':180,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.22,'font.size':10})


def save_csv(path, rows):
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def summarize_errors(k,n):
    # Sufficient statistics; reuse the exact Wilson expression without allocating bits.
    z=1.95996398454;p=k/n;den=1+z*z/n
    center=(p+z*z/(2*n))/den;rad=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return dict(bits=n,errors=k,ber=p,ci95_low=max(0,center-rad),ci95_high=min(1,center+rad))


def sweep_ber(code, ebn0, nbits, rng, jammer=None):
    errors=0;evm2=0
    for start in range(0,nbits,2000):
        b=rng.integers(0,2,min(2000,nbits-start),dtype=np.uint8);x=spread(b,code)
        y=awgn(x,ebn0,rng)
        if jammer is not None:
            js,kind=jammer
            profiles={'tone_inband':('tone',.001,.1),'tone_outofband':('tone',.037,.1),'chirp':('chirp',-.01,.02),'burst':('burst',.037,.1)}
            typ,freq,sweep=profiles[kind]
            y+=interference(len(x),js,float(np.mean(abs(x)**2)),rng,kind=typ,frequency=freq,sweep=sweep)
        dec,soft=despread(y,code);errors+=int(np.count_nonzero(dec!=b));evm2+=float(np.sum(abs(soft-bipolar(b))**2))
    return dict(**summarize_errors(errors,nbits),evm_rms=np.sqrt(evm2/nbits))


def run(output='results', quick=False):
    out=Path(output);figs=out/'figures';figs.mkdir(parents=True,exist_ok=True)
    seed=20260920;rng=np.random.default_rng(seed);nbits=12000 if quick else 60000
    code=spreading_code();unspread=np.ones(127);rows=[]
    for eb in range(0,9,2):
        for name,c in [('BPSK',unspread),('DSSS',code)]:
            rows.append(dict(model=name,ebn0_db=eb,theory=float(theoretical_bpsk(eb)),**sweep_ber(c,eb,nbits,rng)))
    save_csv(out/'awgn.csv',rows)
    fig,ax=plt.subplots(figsize=(7,4.3))
    for name in ['BPSK','DSSS']:
        r=[v for v in rows if v['model']==name];y=np.array([v['ber'] for v in r]);ax.errorbar([v['ebn0_db'] for v in r],y,yerr=[y-[v['ci95_low'] for v in r],[v['ci95_high'] for v in r]-y],marker='o',capsize=3,label=name+' (95% CI)')
    xx=np.linspace(0,8,100);ax.plot(xx,theoretical_bpsk(xx),'k--',label='Coherent BPSK theory');ax.set(yscale='log',xlabel='$E_b/N_0$ (dB)',ylabel='Bit error rate',title='Spreading does not create AWGN coding gain');ax.legend();fig.tight_layout();fig.savefig(figs/'awgn.png');plt.close(fig)
    rows=[]
    for kind in ['tone_inband','tone_outofband','chirp','burst']:
        for js in [-10,0,10,20]:
            for name,c in [('BPSK',unspread),('DSSS',code)]:
                rows.append(dict(jammer=kind,model=name,js_db=js,ebn0_db=8,**sweep_ber(c,8,nbits//2,rng,(js,kind))))
    save_csv(out/'interference.csv',rows)
    fig,axes=plt.subplots(1,4,figsize=(14,3.7),sharey=True)
    for ax,kind in zip(axes,['tone_inband','tone_outofband','chirp','burst']):
        for name in ['BPSK','DSSS']:
            r=[v for v in rows if v['jammer']==kind and v['model']==name]
            ax.semilogy([v['js_db'] for v in r],[max(v['ber'],1/v['bits']) for v in r],'-o',label=name)
        ax.set(title=kind.replace('_',' ').capitalize(),xlabel='Interference / signal (dB)',ylim=(1e-5,1));ax.legend()
    axes[0].set_ylabel('BER (zeros shown at 1/N)');fig.suptitle('Equal information-bit energy, rate and sample rate; $E_b/N_0$ = 8 dB');fig.tight_layout();fig.savefig(figs/'interference.png');plt.close(fig)
    # PN, PSD, and exact hardware recurrence evidence.
    bits,states=hardware_pn();save_csv(out/'pn_sequence.csv',[dict(index=i,state=int(s),bit=int(b)) for i,(s,b) in enumerate(zip(states,bits))])
    acf=periodic_acf(bipolar(bits));save_csv(out/'pn_acf.csv',[dict(lag=i,acf=float(v)) for i,v in enumerate(acf)])
    fig,axes=plt.subplots(1,2,figsize=(10,3.5));axes[0].step(np.arange(40),bits[:40],where='post');axes[0].set(title='Hardware XNOR sequence',xlabel='Chip',ylabel='Logic value');axes[1].plot(acf);axes[1].set(title='Periodic autocorrelation',xlabel='Cyclic chip shift',ylabel='Normalized correlation');fig.tight_layout();fig.savefig(figs/'pn.png');plt.close(fig)
    b=payload(n=3000,seed=seed);rows=[];fig,ax=plt.subplots(figsize=(7,4))
    for name,c in [('BPSK',unspread),('DSSS',code)]:
        x=spread(b,c,sps=4);fs=8e6;f,p,bw=spectrum(x,fs)
        rows.append(dict(model=name,sample_rate_hz=fs,chip_rate_hz=2e6,bit_rate_bps=2e6/127,obw99_hz=bw,mean_discrete_power=float(np.mean(abs(x)**2))))
        ax.plot(f/1e6,10*np.log10(np.maximum(p,1e-30)),label=name)
    ax.set(xlabel='Baseband frequency (MHz)',ylabel='PSD (dB / Hz, discrete amplitude)',title='Rectangular chips; equal bit energy');ax.legend();fig.tight_layout();fig.savefig(figs/'spectrum.png');plt.close(fig);save_csv(out/'spectrum.csv',rows)
    # Real payloads, CRC, and PCM reconstruction.
    rows=[]
    for kind in ['random','alternating','bursts','zeros','ones','text','pcm8']:
        b=payload(kind,n=512,seed=seed);x=spread(b,code);dec,soft=despread(awgn(x,8,rng),code)
        row=dict(payload=kind,**error_metrics(b,dec),evm_rms=evm_rms(soft,b));rows.append(row)
        if kind=='pcm8':
            a=pcm8_decode(b);d=pcm8_decode(dec);fig,ax=plt.subplots(figsize=(8,3));ax.plot(a[:160],label='Quantized input');ax.plot(d[:160],alpha=.7,label='Received');ax.set(xlabel='PCM sample (8 kHz)',ylabel='Amplitude',title='8-bit PCM over DSSS, $E_b/N_0$ = 8 dB');ax.legend();fig.tight_layout();fig.savefig(figs/'pcm.png');plt.close(fig)
    save_csv(out/'payloads.csv',rows)
    rows=[]
    for eb in [0,4,8]:
        failed=0;packet_count=60 if quick else 200
        for i in range(packet_count):
            b=frame_bytes(('DSSS packet %04d'%i).encode());d,_=despread(awgn(spread(b,code),eb,rng),code);_,ok=unframe_bits(d);failed+=not ok
        rows.append(dict(ebn0_db=eb,packets=packet_count,crc_failures=failed,packet_error_rate=failed/packet_count))
    save_csv(out/'packets.csv',rows)
    # Impairment sensitivity with deliberately uncompensated receiver.
    b=payload(n=4000,seed=seed);x=spread(b,code,sps=4);rows=[]
    cases=[('ideal',0,x)]
    for phase in [15,45,80]:cases.append(('phase_degrees',phase,oscillator(x,phase=np.deg2rad(phase))))
    for cfo in [.001,.01,.05]:cases.append(('cfo_cycles_per_bit',cfo,oscillator(x,frequency=cfo/(127*4))))
    for delay in [.25,.5,1]:cases.append(('delay_chips',delay,fractional_delay(x,delay*4)))
    for adc in [2,4,8]:cases.append(('adc_bits',adc,quantize(awgn(x,8,rng),bits=adc,full_scale=.5)))
    for linewidth in [1e-7,1e-6]:cases.append(('phase_noise_cycles_per_sample',linewidth,oscillator(x,linewidth=linewidth,rng=rng)))
    # IQ imbalance matters here after a known quadrature rotation; undo only nominal rotation.
    for mismatch in [1,3]:cases.append(('iq_gain_db',mismatch,iq_imbalance(x*np.exp(1j*np.pi/4),mismatch,5)*np.exp(-1j*np.pi/4)))
    for name,value,y in cases:
        if name!='adc_bits':y=awgn(y,8,rng)
        d,s=despread(y,code,4);rows.append(dict(impairment=name,value=value,**error_metrics(b,d),evm_rms=evm_rms(s,b)))
    save_csv(out/'impairments.csv',rows)
    # Multipath and known-channel matched combining: no channel estimation claim.
    b=payload(n=5000,seed=seed);x=spread(b,code);rows=[]
    for delay in [1,8,64]:
        h=channel_impulse([0,delay],[1,.8*np.exp(.7j)]);r=awgn(signal.fftconvolve(x,h),8,rng)
        for name,y in [('single_finger',r[:len(x)]/h[0]),('known_channel_matched',matched_channel(r,h,len(x)))]:
            d,s=despread(y,code);rows.append(dict(receiver=name,path_delay_chips=delay,**error_metrics(b,d),evm_rms=evm_rms(s,b)))
    save_csv(out/'multipath.csv',rows)
    # Independent Rayleigh fade per symbol, perfect complex CSI at receiver.
    fade=(rng.standard_normal(len(b))+1j*rng.standard_normal(len(b)))/np.sqrt(2)
    y=awgn(x*np.repeat(fade,127),8,rng);_,s=despread(y,code);d=(np.real(np.conj(fade)*s)<0).astype(np.uint8)
    save_csv(out/'rayleigh.csv',[dict(ebn0_db=8,theory=.5*(1-np.sqrt(10**.8/(1+10**.8))),**error_metrics(b,d))])
    # Joint acquisition from a known random preamble, not the repeating code alone.
    pre_bits=payload(n=16,seed=321);pre=spread(pre_bits,code);rows=[];trials=30 if quick else 100
    for eb in [-5,0,5]:
        success=0;delay_errors=[]
        for _ in range(trials):
            delay=int(rng.integers(0,64));f=float(rng.choice([-.0002,0,.0002]));ph=rng.uniform(-np.pi,np.pi)
            r=np.pad(oscillator(pre,frequency=f,phase=ph),(delay,64-delay));r=awgn(r,eb,rng)
            est=acquire(r,pre,64,[-.0002,0,.0002]);success+=est['delay']==delay and abs(est['cfo']-f)<1e-12;delay_errors.append(abs(est['delay']-delay))
        rows.append(dict(ebn0_db=eb,trials=trials,correct_joint_estimates=success,success_rate=success/trials,mean_absolute_delay_error_samples=float(np.mean(delay_errors)),preamble_bits=16,search_delay_samples=64,cfo_grid_count=3))
    save_csv(out/'acquisition.csv',rows)
    # Near-far: second code is a Gold-family member (m=7, preferred decimation 3).
    a=bipolar(hardware_pn()[0]);second=a*a[(3*np.arange(127))%127];b=payload(n=6000,seed=seed);other=payload(n=6000,seed=seed+1);rows=[]
    for nf in [-10,0,10,20,30]:
        y=awgn(spread(b,a)+10**(nf/20)*spread(other,second),8,rng);d,s=despread(y,a)
        rows.append(dict(interferer_to_user_db=nf,code_cross_correlation=float(a@second/127),**error_metrics(b,d)))
    save_csv(out/'near_far.csv',rows)
    # Repetition coding at fixed information-bit energy: each copy gets 1/repeats energy.
    rows=[]
    for eb in [0,4,8]:
        b=payload(n=6000,seed=seed);enc=repetition_encode(b);y=awgn(spread(enc,code)/np.sqrt(3),eb,rng);_,soft=despread(y,code);d=repetition_decode(soft)
        rows.append(dict(ebn0_db=eb,code_rate=1/3,theory_uncoded=float(theoretical_bpsk(eb)),**error_metrics(b,d)))
    save_csv(out/'repetition.csv',rows)
    # Continuous PN hardware trace; data clock case differs from direct square-wave test.
    trace=hardware_trace([0,1,1,0],1000,8);save_csv(out/'hardware_trace_excerpt.csv',[{k:float(v[i]) for k,v in trace.items()} for i in range(240)])
    fig,axes=plt.subplots(2,2,figsize=(10,5.6))
    for ax,key in zip(axes[:,0],['data','recovered']):
        ax.step(trace['time_s'][::8]*1e3,trace[key][::8],where='post');ax.set(xlabel='Time (ms)',ylabel='Logic value',title=key.capitalize()+' across full bit intervals')
    for ax,key in zip(axes[:,1],['pn','tx']):
        ax.step(trace['time_s'][:240]*1e6,trace[key][:240],where='post');ax.set(xlabel='Time (microseconds)',ylabel='Logic value',title=key.upper()+' chip-level detail')
    fig.suptitle('Ideal hardware logic: continuous PN, shared 2 MHz square carrier');fig.tight_layout();fig.savefig(figs/'hardware_logic.png');plt.close(fig)
    metadata=dict(seed=seed,quick=quick,awgn_bits_per_point=nbits,python=sys.version.split()[0],numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform(),model='discrete-time complex baseband, Eb=1, rectangular pulses',hardware_measurements=False)
    (out/'run_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps(metadata));print('Wrote results to',out.resolve())

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='results');parser.add_argument('--quick',action='store_true');args=parser.parse_args();run(args.output,args.quick)
