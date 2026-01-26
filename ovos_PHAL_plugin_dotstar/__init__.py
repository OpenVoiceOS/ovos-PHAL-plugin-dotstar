from threading import Event

from os.path import exists, expanduser, join
from time import sleep

from adafruit_dotstar import DotStar
import board
from gpiozero import LED
from RPi.GPIO import cleanup

from ovos_bus_client.message import Message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_plugin_manager.templates.phal import PHALValidator
from ovos_utils.log import LOG
from ovos_config.config import Configuration

from ovos_i2c_detection import is_wm8960, is_respeaker_4mic, is_respeaker_6mic, is_mark_1

from ovos_color_parser import color_from_description
from ovos_color_parser.models import Color

from ovos_hardware_helpers.led import eval_color
from ovos_hardware_helpers.led.animations import animations

from ovos_PHAL_plugin_dotstar.leds import DotStarLed

# File defined in ovos-i2csound
# https://github.com/OpenVoiceOS/ovos-i2csound/blob/dev/ovos-i2csound#L76
I2C_PLATFORM_FILE = "/etc/OpenVoiceOS/i2c_platform"

PREDEFINED_HATS = {
    "WM8960": DotStar(board.D11, board.D10, 3, brightness=0.2),
    "RESPEAKER4": DotStar(board.D11, board.D10, 12, brightness=0.2),
    "RESPEAKER6": DotStar(board.D11, board.D10, 12, brightness=0.2),
    "ADAFRUIT2MIC": DotStar(board.D6, board.D5, 3, brightness=0.2)
}


def check_i2c_platform():
    if exists(I2C_PLATFORM_FILE):
        with open(I2C_PLATFORM_FILE, "r") as f:
            platform = f.readline().strip()
            LOG.debug(f"platform in check_i2c_platform: {platform}")
            if platform in PREDEFINED_HATS:
                LOG.debug(f"detected {platform} in i2c_platform")
                return platform
    return None


class DotStarLedControlPluginValidator(PHALValidator):

    @staticmethod
    def validate(config=None):
        # If the user enabled the plugin no need to go further
        """
        Validate the configuration for the DotStar LED control plugin.
        
        Determines whether the plugin should be activated based on configuration and hardware detection.
        
        Parameters:
            config (dict, optional): Plugin configuration dictionary. Defaults to None.
        
        Returns:
            bool: True if the plugin should be enabled, False otherwise.
        
        Conditions for validation:
            1. If plugin is explicitly enabled in configuration
            2. If specific audio hardware is detected (WM8960, ReSpeaker 4-mic, ReSpeaker 6-mic)
            3. Excludes Mark 1 hardware configuration
        
        Logs debug information about validation process.
        """
        if config.get("enabled"):
            LOG.debug("user enabled")
            return True
        # Try a direct hardware check
        if is_wm8960() or is_respeaker_4mic() or is_respeaker_6mic():
            if is_mark_1():
                LOG.debug("Mark 1 detected.  Dotstar is not needed")
                return False
            LOG.debug("direct hardware check")
            return True
        LOG.debug("no validation")
        return False


