# Model and measurement conventions

## Two different models

The **hardware logic model** uses a continuous 127-chip PN stream, a 2 MHz square carrier, and ideal XOR operations. With 1,000 chips per data-clock interval, an interval lasts 500 microseconds. That configuration models a 2 kHz data clock. The original board can instead select a direct 2 kHz square-wave test input: each high or low interval then lasts 250 microseconds, or 500 chips. These are different experiments.

The **communications model** resets a selected spreading code at each bit. Its default length is 127 chips and its reference chip rate is 2 Mchip/s, giving 15,748.03 bit/s when a physical rate is needed. This choice makes the baseline experiments easy to interpret; it does not reproduce the hardware's 1,000-chip clock interval. Both models use the same documented feedback recurrence.

## PN recurrence

Represent the active seven-stage state as an integer `s`, with QA in bit 6 and QG in bit 0. Before each update, the exported bit is QA. Compute:

```python
feedback = 1 ^ ((s >> 6) & 1) ^ (s & 1)
s = (s >> 1) | (feedback << 6)
```

This yields the report's initial states `0, 64, 32, 80, 40, 84, 42, 85`. The all-zero reset is allowed; the all-one state is a fixed point and is rejected. The period is 127. QA contains 63 ones and 64 zeros over the period. With bipolar values, periodic normalized autocorrelation is 1 at zero lag and −1/127 elsewhere. The schematic's serial feedback node gives a cyclically shifted version of this sequence; exporting QA does not assert pin-level timing equivalence.

A requested spreading length other than 127 truncates or repeats this sequence. It is **not** a new maximal-length sequence and must not be described as one. Code length, PN period and chips per data bit are separate quantities.

## Energy and AWGN

Bit mapping is `0 -> +1`, `1 -> -1`. For spreading length L and S samples per chip, the rectangular waveform has amplitude `1/sqrt(L*S)`, so its discrete energy per uncoded bit is exactly one. Samples represent an orthonormal discrete-time model, not calibrated voltage or watts at a specified impedance.

Complex AWGN has variance N0/2 in each quadrature, with `N0 = 10**(-EbN0_dB/10)`. The receiver integrates against the unit-energy spreading pulse. For ideal coherent BPSK:

\[
P_b = \tfrac12\operatorname{erfc}\!\left(\sqrt{E_b/N_0}\right).
\]

The unspread baseline uses an all-one pulse over the same L*S samples. Consequently bit rate, sampling rate, bit energy and noise normalization are matched. Spreading does not provide AWGN coding gain. The repetition-code experiment allocates energy 1/3 to each of three copies; it changes time/throughput and is an energy sanity check, not a claim of coding superiority.

## Interference cases

J/S is the mean injected interference power divided by mean desired signal power over the record. Burst duty is 10%; its average power is normalized after gating, so its instantaneous active power is higher. No transmit-power advantage is given to either receiver.

| Case | Frequency in cycles/sample | Interpretation at 2 Msamples/s |
|---|---|---|
| tone_inband | 0.001 | 2 kHz, inside the narrow unspread main lobe |
| tone_outofband | 0.037 | 74 kHz, outside that main lobe, within the DSSS band |
| chirp | Linear sweep −0.01 to +0.01 across each record/batch | −20 kHz to +20 kHz |
| burst | Complex white noise, 100 samples active per 1,000 | Wideband impulsive interference |

Python's BER runner processes 2,000-bit batches and draws a new interference phase per batch. MATLAB uses a single record per point; chirp duration and random streams therefore differ. Neither result is an adversarial-jammer bound. A short deterministic PN code has spectral structure, so a single tone is not sufficient to estimate a general processing gain.

## Synchronization

The hardware logic trace assumes code lock. The original hardware acquisition circuit is not gate-delay simulated in Python.

The advanced receiver uses a known random 16-bit preamble spread over 127 chips/bit. It searches integer delays 0–64 samples and CFO candidates −0.0002, 0 and +0.0002 cycles/sample using complex correlation, then estimates phase. At a 2 MHz sample rate this CFO grid is −400, 0 and +400 Hz. The acquisition experiment reports joint delay/CFO success across repeated trials. The burst example corrects those estimates and checks a CRC-protected text payload.

The CFO trials are **on-grid**, the frame length is known, and there is no unknown-signal detector or false-alarm threshold. There is no fractional timing recovery, sample-clock tracking loop, Costas loop or Doppler tracker. Sensitivity plots with uncorrected CFO/phase explicitly use an uncompensated receiver.

## Multipath, fading and front-end models

Multipath impulse responses have unit total energy. The matched-channel combiner uses exact known taps and delays, so it is an idealized RAKE-equivalent bound without channel-estimation error. It does not remove all intersymbol interference. Rayleigh fading is independent per symbol with perfect complex receiver CSI; there is no correlated Doppler model.

Fractional delay uses linear interpolation and zero-filled boundaries. This approximation attenuates high-frequency samples; it is not a bandlimited fractional-delay filter. IQ imbalance is applied after rotating the BPSK signal by 45 degrees so the Q path is exercised; nominal rotation is undone afterward. ADC quantization clips each quadrature independently to ±0.5 before uniform quantization. Noise is added before quantization. Phase noise is a discrete Wiener phase process, not a measured oscillator spectrum.

RRC pulses have unit tap energy, 10-chip span and four samples per chip. Matched filtering compensates both filter group delays. Finite pulse truncation leaves residual ISI. 99% occupied bandwidth uses equal-tail cumulative Welch PSD power; it is not the report's manually estimated ~80% bandwidth.

## Statistics and reproducibility

BER CSVs include counts and 95% Wilson score intervals. Intervals describe finite-sample binomial uncertainty; correlated interference can violate independence and make those intervals optimistic. Frame results are CRC failure fractions, not an undetected-error guarantee. Raw RMS EVM compares complex decisions directly with ideal ±1 symbols, without fitted gain or phase correction.

The full Python run records the main seed and environment in `results/run_metadata.json`. The separate pulse-shaping example uses seed 99; the framed-burst example uses seed 7. Shared golden samples test exact deterministic receiver agreement across languages; equal numeric RNG seeds do not yield equal MATLAB and NumPy noise streams.
