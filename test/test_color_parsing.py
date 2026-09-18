"""The colour a configuration supplies is parsed, never executed.

`main_color` and `background_color` come from the plugin's configuration, and
configuration is writable over the message bus, so a string that arrives there
must not be able to run as code.
"""
import os
import unittest

from ovos_PHAL_plugin_dotstar import parse_rgb_literal


class TestParseRgbLiteral(unittest.TestCase):

    def test_an_rgb_triple_is_read(self):
        self.assertEqual((255, 0, 0), parse_rgb_literal("(255, 0, 0)"))
        self.assertEqual((22, 66, 99), parse_rgb_literal("[22, 66, 99]"))

    def test_a_payload_does_not_run(self):
        # Under eval() this returned the running process's pid, which is proof
        # the string had executed. It must now raise instead.
        with self.assertRaises(Exception):
            parse_rgb_literal("__import__('os').getpid()")

    def test_a_payload_leaves_no_trace(self):
        # A payload with a side effect: if anything executes it, the marker is
        # set. Asserting only that an exception was raised would pass against
        # an implementation that ran the code first.
        os.environ.pop("DOTSTAR_EVAL_MARKER", None)
        with self.assertRaises(Exception):
            parse_rgb_literal(
                "__import__('os').environ.__setitem__('DOTSTAR_EVAL_MARKER', 'executed')")
        self.assertIsNone(os.environ.get("DOTSTAR_EVAL_MARKER"))

    def test_a_name_is_not_resolved(self):
        with self.assertRaises(Exception):
            parse_rgb_literal("Color")

    def test_a_literal_that_is_not_a_triple_is_rejected(self):
        for value in ("(255, 0)", "(1, 2, 3, 4)", "255", "'red'", "(1.5, 2, 3)"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_rgb_literal(value)

    def test_a_description_is_rejected_so_the_caller_falls_through(self):
        # "Mycroft blue" and "#22A7F0" are handled by the description and hex
        # branches after this one raises.
        for value in ("Mycroft blue", "#22A7F0"):
            with self.subTest(value=value):
                with self.assertRaises(Exception):
                    parse_rgb_literal(value)


if __name__ == "__main__":
    unittest.main()
