# What was actually implemented?

| Capability | Original hardware evidence | Python | MATLAB code |
|---|---|---|---|
| 4 MHz reference / 2 MHz carrier | Report and lab waveforms | Ideal 2 MHz square-carrier trace | Same ideal trace |
| Seven-stage XNOR PN | Report sequence and scope observations | Exact recurrence; automated tests | Same recurrence; golden tests |
| Continuous PN across data intervals | Circuit design | Hardware mode | Hardware mode |
| XOR spreading and square-carrier modulation | Report and Multisim screenshots | Ideal logic model | Ideal logic model |
| Comparator / clock-switch acquisition | Reported code alignment; no measured time | Not gate-level simulated | Not gate-level simulated |
| LM/MC1496 analogue demodulator | Circuit and recovered-waveform evidence | Ideal despreading only | Ideal despreading only |
| 2 kHz test / Morse input | Report | Logic patterns; no physical Morse key | Logic patterns |
| Random data, framed text, CRC32 | No evidence | Implemented | Implemented |
| PCM audio samples | No evidence | Implemented | Implemented |
| BER versus Eb/N0 | No evidence | Executed | Runner provided |
| Tone, chirp and burst interference | No controlled measurements | Executed | Runner provided |
| Joint preamble delay/CFO estimation | No evidence | Executed | Implemented |
| Multipath / ideal known-channel combining | No evidence | Executed | Implemented |
| Rayleigh fading / perfect CSI | No evidence | Executed | Implemented |
| Quantization, timing, IQ, phase impairments | No measured sweeps | Executed | Implemented |
| RRC shaping and matched filtering | No evidence | Executed | Implemented |
| Two-user near-far study | No evidence | Executed | Implemented |
| Repetition-code energy check | No evidence | Executed | Implemented |
| Routed PCB, ERC, DRC, board bring-up | Not completed | Not applicable | Not applicable |

“MATLAB code” means implementation is supplied, not that native MATLAB execution has passed. The CI workflow and `matlab/test_dsss.m` define the pending execution gate.
