import neopixel
from .color import hue_to_rgb

OFF = (0, 0, 0)


def mode(name, data=None):
    return {
        "mode": name,
        "data": data
    }

MODES = {
    "all": {
        "color": "tuple(int, int, int): RGB value of the color. Each between 0 and 255",
    },
    "rainbow": {
        "offset": "int: offset within the Hue Space. Between 0 and 360",
        "brightness": "float: brightness value. Between 0 and 1",
    }
}


def default_mode():
    return mode("all", OFF)


class LEDStrip:

    def __init__(self, data_pin, number_of_leds):
        self.current_mode = default_mode()
        self.number_of_leds = number_of_leds
        self.pixels = neopixel.NeoPixel(data_pin, number_of_leds)

    def all(self, color):
        self.current_mode = mode("all", color)
        for i in range(self.number_of_leds):
            self.pixels[i] = color

        self.pixels.write()

    def off(self):
        self.all(OFF)

    def rainbow(self, offset=0, brightness=0.5):
        self.current_mode = mode("rainbow", {"offset": offset, "brightness": brightness})

        step = 360 / self.number_of_leds
        for i in range(self.number_of_leds):
            self.pixels[i] = hue_to_rgb(offset + step * i, brightness)

        self.pixels.write()

    def set_pixels(self, pixels):
        size = min(len(pixels), self.number_of_leds)
        for i in range(size):
            self.pixels[i] = pixels[i]

        self.pixels.write()
        current_pixels = self.get_pixels()
        self.current_mode = mode("custom", current_pixels)

    def set_pixel(self, index, color):
        if index < 0 or index >= self.number_of_leds:
            return

        self.pixels[index] = color
        self.pixels.write()

        current_pixels = self.get_pixels()
        self.current_mode = mode("custom", current_pixels)

    def get_pixel(self, index):
        if index < 0 or index >= self.number_of_leds:
            return
        return self.pixels[index]

    def get_pixels(self):
        return [self.pixels[x] for x in range(self.number_of_leds)]