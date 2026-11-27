import contextlib
import io
import unittest

from abtest.cli import parse_counts, run

CONFIG = "fixtures/experiment.json"


def invoke(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = run(list(argv))
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_assign_prints_one_line_per_user(self):
        code, out, _ = invoke("assign", "--config", CONFIG, "user-1", "user-2")
        self.assertEqual(code, 0)
        self.assertEqual(len(out.splitlines()), 2)
        self.assertTrue(out.startswith("user-1\t"))

    def test_srm_ok_exits_zero(self):
        code, out, _ = invoke("srm", "--config", CONFIG, "--counts", "control=5010", "concise=4990")
        self.assertEqual(code, 0)
        self.assertTrue(out.endswith("ok\n"))

    def test_srm_mismatch_exits_one(self):
        code, out, _ = invoke("srm", "--config", CONFIG, "--counts", "control=5400", "concise=4600")
        self.assertEqual(code, 1)
        self.assertIn("MISMATCH", out)

    def test_missing_config_names_the_path(self):
        code, _, err = invoke("assign", "--config", "nope.json", "u1")
        self.assertEqual(code, 2)
        self.assertIn("'nope.json'", err)

    def test_bad_count_is_reported(self):
        with self.assertRaisesRegex(ValueError, "'control5'"):
            parse_counts(["control5"])


if __name__ == "__main__":
    unittest.main()
