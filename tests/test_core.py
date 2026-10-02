import unittest

from tutorial.core import Tutorial


def steps():
    return [{"id": "a", "requires": [], "skip_flag": False},
            {"id": "b", "requires": ["a"], "skip_flag": False}]


class BasicTest(unittest.TestCase):
    def test_unknown_step_fails(self):
        self.assertFalse(Tutorial(steps()).activate("ghost", "r1"))

    def test_first_step_can_be_activated(self):
        tut = Tutorial(steps())
        self.assertTrue(tut.activate("a", "r1"))
        self.assertTrue(tut.is_done("a"))

    def test_progress_starts_empty(self):
        self.assertEqual(Tutorial(steps()).progress(), [])

    def test_pending_starts_empty(self):
        self.assertEqual(Tutorial(steps()).pending_list(), [])

    def test_scanned_starts_at_zero(self):
        self.assertEqual(Tutorial(steps()).scanned_count(), 0)


if __name__ == "__main__":
    unittest.main()
