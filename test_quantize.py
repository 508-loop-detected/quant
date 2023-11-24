# test values -- this is voltages but realistically it could just be unsigned ints between 0 and 65535

from quantize import quantize, find_nearest_enabled

test_values = {
  0 : 0,
  .08333 : .08333,
  .16666 : .16666,
  1 : 1,
  1.5 : 1.5,
  2 : 2,
  2.5 : 2.5,
  3 : 3,
  4 : 4,
  5 : 5,
  5.33333 : 5.33333,
  3.08333 : 3.08333,
  3.1 : 3.08333,
  3.16666 : 3.16666,
  3.2 : 3.16666,
  3.25 : 3.25,
  3.33333 : 3.33333,
  3.3 : 3.33333,
  3.41666 : 3.41666,
  3.4 : 3.41666,
  3.43 : 3.41666,
  3.44 : 3.41666,
  3.45 : 3.41666,
  3.46 : 3.5,
  3.47 : 3.5,
  3.415 : 3.41666,
  3.417 : 3.41666,
  3.5 : 3.5,
}

def test_quantize():
  for key, value in test_values.items():
    # mocking the input scaler + ADC:
    print("voltage in",key)
    shifted_voltage = key * .61875 # scaled by op amp
    print("shifted voltage",shifted_voltage)
    # range of the ADC is 3.3V subdivided into 0 - 65535
    # smallest voltage increment measurable is 3.3/65536
    # however it's really a 12-bit ADC so it's actually
    # (0 - 4095) * 16
    voltage_increment = 3.3 / 4096 # 0.0008056640625 volts
    adc_output = int(shifted_voltage/voltage_increment) << 4
    print("adc output",adc_output)
    # everything above here is done in the ADC, invisible to us
    # here is where we start the real quantization
    quantized_value,b = quantize(adc_output)
    print("quantized value is", quantized_value,"and remainder is", b)
    # now we're just mocking the DAC + output scaler:
    dac_input = int(quantized_value) >> 4
    print("dac input", dac_input)
    dac_output = dac_input * voltage_increment
    print("dac output", dac_output)
    voltage_out_intermediate = (dac_output/.61875) * 100000 # scaled by op amp
    voltage_out = int(voltage_out_intermediate)/100000
    print("voltage out", voltage_out)
    print("-----",)
    assert (voltage_out == value) | (voltage_out == value - 0.00001)


# so what *are* the note boundaries that result in the right output?
# voltage_out = (dac_input * 0.0008056640625)/.61875
# voltage_out = dac_input * 0.001302083333333

#successful:
# dac_input = 64; 
# dac output 0.0515625
# voltage out 0.08333 

# voltage_out:
# .083333333 == 64  *16 == 1,024
# .166666666 == 128  *16 == 2,048
# .25 == 192  *16 == 3,072
# .333333333 == 256  *16 == 4,096
# .416666666 == 320  *16 == 5,120
# .5 == 384  *16 == 6,144
# .583333333 == 448  *16 == 7168
# .666666666 == 512  *16 == 8,192
# .75 == 576  *16 == 9,216
# .833333333 == 640  *16 == 10,240
# .916666666 == 704  *16 == 11,264
# 1 == 768  *16 == 12,288

# so my quantization function has to take in "note" and return the above
# where "note" < 12,288
# other rules: where note == 1 to 512, return 0
# where note = 513 to 1536, return 1024
# where note = 1537 to 2560, return 2048
# so: it's all multiples of 1024
# so we need a fn that says For 1 to 512, return 0
# for 513 to 1536, return 1
# for 1537 to 2560 return 2
# so first, subtract 512, then . . .

test_notes = [1024, 
              2048, 
              3072, 
              4096,
              7168,
              9216,]

enabled_notes = {0:0, 
                 1024:1, 
                 2048:0,
                 3072:1,
                 4096:1,
                 5120:0,
                 6144:0,
                 7168:0,
                 8192:1,
                 9216:0,
                 10240:1,
                 11264:1,
                 }

'''sw1: 0000
sw2: 1024
sw3: 2048
sw4: 3072
sw5: 4096
sw6: 5120
sw7: 6144
sw8: 7168
sw9: 8192
sw10: 9216
sw11: 10240
sw12: 11264'''

def test_find_nearest_enabled():
  # first, high remainder:
  remainder = 706
  for note in test_notes:
    print("testing", note, "against", enabled_notes, "with remainder", remainder)
    test_note = find_nearest_enabled(note, remainder, enabled_notes) 
    print("got", test_note)
    assert test_note in enabled_notes
  # next, low remainder:
  remainder = 308
  for note in test_notes:
    print("testing", note, "against", enabled_notes, "with remainder", remainder)
    test_note = find_nearest_enabled(note, remainder, enabled_notes) 
    assert test_note in enabled_notes