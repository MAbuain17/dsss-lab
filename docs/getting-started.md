# Run the project on your computer

## Windows with VS Code

Install Python if `py --version` does not work. Extract or clone the repository, open its folder in VS Code, and open **Terminal > New Terminal**. In PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe examples\burst_link.py
.\.venv\Scripts\python.exe -m dsss_lab.experiments --quick
.\.venv\Scripts\python.exe examples\pulse_shaping.py
```

Using the environment's Python directly avoids changing PowerShell's execution policy. After the quick run works, omit `--quick` for the full experiment. Open `results/figures/awgn.png` and `results/figures/interference.png`, then inspect their CSV files.

If dependencies are already installed and you want to run without packaging:

```powershell
$env:PYTHONPATH = "$PWD\src"
py -m unittest discover -s tests -v
py examples\burst_link.py
```

## MATLAB

Set MATLAB's current folder to the repository root, then run:

```matlab
addpath('matlab');
test_dsss;
run_experiments('results/matlab',12000);
advanced_demo('results/matlab');
plot_results('results/matlab');
```

The first command exposes the functions, the second checks them, and the next two run experiments. `plot_results` creates a MATLAB BER figure. The MATLAB implementation uses base functions rather than Communications Toolbox blocks.

To run the same tests with GNU Octave:

```bash
octave --no-gui --quiet --eval "addpath('matlab'); test_dsss; run_experiments('results/matlab',4000); advanced_demo('results/matlab');"
```

Octave and native MATLAB runs are pending at the initial release. Treat the supplied `.m` files as ready for that validation, not as already executed results.

## Change one thing at a time

Start by changing the input string in `examples/burst_link.py`. Then change delay, phase or CFO while keeping it inside the search grid. Next try an off-grid CFO to see why residual frequency error matters. For interference, keep the in-band and out-of-band cases together and compare them before drawing conclusions about DSSS.

The main model resets PN code each bit. `hardware_trace` instead preserves continuous PN across intervals. The distinction is deliberate; see the methodology before comparing their rates or spectra.
