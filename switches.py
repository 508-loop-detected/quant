# SPDX-FileCopyrightText: 2023 Ross Grady for 508: Loop Detected
#
# SPDX-License-Identifier: CC-BY-NC-SA-4.0

import board
import busio
import time

from adafruit_mcp230xx.mcp23017 import MCP23017
from digitalio import Direction


def mcp_init():
  try:
    # Initialize the I2C bus:
    i2c = busio.I2C(board.SCL, board.SDA)

    # Create an instance of MCP23017 class:
    mcp = MCP23017(i2c) 

    # Make a list of all the pins (a.k.a 0-15)
    pins = []
    for pin in range(16):
      pins.append(mcp.get_pin(pin))

    # Set all the pins to input
    for pin in pins:
      pin.direction = Direction.INPUT

    '''
    # not using GPIOA0
    sw12 = pins[1]
    sw7 = pins[2]
    sw6 = pins[3]
    sw5 = pins[4]
    sw4 = pins[5]
    sw3 = pins[6]
    # not using GPIOA7
    sw1 = pins[8]
    sw2 = pins[9]
    sw11 = pins[10]
    sw10 = pins[11]
    sw9 = pins[12]
    sw8 = pins[13]
    # not using GPIOB6 aka 14
    # not using GPIOB7 aka 15
    '''
    return (mcp, pins)
  except Exception as exc:
    print("Error initializing MCP:", exc)
    time.sleep(.0001)
    mcp_init()


def configure_interrupts(mcp):
  try:
    mcp.gppu = 0xFFFF # pull up all pins to eliminate spurious interrupts from unconnected pins
    mcp.interrupt_enable = 0xFFFF  # enable interrupts on all pins
    mcp.interrupt_configuration = 0x0000  # compare pins against previous values
    mcp.io_control = 0x44  # Interrupt as open drain and mirrored
    mcp.clear_ints()  # clear all interrupts
  except Exception as exc:
    print("Error configuring interrupts:", exc)
    time.sleep(.0001)
    configure_interrupts(mcp)


def init_switch_values(pins):
  switch_values = []
  for i in range(16):
    switch_values.append(int(pins[i].value))
  return switch_values
   

def read_ints(mcp):
  try:
    flag = mcp.int_flag  # retrieves which pin(s) caused the interrupt
    cap = mcp.int_cap  # retrieves pin values captured at time of interrupt
    mcp.clear_ints()  # clear all interrupts
    return(flag,cap)
  except Exception as exc:
    print("Error reading interrupts:", exc)
    time.sleep(.0001)
    read_ints(mcp)


# this works! And it's cleaner/simpler than what I was doing.
