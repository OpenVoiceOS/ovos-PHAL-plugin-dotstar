# ovos-PHAL-plugin-dotstar

This is an OVOS PHAL plugin. It controls DotStar type LEDs on compatible hardware.

**Compatible hardware**
* ReSpeaker 2/4/6/8 i2c microphone HATs
* Adafruit 2-mic VoiceBonnet

## Install

```bash
pip install ovos-PHAL-plugin-dotstar
```

## Usage

You can enable this plugin in three ways.

### Enable manually

Add this to your `~/.config/mycroft/mycroft.conf`.

```json
{
    "PHAL": {
        "ovos-PHAL-plugin-dotstar": {
            "enabled": true
        }
    }
}
```

With this configuration, the plugin makes no other checks. It assumes you have a compatible HAT installed.

### Enable automatically with ovos-i2csound

When [ovos-i2csound](https://github.com/OpenVoiceOS/ovos-i2csound) is installed and running, it creates a file at `/etc/OpenVoiceOS/i2c_platform` with the name of the HAT it detected. This plugin reads that file. If it lists a compatible HAT, the plugin activates.

### Enable automatically with hardware detection

If the two options above do not work, the plugin tries to detect a compatible HAT with `i2c-detect`. If it finds a compatible device address, the plugin activates.

Once enabled, the LEDs on a ReSpeaker i2c microphone HAT show prompts for what your OVOS assistant is doing.

### Adafruit 2-mic VoiceBonnet

You can use the [Adafruit VoiceBonnet](https://learn.adafruit.com/adafruit-voice-bonnet/overview) with this plugin, but it needs one extra configuration step. The detection options above enable the plugin correctly, but this HAT uses different GPIO pins for its LEDs. The plugin cannot tell it apart from a ReSpeaker 2-mic HAT by detection alone.

Add this to your `~/.config/mycroft/mycroft.conf` file.

```json
{
    "PHAL": {
        "ovos-PHAL-plugin-dotstar": {
            "dotstar_hat": "ADAFRUIT2MIC"
        }
    }
}
```

Restart OVOS. The LEDs on your Adafruit VoiceBonnet now show the same prompts as the ReSpeaker devices.

## Custom configuration

You can configure colors and animations in `~/.config/mycroft/mycroft.conf`.

```json
{
    "PHAL": {
        "ovos-PHAL-plugin-dotstar": {
            "main_color": "Mycroft blue",
            "background_color": "OVOS red",
            "listen_animation": "breath",
            "talking_animation": "blink"
        }
    }
}
```

`main_color` -> str:
```
    rgb value -> "32, 195, 63"
    name -> "blue"
    hex value -> "#22A7F0"
```

`background_color` -> str:
```
    rgb value -> "32, 195, 63"
    name -> "red"
    hex value -> "#FF1A1A"
```

`listen_animation` -> str, one of:
```
    'breathe'
    'chase'
    'fill'
    'refill'
    'bounce'
    'blink'
    'alternating'
```

`talking_animation` -> str, one of:
```
    'breathe'
    'chase'
    'fill'
    'refill'
    'bounce'
    'blink'
    'alternating'
```

## Conflicts with

Two other plugins control the same LEDs. Uninstall them with pip, or blacklist them in your `mycroft.conf` file, before you use this plugin.

* [OpenVoiceOS/ovos-PHAL-plugin-respeaker2mic](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-respeaker-2mic)
* [OpenVoiceOS/ovos-PHAL-plugin-respeaker4mic](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-respeaker-4mic)

## Related projects

* [OpenVoiceOS/ovos-i2csound](https://github.com/OpenVoiceOS/ovos-i2csound) — detects i2c HATs and enables this plugin automatically

## License

This project is licensed under the [MIT license](LICENSE).
