# SPDX-FileCopyrightText: 2024 Ross Grady for 508: Loop Detected
#
# SPDX-License-Identifier: CC-BY-NC-SA-4.0

# lib imports

import asyncio
import board

from digitalio import DigitalInOut, Direction, Pull
from keypad import Keys

# my mpy module imports

from all_i2c import \
  init_i2c, \
  init_analogio, \
  get_voltage, \
  get_value, \
  set_value, \
  mcp_init, \
  configure_interrupts, \
  init_switch_values, \
  read_ints

from quantize import \
  hysteresis, \
  quantize 

from led_matrix import \
  init_pins, \
  set_matrix, \
  turn_on_one

from drive_neopixel import \
  pixel_init, \
  neocolor


# board specific hardware inits
i2c = init_i2c()
mcp, pins = mcp_init(i2c)
configure_interrupts(mcp)
pixel, colors = pixel_init()
dac, input_voltage, ground_ref, voltage_ref, output_voltage = init_analogio(i2c)
led_pins = init_pins()
set_matrix(led_pins)

switch_interrupt = DigitalInOut(board.MOSI)
switch_interrupt.direction = Direction.INPUT
switch_interrupt.pull = Pull.UP

cal_button = board.BUTTON

cal_pin = DigitalInOut(board.MISO)
cal_pin.direction = Direction.INPUT
cal_pin.pull = Pull.DOWN


# global vars & arrays inits
last_ADC_value = 9999999
last_DAC_value = 9999999
no_switches_on = False
switch_values = init_switch_values(pins)
# mode 0 is normal, mode 1 is calibration
cal_mode = cal_pin.value
# global for fade in/fade out speed
speed = .001
# global for calibration offset direction -- True is too high, False is too low
offset = False
volt = 1

key_array = [
  99999,
  11264,
  6144,
  5120,
  4096,
  3072,
  1024,
  99999,
  0,
  2048,
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

async def quantizer(input_voltage, dac, notes_dict, key_change=False):
  while True:
    input_val = get_value(input_voltage)
    if switch_interrupt.value == False:
      flag, cap = read_ints(mcp)
      mcp.clear_ints()
      update_enabled_dict(key_array, cap, enabled_notes)
      await quantizer(input_voltage, dac, enabled_notes, True)
    if no_switches_on:
      set_matrix(led_pins)
      set_value(dac, input_val)
      await asyncio.sleep(0)
    else:
      global last_ADC_value
      global last_DAC_value
      if (key_change|hysteresis(input_val, last_ADC_value)):
        last_ADC_value = input_val
        quantized_value, enabled_note = quantize(input_val, notes_dict)
        last_DAC_value = quantized_value
        set_value(dac, quantized_value)
        a,b = led_map[enabled_note]
        turn_on_one(a,b,led_pins)
      await asyncio.sleep(0)


async def catch_cal_button_press(cal_button):
  global volt
  with Keys((cal_button,), value_when_pressed=True) as keys:
    while True:
      event = keys.events.get()
      if event:
        if event.pressed:
          if volt < 5:
            volt = volt +1
          else:
            volt = 1
      await asyncio.sleep(0)


async def calibration():
  global offset
  global speed
  volts = [12288, 24576, 36864, 49152, 61440]
  while True:
    set_value(dac, volts[volt])
    out = get_voltage(output_voltage)
    if out > volt:
      offset = True
    else:
      offset = False
    speed = (abs(out - volt)*30)**2
    await asyncio.sleep(0)


async def set_color_per_offset(pixel, colors):
  while True:
    if offset:
      neocolor(pixel, colors, "pink")
      await asyncio.sleep(0)
    else:
      neocolor(pixel, colors, "blue")
      await asyncio.sleep(0)


async def neopulse(pixel):
    direction = -1
    while True:
      if pixel.brightness == 0:
        direction = 1
        await asyncio.sleep(speed)
      elif pixel.brightness >= .3:
        direction = -1
        await asyncio.sleep(speed)
      pixel.brightness = pixel.brightness + direction*.08
      await asyncio.sleep(0)


# async task declaration
async def main():
  if cal_pin.value == True:
    pulse_task = asyncio.create_task(neopulse(pixel))
    offset_task = asyncio.create_task(set_color_per_offset(pixel, colors))
    button_task = asyncio.create_task(catch_cal_button_press(cal_button))
    calibration_task = asyncio.create_task(calibration())
    await asyncio.gather(pulse_task, offset_task, button_task, calibration_task)

  else:
    quantizer_task = asyncio.create_task(quantizer(input_voltage, dac, enabled_notes))
    await asyncio.gather(quantizer_task)
    

asyncio.run(main())
