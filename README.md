Input: 0 - 6.6V CV buffered and scaled through some op amp situation

  into the ADC input pin on the M4 feather
  code to:
    - read value

      # SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
      #
      # SPDX-License-Identifier: MIT

      """CircuitPython Essentials Analog In example"""
      import time
      import board
      from analogio import AnalogIn

      analog_in = AnalogIn(board.A1) // USE A2 for INPUT

      def get_voltage(pin):
          return (pin.value * 3.3) / 65536
          # pin.value will be 0-65535

      while True:
          print((get_voltage(analog_in),))
          time.sleep(0.1)






    - quantize to 1/12 V standard

      The Penrose code looks like this:

      #define INPUT_VOLTAGE			5.f	//Volt
      #define OCTAVES				10.f	//octaves
      #define VOLT_PER_OCTAVE			(INPUT_VOLTAGE/OCTAVES) // 0.5
      #define VOLT_PER_NOTE			(VOLT_PER_OCTAVE/12.f)  // 0.04166666666666666667
      #define VOLT_PER_ADC_STEP		(INPUT_VOLTAGE/1024.f)  // 0.0048828125
      #define ADC_STEPS_PER_NOTE		(VOLT_PER_NOTE/VOLT_PER_ADC_STEP) //~8.53


      So my version of that would be:

      #define INPUT_VOLTAGE			3.3.f	//Volt
      #define OCTAVES				11.f	//octaves
      #define VOLT_PER_OCTAVE			(INPUT_VOLTAGE/OCTAVES) // 0.3
      #define VOLT_PER_NOTE			(VOLT_PER_OCTAVE/12.f)  // 0.025
      #define VOLT_PER_ADC_STEP		(INPUT_VOLTAGE/4096.f)  // 0.0008056640625
      #define ADC_STEPS_PER_NOTE		(VOLT_PER_NOTE/VOLT_PER_ADC_STEP) // 31.03030303030303

      So it's a 12-bit ADC but the thingy uses 16-bit numbers so the minimum step is 16

      3.3V / 65536 == 0.000050354003906 volts per 16-bit ADC increment
      0.000050354003906 * 16 == 0.0008056640625 volts per actual 12-bit ADC increment
      31.03030303030303030303 == ADC steps per note
      Can we round? Or if we round, does shitty stuff happen?

      The goal should be that at 1V in, you're always at 0.3V out

      To get 0.3V you'd just tell it to do: 5,957.818181847761483 (LOL)
      But so I'm pretty sure given that you have +/- 8 in either direction due to the chopping off of the bottom 4 LSBs, you could round that to 5958.

      So to get 0.025 (which is our version of .08333333333) you'd do 0.025/0.000050354003906 == 496.484848487313457

      So can you round that to 496????

      496
      922
      1,488
      1,984
      2,480
      2,976
      3,472
      3,968
      4,464
      4,960
      5,456
      5,952

      So if you do round it to 496 then after an octave you're at 5952 instead of 5958

      So this is why he was doing this math like that -- we've lost 6, or about a half per step

      So instead of going up by 496 or 496.5, you multiply 496.5 * 2 == 993

      And then once you've done all your math, divide the final number by 2.

Hmmmm, so this looks promising: 40k   	0.4	    0.0333333333333333	    0.00005035400390625	   
661.979797979797 DAC steps per note

Could safely be rounded to 662 DAC steps per note & not cause any trouble until you got to 22 octaves.

      
      Let's actually think about this. So we're using a scaling op-amp that follows the
      inverting scaling op amp formula:

      Vout = - Rf/Rin x Vin
      Vout = - 30/100 x Vin

      So our VOLT_PER_OCTAVE = .3 because .3V = 30/100 x 1V
      OCTAVES doesn't really matter as long as we stick to the formula, but we can reverse engineer it
      our input voltage range is 3.3V so 3.3V / .3 == 11 octaves maximum range 


    - lookup closest allowable value from 'notes-enabled' array
    - tell correct LED to light up
    - output value via DAC pin

