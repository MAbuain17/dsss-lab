# CV wording and interview preparation

## Hardware-focused CV bullet

Implemented and tested a 2 MHz DSSS-BPSK laboratory link based on a published QEX design, using Multisim, discrete logic, PN-code synchronization and balanced demodulation; validated spreading and data recovery with oscilloscope and spectrum-analyzer measurements.

## Software-extension CV bullet

Extended the hardware study into a Python/MATLAB DSSS simulation suite covering BER, interference, synchronization, multipath and receiver impairments; validated 17 Python tests plus native MATLAB and GNU Octave execution through GitHub Actions, with reproducible datasets and plots.

Repository: https://github.com/MAbuain17/dsss-lab

The current evidence supports Python, GNU Octave and native MathWorks MATLAB validation. Keep physical-hardware claims separate from these software results.

## Explain the engineering decisions

**Why DSSS?** It provides a clear way to study the relationship between bandwidth, correlation and interference. The useful comparison fixes information-bit energy and rate; otherwise apparent gain can come from extra transmit energy.

**What did you personally contribute?** The university work was an individual implementation of Kesteloot's published circuit: circuit simulation, physical assembly, measurement and documentation. The later software extension was developed with AI assistance. The base circuit and DSSS method are not claimed as original inventions.

**Why does the report's 30 dB need qualification?** It comes from a rate ratio under a particular data-rate assumption. It was not measured as end-to-end SNR improvement. White-noise BER at fixed Eb/N0 remains the coherent BPSK result.

**Why test out-of-band interference?** It reveals a real limitation: widening the receiver's admitted spectrum can expose it to interference that a narrow unspread receiver largely rejects. Processing gain is conditional on the interference and receiver model.

**What is incomplete?** Rerunning Multisim, a fully connected/routed PCB, independent hardware timing recovery and new controlled hardware BER tests.
