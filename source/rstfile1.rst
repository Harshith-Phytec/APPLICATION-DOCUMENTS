.. START:section:0:0
1. Overview
===========

.. END:section:0:0

.. START:main_content:0:0
Sensor integration and data acquisition involve connecting a hardware peripheral to an embedded Linux platform, verifying its availability, establishing communication, and retrieving sensor data through an application.

This document describes the general procedure for integrating and testing peripherals using Linux commands and application-level testing. The procedure can be adapted for interfaces such as **I²C, SPI, UART, GPIO,** and other supported peripherals.

.. END:main_content:0:0

.. START:section:0:1
2. Check Peripheral Availability
================================

.. END:section:0:1

.. START:main_content:0:1
Before developing or executing an application, **verify that the required peripheral is enabled** and accessible on the target board.

.. END:main_content:0:1

Step 1: Identify Available Peripheral Devices
---------------------------------------------

.. START:code:0:1:1

.. code-block:: console

   ls /dev/i2c*
   ls /dev/spidev*
   ls /dev/tty*

.. END:code:0:1:1

These commands list the available I²C, SPI, and serial device nodes, respectively. The presence of a device node does not necessarily confirm that the peripheral is connected or functioning correctly.

Step 2: Check I²C Bus Availability
----------------------------------

For an I²C-based peripheral, use:

.. START:code:0:1:5

.. code-block:: console

   i2cdetect -l

.. END:code:0:1:5

This command lists the I²C buses registered with the Linux system.

To inspect a particular bus, for example bus 0:

.. START:code:0:1:7

.. code-block:: console

   i2cdetect -y 0

.. END:code:0:1:7

Check whether the expected peripheral address appears in the scan. The bus number and device address depend on the hardware configuration.

.. START:note:0:1:9

.. note::

   Perform an I²C scan only when appropriate for the peripheral. Some devices may not respond to scanning, and scanning can interfere with certain devices or drivers.

.. END:note:0:1:9

Step 3: Check Kernel Messages
-----------------------------

.. START:code:0:1:11

.. code-block:: console

   dmesg | grep -i -E "i2c|spi|uart|sensor"

.. END:code:0:1:11

Review the output for peripheral initialization messages, driver errors, or communication-related issues.

Step 4: Verify Device Permissions
---------------------------------

For an I²C device on bus 0:

.. START:code:0:1:14

.. code-block:: console

   ls -l /dev/i2c-0

.. END:code:0:1:14

Check whether the current user has permission to access the device. Use appropriate permissions or elevated privileges when required.

.. START:section:0:2
3. Verify Peripheral Communication
==================================

.. END:section:0:2

.. START:main_content:0:2
After confirming that the peripheral interface is available, verify communication between the Linux system and the connected hardware.

For an I²C sensor, confirm the following:

.. END:main_content:0:2

.. START:list:0:2:0

.. LIST_META: {"type": "bullet", "head": "", "items": ["The sensor has the correct power supply.", "The SDA and SCL connections are correct.", "The sensor is connected to the intended I²C bus.", "The I²C address matches the sensor configuration.", "No conflicting kernel driver or application is interfering with communication."]}

- The sensor has the correct power supply.
- The SDA and SCL connections are correct.
- The sensor is connected to the intended I²C bus.
- The I²C address matches the sensor configuration.
- No conflicting kernel driver or application is interfering with communication.

.. END:list:0:2:0

If the peripheral is detected, proceed with application-level testing. If it is not detected, investigate the hardware connections, device tree configuration, kernel support, and interface settings before proceeding.

.. START:section:0:3
4. Application Development
==========================

.. END:section:0:3

.. START:main_content:0:3
Develop an application using the programming language and interface appropriate for the target peripheral.

For a Linux I²C sensor, a Python application can use the Linux I²C device interface to send commands and receive measurement data.

The application should implement the following operations:

.. END:main_content:0:3

.. START:list:0:3:0

.. LIST_META: {"type": "auto", "head": "", "items": ["Open the appropriate peripheral device.", "Configure the required bus and device address.", "Initialize the peripheral if required.", "Send the appropriate command or request.", "Read the response from the peripheral.", "Validate the received data.", "Convert raw data into meaningful engineering values.", "Display or forward the processed data to the application layer.", "Handle communication errors and release resources when the application exits."]}

1. Open the appropriate peripheral device.
2. Configure the required bus and device address.
3. Initialize the peripheral if required.
4. Send the appropriate command or request.
5. Read the response from the peripheral.
6. Validate the received data.
7. Convert raw data into meaningful engineering values.
8. Display or forward the processed data to the application layer.
9. Handle communication errors and release resources when the application exits.

.. END:list:0:3:0

The exact commands, data format, timing requirements, and conversion formulas must follow the relevant peripheral datasheet.

.. START:section:0:4
5. Example: I²C Sensor Application
==================================