Output: 0 - 3.3V CV buffered and scaled through some op amp situation


# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Analog Out example"""
import board
from analogio import AnalogOut

analog_out = AnalogOut(board.A0) // USE A0 for OUTPUT

while True:
    # Count up from 0 to 65535, with 64 increment
    # which ends up corresponding to the DAC's 10-bit range
    for i in range(0, 65535, 64):
        analog_out.value = i


Hmm, the 51 is 12-bit but is it still constrained to this range?

  The DAC on the SAMD21 is a 10-bit output, from 0-3.3V. So in theory you will have a resolution of 0.0032 Volts per bit. To allow CircuitPython to be general-purpose enough that it can be used with chips with anything from 8 to 16-bit DACs, the DAC takes a 16-bit value and divides it down internally.

  For example, writing 0 will be the same as setting it to 0 - 0 Volts out.

  Writing 5000 is the same as setting it to 5000 / 64 = 78, and 78 / 1024 * 3.3V = 0.25V output.

  Writing 65535 is the same as 1023 which is the top range and you'll get 3.3V output

We should do some tests!


Switch 1 - 12

  into digital I/O pins on _____
  code to:
    - read value
    - update correct slot in 'notes-enabled' array

LED 1 - 12

  fed from digital I/O pins on ______
 




Here's the whole quantize function from Penrose:

#define INPUT_VOLTAGE			5.f	//Volt
#define OCTAVES				10.f	//octaves
#define VOLT_PER_OCTAVE			(INPUT_VOLTAGE/OCTAVES) // 0.5
#define VOLT_PER_NOTE			(VOLT_PER_OCTAVE/12.f)  // 0.04166666666666666667
#define VOLT_PER_ADC_STEP		(INPUT_VOLTAGE/1024.f)  // 0.0048828125
#define ADC_STEPS_PER_NOTE		(VOLT_PER_NOTE/VOLT_PER_ADC_STEP) //~8.53

static uint8_t lastInput=0;
uint8_t quantizeValue(uint16_t input)
{

  // so literally if there are no switches on, it just outputs 0?
  if(io_getActiveSteps()==0)
  {
    //no stepselected
    io_setCurrentQuantizedValue(99); //no active step LED
    return 0;
  }
  
  // this is the hysteresis -- basically, if the thing hasn't changed by at least 2, just return the same value as before
  if(abs(input-lastInput) >= 2)
  {
    lastInput = input;
  } else return lastQuantValue;
  
	//quantize input value to all steps


  // he's concerned about floating point math here, so he multiplies everything by 2 and then divides later
	/* instead of input/ADC_STEPS_PER_NOTE we use the magic number 17 here.
	 * ADC_STEPS_PER_NOTE = 8.5 which will reult in a rounding error pretty quick
	 * so we use ADC_STEPS_PER_NOTE * 2 = 17
	 * we shift the result up by ~ADC_STEPS_PER_NOTE/2 = 8
	 * to bring the note values (played by keyboard fr example) in the middle of a step, 
	 * thus increasing the note tracking over several octaves
	 */
	uint8_t quantValue = ((input<<1)+8)/17;//ADC_STEPS_PER_NOTE;

	//calculate the current active step
	uint8_t octave = quantValue/12;
	uint8_t note = quantValue-(octave*12);

	
	//quantize to active steps
	//search for the lowest matching activated note (lit led)
	int i=0;
	for(;i<13;i++)
	{
	  if( ((1<<  ((note+i)%12) ) & io_getActiveSteps()) != 0) break;
	}
	
	note = note+i;
	if(note>=12)
	{
	  note -= 12;
	  octave++;
	}
	
	quantValue = octave*12+note;
	
	//store to matrix
	io_setCurrentQuantizedValue(note);
	return quantValue*2;
}