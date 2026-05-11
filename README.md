# Bridging the Quantum Threat and Post-Quantum Defense

An empirical study of Shor's algorithm on real quantum hardware and ML-KEM-768 performance on classical hardware.

**BTech Project-I** — Demonstrates both sides of the quantum cryptography challenge:
1. **The Threat**: Shor's algorithm on IBM Quantum hardware factoring small numbers (N=15, N=21)
2. **The Defense**: ML-KEM-768 (NIST FIPS 203) benchmarks quantifying the cost of post-quantum migration

## Prerequisites

- **Python 3.12+** (tested on 3.14.3)
- **git**
- **Homebrew** (macOS) — for building `liboqs` from source
- **cmake** — `brew install cmake`
- **IBM Quantum account** — free at [quantum.ibm.com](https://quantum.ibm.com/)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/utkarshc-sudo/btech-pqc-shors.git
cd btech-pqc-shors
```

### 2. Set up IBM Quantum token

```bash
cp .env.example .env
# Open .env in your editor and replace paste_your_token_here with your IBM Quantum API token
# Get your token at: https://quantum.ibm.com/account
```

**Important**: `.env` is gitignored and will never be committed. Never share your token.

### 3. Build liboqs from source (required for ML-KEM)

The `liboqs-python` package requires the `liboqs` shared library. Homebrew's formula only installs the static library, so we build from source:

```bash
brew install liboqs cmake  # for headers and build tools

git clone --depth 1 --branch 0.15.0 https://github.com/open-quantum-safe/liboqs.git /tmp/liboqs-build
cd /tmp/liboqs-build
mkdir build && cd build
cmake -DBUILD_SHARED_LIBS=ON -DCMAKE_INSTALL_PREFIX=$HOME/.local ..
make -j$(sysctl -n hw.ncpu)
make install
cd -
rm -rf /tmp/liboqs-build
```

Verify the library exists:
```bash
ls ~/.local/lib/liboqs.dylib
```

### 4. Install Python dependencies

```bash
make install
```

This creates a virtual environment in `.venv/` and installs all pinned dependencies from `requirements.txt`.

### 5. Activate the environment

```bash
source .venv/bin/activate
```

### 6. Run the smoke test

```bash
make test
```

## Running the Experiments

### Shor's Algorithm (Simulator)

```bash
make shors-sim
```

Runs Shor's algorithm for N=15 on the Qiskit Aer simulator. Results are saved to `results/raw/`.

### Shor's Algorithm (IBM Quantum Hardware)

```bash
make shors-hw
```

**Warning**: This submits a job to real quantum hardware and consumes your monthly quota. You will be prompted for confirmation before submission.

### ML-KEM Benchmarks

```bash
make mlkem-bench
```

Benchmarks ML-KEM-512/768/1024 key generation, encapsulation, and decapsulation alongside X25519 for comparison. Results are saved to `results/raw/`.

### Generate Figures

```bash
make figures
```

Regenerates all plots from raw CSV data into `results/figures/`.

## Project Structure

```
btech-pqc-shors/
├── README.md                 # This file
├── PROJECT_PLAN.md           # 12-week plan and milestones
├── CONCEPTS.md               # Plain-English concept explainer
├── requirements.txt          # Pinned Python dependencies
├── Makefile                  # Build and run targets
├── src/
│   ├── shors/                # Shor's algorithm implementation
│   │   ├── circuit.py        # Quantum circuit construction
│   │   ├── classical.py      # Classical post-processing (GCD, continued fractions)
│   │   ├── run_simulator.py  # Run on Aer simulator
│   │   └── run_hardware.py   # Run on IBM Quantum hardware
│   ├── mlkem/                # ML-KEM benchmarks
│   │   ├── benchmark.py      # ML-KEM-512/768/1024 benchmark harness
│   │   └── compare_x25519.py # X25519 baseline comparison
│   └── analysis/             # Data analysis and visualization
│       ├── plots.py          # Figure generation
│       └── stats.py          # Statistical analysis
├── notebooks/
│   ├── 01_shors_threat.ipynb       # Interactive Shor's analysis
│   └── 02_mlkem_defense.ipynb      # Interactive ML-KEM analysis
├── tests/                    # pytest test suite
├── results/
│   ├── raw/                  # Raw benchmark data (gitignored)
│   └── figures/              # Generated plots (committed)
└── report/                   # Report markdown sources
```

## Troubleshooting

### `liboqs` import error: "No oqs shared libraries found"

The `DYLD_LIBRARY_PATH` environment variable must include the path to `liboqs.dylib`. The Makefile sets this automatically. If running Python directly:

```bash
export DYLD_LIBRARY_PATH=$HOME/.local/lib:$DYLD_LIBRARY_PATH
```

### IBM Quantum token errors

- Ensure `.env` exists and contains a valid `IBM_QUANTUM_TOKEN=...`
- Get your token at [quantum.ibm.com/account](https://quantum.ibm.com/account)
- The token should be a ~40-character alphanumeric string

### Python version compatibility

This project is developed on Python 3.14.3. Python 3.12+ should work. If you encounter build issues, try Python 3.12 via `pyenv`:

```bash
pyenv install 3.12.8
pyenv local 3.12.8
```

### Smoke test failures

Run `make test` to check your setup. Expected first-run behavior:
- `test_qiskit_import` — should pass
- `test_qiskit_aer_import` — should pass
- `test_liboqs_import` — should pass (if liboqs built correctly)
- `test_env_token_exists` — fails until you update `.env` with your real token

## License

Academic project — not for redistribution.
