from threading import Event

from os.path import exists, expanduser, join
from time import sleep

from adafruit_dotstar import DotStar

from ovos_bus_client.message import Message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_plugin_manager.templates.phal import PHALValidator
from ovos_utils.log import LOG
from ovos_config.config import Configuration

from ovos_PHAL.detection import is_respeaker_2mic, is_respeaker_4mic, is_respeaker_6mic

from lingua_franca.util.colors import Color
from lingua_franca.internal import load_language

from ovos_PHAL_plugin_dotstar.boards import RESPEAKER2MIC, RESPEAKER4_6_8MIC, ADAFRUIT2MIC

from ovos_PHAL_plugin_dotstar.light_patterns import BreathAnimation  , ChaseAnimation


I2C_PLATFORM_FILE = "/home/ovos/.config/mycroft/i2c_platform"

PREDEFINED_CARDS = {
    "WM8960": RESPEAKER2MIC,
    "RESPEAKER4": RESPEAKER4_6_8MIC,
    "RESPEAKER6": RESPEAKER4_6_8MIC,
    "ADAFRUIT2": ADAFRUIT2MIC
}


def check_i2c_platform():
    if exists(I2C_PLATFORM_FILE):
        with open(I2C_PLATFORM_FILE, "r") as f:
            platform = f.readline().strip().lower()
            if platform in PREDEFINED_CARDS:
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
        # Check for a file created by ovos-i2csound
        # https://github.com/OpenVoiceOS/ovos-i2csound/blob/dev/ovos-i2csound#L76
        LOG.debug(f"checking file {I2C_PLATFORM_FILE}")
        if check_i2c_platform():
            LOG.debug("checking i2c_platform")
            return True
        # Try a direct hardware check
        if is_respeaker_2mic() or is_respeaker_4mic() or is_respeaker_6mic():
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
        self.leds = []
        self.active_animation = None
        self.ds = None
        # Check and see if there is a configuration for a specific board
        if self.config.get("dotstar_hat") and self.config.get("dotstar_hat") in PREDEFINED_CARDS:
            LOG.debug(f"loading {self.config.get('dotstar_hat')}")
            self.ds = PREDEFINED_CARDS[self.config.get("dotstar_hat")]

        try:
            self.ds = PREDEFINED_CARDS[check_i2c_platform()]
        except KeyError as e:
            LOG.error(e)
        except Exception as e:
            LOG.error(e)
        finally:
            if not self.ds:
                self.ds = RESPEAKER4_6_8MIC

        LOG.debug("Show activation lights")
        self.ds.fill(Color.from_description("mycroft blue").rgb255)
        sleep(1.0)
        self.on_reset()

    def on_record_begin(self, message=None):
        LOG.debug("recording begin")
        self.active_animation = BreathAnimation(
            self.ds, Color.from_description("mycroft blue").rgb255)
        self.active_animation.run()

    def on_record_end(self, message=None):
        LOG.debug("record end")
        self.on_reset()

    def on_audio_output_start(self, message=None):
        # for led in self.ds:
        LOG.debug("I am talking")
        self.active_animation = ChaseAnimation(
            self.ds, Color.from_description("mycroft blue").rgb255)
        self.active_animation.run()

    def on_audio_output_end(self, message=None):
        LOG.debug("done talking")
        self.on_reset()

    def on_think(self, message=None):
        self.on_reset()

    def on_reset(self, message=None):
        LOG.debug("resetting")
        if self.active_animation:
            self.active_animation.stop()
            self.active_animation = None
        self.ds.fill(Color.from_description("black").rgb255)

    def on_system_reset(self, message=None):
        self.on_reset()

    def shutdown(self):
        self.reset()
        super().shutdown()
