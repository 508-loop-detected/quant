

from quantize import \
  hysteresis, \
  quantize, \
  doublecheck, \
  find_nearest_enabled \


test_values = {
0: 0,
300: 0,
511: 0,
512: 1024,
625: 1024,
1024: 1024,
1151: 1024,
1535: 1024,
1536: 2048,
2048: 2048,
3072: 3072,
4096: 4096,
5120: 5120,
6144: 6144,
7168: 7168,
8192: 8192,
9216: 9216,
10240: 10240,
11264: 11264
}


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

'''
sw1: 0000
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
sw12: 11264
'''

enabled_notes = {0:1, 
                 1024:1, 
                 2048:1,
                 3072:1,
                 4096:1,
                 5120:1,
                 6144:1,
                 7168:1,
                 8192:1,
                 9216:1,
                 10240:1,
                 11264:1,
                 99999:0,
                 }

enabled_notes_2 = {0:0, 
                 1024:0, 
                 2048:1,
                 3072:0,
                 4096:1,
                 5120:1,
                 6144:1,
                 7168:0,
                 8192:1,
                 9216:0,
                 10240:1,
                 11264:1,
                 99999:1,
                 }

sample_int_arr = [
                  1, #99999
                  1, #11264
                  1, #6144
                  1, #5120
                  1, #4096
                  0, #3072
                  1, #2048
                  1, #99999
                  0, #0
                  0, #1024
                  1, #10240
                  0, #9216
                  1, #8192
                  0, #7168
                  1, #99999
                  1, #99999
                  ]
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
  ]

'''
# not using GPIOA0
sw12 : 1,
sw7 : 2,
sw6 : 3,
sw5 : 4,
sw4 : 5,
sw3 : 6,
# not using GPIOA7
sw1 : 8,
sw2 : 9,
sw11 : 10,
sw10 : 11,
sw9 : 12,
sw8 : 13,
# not using GPIOB6 aka 14
# not using GPIOB7 aka 15
'''

def test_quantize():
  for key, value in test_values.items():
    # mocking the input scaler + ADC:
    # here is where we start the real quantization
    quantized_value, enabled_note = quantize(key,enabled_notes)
    print("input is", key, "and expected output is", value)
    print("quantized value is", quantized_value,"and enabled note is", enabled_note)
    assert quantized_value == value


def test_find_nearest_enabled():
  # first, high remainder:
  remainder = 706
  for note in test_notes:
    print("testing", note, "against", enabled_notes_2, "with remainder", remainder)
    test_note = find_nearest_enabled(note, remainder, enabled_notes) 
    print("got", test_note)
    assert test_note in enabled_notes_2
  # next, low remainder:
  remainder = 308
  for note in test_notes:
    print("testing", note, "against", enabled_notes_2, "with remainder", remainder)
    test_note = find_nearest_enabled(note, remainder, enabled_notes_2) 
    assert test_note in enabled_notes_2



hysteresis_test_vals = [
  (0,0, False),
  (16,0, False),
  (32,0, False),
  (35,0, True),
  (48,48, False),
  (32,48, False),
  (48,48, False),
  (64,48, False),
  (80,48, False),
  (96,96, False),
  (96,104, False),
  (96,128, False),
  (96,136, True),
]

def test_hysteresis():
  for (key,value,outcome) in hysteresis_test_vals:
    print(key, value)
    assert outcome == hysteresis(key,value)