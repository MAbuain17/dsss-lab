# PCB audit and proposed redesign

**Status: no fabrication release.** The supplied KiCad board is a placement study. A read-only structural audit found 169 footprints, 532 pads, 112 pads assigned a nonzero net, 26 declared nets, two zones, zero track segments, and zero vias. The supplied schematic contains 10 placed symbols and zero wires. These counts are reproduced by `python tools/audit_kicad.py` and recorded in `structural-audit.json`.

KiCad is not installed in the current execution environment. No native ERC, DRC, 3D validation or manufacturing export has been run. A polished-looking rendering would not change that electrical status.

## Electrical issues to resolve before layout

| Area | Required work | Acceptance evidence |
|---|---|---|
| Source of truth | Export the as-built Multisim netlist and compare it with the report and QEX schematic | Pin-by-pin reviewed netlist and reconciled BOM |
| Logic families | Audit LS outputs into HC and 4000-series CMOS, including the comparator | Worst-case VOH/VOL versus VIH/VIL and fanout worksheet; validated substitutions |
| PN generator | Confirm QA/QG taps, inversion, reset, unused eighth output and feedback pin assignment | 127-state capture and reset test |
| Clock doubler | Check RC timing, pulse widths, hysteresis and frequency over supply/tolerance | Minimum high/low pulse margins for the selected receiving IC |
| Clock switching | Check CD4066 pulse integrity and avoid runt pulses while switching 4/2 MHz | Clock capture through acquisition and repeated resets |
| Comparator/latch | Confirm unused comparator input pair, enable pin, polarity and startup state | Deliberately varied initial code phases and verified lock |
| Demodulator | Validate exact MC/LM1496 manufacturer pinout, bias, input attenuation and load | DC operating points, gain and clipping measurements |
| Power | Separate labelled +5 V logic and +12 V analogue inputs with common reference | Current limits, local decoupling, startup/reset behaviour |
| Output conditioning | Design/verify low-pass filtering and logic threshold recovery | Recovered waveform, duty distortion and BER under a defined test |
| Testability | Add labelled probes for reference, carrier, TX PN, RX PN, spread data, lock and recovered data | Accessible ground-return pairs and test-point map |

The 74HC688 is not automatically a guaranteed replacement for an LS-compatible comparator. Determine input margins using the exact ordered parts' data sheets; an HCT-family implementation may be appropriate, but no substitution is approved by this document. The original 74LS04 stages and external feedback network also need actual pulse/hysteresis verification rather than assuming every inverter is internally Schmitt-triggered.

## Proposed physical organization

Use one board with clearly separated reference/divider, transmitter, acquisition and demodulator regions. Put external connections at the edges and the analogue demodulator away from the clock doubler. Keep a continuous ground reference, short clock paths, local decoupling at every IC, mounting holes, legible pin-one marks and measurement points with adjacent grounds. Footprints must match the verified BOM, including the actual demodulator package.

A two-layer board is a candidate, not an established requirement. Stack-up, trace widths, connector types, supply arrangement and mounting dimensions should follow the validated netlist and equipment interface. Do not autoroute the historical footprint placement: its schematic is incomplete and it contains unrelated/unconnected footprints.

## Release gates

1. Complete and review the schematic and BOM, including power and unused pins.
2. Run ERC with documented, justified exclusions; validate timing and analogue bias.
3. Place and route the board from that schematic; run DRC with zero unexplained violations and zero unrouted nets.
4. Inspect copper, return paths, clearances, drill sizes, silkscreen and 3D fit; independently compare netlist and board.
5. Generate fabrication files only after those checks, then build and measure a prototype before calling it hardware-validated.

This repository supplies the audit and test requirements. It does not supply a new connected PCB, Gerbers or a claimed manufacturing-ready design.
