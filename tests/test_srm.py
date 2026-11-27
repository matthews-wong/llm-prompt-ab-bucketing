import unittest

from abtest.srm import check_srm

EVEN = {"control": 1, "concise": 1}


class SrmTest(unittest.TestCase):
    def test_matches_known_chi_square_tail(self):
        # df=1 reference: chi2 = 3.7636 gives p = erfc(sqrt(chi2 / 2)) = 0.0524.
        result = check_srm({"control": 5000 + 97, "concise": 5000 - 97}, EVEN)
        self.assertAlmostEqual(result.chi_square, 3.7636, places=3)
        self.assertAlmostEqual(result.p_value, 0.0524, places=3)

    def test_df_two_closed_form(self):
        # For df=2 the survival function is exp(-x/2).
        result = check_srm({"a": 120, "b": 100, "c": 80}, {"a": 1, "b": 1, "c": 1})
        self.assertAlmostEqual(result.p_value, 0.0183156, places=5)

    def test_balanced_split_passes(self):
        result = check_srm({"control": 5010, "concise": 4990}, EVEN)
        self.assertFalse(result.mismatch)

    def test_skewed_split_is_flagged(self):
        result = check_srm({"control": 5400, "concise": 4600}, EVEN)
        self.assertTrue(result.mismatch)

    def test_unequal_weights_are_respected(self):
        result = check_srm({"control": 7500, "concise": 2500}, {"control": 3, "concise": 1})
        self.assertEqual(result.chi_square, 0.0)
        self.assertEqual(result.p_value, 1.0)

    def test_unknown_variant_is_reported(self):
        with self.assertRaisesRegex(ValueError, "'verbose'"):
            check_srm({"control": 10, "verbose": 5}, EVEN)

    def test_zero_total_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "total count"):
            check_srm({}, EVEN)


if __name__ == "__main__":
    unittest.main()
