VENV := .venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest

# liboqs shared library path (built from source)
export DYLD_LIBRARY_PATH := $(HOME)/.local/lib:$(DYLD_LIBRARY_PATH)

.PHONY: install shors-sim shors-hw mlkem-bench test clean figures

install: $(VENV)/bin/activate
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo ""
	@echo "=== Setup complete ==="
	@echo "Activate with: source $(VENV)/bin/activate"
	@echo "Make sure liboqs shared library is at ~/.local/lib/liboqs.dylib"
	@echo "See README.md for liboqs build instructions if needed."

$(VENV)/bin/activate:
	python3 -m venv $(VENV)

shors-sim:
	$(PYTHON) -m src.shors.run_simulator

shors-hw:
	@echo "=== WARNING: This submits a job to IBM Quantum hardware ==="
	@echo "This consumes your monthly quota."
	@read -p "Continue? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	$(PYTHON) -m src.shors.run_hardware

mlkem-bench:
	$(PYTHON) -m src.mlkem.benchmark

test:
	$(PYTEST) tests/ -v

clean:
	rm -rf results/figures/*.png results/figures/*.pdf
	rm -rf __pycache__ src/**/__pycache__ tests/__pycache__
	rm -rf .ipynb_checkpoints notebooks/.ipynb_checkpoints

figures:
	$(PYTHON) -m src.analysis.plots
