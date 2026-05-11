"""Smoke tests to verify project setup."""

import os
from pathlib import Path


def test_qiskit_import():
    """Verify qiskit is installed and importable."""
    import qiskit
    assert hasattr(qiskit, "__version__")


def test_qiskit_aer_import():
    """Verify qiskit-aer simulator is available."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    assert sim is not None


def test_liboqs_import():
    """Verify liboqs-python is installed and ML-KEM-768 is available."""
    import oqs
    kem = oqs.KeyEncapsulation("ML-KEM-768")
    assert kem is not None


def test_env_token_exists():
    """Verify .env file has a real IBM Quantum token (not the placeholder)."""
    from dotenv import load_dotenv

    env_path = Path(__file__).resolve().parent.parent / ".env"
    assert env_path.exists(), f".env file not found at {env_path}"

    load_dotenv(env_path)
    token = os.environ.get("IBM_QUANTUM_TOKEN", "")

    # Token must exist and not be the placeholder
    assert token, "IBM_QUANTUM_TOKEN is empty"
    assert token != "paste_your_token_here", (
        "IBM_QUANTUM_TOKEN is still the placeholder — "
        "update .env with your real token from quantum.ibm.com/account"
    )
    # Sanity: token should be non-trivial length (real tokens are ~40+ chars)
    assert len(token) > 10, "IBM_QUANTUM_TOKEN looks too short to be valid"
