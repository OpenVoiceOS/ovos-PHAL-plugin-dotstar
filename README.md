# ovos-PHAL-plugin-dotstar

**Compatible with**
* Respeaker 2/4/6/8 i2c microphone HAT's
* Adafruit 2 mic VoiceBonnet

# Usage

There are a few ways for this plugin to get enabled.

* Enable manually

Add this to your `~/.config/mycroft/mycroft.conf`

```json
{
    "PHAL": {
        "ovos-PHAL-plugin-dotstar": {
            "enabled": true
        }
    }
}
```
With this configuration, no other validation checks are made.  It is assuming you have a compatible HAT installed.

* Automatically with [ovos-i2csound](https://github.com/OpenVoiceOS/ovos-i2csound)

When `ovos-i2csound` is installed and running, it creates a file at `/etc/OpenVoiceOS/i2c_platform` with the HAT name it detected.  This plugin then checks that file and if a compatible HAT is detected, the plugin is activated.

* Automatically with hardware detection

If the above two options don't work, the plugin tries to detect a compatible HAT using `i2c-detect`.  If a compatible device address is found, the plugin will activate.

From this point, if you are using a ReSpeaker i2c microphone, your LED's should give you prompts of what is going on with your OVOS assistant.

### Adafruit 2mic voicebonnet

The [Adafruit voicebonnet](https://learn.adafruit.com/adafruit-voice-bonnet/overview) can be used with this plugin, but it requires one more step of manual configuration.  While the above detection options will properly enable the plugin, this HAT uses different GPIO pins for it's LED's, therefore cannot be easily distinguished from a ReSpeaker 2mic HAT.

Add the following to your `~/.config/mycroft/mycroft.conf` file

```json
{
    "PHAL": {
        "ovos-PHAL-plugin-dotstar": {
            "dotstar_hat": "ADAFRUIT2MIC"
        }
    }
}
```

And restart OVOS

Your LED's on your Adafruit voicebonnet will now show the same prompts as the ReSpeaker devices.

## Custom Configuration

Colors and animations can be configured in `~/.config/mycroft/mycroft.conf`

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

`background_color` -> str
```
    rgb value -> "32, 195, 63"
    name -> "red"
    hex value -> "#FF1A1A"
```

`listen_animation` -> str:
```
    one of:
        'breathe'
        'chase'
        'fill'
        'refill'
        'bounce'
        'blink'
        'alternating'
```

`talking_animation` -> str:
```
    one of:
        'breathe'
        'chase'
        'fill'
        'refill'
        'bounce'
        'blink'
        'alternating'
```
## Conflicts With

There are two pre-existing plugins that either need uninstalled with pip, or blacklisted in your `mycroft.conf` file.

[ovos-PHAL-plugin-respeaker2mic](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-respeaker-2mic)
[ovos-PHAL-plugin-respeaker4mic](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-respeaker-4mic)

### TODO

- [x] Add more animations
- [x] User configurable colors
- [ ] Theme support
- [x] User configurable animations
- [ ] Add github tests and automation

Please enjoy this plugin and don't be afraid to create an [issue](#) if you run into any problems.
