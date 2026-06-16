"""Unit tests for ovos-PHAL-plugin-dotstar.

These exercise the pure-python logic of the plugin (HAT pin tables, i2c platform
detection, the DotStarLed wrapper and the LED animations) without requiring any
real LED/GPIO hardware. The Raspberry Pi hardware libraries (adafruit_dotstar,
board, gpiozero, RPi.GPIO) are imported lazily inside the plugin, so the package
imports cleanly here and the LED strip is replaced by a simple in-memory fake.
"""
import unittest
from unittest.mock import patch

import ovos_PHAL_plugin_dotstar as dotstar
from ovos_PHAL_plugin_dotstar import (
    PREDEFINED_HAT_PINS,
    check_i2c_platform,
    get_predefined_hat,
)
from ovos_PHAL_plugin_dotstar.leds import DotStarLed
from ovos_PHAL_plugin_dotstar.animations import (
    animations,
    BlinkLedAnimation,
    FillLedAnimation,
)


class FakeStrip:
    """Minimal stand-in for an adafruit_dotstar.DotStar strip."""

    def __init__(self, n=4):
        self.n = n
        self.pixels = [(0, 0, 0)] * n
        self.filled = None
        self.shown = 0

    def __setitem__(self, idx, color):
        self.pixels[idx] = color

    def fill(self, color):
        self.filled = color

    def show(self):
        self.shown += 1


class TestModuleImport(unittest.TestCase):
    def test_imports_without_hardware(self):
        # Importing the plugin must not require LED/GPIO hardware libraries.
        self.assertTrue(hasattr(dotstar, "DotStarLedControlPlugin"))
        self.assertTrue(hasattr(dotstar, "DotStarLedControlPluginValidator"))

    def test_predefined_hat_pins_known(self):
        self.assertIn("WM8960", PREDEFINED_HAT_PINS)
        self.assertIn("RESPEAKER4", PREDEFINED_HAT_PINS)
        self.assertIn("RESPEAKER6", PREDEFINED_HAT_PINS)
        self.assertIn("ADAFRUIT2MIC", PREDEFINED_HAT_PINS)
        for clock, data, num in PREDEFINED_HAT_PINS.values():
            self.assertIsInstance(clock, str)
            self.assertIsInstance(data, str)
            self.assertIsInstance(num, int)


class TestGetPredefinedHat(unittest.TestCase):
    def test_builds_strip_with_board_pins(self):
        captured = {}

        class FakeBoard:
            D11 = "PIN_D11"
            D10 = "PIN_D10"

        def fake_dotstar(clock, data, num_led, brightness=0.2):
            captured.update(clock=clock, data=data, num_led=num_led,
                            brightness=brightness)
            return FakeStrip(num_led)

        import sys
        import types
        fake_mod = types.ModuleType("adafruit_dotstar")
        fake_mod.DotStar = fake_dotstar
        with patch.dict(sys.modules, {"adafruit_dotstar": fake_mod,
                                      "board": FakeBoard()}):
            strip = get_predefined_hat("WM8960")
        self.assertEqual(captured["clock"], "PIN_D11")
        self.assertEqual(captured["data"], "PIN_D10")
        self.assertEqual(captured["num_led"], 3)
        self.assertIsInstance(strip, FakeStrip)

    def test_unknown_hat_raises(self):
        with self.assertRaises(KeyError):
            get_predefined_hat("NOPE")


class TestCheckI2cPlatform(unittest.TestCase):
    def test_missing_file_returns_none(self):
        with patch("ovos_PHAL_plugin_dotstar.exists", return_value=False):
            self.assertIsNone(check_i2c_platform())

    def test_known_platform_returned(self):
        from unittest.mock import mock_open
        m = mock_open(read_data="WM8960\n")
        with patch("ovos_PHAL_plugin_dotstar.exists", return_value=True), \
                patch("builtins.open", m):
            self.assertEqual(check_i2c_platform(), "WM8960")

    def test_unknown_platform_returns_none(self):
        from unittest.mock import mock_open
        m = mock_open(read_data="SOMETHING_ELSE\n")
        with patch("ovos_PHAL_plugin_dotstar.exists", return_value=True), \
                patch("builtins.open", m):
            self.assertIsNone(check_i2c_platform())


class TestDotStarLed(unittest.TestCase):
    def setUp(self):
        self.strip = FakeStrip(n=4)
        self.led = DotStarLed(self.strip)

    def test_num_leds(self):
        self.assertEqual(self.led.num_leds, 4)

    def test_set_led(self):
        self.led.set_led(2, (1, 2, 3))
        self.assertEqual(self.strip.pixels[2], (1, 2, 3))

    def test_fill(self):
        self.led.fill((9, 9, 9))
        self.assertEqual(self.strip.filled, (9, 9, 9))

    def test_show(self):
        self.led.show()
        self.assertEqual(self.strip.shown, 1)


class TestAnimationsRegistry(unittest.TestCase):
    def test_registry_keys(self):
        for key in ("breathe", "chase", "fill", "refill", "bounce", "blink",
                    "alternating"):
            self.assertIn(key, animations)


class TestFillAnimation(unittest.TestCase):
    def test_fill_sets_each_led(self):
        from lingua_franca.util.colors import Color
        strip = FakeStrip(n=3)
        led = DotStarLed(strip)
        anim = FillLedAnimation(led, Color.from_rgb(10, 20, 30))
        # patch the internal delay so the test does not sleep
        anim._delay.set()
        anim.start()
        # all three pixels should have been written
        for px in strip.pixels:
            self.assertEqual(px, (10, 20, 30))


class TestBlinkAnimationOneShot(unittest.TestCase):
    def test_blink_one_shot_terminates(self):
        from lingua_franca.util.colors import Color
        strip = FakeStrip(n=2)
        led = DotStarLed(strip)
        anim = BlinkLedAnimation(led, Color.from_rgb(255, 0, 0), num_blinks=1)
        anim._delay.set()
        # one_shot must terminate the loop without an explicit stop()
        anim.start(one_shot=True)
        self.assertTrue(anim.stopping.is_set())


if __name__ == "__main__":
    unittest.main()
