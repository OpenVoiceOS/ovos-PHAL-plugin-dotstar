from enum import Enum

from queue import Queue
from threading import Thread, Event
from time import sleep, time

from lingua_franca.util.colors import Color
from lingua_franca.internal import load_language

from ovos_config.config import Configuration
from ovos_utils.log import LOG


class Animation():
    def __init__(self, speed: float = 0.1, timeout: int = None, one_shot: bool = False):
        self._lang = Configuration().get("lang", "en")
        load_language(self._lang)
        self._speed = speed
        self._timeout = timeout
        self._one_shot = one_shot
        self._delay = Event()
        self.alive = True
        self.daemon = True

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed: float):
        self._speed = speed

    def run(self):
        """Override this method for each animation"""

    def stop(self):
        """Override this method for each animation"""


class BreathAnimation(Animation):
    def __init__(self, led_strip, color: tuple, step: float = 0.1):
        """led_strip -> adifruit.DotStar"""
        self._led_strip = led_strip
        self._color = color
        self._step = step
        self.stopping = Event()
        super().__init__()

    def run(self):
        LOG.debug("BreathAnimation running")
        ending = False
        try:
            self.stopping.clear()
            step = self._step
            brightness = 1.0
            self._led_strip.fill(self._color)
            end_time = time() + self._timeout if self._timeout else None
            while not self.stopping.is_set():
                if brightness >= 1.0:
                    step = -1 * self._step
                    LOG.debug(f"going down: {step}")
                if brightness <= 0.1:
                    step = self._step
                    LOG.debug(f"going up: {step}")
                brightness += step
                brightness = round(brightness, 1)
                color = self._color + (brightness,)
                self._led_strip.fill(color)
                self._delay.wait(self.speed)
                if self._one_shot and brightness >= 1.0:
                    ending = True
                if ending and brightness <= 0.1:
                    self.stopping.set()
                if end_time and end_time >= time():
                    self.stopping.set()
        except Exception as e:
            LOG.error(f"could not run BreathAnimation:  {e}")

    def stop(self):
        self.stopping.set()
        self._delay.set()


class ChaseAnimation(Animation):
    def __init__(self, led_strip, fg_color: tuple, bg_color: tuple = None, reverse: bool = False):
        self._led_strip = led_strip
        self._fg_color = fg_color
        self._bg_color = bg_color or Color.from_description("black").rgb255
        self._reverse = reverse
        self.stopping = Event()
        super().__init__()

    def run(self):
        LOG.debug("ChaseAnimation running")
        ending = False
        try:
            self.stopping.clear()
            self._led_strip.fill(self._bg_color)
            end_time = time() + self._timeout if self._timeout else None
            while not self.stopping.is_set():
                leds = list(range(0, self._led_strip.n))
                if self._reverse:
                    leds.reverse()
                for led in leds:
                    self._led_strip[led] = self._fg_color
                    try:
                        self._led_strip[leds.index(led) - 1] = self._bg_color
                    except IndexError:
                        self._led_strip[leds[-1]] = self._bg_color
                    self._delay.wait(self.speed)
                if self._one_shot:
                    self.stopping.set()
                if end_time and end_time >= time():
                    self.stopping.set()
        except Exception as e:
            LOG.error(f"Could not run ChaseAnimation:  {e}")

    def stop(self):
        self.stopping.set()
        self._delay.set()
