"""
Comprehensive unit test suite for shared/validators.py
Tests ABHA IDs, mobile numbers, pincodes, SpO2, Temperature, password strength, and age ranges.
"""

import unittest
from shared.validators import (
    validate_abha_id,
    validate_indian_mobile,
    validate_pincode,
    validate_spo2,
    validate_temperature_f,
    validate_password_strength,
    validate_age,
)


class TestValidators(unittest.TestCase):

    def test_valid_abha_id(self):
        valid, msg = validate_abha_id("12-3456-7890-1234")
        self.assertTrue(valid)
        self.assertIsNone(msg)

    def test_invalid_abha_id_pattern(self):
        valid, msg = validate_abha_id("1234-5678-9012")
        self.assertFalse(valid)
        self.assertIn("Invalid ABHA ID format", msg)

    def test_invalid_abha_id_characters(self):
        valid, _ = validate_abha_id("12-abcd-7890-1234")
        self.assertFalse(valid)

    def test_valid_indian_mobile(self):
        valid, _ = validate_indian_mobile("9876543210")
        self.assertTrue(valid)
        valid, _ = validate_indian_mobile("+91 9876543210")
        self.assertTrue(valid)

    def test_invalid_indian_mobile(self):
        valid, msg = validate_indian_mobile("1234567890")
        self.assertFalse(valid)
        self.assertIn("Must be a 10-digit number", msg)

    def test_valid_pincode(self):
        valid, _ = validate_pincode("110001")
        self.assertTrue(valid)
        valid, _ = validate_pincode("751024")
        self.assertTrue(valid)

    def test_invalid_pincode(self):
        valid, _ = validate_pincode("010001")  # Cannot start with 0
        self.assertFalse(valid)
        valid, _ = validate_pincode("1100")
        self.assertFalse(valid)

    def test_valid_spo2(self):
        valid, err = validate_spo2(98.5)
        self.assertTrue(valid)
        self.assertIsNone(err)

    def test_invalid_spo2(self):
        valid, err = validate_spo2(105.0)
        self.assertFalse(valid)
        self.assertIn("outside the valid range", err)
        valid, err = validate_spo2(55.0)
        self.assertFalse(valid)

    def test_temperature_validation(self):
        valid, _ = validate_temperature_f(98.6)
        self.assertTrue(valid)
        valid, _ = validate_temperature_f(102.5)
        self.assertTrue(valid)
        valid, _ = validate_temperature_f(85.0)
        self.assertFalse(valid)

    def test_password_strength(self):
        strong, _ = validate_password_strength("Ayushman@2026Safe")
        self.assertTrue(strong)

        weak, msg = validate_password_strength("pass")
        self.assertFalse(weak)
        self.assertIsNotNone(msg)

    def test_age_validation(self):
        valid, _ = validate_age(25)
        self.assertTrue(valid)
        valid, _ = validate_age(-1)
        self.assertFalse(valid)
        valid, _ = validate_age(140)
        self.assertFalse(valid)


    def test_user_roles(self):
        from shared.types import UserRole
        self.assertEqual(UserRole.CLINICIAN, "CLINICIAN")
        self.assertEqual(UserRole.BENEFICIARY, "BENEFICIARY")


    def test_pulse_rate_validation(self):
        from shared.validators import validate_pulse_rate
        valid, _ = validate_pulse_rate(72)
        self.assertTrue(valid)
        valid, msg = validate_pulse_rate(20)
        self.assertFalse(valid)
        valid, msg = validate_pulse_rate(300)
        self.assertFalse(valid)
        valid, msg = validate_pulse_rate('abc')
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()

    def test_respiratory_rate_validation(self):
        from shared.validators import validate_respiratory_rate
        self.assertTrue(validate_respiratory_rate(16))
        self.assertTrue(validate_respiratory_rate(12.5))
        self.assertFalse(validate_respiratory_rate(4))
        self.assertFalse(validate_respiratory_rate(75))
        self.assertFalse(validate_respiratory_rate('16'))
        self.assertFalse(validate_respiratory_rate(True))

    def test_body_temperature_validation(self):
        from shared.validators import validate_body_temperature
        self.assertTrue(validate_body_temperature(37.0))
        self.assertTrue(validate_body_temperature(36.5))
        self.assertFalse(validate_body_temperature(29.0))
        self.assertFalse(validate_body_temperature(45.0))
        self.assertFalse(validate_body_temperature('37.0'))
        self.assertFalse(validate_body_temperature(True))
