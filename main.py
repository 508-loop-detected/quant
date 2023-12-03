# SPDX-FileCopyrightText: 2023 Ross Grady for 508: Loop Detected
#
# SPDX-License-Identifier: CC-BY-NC-SA-4.0

# lib imports

import asyncio
import board
import digitalio

from keypad import Keys

# my mpy module imports
from quantize import \
  hysteresis, \
  quantize, \
  init_analogio, \
  get_voltage, \
  set_voltage

from led_matrix import \
  init_pins, \
  set_matrix, \
  turn_on_one

from switches import \
  mcp_init, \
  configure_interrupts, \
  init_switch_values, \
  read_ints \

from drive_neopixel import \
  pixel_init, \
  neocolor


# board specific hardware inits
mcp, pins = mcp_init()
configure_interrupts(mcp)
pixel = pixel_init()
analog_in, analog_out = init_analogio()
led_pins = init_pins()
set_matrix(led_pins)

switch_interrupt = board.A1
cal_button = board.D4
cal_pin = digitalio.DigitalInOut(board.TX)
cal_pin.direction = digitalio.Direction.INPUT
cal_pin.pull = digitalio.Pull.DOWN

# global vars & arrays inits
last_ADC_value = 9999999
last_DAC_value = 9999999
no_switches_on = False
switch_values = init_switch_values(pins)

key_array = [
  99999,
  11264,
  6144,
  5120,
  4096,
  3072,
  2048,
  99999,
  0,
  1024,
  10240,
  9216,
  8192,
  7168,
  99999,
  99999
  ] # this is what relates hardware switches to notes

(A1,A2,A3,C1,C2,C3,C4) = led_pins
led_map = {
        0: (A1,C1), 
        1024: (A1,C2), 
        2048: (A1,C3), 
        3072: (A1,C4), 
        4096: (A2,C1), 
        5120: (A2,C2), 
        6144: (A2,C3), 
        7168: (A2,C4), 
        8192: (A3,C1), 
        9216: (A3,C2), 
        10240: (A3,C3), 
        11264: (A3,C4),
        12288: (A1,C1)
        } # this relates notes to LEDs

def update_enabled_dict(key_arr, int_arr, notes_dict):
  # key_arr is the reference for switches to notes
  # int_arr is the array returned by the interrupt
  # notes_dict is the dict of enabled notes
  global no_switches_on
  switch_tally = True
  for i in range(16):
    if int_arr[i] == 1:
      switch_tally = False
    notes_dict[key_arr[i]] = int_arr[i]
  no_switches_on = switch_tally

enabled_notes = {}
update_enabled_dict(key_array, switch_values, enabled_notes)

# mode determination logic & branch

async def quantizer(analog_in, analog_out, notes_dict, key_change=False):
  while True:
    input_val = get_voltage(analog_in)
    if no_switches_on:
      set_matrix(led_pins)
      set_voltage(analog_out, input_val)
      await asyncio.sleep(0)
    else:
      global last_ADC_value
      global last_DAC_value
      if (hysteresis(input_val, last_ADC_value)|key_change):
        last_ADC_value = input_val
        quantized_value, enabled_note = quantize(input_val, notes_dict)
        last_DAC_value = quantized_value
        set_voltage(analog_out, quantized_value)
        a,b = led_map[enabled_note]
        turn_on_one(a,b,led_pins)
      await asyncio.sleep(0)


async def catch_switch_transitions(interrupt_pin, mcp):
  with Keys((interrupt_pin,), value_when_pressed=False) as keys:
    while True:
      event = keys.events.get()
      if event:
        if event.pressed:
          flag, cap = read_ints(mcp)
          update_enabled_dict(key_array, cap, enabled_notes)
          await quantizer(analog_in, analog_out, enabled_notes, True)
      await asyncio.sleep(0)


async def catch_cal_button_press(cal_button):
  with Keys((cal_button,), value_when_pressed=False) as keys:
    while True:
      event = keys.events.get()
      if event:
        if event.pressed:
          #<do something here>
          print("pressed")
      await asyncio.sleep(0)

# async task declaration
async def main():
  if cal_pin.value == True:
    cal_task = asyncio.create_task(catch_cal_button_press(cal_button))
    await asyncio.gather(cal_task)
  else:
    interrupt_task = asyncio.create_task(catch_switch_transitions(switch_interrupt, mcp))
    quantizer_task = asyncio.create_task(quantizer(analog_in, analog_out, enabled_notes))
    await asyncio.gather(interrupt_task, quantizer_task)
    

asyncio.run(main())
