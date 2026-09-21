"""Energy-normalized BPSK/DSSS primitives. See docs/methodology.md for conventions."""
from __future__ import annotations
from dataclasses import dataclass
import zlib
import numpy as np
from scipy import signal
from scipy.special import erfc


def binary(bits):
    a = np.asarray(bits)
    if a.ndim != 1 or not len(a) or not np.all((a == 0) | (a == 1)):
        raise ValueError("Expected a nonempty one-dimensional binary sequence")
    return a.astype(np.uint8)


def bipolar(bits):
    return 1.0 - 2.0 * binary(bits)


def hardware_pn(n=127, seed=0):
    """Seven active stages, XNOR(QA,QG), MSB output before update.

    Integer state bit 6 is QA; bit 0 is QG. Matches report Table 1.
    All-zero is allowed; 127 is the excluded fixed point. Output polarity is
    0 -> +1 when used with bipolar(). Feedback stream is a cyclic shift.
    """
    if not isinstance(n, (int, np.integer)) or n < 1 or seed not in range(127):
        raise ValueError("n must be positive; hardware seed must be 0..126")
    states = np.empty(n, dtype=np.uint8)
    state = int(seed)
    for i in range(n):
        states[i] = state
        fb = 1 ^ ((state >> 6) & 1) ^ (state & 1)
        state = (state >> 1) | (fb << 6)
    return ((states >> 6) & 1), states


def periodic_acf(code):
    c = np.asarray(code, float)
    return np.fft.ifft(abs(np.fft.fft(c))**2).real / len(c)


def spreading_code(length=127, offset=0):
    if length < 1 or int(length) != length:
        raise ValueError("Positive integer spreading length required")
    return np.roll(np.resize(bipolar(hardware_pn()[0]), int(length)), int(offset))


def spread(bits, code, sps=1):
    """Reset code at each bit. Discrete energy per uncoded bit equals one."""
    c = np.asarray(code, float)
    if c.ndim != 1 or not len(c) or not np.all(np.abs(c) == 1) or sps < 1 or int(sps) != sps:
        raise ValueError("code must be +/-1; sps must be a positive integer")
    pulse = np.repeat(c, int(sps))
    return (bipolar(bits)[:, None] * pulse[None, :] / np.sqrt(len(pulse))).ravel()


def despread(rx, code, sps=1):
    pulse = np.repeat(np.asarray(code, float), sps)
    y = np.asarray(rx)
    if y.ndim != 1 or len(y) % len(pulse):
        raise ValueError("Receiver input must contain complete symbols")
    soft = y.reshape(-1, len(pulse)) @ pulse / np.sqrt(len(pulse))
    return (soft.real < 0).astype(np.uint8), soft


def awgn(x, ebn0_db, rng):
    """Complex noise: E[|n|^2]=N0, variance per quadrature=N0/2; Eb=1."""
    if np.isposinf(ebn0_db): return np.asarray(x, complex).copy()
    if not np.isfinite(ebn0_db): raise ValueError("Eb/N0 must be finite or +inf")
    sigma = np.sqrt(0.5 * 10.0**(-ebn0_db / 10.0))
    return x + sigma * (rng.standard_normal(len(x)) + 1j*rng.standard_normal(len(x)))


def theoretical_bpsk(ebn0_db):
    return 0.5 * erfc(np.sqrt(10.0**(np.asarray(ebn0_db)/10)))


def error_metrics(truth, decoded):
    a, b = binary(truth), binary(decoded)
    if len(a) != len(b): raise ValueError("Bit counts differ")
    n = len(a); k = int(np.count_nonzero(a != b)); p = k/n; z = 1.95996398454
    center = (p + z*z/(2*n))/(1+z*z/n)
    radius = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return dict(bits=n, errors=k, ber=p, ci95_low=max(0.,center-radius), ci95_high=min(1.,center+radius))


def evm_rms(soft, bits):
    """Raw RMS decision EVM, no fitted gain/phase correction."""
    return float(np.sqrt(np.mean(abs(np.asarray(soft)-bipolar(bits))**2)))


