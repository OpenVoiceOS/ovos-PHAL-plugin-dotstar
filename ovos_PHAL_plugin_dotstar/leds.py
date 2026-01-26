from abc import abstractmethod

from adafruit_dotstar import DotStar
import board

from ovos_hardware_helpers.led import AbstractLed


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
        Scale a single RGB channel value by a brightness factor and clamp to 0–255.
        
        Parameters:
            color_val (int): Channel value in the range 0–255.
            bright_val (float): Brightness multiplier where 0.0 means off and 1.0 means unchanged.
        
        Returns:
            int: Scaled channel value rounded to the nearest integer and clamped to the range 0–255.
        """
        return min(255, round(color_val * bright_val))