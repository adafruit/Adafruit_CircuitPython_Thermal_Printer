# Simple demo of printer functionality.
# Author: Tony DiCola
import board
import busio

# Pick which version thermal printer to import.  Only ONE of these lines should
# be uncommented depending on the version of your printer.  Hold the button on
# the printer as it's powered on and it will print a test page that displays
# the firmware version, like 2.64, 2.68, etc.
# Use this line for printers with version 2.68 or higher:
import adafruit_thermal_printer.thermal_printer as thermal_printer
# Use this line for printers with version 2.64 up to (but not including) 2.68:
#import adafruit_thermal_printer.thermal_printer_264 as thermal_printer
# Use this line for printers with version up to (but not including) 2.64:
#import adafruit_thermal_printer.thermal_printer_legacy as thermal_printer

# Define RX and TX pins for the board's serial port connected to the printer.
# Only the TX pin needs to be configued, and note to take care NOT to connect
# the RX pin if your board doesn't support 5V inputs.  If RX is left unconnected
# the only loss in functionality is checking if the printer has paper--all other
# functions of the printer will work.
RX = board.RX
TX = board.TX

# Create a serial connection for the printer.  You must use the same baud rate
# as your printer is configured (print a test page by holding the button
# during power-up and it will show the baud rate).  Most printers use 19200.
uart = busio.UART(TX, RX, baudrate=19200)

# Create the printer instance.
printer = thermal_printer.ThermalPrinter(uart)

# Initialize the printer.  Note this will take a few seconds for the printer
# to warm up and be ready to accept commands (hence calling it explicitly vs.
# automatically in the initializer above).
printer.begin()

# Check if the printer has paper.  This only works if the RX line is connected
# on your board (but BE CAREFUL as mentioned above this RX line is 5V!)
if printer.has_paper():
    print('Printer has paper!')
else:
    print('Printer might be out of paper, or RX is disconnected!')

# Print a test page:
printer.test_page()

# Move the paper forward two lines:
printer.feed(2)

# Print a line of text:
printer.print('Hello world!')

# Print a bold line of text:
printer.bold = True
printer.print('Bold hello world!')
printer.bold = False

# Print a normal/thin underline line of text:
printer.underline_thin()
printer.print('Thin underline!')

# Print a thick underline line of text:
printer.underline_thick()
printer.print('Thick underline!')

# Disable underlines.
printer.underline_off()

# Print an inverted line.
printer.inverse = True
printer.print('Inverse hello world!')
printer.inverse = False

# Print an upside down line.
printer.upside_down = True
printer.print('Upside down hello!')
printer.upside_down = False

# Print a double height line.
printer.double_height = True
printer.print('Double height!')
printer.double_height = False

# Print a double width line.
printer.double_width = True
printer.print('Double width!')
printer.double_width = False

# Print a strike-through line.
printer.strike = True
printer.print('Strike-through hello!')
printer.strike = False

# Print medium size text.
printer.set_size_medium()
printer.print('Medium size text!')

# Print large size text.
printer.set_size_large()
printer.print('Large size text!')

# Back to normal / small size text.
printer.set_size_small()

# Print center justified text.
printer.justify_center()
printer.print('Center justified!')

# Print right justified text.
printer.justify_right()
printer.print('Right justified!')

# Back to left justified / normal text.
printer.justify_left()

# Print a UPC barcode.
printer.print('UPCA barcode:')
printer.print_barcode('123456789012', printer.UPC_A)

# Feed a few lines to see everything.
printer.feed(2)
