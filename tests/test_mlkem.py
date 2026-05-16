"""
Tests for ML-KEM and X25519 key exchange correctness.

Run from repo root:
    pytest tests/test_mlkem.py -v
"""

import oqs
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey


class TestMLKEM768Roundtrip:
    """Test that ML-KEM-768 keygen -> encaps -> decaps produces matching secrets."""

    def test_mlkem_768_roundtrip(self):
        algorithm = "ML-KEM-768"

        # Key generation
        kem_keygen = oqs.KeyEncapsulation(algorithm)
        public_key = kem_keygen.generate_keypair()
        secret_key = kem_keygen.export_secret_key()

        assert public_key is not None
        assert len(public_key) > 0
        assert len(secret_key) > 0

        # Encapsulation (by a second party using the public key)
        kem_encaps = oqs.KeyEncapsulation(algorithm)
        ciphertext, shared_secret_enc = kem_encaps.encap_secret(public_key)

        assert ciphertext is not None
        assert shared_secret_enc is not None
        assert len(ciphertext) > 0
        assert len(shared_secret_enc) > 0

        # Decapsulation (by the key owner using their secret key)
        kem_decaps = oqs.KeyEncapsulation(algorithm, secret_key=secret_key)
        shared_secret_dec = kem_decaps.decap_secret(ciphertext)

        assert shared_secret_dec is not None
        assert len(shared_secret_dec) > 0

        # The shared secrets must match
        assert shared_secret_enc == shared_secret_dec, (
            "Shared secrets from encapsulation and decapsulation do not match"
        )


class TestMLKEMAllVariants:
    """Test all ML-KEM parameter sets for correct roundtrip behavior."""

    def test_mlkem_all_variants(self):
        algorithms = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]

        for algorithm in algorithms:
            # Keygen
            kem = oqs.KeyEncapsulation(algorithm)
            public_key = kem.generate_keypair()
            secret_key = kem.export_secret_key()

            # Encapsulate
            kem_enc = oqs.KeyEncapsulation(algorithm)
            ciphertext, shared_secret_enc = kem_enc.encap_secret(public_key)

            # Decapsulate
            kem_dec = oqs.KeyEncapsulation(algorithm, secret_key=secret_key)
            shared_secret_dec = kem_dec.decap_secret(ciphertext)

            assert shared_secret_enc == shared_secret_dec, (
                f"{algorithm}: shared secrets do not match"
            )

            # Shared secret should be 32 bytes for all ML-KEM variants
            assert len(shared_secret_enc) == 32, (
                f"{algorithm}: expected 32-byte shared secret, got {len(shared_secret_enc)}"
            )


class TestX25519Exchange:
    """Test that X25519 ECDH key exchange produces matching shared secrets."""

    def test_x25519_exchange(self):
        # Alice generates her keypair
        alice_private = X25519PrivateKey.generate()
        alice_public = alice_private.public_key()

        # Bob generates his keypair
        bob_private = X25519PrivateKey.generate()
        bob_public = bob_private.public_key()

        # Both derive the same shared secret
        shared_secret_alice = alice_private.exchange(bob_public)
        shared_secret_bob = bob_private.exchange(alice_public)

        assert shared_secret_alice == shared_secret_bob, (
            "X25519: Alice and Bob derived different shared secrets"
        )

        # X25519 shared secret is always 32 bytes
        assert len(shared_secret_alice) == 32, (
            f"X25519: expected 32-byte shared secret, got {len(shared_secret_alice)}"
        )


class TestMLKEMKeySizes:
    """Verify that ML-KEM key and ciphertext sizes match the specification."""

    # Expected sizes from NIST FIPS 203 (ML-KEM standard)
    EXPECTED_SIZES = {
        "ML-KEM-512": {
            "public_key_bytes": 800,
            "secret_key_bytes": 1632,
            "ciphertext_bytes": 768,
        },
        "ML-KEM-768": {
            "public_key_bytes": 1184,
            "secret_key_bytes": 2400,
            "ciphertext_bytes": 1088,
        },
        "ML-KEM-1024": {
            "public_key_bytes": 1568,
            "secret_key_bytes": 3168,
            "ciphertext_bytes": 1568,
        },
    }

    def test_mlkem_key_sizes(self):
        for algorithm, expected in self.EXPECTED_SIZES.items():
            # Generate keys
            kem = oqs.KeyEncapsulation(algorithm)
            public_key = kem.generate_keypair()
            secret_key = kem.export_secret_key()

            # Encapsulate to get a ciphertext
            kem_enc = oqs.KeyEncapsulation(algorithm)
            ciphertext, shared_secret = kem_enc.encap_secret(public_key)

            # Verify sizes
            assert len(public_key) == expected["public_key_bytes"], (
                f"{algorithm}: public key size {len(public_key)} != "
                f"expected {expected['public_key_bytes']}"
            )
            assert len(secret_key) == expected["secret_key_bytes"], (
                f"{algorithm}: secret key size {len(secret_key)} != "
                f"expected {expected['secret_key_bytes']}"
            )
            assert len(ciphertext) == expected["ciphertext_bytes"], (
                f"{algorithm}: ciphertext size {len(ciphertext)} != "
                f"expected {expected['ciphertext_bytes']}"
            )
            # All ML-KEM variants produce 32-byte shared secrets
            assert len(shared_secret) == 32, (
                f"{algorithm}: shared secret size {len(shared_secret)} != 32"
            )
