
# SPDX-FileCopyrightText: 2024 Ross Grady for 508: Loop Detected
#
# SPDX-License-Identifier: CC-BY-NC-SA-4.0


def hysteresis(adc_output, last_value):
  if(abs(adc_output - last_value) <= 148):
    return False
  else:
    return True


def quantize(adc_output, notes_dict):
  # 1 oct for the input = 5333.2
  # 1 oct for the output = 12288
  working_value = round(adc_output * 122880 / 53332)
  octave, note = divmod(working_value, 12288)
  a, remainder = divmod((note-512), 1024)
  quantized_note = (a+1)*1024
  enabled_note, octave_adder = find_nearest_enabled(quantized_note, remainder, notes_dict)
  octave = octave + octave_adder
  quantized_output = (octave * 12288) + enabled_note
  if quantized_output > 65535:
    quantized_output = 65535
  return quantized_output, enabled_note


def doublecheck(note, octave_adder, notes, remainder, jump = 1):
  local_octave_adder_one = octave_adder
  local_octave_adder_two = octave_adder
  if remainder > 504:
    note_one = note + (1024*jump)
    if note_one >= 12288:
      note_one = 0
      local_octave_adder_one = octave_adder +1
    note_two = note - (1024*jump)
    if note_two < 0:
      note_two = 11264
      local_octave_adder_two = octave_adder -1
  else:
    note_one = note - (1024*jump)
    if note_one < 0:
      note_one = 11264
      local_octave_adder_one = octave_adder -1
    note_two = note + (1024*jump)
    if note_two >= 12288:
      note_two = 0
      local_octave_adder_two = octave_adder +1
  if notes[note_one]:
    return note_one, local_octave_adder_one
  elif notes[note_two]:
    return note_two, local_octave_adder_two
  else:
    return doublecheck(note, octave_adder, notes, remainder, jump+1)


def find_nearest_enabled(note, remainder, notes):
  # checks to see if a note is enabled
  # and returns the nearest match if not
  octave_adder = 0
  if note == 12288:
    # treat it internally as zero
    note = 0
    octave_adder = 1
  if notes[note]:
    return note, octave_adder
  else:
    return doublecheck(note, octave_adder, notes, remainder)

