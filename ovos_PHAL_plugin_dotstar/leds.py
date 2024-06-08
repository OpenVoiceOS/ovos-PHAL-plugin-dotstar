from abc import abstractmethod

from adafruit_dotstar import DotStar
import board

from ovos_plugin_manager.hardware.led import AbstractLed


class DotStarLed(AbstractLed):
    def __init__(self, dotstar_led_strip: DotStar):
        self.dotstar = dotstar_led_strip

    @property
    def num_leds(self):
        return self.dotstar.n

    @property
    def capabilities(self):
        pass

    def set_led(self, led_idx: int, color: tuple, immediate: bool = True):
        self.dotstar[led_idx] = color

    def fill(self, color: tuple):
        self.dotstar.fill(color)

    def show(self):
        self.dotstar.show()

    def shutdown(self):
        # TODO: something
        pass

    def scale_brightness(color_val: int, bright_val: float) -> float:
        """
        Scale an individual color value by a specified brightness.
        :param color_val: 0-255 R, G, or B value
        :param bright_val: 0.0-1.0 brightness scalar value
        :returns: Float modified color value to account for brightness
        """
        return min(255.0, round(color_val * bright_val))
