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

from ovos_i2c_detection import is_wm8960, is_respeaker_4mic, is_respeaker_6mic

from lingua_franca.util.colors import Color
from lingua_franca.internal import load_language

# from ovos_PHAL_plugin_dotstar.boards import RESPEAKER2MIC, RESPEAKER4_6_8MIC, ADAFRUIT2MIC
from ovos_PHAL_plugin_dotstar.leds import DotStarLed
from ovos_PHAL_plugin_dotstar.animations import animations

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
        if config.get("enabled"):
            LOG.debug("user enabled")
            return True
        # Try a direct hardware check
        if is_wm8960() or is_respeaker_4mic() or is_respeaker_6mic():
            LOG.debug("direct hardware check")
            return True
        LOG.debug("no validation")
        return False


class DotStarLedControlPlugin(PHALPlugin):
    validator = DotStarLedControlPluginValidator

    lang = Configuration().get("lang", "en")
    try:
        load_language(lang)
    except Exception as e:
        LOG.error(f"Could not load language model {e}")

    def __init__(self, bus=None, config=None):
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
            LOG.debug("enable LED's")
            cleanup(5)
            self._enable_pin = LED(5)
            self._enable_pin.on()

        self.ds.fill(Color.from_description("Mycroft blue").rgb255)
        sleep(1.0)
        self.on_reset()

    def on_record_begin(self, message=None):
        self.active_animation = animations["breathe"](
            self.ds, Color.from_description("mycroft blue"))
        self.active_animation.start()

    def on_record_end(self, message=None):
        self.on_reset()

    def on_audio_output_start(self, message=None):
        self.active_animation = animations["blink"](
            self.ds, Color.from_description("mycroft blue"), repeat=True)
        self.active_animation.start()

    def on_audio_output_end(self, message=None):
        self.on_reset()

    def on_think(self, message=None):
        self.on_reset()

    def on_reset(self, message=None):
        if self.active_animation:
            self.active_animation.stop()
            self.active_animation = None
        self.ds.fill(Color.from_description("black").rgb255)

    def on_system_reset(self, message=None):
        self.on_reset()

    def shutdown(self):
        self.reset()
        super().shutdown()
