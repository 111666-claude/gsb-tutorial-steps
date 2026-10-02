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




class RequireTest(unittest.TestCase):
    def test_blocked_before_requires_done(self):
        tut = Tutorial(steps())
        self.assertFalse(tut.activate("b", "r1"))
        self.assertEqual(tut.pending_list(), ["b"])
        self.assertFalse(tut.is_done("b"))
        self.assertNotIn("r1", tut.applied)

    def test_allowed_after_requires_done(self):
        tut = Tutorial(steps())
        self.assertTrue(tut.activate("a", "r1"))
        self.assertTrue(tut.activate("b", "r2"))
        self.assertTrue(tut.is_done("b"))
        self.assertEqual(tut.pending_list(), [])


class SkipTest(unittest.TestCase):
    def test_skip_flag_marks_skipped_not_done(self):
        skip_steps = [{"id": "a", "requires": [], "skip_flag": True},
                      {"id": "b", "requires": ["a"], "skip_flag": False}]
        tut = Tutorial(skip_steps)
        self.assertTrue(tut.activate("a", "r1"))
        self.assertEqual(tut.skipped_list(), ["a"])
        self.assertFalse(tut.is_done("a"))

    def test_skipped_satisfies_dependency(self):
        skip_steps = [{"id": "a", "requires": [], "skip_flag": True},
                      {"id": "b", "requires": ["a"], "skip_flag": False}]
        tut = Tutorial(skip_steps)
        tut.activate("a", "r1")
        self.assertTrue(tut.activate("b", "r2"))
        self.assertTrue(tut.is_done("b"))

    def test_skipped_step_cannot_trigger_again(self):
        skip_steps = [{"id": "a", "requires": [], "skip_flag": True}]
        tut = Tutorial(skip_steps)
        tut.activate("a", "r1")
        self.assertFalse(tut.activate("a", "r2"))
        self.assertEqual(tut.skipped_list(), ["a"])


class IdempotencyTest(unittest.TestCase):
    def test_same_req_id_applies_once(self):
        tut = Tutorial(steps())
        self.assertTrue(tut.activate("a", "same"))
        self.assertFalse(tut.activate("a", "same"))

    def test_repeated_req_does_not_change_state(self):
        other = [{"id": "a", "requires": [], "skip_flag": False},
                 {"id": "b", "requires": [], "skip_flag": False}]
        tut = Tutorial(other)
        tut.activate("a", "same")
        self.assertFalse(tut.activate("b", "same"))
        self.assertFalse(tut.is_done("b"))


class OrderTest(unittest.TestCase):
    def test_progress_follows_definition_order(self):
        free = [{"id": "a", "requires": [], "skip_flag": False},
                {"id": "b", "requires": [], "skip_flag": False}]
        tut = Tutorial(free)
        tut.activate("b", "r1")
        tut.activate("a", "r2")
        self.assertEqual(tut.progress(), ["a", "b"])

    def test_progress_includes_done_and_skipped_in_order(self):
        mixed = [{"id": "a", "requires": [], "skip_flag": True},
                 {"id": "b", "requires": [], "skip_flag": False},
                 {"id": "c", "requires": [], "skip_flag": False}]
        tut = Tutorial(mixed)
        tut.activate("c", "r1")
        tut.activate("a", "r2")
        self.assertEqual(tut.progress(), ["a", "c"])


class InvariantTest(unittest.TestCase):
    def test_done_and_skipped_disjoint(self):
        tut = Tutorial(steps())
        tut.activate("a", "r1")
        tut.activate("b", "r2")
        self.assertTrue(tut.done.isdisjoint(tut.skipped))

    def test_step_completes_at_most_once(self):
        tut = Tutorial(steps())
        self.assertTrue(tut.activate("a", "r1"))
        self.assertFalse(tut.activate("a", "r2"))
        self.assertEqual(tut.progress().count("a"), 1)


class ScanCostTest(unittest.TestCase):
    def test_scanned_count_not_linear_in_step_count(self):
        big = [{"id": "s-%d" % index, "requires": [], "skip_flag": False}
               for index in range(3000)]
        tut = Tutorial(big)
        for index in range(3000):
            tut.activate("s-%d" % index, "r-%d" % index)
        self.assertLessEqual(tut.scanned_count(), 6000)

    def test_many_steps_many_triggers_amortized_constant(self):
        n = 10000
        big = [{"id": "s-%d" % index, "requires": [], "skip_flag": False}
               for index in range(n)]
        tut = Tutorial(big)
        for index in range(n):
            tut.activate("s-%d" % index, "r-%d" % index)
        self.assertLessEqual(tut.scanned_count(), 2 * n)
        self.assertEqual(len(tut.progress()), n)


if __name__ == "__main__":
    unittest.main()