.. END:section:0:4

.. START:main_content:0:4
As an implementation example, the 7SEMI ES1351X temperature and humidity sensor can be accessed through the Linux I²C interface.

The example Python application performs the following operations:

.. END:main_content:0:4

.. START:list:0:4:0

.. LIST_META: {"type": "bullet", "head": "", "items": ["Initializes the sensor using a software reset command.", "Reads the sensor serial number.", "Requests temperature and humidity measurements.", "Reads the sensor response.", "Checks the received data using CRC-8.", "Converts raw measurement values into temperature and relative humidity.", "Displays the readings periodically."]}

- Initializes the sensor using a software reset command.
- Reads the sensor serial number.
- Requests temperature and humidity measurements.
- Reads the sensor response.
- Checks the received data using CRC-8.
- Converts raw measurement values into temperature and relative humidity.
- Displays the readings periodically.

.. END:list:0:4:0

The 7SEMI ES1351X temperature and humidity sensor is used as an example to demonstrate sensor integration and data acquisition through the Linux I²C interface.

The Python application communicates with the sensor using its configured I²C address (0x44). It initializes the sensor, retrieves its serial number, reads temperature and humidity measurements, validates the received data using CRC-8, and displays the measurements periodically.

The following source code implements the sensor communication and data acquisition process.

Python Source Code (es1351x.py)
-------------------------------

.. START:code:0:4:3

.. code-block:: console

   nano es1351x.py

.. END:code:0:4:3

.. START:code:0:4:4

.. code-block:: console

   #!/usr/bin/env python3
   """7SEMI ES1351X (ES13511/2/3) humidity + temperature sensor over Linux I2C."""
   import fcntl, os, sys, time
   
   I2C_SLAVE       = 0x0703
   I2C_SLAVE_FORCE = 0x0706
   
   CMD_MEASURE_HIGH = 0xFD   # high repeatability, max 8.3 ms
   CMD_MEASURE_MED  = 0xF6   # medium repeatability, max 4.5 ms
   CMD_MEASURE_LOW  = 0xE0   # low repeatability, max 1.6 ms
   CMD_SERIAL       = 0x89
   CMD_SOFT_RESET   = 0x94
   
   def crc8(data):
       """CRC-8, poly 0x31, init 0xFF, no reflection, no final XOR."""
       crc = 0xFF
       for b in data:
           crc ^= b
           for _ in range(8):
               crc = ((crc << 1) ^ 0x31) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
       return crc
   
   assert crc8(b"\xBE\xEF") == 0x92  # datasheet check value
   
   
   class ES1351X:
       def __init__(self, bus=0, addr=0x44):
           self.fd = os.open("/dev/i2c-%d" % bus, os.O_RDWR)
           try:
               fcntl.ioctl(self.fd, I2C_SLAVE, addr)
           except OSError:  # address claimed by a kernel driver
               fcntl.ioctl(self.fd, I2C_SLAVE_FORCE, addr)
   
       def close(self):
           os.close(self.fd)
   
       def _read6(self, retries=10):
           # Sensor NACKs the read header while it is still measuring.
           for _ in range(retries):
               try:
                   data = os.read(self.fd, 6)
                   if len(data) == 6:
                       return data
               except OSError:
                   pass
               time.sleep(0.005)
           raise IOError("sensor did not return data (check wiring/address)")
   
       @staticmethod
       def _check(word):
           if crc8(word[0:2]) != word[2]:
               raise IOError("CRC error in word %s" % word.hex())
   
       def soft_reset(self):
           os.write(self.fd, bytes([CMD_SOFT_RESET]))
           time.sleep(0.002)  # max 1 ms
   
       def serial_number(self):
           os.write(self.fd, bytes([CMD_SERIAL]))
           time.sleep(0.01)
           d = self._read6()
           self._check(d[0:3]); self._check(d[3:6])
           return (d[0] << 24) | (d[1] << 16) | (d[3] << 8) | d[4]
   
       def measure(self, cmd=CMD_MEASURE_HIGH):
           """Returns (temperature_C, relative_humidity_percent)."""
           os.write(self.fd, bytes([cmd]))
           time.sleep({CMD_MEASURE_HIGH: 0.010,
                       CMD_MEASURE_MED: 0.006,
                       CMD_MEASURE_LOW: 0.003}[cmd])
           d = self._read6()
           self._check(d[0:3]); self._check(d[3:6])
           t_ticks  = (d[0] << 8) | d[1]
           rh_ticks = (d[3] << 8) | d[4]
           t_c = -45.0 + 175.0 * t_ticks / 65535.0
           rh  = -6.0 + 125.0 * rh_ticks / 65535.0
           rh  = max(0.0, min(100.0, rh))   # datasheet 4.6: crop to 0..100
           return t_c, rh
   
   if __name__ == "__main__":
       bus = int(sys.argv[1]) if len(sys.argv) > 1 else 0
       s = ES1351X(bus=bus)
       s.soft_reset()
       try:
           print("Serial number: 0x%08X" % s.serial_number())
       except IOError as e:
           print("Serial read failed:", e)
       try:
           while True:
               t, rh = s.measure()
               print("Temperature: %6.2f C   (%6.2f F)   Humidity: %6.2f %%RH"
                     % (t, t * 9 / 5 + 32, rh))
               time.sleep(1.0)
       except KeyboardInterrupt:
           pass
       finally:
           s.close()

