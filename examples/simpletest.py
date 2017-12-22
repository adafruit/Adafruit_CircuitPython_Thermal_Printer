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
# during power-up and it will show the baud rate).  Most printers use 119200.
uart = busio.UART(TX, RX, baudrate=119200)

# Create the printer instance.
printer = thermal_printer.ThermalPrinter(uart)

# Initialize the printer.  Note this will take a few seconds for the printer
# to warm up and be ready to accept commands (hence calling it explicitly vs.
# automatically in the initializer above).
printer.begin()

# Print a test page:
printer.test_page()

# Move the paper forward two lines:
printer.feed(2)

# Print a line of text:
printer.print('Hello world!')

# Move the paper forward two lines:
printer.feed(2)
