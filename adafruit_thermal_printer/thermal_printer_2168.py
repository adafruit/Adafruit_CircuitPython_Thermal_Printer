# The MIT License (MIT)
#
# Copyright (c) 2020 Tony DiCola, Grzegorz Nowicki
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
`adafruit_thermal_printer.thermal_printer_2168.ThermalPrinter`
==============================================================

Thermal printer control module built to work with small serial thermal
receipt printers.  Note that these printers have many different firmware
versions and care must be taken to select the appropriate module inside this
package for your firmware printer:

* thermal_printer_2168 = Printers with firmware version 2.168+.
* thermal_printer = The latest printers with firmware version 2.68 up to 2.168
* thermal_printer_264 = Printers with firmware version 2.64 up to 2.68.
* thermal_printer_legacy = Printers with firmware version before 2.64.

* Author(s): Tony DiCola, Grzegorz Nowicki
"""

import math
import imageio
import numpy as np
import adafruit_thermal_printer.thermal_printer as thermal_printer


# pylint: disable=too-many-arguments
class ThermalPrinter(thermal_printer.ThermalPrinter):
    """Thermal printer for printers with firmware version from 2.168"""

    # Barcode types.  These vary based on the firmware version so are made
    # as class-level variables that users can reference (i.e.
    # ThermalPrinter.UPC_A, etc) and write code that is independent of the
    # printer firmware version.
    UPC_A = 65
    UPC_E = 66
    EAN13 = 67
    EAN8 = 68
    CODE39 = 69
    ITF = 70
    CODABAR = 71
    CODE93 = 72
    CODE128 = 73

    def __init__(
        self,
        uart,
        byte_delay_s=0.00057346,
        dot_feed_s=0.0021,
        dot_print_s=0.03,
        auto_warm_up=True,
    ):
        """Thermal printer class.  Requires a serial UART connection with at
        least the TX pin connected.  Take care connecting RX as the printer
        will output a 5V signal which can damage boards!  If RX is unconnected
        the only loss in functionality is the has_paper function, all other
        printer functions will continue to work.  The byte_delay_s, dot_feed_s,
        and dot_print_s values are delays which are used to prevent overloading
        the printer with data.  Use the default delays unless you fully
        understand the workings of the printer and how delays, baud rate,
        number of dots, heat time, etc. relate to each other.
        """
        super().__init__(
            uart,
            byte_delay_s=byte_delay_s,
            dot_feed_s=dot_feed_s,
            dot_print_s=dot_print_s,
            auto_warm_up=auto_warm_up,
        )

    def warm_up(self, heat_time=120):
        """Apparently there are no parameters for setting darkness in 2.168
        (at least commands from 2.68 dont work), So it is little
        compatibility method to reuse older code.
        """
        self._set_timeout(0.5)  # Half second delay for printer to initialize.
        self.reset()

    def print_bitmap(self, file):
        """ Convert bitmap file and print as picture using GS v 0 command """
        # pylint: disable=too-many-locals
        img = imageio.imread(file)
        try:
            if img.shape[2] == 4:  # 3 colors with alpha channel
                red, green, blue, alpha = np.split(img, 4, axis=2)
            else:  # just 3 colors
                red, green, blue = np.split(img, 3, axis=2)

            red = red.reshape(-1)
            green = green.reshape(-1)
            blue = blue.reshape(-1)

            bitmap = list(
                map(
                    lambda x: 0.333 * x[0] + 0.333 * x[1] + 0.333 * x[2],
                    zip(red, green, blue),
                )
            )
            bitmap = np.array(bitmap).reshape([img.shape[0], img.shape[1]])
            bitmap = np.multiply((bitmap > 208).astype(float), 255)

            data_array = np.array(bitmap.astype(np.uint8))

        except IndexError:  # 2D monochromatic array
            data_array = np.array(img)

        assert data_array.shape[1] < 385, "bitmap should be less than 385 pixels wide"
        assert (
            data_array.shape[0] < 65535
        ), "bitmap should be less than 65535 pixels high"

        ### Assertion for height is irrelevant. I tested it for over 6000 pixels high
        ### picture and while it took a long time to send, it printed it without a hitch.
        ### Theoretical maximum is 65535 pixels but I don't want to waste 7m of paper

        data = self._convert_data_horizontally(data_array)

        ### split into two bytes and prepare to format for printer, x and y sizes of an image
        img_x = math.ceil(data_array.shape[1] / 8)
        img_y = data_array.shape[0]
        img_lx = (img_x & 0xFF).to_bytes(1, byteorder="big")
        img_hx = ((img_x & 0xFF00) >> 8).to_bytes(1, byteorder="big")
        img_ly = (img_y & 0xFF).to_bytes(1, byteorder="big")
        img_hy = ((img_y & 0xFF00) >> 8).to_bytes(1, byteorder="big")
        mode = b"\x00"

        self._print_horizontal(mode, img_lx, img_hx, img_ly, img_hy, data)
        # pylint: enable=too-many-locals

    def _print_horizontal(self, mode, img_lx, img_hx, img_ly, img_hy, data):
        """Send "Print Graphics horizontal module data" command,
        GS v 0 and append it with provided data,
        data must conform to printer's required format,
        use _convert_data_horizontally() to convert data from bitmap to this format
        """
        self._uart.write(
            b"\x1D\x76\x30%s%s%s%s%s%s" % (mode, img_lx, img_hx, img_ly, img_hy, data)
        )
        # pylint: disable=invalid-name
        ### this is pain in the butt
        for d in data:
            self._uart.write(d)
        # pylint: enable=invalid-name

    def _write_to_byte(self, pos, byte):
        """Helper method used in _convert_data_horizontally to compress pixel data into bytes"""
        if pos == 0:
            return byte | 0b10000000
        if pos == 1:
            return byte | 0b01000000
        if pos == 2:
            return byte | 0b00100000
        if pos == 3:
            return byte | 0b00010000
        if pos == 4:
            return byte | 0b00001000
        if pos == 5:
            return byte | 0b00000100
        if pos == 6:
            return byte | 0b00000010
        if pos == 7:
            return byte | 0b00000001

    def _convert_data_horizontally(self, data_array):
        """Convert data from numpy array format to printer's horizontal printing module format"""
        x_size = data_array.shape[1]
        y_size = data_array.shape[0]

        datas = bytearray()
        # pylint: disable=invalid-name
        for y in range(y_size):
            for x in range(0, x_size, 8):
                data = 0
                for bit in range(8):
                    try:
                        if data_array[y][x + bit] == 0:
                            data = self._write_to_byte(bit, data)

                    except IndexError:
                        pass
                    finally:
                        pass
                datas.append(data)
        return datas
        # pylint: enable=invalid-name
