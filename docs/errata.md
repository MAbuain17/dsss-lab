# Technical corrections to the original report

The historical PDF is preserved. These corrections govern the README and new simulations.

| Report issue | Correct interpretation |
|---|---|
| “Measured ~30 dB SNR improvement” | 30 dB is a rate-ratio calculation assuming 2 Mchip/s and 2 kbit/s. No direct input/output SNR or jammer-rejection measurement establishes that gain. |
| 2 kHz waveform equated with 2 kbit/s | The 2 kHz data-clock path and direct 2 kHz square-wave test are different. Alternating NRZ levels with a 2 kHz fundamental have 4,000 bit intervals/s. The board's Morse data does not continuously carry 2,000 random bits/s. |
| 28.41 dB from 10.7 MHz / 15.4 kHz | The arithmetic is correct, but a manual bandwidth ratio with approximate 80% power criteria is not a measured SNR improvement. Square-carrier harmonics also affect the estimate. |
| 74164 described as seven-stage IC | It is an eight-stage IC using seven active feedback stages in this circuit. |
| All-zero state described as forbidden | Applies to conventional XOR feedback, not this inverted-feedback arrangement. Here all-one is the excluded fixed point. |
| “Near-instantaneous” or a few-cycle lock | The observation did not resolve acquisition time. A high clock rate alone does not prove a short search time. |
| Synchronization LED treated as continuous lock proof | Data can change the comparison output while the latch retains the clock state. The indicator alone cannot establish timing accuracy or error-free reception. |
| DSSS described as encryption/security | The publicly specified short PN code is not encryption. No confidentiality result is demonstrated. |
| Wireless/radio-link implications | The tested connection was a wire with a shared reference. Antennas, RF front end and independent receiver recovery were not demonstrated. |
| PCB evolution presented as robust implementation | The KiCad files contain no routed tracks and no schematic wires. They remain a placement study. |
| Bill of materials arithmetic | For example, two CD4017s at 5 LYD cannot total 15 LYD, while the schematic describes three divider stages. Component counts need reconciliation against the actual Multisim netlist. |
| Schematic source attribution incomplete | Credit Kesteloot's December 1986 QEX article directly. His article is the source of the underlying design and method. |

For the 1,000-chip clock interval, a nominal spreading factor is 1,000 (30 dB). For a 500-chip half-cycle in a direct square-wave test, the corresponding interval ratio is 500 (~27 dB). Neither number is a measured end-to-end interference rejection value. Neither is the PN period, which remains 127 chips.
