def quantize(adc_output):
  # 1 oct = 12288
  (octave, note) = divmod(adc_output, 12288)
  print("octave", octave)
  print("note", note)
  a,remainder = divmod((note-512), 1024)
  quantized_note = (a+1)*1024
  quantized_output = (octave * 12288) + quantized_note
  print("quantized output", quantized_output)
  # we just pass quantized_output to the DAC
  return quantized_output,remainder
  # rounding down, remainder is > 512
  # rounding up, remainder is < 496


def doublecheck(note, notes, remainder, jump = 1):
  if remainder > 504:
    note_one = note + (1024*jump)
    note_two = note - (1024*jump)
  else:
    note_one = note - (1024*jump)
    note_two = note + (1024*jump)
  print("trying", note_one, "and then", note_two)
  if notes[note_one]:
    print("hit on", note_one)
    return note_one
  elif notes[note_two]:
    print("hit on", note_two)
    return note_two
  else:
    return doublecheck(note, notes, remainder, jump+1)


def find_nearest_enabled(note, remainder, notes):
  # checks to see if a note is enabled
  # and returns the nearest match if not
  print("looking for closest match to", note, "in", notes)
  if notes[note]:
    print("hit on", note)
    return note
  else:
    print(note, "not in", notes)
    print("digging deeper")
    return doublecheck(note, notes, remainder)


# for the next time I get to work on this:
# hysteresis!
# should be storing the last-seen adc_output
# and just returning the most recently seen quantized_output
# if the new value is +/- ____ from the last one
# but you shouldn't update the last-seen with the new value
# otherwise a slowly steadily rising or falling input
# could get stuck on one value inappropriately
# caveat: switches can get flipped at any time
# so you probably still want to test every round
# against the switches array