from machine import Pin
import uasyncio as asyncio
import tinyweb
from led_strip import color, LEDStrip

# Datapin is on D7 = GPIO10
DATA_PIN = Pin(10, Pin.OUT)
NUMBER_OF_LEDS = 125

strip = LEDStrip(DATA_PIN, NUMBER_OF_LEDS)
strip.off()

class Config():
    def get(self, data):
        return {
          "numberOfLeds": strip.number_of_leds,
          "location": 'office'
        }

class LedList():
  def get(self, _data):
    return {"leds": strip.get_pixels()}

  def put(self, data):
    pixels = data["leds"]
    strip.set_pixels(pixels)
    return {"leds": strip.get_pixels()}

class Led():
  def not_exists(self):
    return {'message': 'no such led'}, 404

  def get(self, _data, index):
    i = int(index)
    if i >= strip.number_of_leds or i < 0:
      return self.not_exists()

    return {"index": i, "color": strip.get_pixel(i) }

  def put(self, data, index):
    i = int(index)
    if i >= strip.number_of_leds or i < 0:
      return self.not_exists()

    strip.set_pixel(i, data["color"])
    return {"index": i, "color": strip.get_pixel(i)}

  def delete(self, _data, index):
    i = int(index)
    if i >= strip.number_of_leds or i < 0:
      return self.not_exists()

    strip.set_pixel(i, (0, 0, 0))
    return {"index": i, "color": strip.get_pixel(i)}

app = tinyweb.webserver()
app.add_resource(Config, '/config')
app.add_resource(LedList, '/leds')
app.add_resource(Led, '/leds/<index>')

async def all_shutdown():
    await asyncio.sleep_ms(100)

try:
  app.run(host='0.0.0.0', port=8080)
except KeyboardInterrupt as e:
  print(' CTRL+C pressed - terminating...')
  app.shutdown()
  asyncio.get_event_loop().run_until_complete(all_shutdown())
