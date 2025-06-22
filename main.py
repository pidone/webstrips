from machine import Pin
from neopixel import NeoPixel
from time import sleep_ms
import uasyncio as asyncio
import tinyweb
import color

# Datapin is on D7 = GPIO10
DATA_PIN = Pin(10, Pin.OUT)
NUMBER_OF_LEDS = 125
LIGHT_WHITE = (50, 50, 50)
OFF = (0, 0, 0)

pixels = NeoPixel(DATA_PIN, NUMBER_OF_LEDS)

for i in range(NUMBER_OF_LEDS):
  pixels[i] = OFF

pixels.write()


modes = {'CUSTOM': 'custom' , 'ALL': 'all', 'OFF': 'off', 'RAINBOW': 'rainbow'}

db = {
  "current_state": {
    "mode": modes['ALL'],
    "data": OFF
  }
}

def apply_state(state):
  if state["mode"] == modes['ALL']:
    for i in range(NUMBER_OF_LEDS):
      pixels[i] = state['data']
  elif state["mode"] == modes['CUSTOM']:
    for i in range(NUMBER_OF_LEDS):
      pixels[i] = state['data'][i]
  elif state["mode"] == modes['OFF']:
    for i in range(NUMBER_OF_LEDS):
      pixels[i] = OFF
  elif state["mode"] == modes['RAINBOW']:
    step = 360 / NUMBER_OF_LEDS
    offset = 0
    brightness = 0.5
    if "data" in state:
      if "offset" in state["data"]:
        offset = int(state["data"]["offset"])
      if "brightness" in state["data"]:
        brightness = float(state["data"]["brightness"])
    
    for i in range(NUMBER_OF_LEDS):
      pixels[i] = color.hue_to_rgb(offset + step * i, brightness)


  pixels.write()

def get_current_pixel_state():
  return [pixels[x] for x in range(NUMBER_OF_LEDS)]

class Config():
    def get(self, data):
        return {
          "numberOfLeds": NUMBER_OF_LEDS,
          "location": 'office',
          "availableModes": list(modes.values())
        }

class LedList():
  def get(self, data):
    return {"currentState": db["current_state"]}

  def put(self, data):
    db["current_state"] = data
    apply_state(db["current_state"])
    return {"currentState": db["current_state"]}

class Led():
  def not_exists(self):
    return {'message': 'no such customer'}, 404

  def get(self, data, index):
    i = int(index)
    return {"index": i, "color": pixels[i] }

  def put(self, data, index):
    i = int(index)
    db["current_state"]['mode'] = modes['CUSTOM']
    pixels[i] = data['color']
    pixels.write()
    db["current_state"]['data'] = get_current_pixel_state()

    return {"index": i, "color": pixels[i] }

  def delete(self, data, index):
    return {'message': 'successfully deleted'}

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
