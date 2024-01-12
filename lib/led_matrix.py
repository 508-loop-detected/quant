# SPDX-FileCopyrightText: 2024 Ross Grady for 508: Loop Detected
#
# SPDX-License-Identifier: CC-BY-NC-SA-4.0

import board
from digitalio import DigitalInOut, Direction

# updated for the QT PY RP2040:

def init_pins():
    A1 = DigitalInOut(board.A2)
    A2 = DigitalInOut(board.TX)
    A3 = DigitalInOut(board.SCK)
    C1 = DigitalInOut(board.A0)
    C2 = DigitalInOut(board.RX)
    C3 = DigitalInOut(board.A1)
    C4 = DigitalInOut(board.A3)
    A1.direction = Direction.OUTPUT
    A2.direction = Direction.OUTPUT
    A3.direction = Direction.OUTPUT
    C1.direction = Direction.OUTPUT
    C2.direction = Direction.OUTPUT
    C3.direction = Direction.OUTPUT
    C4.direction = Direction.OUTPUT
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