class DotStarLedControlPlugin(PHALPlugin):
    validator = DotStarLedControlPluginValidator

    def __init__(self, bus=None, config=None):
        """
        Initialize the DotStar LED control plugin, configure the DotStar device from configuration or detected hardware, enable ReSpeaker hardware if required, and apply the configured main color.
        
        The constructor will:
        - Use config["dotstar_hat"] when present to load a predefined hat by key or construct a DotStar from a dict.
        - Fall back to platform detection via check_i2c_platform() or direct hardware checks (WM8960, ReSpeaker 4/6) to choose a predefined hat.
        - Enable the ReSpeaker enable pin when running on ReSpeaker hardware (not WM8960).
        - Evaluate and store the main color via eval_color, fill the LEDs with that color, wait briefly, then reset the LED state.
        
        Parameters:
            bus: Optional hardware bus or service (commonly provided by the runtime).
            config (dict): Plugin configuration. Relevant keys:
                - "dotstar_hat": either a string key referencing PREDEFINED_HATS or a dict with keys
                    "clock_pin", "led_pin", "num_led", optional "brightness" (float), and optional "enable_pin".
                - "main_color": color description (string or other accepted format) used to set the initial main color; defaults to "Mycroft Blue".
        """
        super().__init__(bus=bus, name="ovos-PHAL-plugin-dotstar", config=config)
        self._enable_pin = None
        self.active_animation = None
        self.ds = None
        # Check and see if there is a configuration for a specific board
        if self.config.get("dotstar_hat"):
            ds = self.config.get("dotstar_hat")
            if ds in PREDEFINED_HATS:
                LOG.debug(f"loading {ds} from config")
                try:
                    self.ds = DotStarLed(PREDEFINED_HATS[ds])
                except Exception as e:
                    LOG.error(f"Could not load {ds} from config:  {e}")
            elif isinstance(self.config.get("dotstar_hat"), dict):
                try:
                    self.ds = DotStar(
                        ds["clock_pin"], ds["led_pin"], ds["num_led"], brightness=ds.get("brightness", 0.2))
                    self._enable_pin = ds.get("enable_pin", None)
                except Exception as e:
                    LOG.error(f"Could not create led array:  {e}")
        else:
            try:
                self.ds = DotStarLed(PREDEFINED_HATS[check_i2c_platform()])
            except KeyError as e:
                LOG.debug(f"check_i2c_platform failed {e}")
            except Exception as e:
                LOG.error(e)
        # No manual configuration and i2csound is not installed or failed
        if not self.ds:
            # Direct hardware checks
            if is_wm8960:
                self.ds = DotStarLed(PREDEFINED_HATS["WM8960"])
            elif is_respeaker_4mic:
                self.ds = DotStarLed(PREDEFINED_HATS["RESPEAKER4"])
            elif is_respeaker_6mic:
                self.ds = DotStarLed(PREDEFINED_HATS["RESPEAKER6"])
            # All else fails, fall back to respeker 4mic
            else:
                self.ds = DotStarLed(PREDEFINED_HATS["RESPEAKER4"])

        # Required for ReSpeaker 4/6/8 mic
        if not is_wm8960():
            LOG.debug("enable ReSpeaker 4/6/8")
            cleanup(5)
            self._enable_pin = LED(5)
            self._enable_pin.on()
        
        color = self.config.get("main_color", "Mycroft Blue")
        self._main_color = eval_color(color)
        
        self.ds.fill((self.main_color.r, self.main_color.g, self.main_color.b))
        sleep(1.0)
        self.on_reset()

    @property
    def main_color(self):
        """
        Get the plugin's current primary LED color.
        
        Returns:
            Color: The evaluated primary color used for LED animations and fills.
        """
        return self._main_color
        
    @main_color.setter
    def main_color(self, color):
        """
        Set the plugin's main LED color by normalizing the provided color specification.
        
        Attempts to evaluate `color` via `eval_color`; if evaluation fails, falls back to the Color for "Mycroft Blue" (with fuzzy matching disabled). The resulting Color object is stored in `self._main_color`.
        
        Parameters:
            color: A color specification (e.g., name string, hex string, dict, tuple, or Color instance) to be normalized and stored as the main color.
        """
        self._main_color = eval_color(color) or color_from_description("Mycroft Blue", fuzzy=False)

    @property
    def background_color(self):
        """
        Resolve and return the plugin's background Color from configuration.
        
        The method accepts several configuration formats: a Color instance, a string containing a Python expression that evaluates to an (r, g, b) tuple, a descriptive color name, or a hex color string. If resolution fails, returns the Color for "OVOS red".
        
        Returns:
            Color: The resolved background color.
        """
        color = self.config.get(
            "background_color", Color.from_description("OVOS red"))
        if isinstance(color, str):
            try:
                color = eval(color)
                color = Color.from_rgb(color[0], color[1], color[2])
            except Exception as e:
                LOG.debug(f"Exception caught in eval {e}")
                try:
                    color = Color.from_description(color)
                except Exception as e:
                    LOG.debug(f"Exception caught in description {e}")
                    try:
                        color = Color.from_hex(color)
                    except Exception as e:
                        LOG.warning(f"could not set color to {color}: {e}")
                        color = Color.from_description("OVOS red")
        return color

    @property
    def listen_animation(self):
        return self.config.get("listen_animation", "breathe")

    @property
    def talking_animation(self):
        return self.config.get("talking_animation", "blink")

    def on_record_begin(self, message=None):
        self.active_animation = animations[self.listen_animation](
            self.ds, self.main_color)
        self.active_animation.start()

    def on_record_end(self, message=None):
        """
        Reset the DotStar LEDs when a recording ends.
        
        Parameters:
            message (optional): The event message object for the recording-end signal; accepted for handler compatibility and ignored by this method.
        """
        self.on_reset()

    def on_audio_output_start(self, message=None):
        """
        Start the configured talking animation on the DotStar LED.
        
        Sets the plugin's active animation to the configured talking animation (in repeat mode) and starts it.
        
        Parameters:
            message (optional): Optional bus message payload; accepted for handler compatibility but not used.
        """
        self.active_animation = animations[self.talking_animation](
            self.ds, self.main_color, repeat=True)
        self.active_animation.start()

    def on_audio_output_end(self, message=None):
        """
        Handle the end of audio output by resetting the DotStar LED state.
        
        Parameters:
            message (optional): Event payload received when audio output ends; ignored by this handler.
        """
        self.on_reset()

    def on_think(self, message=None):
        self.on_reset()

    def on_reset(self, message=None):
        """
        Stop any active LED animation and turn all DotStar LEDs off.
        
        Parameters:
            message (optional): Event context or payload (accepted but ignored).
        """
        if self.active_animation:
            self.active_animation.stop()
            self.active_animation = None
        self.ds.fill((0, 0, 0))

    def on_system_reset(self, message=None):
        """
        Handle a system reset event by restoring the plugin's LED state.
        
        Triggers the plugin's on_reset behavior to stop animations and clear LEDs. The optional
        message parameter, if provided, is accepted for event compatibility but ignored.
         
        Parameters:
            message (Any, optional): Event message payload (unused).
        """
        self.on_reset()

    def shutdown(self):
        self.reset()
        super().shutdown()