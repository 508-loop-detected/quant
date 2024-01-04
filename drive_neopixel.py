# SPDX-FileCopyrightText: 2024 Ross Grady for 508: Loop Detected
#
# SPDX-License-Identifier: CC-BY-NC-SA-4.0

import neopixel
import board


def pixel_init():
  pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
  pixel.brightness = 0
  colors = {
      "pink" : (255,0,255),
      "blue" : (0,0,255),
      "orange" : (255,128,0),
      "green" : (0,255,0),
      "red" : (255,0,0)
      }
  return pixel, colors


def neocolor(pixel, colors, color):
    pixel.fill(colors[color])