def payload(kind="random", n=1024, seed=17, text="DSSS | Mohamed Abuain | Tripoli", samples=None):
    if kind == "random": return np.random.default_rng(seed).integers(0,2,n,dtype=np.uint8)
    if kind == "alternating": return (np.arange(n)%2).astype(np.uint8)
    if kind == "ones": return np.ones(n,dtype=np.uint8)
    if kind == "zeros": return np.zeros(n,dtype=np.uint8)
    if kind == "bursts": return ((np.arange(n)//32)%2).astype(np.uint8)
    if kind == "text": return np.unpackbits(np.frombuffer(text.encode("utf-8"),dtype=np.uint8))
    if kind == "pcm8":
        if samples is None:
            t = np.arange(n)/8000
            samples = .6*np.sin(2*np.pi*440*t)+.25*np.sin(2*np.pi*880*t)
        quantized = np.rint((np.clip(samples,-1,1)+1)*127.5).astype(np.uint8)
        return np.unpackbits(quantized)
    raise ValueError("Unknown payload kind")


def pcm8_decode(bits):
    if len(bits)%8: raise ValueError("Whole PCM bytes required")
    return np.packbits(binary(bits)).astype(float)/127.5 - 1


def frame_bytes(data: bytes):
    """Length (16-bit big endian), payload, CRC32 over length + payload."""
    if len(data)>65535: raise ValueError("Payload too long")
    body=len(data).to_bytes(2,"big")+data
    return np.unpackbits(np.frombuffer(body+zlib.crc32(body).to_bytes(4,"big"),dtype=np.uint8))


def unframe_bits(bits):
    a=binary(bits)
    if len(a)%8 or len(a)<48: return b"",False
    raw=np.packbits(a).tobytes(); n=int.from_bytes(raw[:2],"big")
    ok=len(raw)==n+6 and zlib.crc32(raw[:-4])==int.from_bytes(raw[-4:],"big")
    return raw[2:-4],bool(ok)


def repetition_encode(bits, repeats=3):
    if repeats<1 or repeats%2!=1: raise ValueError("Odd positive repeat count required")
    return np.repeat(binary(bits), repeats)


def repetition_decode(soft, repeats=3):
    if repeats<1 or repeats%2!=1 or len(soft)%repeats: raise ValueError("Invalid repetition block")
    return (np.asarray(soft).reshape(-1,repeats).real.sum(axis=1)<0).astype(np.uint8)


def interference(n, js_db, signal_power, rng, kind="tone", frequency=.037, sweep=.1, duty=.1):
    """frequency/sweep in cycles/sample; J/S is mean power over the full record."""
    if n<1 or signal_power<0 or not 0<duty<=1: raise ValueError("Invalid interference settings")
    t=np.arange(n); phase=rng.uniform(-np.pi,np.pi)
    if kind == "tone": j=np.exp(1j*(2*np.pi*frequency*t+phase))
    elif kind == "chirp": j=np.exp(1j*(2*np.pi*(frequency*t+.5*sweep*t*t/n)+phase))
    elif kind == "burst":
        j=(rng.standard_normal(n)+1j*rng.standard_normal(n))/np.sqrt(2)
        j*=((t%1000)<max(1,round(duty*1000)))
    elif kind == "noise": j=(rng.standard_normal(n)+1j*rng.standard_normal(n))/np.sqrt(2)
    else: raise ValueError("Unknown jammer")
    return j*np.sqrt(signal_power*10**(js_db/10)/np.mean(abs(j)**2))


def oscillator(x, frequency=0., phase=0., linewidth=0., rng=None):
    """CFO cycles/sample; Wiener phase noise variance increment=2*pi*linewidth."""
    p=phase+2*np.pi*frequency*np.arange(len(x))
    if linewidth<0: raise ValueError("Negative phase linewidth")
    if linewidth:
        if rng is None: raise ValueError("Phase noise requires rng")
        p=p+np.cumsum(rng.normal(0,np.sqrt(2*np.pi*linewidth),len(x)))
    return np.asarray(x)*np.exp(1j*p)


def fractional_delay(x, delay):
    """Linear interpolation with zero boundaries; deliberately not bandlimited."""
    t=np.arange(len(x)); y=np.asarray(x)
    return np.interp(t-delay,t,y.real,left=0,right=0)+1j*np.interp(t-delay,t,y.imag,left=0,right=0)


def quantize(x, bits=8, full_scale=1.):
    if bits<2 or int(bits)!=bits or full_scale<=0: raise ValueError("Invalid ADC settings")
    levels=2**bits-1
    def q(v): return np.rint((np.clip(v,-full_scale,full_scale)+full_scale)/(2*full_scale)*levels)/levels*(2*full_scale)-full_scale
    return q(np.real(x))+1j*q(np.imag(x))


def iq_imbalance(x, gain_db=0., phase_deg=0.):
    """I unchanged; Q branch amplitude and quadrature error applied explicitly."""
    g=10**(gain_db/20); p=np.deg2rad(phase_deg); x=np.asarray(x)
    return x.real-g*np.sin(p)*x.imag+1j*g*np.cos(p)*x.imag


def channel_impulse(delays=(0,3), gains=(1.,.5)):
    if len(delays)!=len(gains) or any(d<0 or int(d)!=d for d in delays): raise ValueError("Invalid paths")
    h=np.zeros(max(delays)+1,complex)
    for d,g in zip(delays,gains): h[d]+=g
    if np.linalg.norm(h)==0: raise ValueError("Zero channel")
    return h/np.linalg.norm(h)


def matched_channel(rx, h, output_length):
    """Known-channel matched filter (RAKE equivalent); no ISI equalization."""
    y=signal.fftconvolve(rx,np.conj(h[::-1]),mode="full")
    return y[len(h)-1:len(h)-1+output_length]/np.sum(abs(h)**2)


def acquire(rx, preamble, max_delay, cfo_grid=(0.,)):
    """Joint known-preamble delay/CFO grid search; no oracle timing used.

    Returns score normalized by template energy, not a lock probability.
    One preamble cannot distinguish offsets outside the searched interval.
    """
    r=np.asarray(rx); p=np.asarray(preamble); m=len(p)
    if max_delay<0 or len(r)<m+max_delay: raise ValueError("Insufficient acquisition window")
    best=None
    for f in cfo_grid:
        template=p*np.exp(2j*np.pi*f*np.arange(m))
        corr=signal.correlate(r[:m+max_delay],template,mode="valid",method="fft")
        delay=int(np.argmax(abs(corr))); value=corr[delay]
        candidate=dict(delay=delay,cfo=float(f),phase=float(np.angle(value)),score=float(abs(value)/np.vdot(p,p).real))
        if best is None or candidate['score']>best['score']: best=candidate
    return best


def spectrum(x, fs=1., nperseg=4096, fraction=.99):
    if not 0<fraction<1: raise ValueError("Power fraction must be in (0,1)")
    f,p=signal.welch(x,fs=fs,nperseg=min(nperseg,len(x)),return_onesided=False,detrend=False,scaling="density")
    order=np.argsort(f);f=f[order];p=p[order]; cumulative=np.cumsum(p)/np.sum(p)
    lo=int(np.searchsorted(cumulative,(1-fraction)/2));hi=min(len(f)-1,int(np.searchsorted(cumulative,1-(1-fraction)/2)))
    return f,p,float(f[hi]-f[lo])


def hardware_trace(bits, chips_per_bit=1000, sps=8, chip_rate=2e6):
    """Continuous PN, ideal square carrier, shared clock and ideal XOR recovery.

    Does not model acquisition gates, propagation delays, analogue LM1496 or filter.
    sps must be even so carrier edges are represented exactly.
    """
    if sps<2 or sps%2: raise ValueError("Even sps >=2 required")
    data=np.repeat(binary(bits),chips_per_bit*sps)
    pn=np.repeat(hardware_pn(len(bits)*chips_per_bit)[0],sps)
    carrier=(np.arange(len(data))%sps >= sps//2).astype(np.uint8)
    spread_data=data^pn; tx=spread_data^carrier; recovered=tx^pn^carrier
    return dict(time_s=np.arange(len(data))/(chip_rate*sps),data=data,pn=pn,carrier=carrier,spread=spread_data,tx=tx,recovered=recovered)


def rrc_taps(beta=.35, span=10, sps=4):
    """Unit-energy root-raised-cosine FIR; span in chips, sps samples/chip."""
    if not 0<beta<=1 or span<2 or span%2 or sps<2 or int(sps)!=sps:
        raise ValueError("Require 0<beta<=1, even span>=2, integer sps>=2")
    t=np.arange(-span*sps/2,span*sps/2+1)/sps;h=np.zeros(len(t))
    for i,v in enumerate(t):
        if abs(v)<1e-12:h[i]=1+beta*(4/np.pi-1)
        elif abs(abs(v)-1/(4*beta))<1e-12:
            h[i]=beta/np.sqrt(2)*((1+2/np.pi)*np.sin(np.pi/(4*beta))+(1-2/np.pi)*np.cos(np.pi/(4*beta)))
        else:h[i]=(np.sin(np.pi*v*(1-beta))+4*beta*v*np.cos(np.pi*v*(1+beta)))/(np.pi*v*(1-(4*beta*v)**2))
    return h/np.linalg.norm(h)


def pulse_shape(chips, taps, sps):
    return signal.upfirdn(taps,chips,up=sps)


def matched_pulse(rx, taps, sps, nchips):
    y=signal.convolve(rx,np.conj(np.asarray(taps)[::-1]),mode='full')
    return y[len(taps)-1:len(taps)-1+nchips*sps:sps]


def receive_burst(rx, preamble, payload_bit_count, code, max_delay, cfo_grid):
    """Acquire known preamble; correct grid CFO and measured phase; detect payload.

    Requires integer-sample timing and enough samples for the payload. CFO
    outside/on neither grid point leaves residual error; no tracking loop.
    """
    est=acquire(rx,preamble,max_delay,cfo_grid)
    start=est['delay'];n=len(preamble)+payload_bit_count*len(code)
    if len(rx)<start+n:raise ValueError('Truncated burst')
    r=np.asarray(rx)[start:start+n]
    corrected=r*np.exp(-1j*(est['phase']+2*np.pi*est['cfo']*np.arange(n)))
    bits,soft=despread(corrected[len(preamble):],code)
    return bits,soft,est
