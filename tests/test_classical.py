"""Tests for Shor's classical post-processing."""

import pytest
from src.shors.classical import (
    classical_order,
    measurement_to_phase,
    phase_to_period,
    find_factors_from_period,
)


class TestClassicalOrder:
    def test_order_7_mod_15(self):
        assert classical_order(7, 15) == 4

    def test_order_11_mod_15(self):
        assert classical_order(11, 15) == 2

    def test_order_2_mod_15(self):
        assert classical_order(2, 15) == 4

    def test_order_13_mod_15(self):
        assert classical_order(13, 15) == 4

    def test_order_2_mod_21(self):
        assert classical_order(2, 21) == 6

    def test_not_coprime(self):
        assert classical_order(3, 15) is None

    def test_not_coprime_21(self):
        assert classical_order(7, 21) is None


class TestMeasurementToPhase:
    def test_zero(self):
        assert measurement_to_phase(0, 8) == 0.0

    def test_half(self):
        assert measurement_to_phase(128, 8) == 0.5

    def test_quarter(self):
        assert measurement_to_phase(64, 8) == 0.25


class TestPhaseToPeriod:
    def test_phase_zero(self):
        assert phase_to_period(0.0, 15) == 0

    def test_phase_quarter_gives_r4(self):
        assert phase_to_period(0.25, 15) == 4

    def test_phase_half_gives_r2(self):
        assert phase_to_period(0.5, 15) == 2

    def test_phase_three_quarters_gives_r4(self):
        assert phase_to_period(0.75, 15) == 4

    def test_approximate_phase(self):
        # 1/6 ≈ 0.1667, should recover r=6
        r = phase_to_period(0.1667, 21)
        assert r == 6 or r == 3  # continued fractions may give divisor


class TestFindFactors:
    def test_n15_r4_a7(self):
        factors = find_factors_from_period(7, 4, 15)
        assert factors == (3, 5)

    def test_n15_r2_a11(self):
        factors = find_factors_from_period(11, 2, 15)
        assert factors == (3, 5)

    def test_n21_r6_a2(self):
        factors = find_factors_from_period(2, 6, 21)
        assert factors == (3, 7)

    def test_odd_period_fails(self):
        assert find_factors_from_period(7, 3, 15) is None

    def test_zero_period_fails(self):
        assert find_factors_from_period(7, 0, 15) is None

    def test_trivial_factor_fails(self):
        # a^(r/2) ≡ -1 (mod N) → trivial case, no factors
        # 4^(2/2) mod 15 = 4, gcd(5,15)=5, gcd(3,15)=3 → actually works
        # Use a=14, r=2: 14^1 mod 15 = 14 = -1 mod 15 → trivial
        assert find_factors_from_period(14, 2, 15) is None
