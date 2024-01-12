# quants

<img src="quants.jpeg" width=400>

It's a quantizer. This is my first module that includes a microcontroller and thus source code. There are 5 files:
- main.py
- lib/all_i2c.py
- lib/drive_neopixel.py
- lib/led_matrix.py
- lib/quantize.py

On my module, I compile the libs to bytecode mpy files using the [Circuitpython cross-compiler](https://learn.adafruit.com/welcome-to-circuitpython/library-file-types-and-frozen-libraries#creating-an-mpy-file-3118108)

The microcontroller (really a dev board) this was designed around is the [Adafruit QT Py RP2040](https://learn.adafruit.com/adafruit-qt-py-2040). You can use any Circuitpython-compatible microcontroller if you want to redesign the boards -- you'll just need to modify any/all pinout references in the code :) 

What's the deal with it? It's the same format as the following quantizers you may be familiar with:
- [Intellijel uScale](https://www.modulargrid.net/e/intellijel-%CE%BCscale-v2)
- [Sonic Potions Penrose](https://www.modulargrid.net/e/sonic-potions-penrose-quantizer)
- any/every other quantizer that has a bunch of switches arranged like piano keys

In this case, the switches are submini toggles instead of pushbuttons because I really don't like pushbuttons all that much.

It can be built as a 5HP 3U module, or an 18HP 1U module (PulpLogic format).

There are surface-mount LEDs on the back of the IO board, which fire through holes in the PCB. They're bi-color & you'll need to be careful to use the right ones. You also need light pipes to get to the front panel -- I use Bivar PLPC2-500s.

You'll want to use 2.54mm female headers to mount the QT Py, more than likely, to provide enough room for airflow (and to make it possible to remove it in the future). Adafruit sells these low-profile ones that I haven't found elsewhere: https://www.adafruit.com/product/3008

You can trim 2-3mm off your male headers to get a nice snug fit, & it saves you 3mm in overall depth, if you care about such things. 

For everything else other than the QT Py mount, this module, like many of my modules, uses 2mm-pitch male/female headers. Be sure you order/use the right thing!

Most ICs are SOIC 8/14/16; all passives are 0805. The BOMs prefixed with `fixed` are easier to read; the others can be used along with the Pick-and-place and gerber files to order PCBs.


