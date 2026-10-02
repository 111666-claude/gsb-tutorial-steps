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


class RequiresTest(unittest.TestCase):
    def test_unmet_requirement_blocks_activation(self):
        tut = Tutorial(steps())
        self.assertFalse(tut.activate("b", "r1"))
        self.assertFalse(tut.is_done("b"))

    def test_unmet_requirement_goes_to_pending(self):
        tut = Tutorial(steps())
        tut.activate("b", "r1")
        self.assertEqual(tut.pending_list(), ["b"])

    def test_activation_succeeds_after_requirement_done(self):
        tut = Tutorial(steps())
        tut.activate("b", "r1")
        self.assertTrue(tut.activate("a", "r2"))
        self.assertTrue(tut.activate("b", "r3"))
        self.assertTrue(tut.is_done("b"))


class SkipTest(unittest.TestCase):
    def make(self):
        return Tutorial([{"id": "a", "requires": [], "skip_flag": True},
                         {"id": "b", "requires": ["a"], "skip_flag": False}])

    def test_skip_flag_marks_skipped_not_done(self):
        tut = self.make()
        self.assertTrue(tut.activate("a", "r1"))
        self.assertEqual(tut.skipped_list(), ["a"])
        self.assertFalse(tut.is_done("a"))

    def test_skipped_step_satisfies_requirement(self):
        tut = self.make()
        tut.activate("a", "r1")
        self.assertTrue(tut.activate("b", "r2"))

    def test_done_and_skipped_are_disjoint(self):
        tut = self.make()
        tut.activate("a", "r1")
        tut.activate("b", "r2")
        self.assertEqual(set(tut.skipped_list()) & {s for s in tut.progress() if tut.is_done(s)}, set())


class IdempotencyTest(unittest.TestCase):
    def test_same_req_id_applies_once(self):
        tut = Tutorial(steps())
        self.assertTrue(tut.activate("a", "same"))
        self.assertFalse(tut.activate("a", "same"))

    def test_duplicate_req_id_does_not_change_state(self):
        tut = Tutorial(steps())
        tut.activate("a", "same")
        before = (tut.progress(), tut.scanned_count())
        tut.activate("a", "same")
        self.assertEqual((tut.progress(), tut.scanned_count()), before)

    def test_step_not_completed_twice(self):
        tut = Tutorial(steps())
        tut.activate("a", "r1")
        self.assertFalse(tut.activate("a", "r2"))
        self.assertEqual(tut.progress(), ["a"])


class OrderTest(unittest.TestCase):
    def test_progress_follows_definition_order(self):
        tut = Tutorial([{"id": "a", "requires": [], "skip_flag": False},
                        {"id": "b", "requires": [], "skip_flag": False}])
        tut.activate("b", "r1")
        tut.activate("a", "r2")
        self.assertEqual(tut.progress(), ["a", "b"])

    def test_progress_includes_skipped_in_definition_order(self):
        tut = Tutorial([{"id": "a", "requires": [], "skip_flag": False},
                        {"id": "b", "requires": [], "skip_flag": True},
                        {"id": "c", "requires": [], "skip_flag": False}])
        tut.activate("c", "r1")
        tut.activate("b", "r2")
        self.assertEqual(tut.progress(), ["b", "c"])
