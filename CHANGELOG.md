# Changelog

## 0.1.1 — publication and CI maintenance

- Published the complete project repository with source code, evidence, datasets and generated figures.
- Passed the Python and GNU Octave jobs in GitHub Actions and retained both result artifacts.
- Passed the native MathWorks MATLAB workflow and retained its generated result artifact.
- Updated GitHub-maintained actions to Node.js 24-compatible major versions.
- Scoped automatic native MATLAB runs to relevant implementation, vector and workflow changes.

## 0.1.0 — initial software extension

- Added Python DSSS primitives and MATLAB counterparts with shared deterministic vectors.
- Added AWGN, interference, payload, CRC, acquisition, multipath, fading, near-far, front-end impairment and pulse-shaping studies.
- Added a framed burst receiver that acquires integer delay and grid CFO and corrects phase before decoding.
- Verified the report's inverted-feedback PN recurrence and documented rate/gain corrections.
- Preserved selected individual hardware evidence and source files with QEX attribution.
- Audited historical KiCad files as unrouted; documented the prerequisites for a new board.
- Prepared automated Python/Octave checks and a manual native MATLAB workflow.
