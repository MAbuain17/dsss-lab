# What was actually implemented?

| Capability | Original hardware evidence | Python | MATLAB / Octave |
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
| BER versus Eb/N0 | No evidence | Executed | Executed |
| Tone, chirp and burst interference | No controlled measurements | Executed | Executed |
| Joint preamble delay/CFO estimation | No evidence | Executed | Executed |
| Multipath / ideal known-channel combining | No evidence | Executed | Executed |
| Rayleigh fading / perfect CSI | No evidence | Executed | Executed |
| Quantization, timing, IQ, phase impairments | No measured sweeps | Executed | Executed |
| RRC shaping and matched filtering | No evidence | Executed | Executed |
| Two-user near-far study | No evidence | Executed | Executed |
| Repetition-code energy check | No evidence | Executed | Executed |
| Routed PCB, ERC, DRC, board bring-up | Not completed | Not applicable | Not applicable |

The MATLAB-compatible implementation passed both GNU Octave and native MathWorks MATLAB workflows. These remain software simulations; the table does not convert unmeasured hardware capabilities into physical evidence.
