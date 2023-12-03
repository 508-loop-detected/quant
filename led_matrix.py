# SPDX-FileCopyrightText: 2023 Ross Grady for 508: Loop Detected
#
# SPDX-License-Identifier: CC-BY-NC-SA-4.0

import digitalio
import board


def init_pins():
    A1 = digitalio.DigitalInOut(board.MISO)
    A2 = digitalio.DigitalInOut(board.A4)
    A3 = digitalio.DigitalInOut(board.A3)
    C1 = digitalio.DigitalInOut(board.RX)
    C2 = digitalio.DigitalInOut(board.MOSI)
    C3 = digitalio.DigitalInOut(board.SCK)
    C4 = digitalio.DigitalInOut(board.A5)
    A1.direction = digitalio.Direction.OUTPUT
    A2.direction = digitalio.Direction.OUTPUT
    A3.direction = digitalio.Direction.OUTPUT
    C1.direction = digitalio.Direction.OUTPUT
    C2.direction = digitalio.Direction.OUTPUT
    C3.direction = digitalio.Direction.OUTPUT
    C4.direction = digitalio.Direction.OUTPUT
    return(A1,A2,A3,C1,C2,C3,C4)


def set_matrix(pins):
    (A1,A2,A3,C1,C2,C3,C4) = pins
    A1.value = False
    A2.value = False
    A3.value = False
    C1.value = True
    C2.value = True
    C3.value = True
    C4.value = True


def turn_on_one(a,c,pins):
  set_matrix(pins)
  a.value = True
  c.value = False
