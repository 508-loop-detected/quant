# SPDX-FileCopyrightText: 2023 Ross Grady for 508: Loop Detected
#
# SPDX-License-Identifier: CC-BY-NC-SA-4.0

import board
import time

from analogio import AnalogIn
from analogio import AnalogOut


def init_analogio():
  analog_in = AnalogIn(board.A2)
  analog_out = AnalogOut(board.A0)
  return analog_in, analog_out


def get_voltage(pin):
  try:
    return pin.value
    # pin.value will be 0-65535
  except Exception as exc:
    #fuckit let's try again
    print("Error reading voltage:",exc)
    time.sleep(.0001)
    return get_voltage(pin)


def set_voltage(pin, voltage):
  try:
    pin.value = voltage
  except Exception as exc:
    print("Error setting voltage", voltage, exc)
    #fuckit, let's try again
    time.sleep(.0001)
    set_voltage(pin, voltage)


def hysteresis(adc_output, last_value):
  if(abs(adc_output - last_value) <= 32):
    return False
  else:
    return True


def quantize(adc_output, notes_dict):
  # 1 oct = 12288
  octave, note = divmod(adc_output, 12288)
  a, remainder = divmod((note-512), 1024)
  quantized_note = (a+1)*1024
  if quantized_note == 12288:
    octave = octave +1
    quantized_note = 0
  enabled_note = find_nearest_enabled(quantized_note, remainder, notes_dict)
  quantized_output = (octave * 12288) + enabled_note
  if quantized_output > 65535:
    quantized_output = 65535
  return quantized_output, enabled_note


def doublecheck(note, notes, remainder, jump = 1):
  if remainder > 504:
    note_one = note + (1024*jump)
    if note_one >= 12288:
      note_one = 0
    note_two = note - (1024*jump)
    if note_two <= 0:
      note_two = 11264
  else:
    note_one = note - (1024*jump)
    if note_one <= 0:
      note_one = 11264
    note_two = note + (1024*jump)
    if note_two >= 12288:
      note_two = 0
  if notes[note_one]:
    return note_one
  elif notes[note_two]:
    return note_two
  else:
    return doublecheck(note, notes, remainder, jump+1)


def find_nearest_enabled(note, remainder, notes):
  # checks to see if a note is enabled
  # and returns the nearest match if not
  if notes[note]:
    return note
  else:
    return doublecheck(note, notes, remainder)

