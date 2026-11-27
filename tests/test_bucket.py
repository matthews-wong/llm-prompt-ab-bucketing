import unittest
from collections import Counter

from abtest.bucket import Experiment, assign, unit_interval

EXPERIMENT = Experiment("tone", {"control": 1, "concise": 1})


class BucketTest(unittest.TestCase):
    def test_assignment_is_stable(self):
        self.assertEqual(assign(EXPERIMENT, "user-7"), assign(EXPERIMENT, "user-7"))

    def test_known_values_do_not_drift(self):
        # Guards the hash layout: changing it silently moves every user.
        self.assertAlmostEqual(unit_interval("tone", "user-1"), 0.7512, places=3)

    def test_experiments_bucket_independently(self):
        self.assertNotEqual(unit_interval("tone", "u1"), unit_interval("length", "u1"))

    def test_split_follows_weights(self):
        experiment = Experiment("tone", {"control": 3, "concise": 1})
        counts = Counter(assign(experiment, f"u{i}") for i in range(20000))
        share = counts["control"] / 20000
        self.assertAlmostEqual(share, 0.75, delta=0.02)

    def test_rejects_non_positive_weight(self):
        with self.assertRaisesRegex(ValueError, "'concise'.*got 0"):
            Experiment("tone", {"control": 1, "concise": 0})

    def test_rejects_empty_user_id(self):
        with self.assertRaisesRegex(ValueError, "'tone'"):
            assign(EXPERIMENT, "")


if __name__ == "__main__":
    unittest.main()
