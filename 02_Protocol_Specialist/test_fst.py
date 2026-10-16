import unittest
from fst_dialogue_manager import FSTDialogueManager


class TestFST(unittest.TestCase):
    def setUp(self):
        self.fst = FSTDialogueManager()

    def test_start_state(self):
        self.assertEqual(self.fst.state, "IDLE")

    def test_happy_path_reaches_repaired(self):
        self.fst.run(["hello", "run a scan", "yes", "yes"])
        self.assertEqual(self.fst.state, "REPAIRED")
        self.assertIn("14.2%", self.fst.history[-1].output)

    def test_determinism(self):
        a = FSTDialogueManager().run(["hi", "status", "no"])
        b = FSTDialogueManager().run(["hi", "status", "no"])
        self.assertEqual(a, b)

    def test_unknown_input_keeps_state(self):
        self.fst.step("hello")
        self.fst.step("banana smoothie")
        self.assertEqual(self.fst.state, "READY")

    def test_closed_is_absorbing(self):
        self.fst.run(["hello", "bye", "hello"])
        self.assertEqual(self.fst.state, "CLOSED")

    def test_every_state_has_fallback(self):
        for s in self.fst.states:
            self.assertIn((s, "unknown"), self.fst.delta)

    def test_reset(self):
        self.fst.step("hello")
        self.fst.reset()
        self.assertEqual((self.fst.state, self.fst.history), ("IDLE", []))


if __name__ == "__main__":
    unittest.main()
