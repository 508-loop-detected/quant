import neopixel
import board

def pixel_init():
  pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
  pixel.brightness = .03
  return pixel

def neocolor(pixel, color):
  if color == "pink":
    pixel.fill((255,0,255))
  elif color == "blue":
    pixel.fill((0,0,255))
  elif color == "orange":
    pixel.fill((255,128,0))
  elif color == "green":
    pixel.fill((0,255,0))
  elif color == "red":
    pixel.fill((255,0,0))
  else:
    pixel.fill((128,128,128))
    