.. END:code:0:4:4

Copy the sensor application code into the file and save it.

Before running the application, verify that the configured I²C bus and sensor address match the target hardware.

.. START:section:0:5
6. Execute the Application
==========================

.. END:section:0:5

.. START:main_content:0:5
For a sensor connected to I²C bus 0:

.. END:main_content:0:5

.. START:code:0:5:0

.. code-block:: console

   python3 es1351x.py

.. END:code:0:5:0

For a sensor connected to I²C bus 1:

.. START:code:0:5:2

.. code-block:: console

   python3 es1351x.py 1

.. END:code:0:5:2

The bus number passed to the application must correspond to the bus connected to the sensor.

To stop continuous monitoring, press:

.. START:code:0:5:4

.. code-block:: console

   Ctrl+C

.. END:code:0:5:4

.. START:section:0:6
7. Verify Application Output
============================

.. END:section:0:6

.. START:main_content:0:6
When communication is successful, the application should display the sensor serial number, if supported and successfully retrieved, followed by periodic measurement readings.

output :

.. END:main_content:0:6

.. START:code:0:6:0

.. code-block:: console

   Serial number: 0x12345678
   Temperature:  31.25 C ( 88.25 F) Humidity:  54.32 %RH
   Temperature:  31.27 C ( 88.29 F) Humidity:  54.28 %RH
   Temperature:  31.26 C ( 88.27 F) Humidity:  54.35 %RH
   Temperature:  31.28 C ( 88.30 F) Humidity:  54.31 %RH
   Temperature:  31.29 C ( 88.32 F) Humidity:  54.29 %RH

.. END:code:0:6:0

The readings should be checked for valid formatting, reasonable values, and consistency with the surrounding environmental conditions.

Record the actual output obtained during testing. Do not use illustrative values as measured test results.

.. START:section:0:7
8. Troubleshooting
==================

.. END:section:0:7

.. START:table:0:7:0

.. csv-table::
   :header: "Problem", "Checks and corrective action"
   :widths: 35, 65
   :align: center

   "Peripheral device node is missing", "Verify that the interface is enabled in the device tree and supported by the kernel."
   "I²C bus is unavailable", "Check the kernel configuration, device tree, and registered I²C adapters."
   "Sensor address is not detected", "Verify power, wiring, bus selection, and the address specified in the datasheet."
   "Application cannot open the device", "Check the device path, user permissions, and whether the device exists."
   "Communication fails", "Check the bus configuration, command sequence, timing, and possible driver conflicts."
   "Received data fails CRC validation", "Check the communication connection and confirm the data format and CRC implementation."
   "Sensor readings are unexpected", "Verify the conversion formulas, sensor configuration, wiring, and environmental conditions."
   "Application stops unexpectedly", "Review the error message and add suitable exception handling and resource cleanup."

.. END:table:0:7:0

.. START:section:0:8
9. Testing and Validation
=========================

.. END:section:0:8

.. START:main_content:0:8
Complete the following checks before integrating the peripheral into the main application:

.. END:main_content:0:8

.. START:list:0:8:2

.. LIST_META: {"type": "bullet", "head": "", "items": ["Confirm that the required peripheral interface is available.", "Verify the bus or interface configuration.", "Confirm that the peripheral responds to the expected communication requests.", "Execute the application and verify that data is received.", "Validate the received data according to the peripheral protocol.", "Confirm that the converted measurements are reasonable.", "Test application behavior when communication fails.", "Record the test results and any issues identified."]}

- Confirm that the required peripheral interface is available.
- Verify the bus or interface configuration.
- Confirm that the peripheral responds to the expected communication requests.
- Execute the application and verify that data is received.
- Validate the received data according to the peripheral protocol.
- Confirm that the converted measurements are reasonable.
- Test application behavior when communication fails.
- Record the test results and any issues identified.

.. END:list:0:8:2

.. START:section:0:9
10. Conclusion
==============

.. END:section:0:9

.. START:main_content:0:9
The peripheral integration procedure provides a systematic approach to verifying hardware availability, establishing communication, acquiring data, and validating application output on an embedded Linux platform.

Following these steps helps identify hardware, configuration, driver, and application-level issues before integrating the peripheral into the complete application.

.. END:main_content:0:9
