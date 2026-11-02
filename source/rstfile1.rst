.. START:section:0:0
Overview
========

.. END:section:0:0

.. START:main_content:0:0
This document describes how to read temperature and humidity measurements from the 7SEMI ES1351X sensor connected to the phyBOARD-Wega and transmit the data to ThingsBoard Cloud using MQTT.

The implementation consists of two Python files: a sensor driver that reads measurements over I²C and an application that publishes the measurements to ThingsBoard Cloud.

.. END:main_content:0:0

.. START:section:0:1
System Architecture
===================

.. END:section:0:1

Data Flow:
----------

ES1351X Sensor → I²C → phyBOARD-Wega → Python Application → MQTT → ThingsBoard Cloud

.. START:section:0:2
Prerequisites
=============

.. END:section:0:2

.. START:list:0:2:0

.. LIST_META: {"type": "bullet", "head": "", "items": ["phyBOARD-Wega running Linux.", "7SEMI ES1351X temperature and humidity sensor connected over I²C.", "Python 3 installed on the board.", "An enabled I²C interface.", "Internet connectivity from the board.", "A ThingsBoard Cloud account and device access token."]}

- phyBOARD-Wega running Linux.
- 7SEMI ES1351X temperature and humidity sensor connected over I²C.
- Python 3 installed on the board.
- An enabled I²C interface.
- Internet connectivity from the board.
- A ThingsBoard Cloud account and device access token.

.. END:list:0:2:0

.. START:section:0:3
Software Implementation
=======================

.. END:section:0:3

.. START:main_content:0:3
The application uses two Python files:

.. END:main_content:0:3

.. START:table:0:3:0

.. csv-table::
   :header: "File Name", "Purpose"
   :widths: 35, 65
   :align: center

   "``es1351x.py``", "Reads temperature and humidity measurements from the sensor using I²C."
   "``send_to_thingsboard.py``", "Publishes sensor measurements to ThingsBoard Cloud using MQTT."

.. END:table:0:3:0

.. START:section:0:4
Sensor Driver — es1351x.py
==========================

.. END:section:0:4

Save the following code as es1351x.py.

.. START:code:0:4:1

.. code-block:: console

   #!/usr/bin/env python3
   """ES1351X temperature and humidity sensor driver over Linux I2C."""
   
   import fcntl
   import os
   import sys
   import time
   
   I2C_SLAVE = 0x0703
   I2C_SLAVE_FORCE = 0x0706
   
   CMD_MEASURE_HIGH = 0xFD
   CMD_MEASURE_MED = 0xF6
   CMD_MEASURE_LOW = 0xE0
   CMD_SERIAL = 0x89
   CMD_SOFT_RESET = 0x94
   
   
   def crc8(data):
       """Calculate CRC-8 using polynomial 0x31 and initial value 0xFF."""
       crc = 0xFF
   
       for b in data:
           crc ^= b
   
           for _ in range(8):
               if crc & 0x80:
                   crc = ((crc << 1) ^ 0x31) & 0xFF
               else:
                   crc = (crc << 1) & 0xFF
   
       return crc
   
   
   assert crc8(b"\xBE\xEF") == 0x92
   
   
   class ES1351X:
       def __init__(self, bus=0, addr=0x44):
           self.fd = os.open("/dev/i2c-%d" % bus, os.O_RDWR)
   
           try:
               fcntl.ioctl(self.fd, I2C_SLAVE, addr)
           except OSError:
               fcntl.ioctl(self.fd, I2C_SLAVE_FORCE, addr)
   
       def close(self):
           if self.fd is not None:
               os.close(self.fd)
               self.fd = None
   
       def _read6(self, retries=10):
           """Read six bytes from the sensor."""
   
           for _ in range(retries):
               try:
                   data = os.read(self.fd, 6)
   
                   if len(data) == 6:
                       return data
   
               except OSError:
                   pass
   
               time.sleep(0.005)
   
           raise IOError("Sensor did not return data; check I2C configuration.")
   
       @staticmethod
       def _check(word):
           if crc8(word[0:2]) != word[2]:
               raise IOError("CRC error in word %s" % word.hex())
   
       def soft_reset(self):
           os.write(self.fd, bytes([CMD_SOFT_RESET]))
           time.sleep(0.002)
   
       def serial_number(self):
           os.write(self.fd, bytes([CMD_SERIAL]))
           time.sleep(0.010)
   
           data = self._read6()
   
           self._check(data[0:3])
           self._check(data[3:6])
   
           return (
               (data[0] << 24)
               | (data[1] << 16)
               | (data[3] << 8)
               | data[4]
           )
   
       def measure(self, cmd=CMD_MEASURE_HIGH):
           """Return temperature in Celsius and relative humidity in percent."""
   
           delays = {
               CMD_MEASURE_HIGH: 0.010,
               CMD_MEASURE_MED: 0.006,
               CMD_MEASURE_LOW: 0.003,
           }
   
           if cmd not in delays:
               raise ValueError("Unsupported measurement command")
   
           os.write(self.fd, bytes([cmd]))
           time.sleep(delays[cmd])
   
           data = self._read6()
   
           self._check(data[0:3])
           self._check(data[3:6])
   
           t_ticks = (data[0] << 8) | data[1]
           rh_ticks = (data[3] << 8) | data[4]
   
           temperature = -45.0 + 175.0 * t_ticks / 65535.0
           humidity = -6.0 + 125.0 * rh_ticks / 65535.0
   
           humidity = max(0.0, min(100.0, humidity))
   
           return temperature, humidity
   
   
   def main():
       bus = int(sys.argv[1]) if len(sys.argv) > 1 else 0
       sensor = ES1351X(bus=bus)
   
       try:
           sensor.soft_reset()
   
           try:
               print("Serial number: 0x%08X" % sensor.serial_number())
           except IOError as error:
               print("Serial read failed:", error)
   
           while True:
               try:
                   temperature, humidity = sensor.measure()
   
                   print(
                       "Temperature: %6.2f C (%6.2f F) "
                       "Humidity: %6.2f %%RH"
                       % (
                           temperature,
                           temperature * 9 / 5 + 32,
                           humidity,
                       )
                   )
   
               except IOError as error:
                   print("Sensor read error:", error, file=sys.stderr)
   
               time.sleep(1.0)
   
       except KeyboardInterrupt:
           print("\nSensor monitoring stopped.")
   
       finally:
           sensor.close()
   
   
   if __name__ == "__main__":
       main()

.. END:code:0:4:1

MQTT Application — send_to_thingsboard.py
-----------------------------------------

Save the following code in the same directory as es1351x.py.

The application reads sensor measurements and sends them to ThingsBoard Cloud using MQTT 3.1.1.

.. START:code:0:4:4

.. code-block:: console

   #!/usr/bin/env python3
   """Publish ES1351X readings to ThingsBoard Cloud using MQTT 3.1.1."""
   
   import json
   import socket
   import ssl
   import struct
   import sys
   import time
   
   from es1351x import ES1351X
   
   
   BROKER = "mqtt.thingsboard.cloud"
   PORT = 1883
   USE_TLS = False
   CA_FILE = None
   
   ACCESS_TOKEN = "YOUR-DEVICE-ACCESS-TOKEN"
   CLIENT_ID = "phyboard-wega-es1351x"
   
   INTERVAL = 10
   KEEPALIVE = 60
   I2C_BUS = 0
   
   TOPIC = "v1/devices/me/telemetry"
   
   
   def enc_str(value):
       data = value.encode("utf-8")
       return struct.pack("!H", len(data)) + data
   
   
   def enc_len(length):
       output = bytearray()
   
       while True:
           digit = length % 128
           length //= 128
   
           if length:
               digit |= 0x80
   
           output.append(digit)
   
           if not length:
               return bytes(output)
   
   
   def recv_exact(sock, length):
       buffer = b""
   
       while len(buffer) < length:
           chunk = sock.recv(length - len(buffer))
   
           if not chunk:
               raise IOError("Connection closed by broker")
   
           buffer += chunk
   
       return buffer
   
   
   def recv_packet(sock):
       header = recv_exact(sock, 1)[0]
   
       multiplier = 1
       remaining_length = 0
   
       for _ in range(4):
           digit = recv_exact(sock, 1)[0]
           remaining_length += (digit & 0x7F) * multiplier
   
           if not digit & 0x80:
               break
   
           multiplier *= 128
   
       else:
           raise IOError("Invalid MQTT remaining-length field")
   
       body = recv_exact(sock, remaining_length)
   
       return header, body
   
   
   class MQTT:
       def __init__(self):
           self.sock = None
   
       def connect(self):
           if ACCESS_TOKEN == "YOUR-DEVICE-ACCESS-TOKEN":
               raise ValueError(
                   "Configure ACCESS_TOKEN with your ThingsBoard device token."
               )
   
           sock = socket.create_connection(
               (BROKER, PORT),
               timeout=15
           )
   
           try:
               if USE_TLS:
                   context = ssl.create_default_context(cafile=CA_FILE)
                   sock = context.wrap_socket(
                       sock,
                       server_hostname=BROKER
                   )
   
               # MQTT 3.1.1: clean session and username.
               flags = 0x02 | 0x80
   
               payload = enc_str(CLIENT_ID) + enc_str(ACCESS_TOKEN)
   
               body = (
                   enc_str("MQTT")
                   + bytes([4, flags])
                   + struct.pack("!H", KEEPALIVE)
                   + payload
               )
   
               sock.sendall(
                   bytes([0x10]) + enc_len(len(body)) + body
               )
   
               header, response = recv_packet(sock)
   
               if header != 0x20 or len(response) != 2:
                   raise IOError("Invalid MQTT CONNACK response")
   
               if response[1] != 0:
                   raise IOError(
                       "MQTT connection refused; code %d" % response[1]
                   )
   
               self.sock = sock
               self.sock.settimeout(None)
   
               print("Connected to", BROKER)
   
           except Exception:
               sock.close()
               raise
   
       def publish(self, topic, payload):
           if self.sock is None:
               raise IOError("MQTT client is not connected")
   
           body = enc_str(topic) + payload.encode("utf-8")
   
           packet = bytes([0x30]) + enc_len(len(body)) + body
   
           self.sock.sendall(packet)
   
       def close(self):
           if self.sock is not None:
               sock = self.sock
               self.sock = None
   
               try:
                   sock.sendall(b"\xE0\x00")
               except OSError:
                   pass
               finally:
                   sock.close()
   
   
   def main():
       sensor = None
       mqtt = MQTT()
   
       try:
           sensor = ES1351X(bus=I2C_BUS)
           sensor.soft_reset()
   
           while True:
               try:
                   temperature, humidity = sensor.measure()
   
                   telemetry = {
                       "temperature": round(temperature, 2),
                       "humidity": round(humidity, 2),
                   }
   
                   if mqtt.sock is None:
                       mqtt.connect()
   
                   mqtt.publish(
                       TOPIC,
                       json.dumps(telemetry)
                   )
   
                   print(
                       "Sent T=%.2f C RH=%.2f %%"
                       % (temperature, humidity)
                   )
   
               except (OSError, IOError, ssl.SSLError) as error:
                   print(
                       "Communication error:",
                       error,
                       "- retrying",
                       file=sys.stderr
                   )
   
                   mqtt.close()
   
               time.sleep(INTERVAL)
   
       except KeyboardInterrupt:
           print("\nApplication stopped.")
   
       finally:
           mqtt.close()
   
           if sensor is not None:
               sensor.close()
   
   
   if __name__ == "__main__":
       main()

.. END:code:0:4:4

.. START:section:0:5
ThingsBoard Cloud Configuration
===============================

.. END:section:0:5

.. START:list:0:5:0

.. LIST_META: {"type": "bullet", "head": "", "items": ["Open ThingsBoard Cloud.", "Navigate to Devices & assets → Devices.", "Create a device named ES1351X_PHYBOARD_WEGA.", "Open the device credentials and copy the access token.", "Update the ACCESS_TOKEN value in send_to_thingsboard.py."]}

- Open ThingsBoard Cloud.
- Navigate to Devices & assets → Devices.
- Create a device named ES1351X_PHYBOARD_WEGA.
- Open the device credentials and copy the access token.
- Update the ACCESS_TOKEN value in send_to_thingsboard.py.

.. END:list:0:5:0

The access token is used to authenticate the device with ThingsBoard Cloud.

Application Execution
---------------------

Place both Python files in the same directory on the phyBOARD-Wega.

Step 1: Verify Python
---------------------

.. START:code:0:5:5

.. code-block:: console

   python3 --version

.. END:code:0:5:5

Check the I²C Interface
-----------------------

.. START:code:0:5:7

.. code-block:: console

   ls /dev/i2c*

.. END:code:0:5:7

If the sensor is connected to bus 0, check for its address:
-----------------------------------------------------------

.. START:code:0:5:9

.. code-block:: console

   i2cdetect -y 0

.. END:code:0:5:9

The example driver uses I²C address 0x44. Verify the actual address and bus against your hardware configuration.

Test the Sensor Driver
----------------------

.. START:code:0:5:12

.. code-block:: console

   python3 es1351x.py

.. END:code:0:5:12

Example output:

.. START:code:0:5:14

.. code-block:: console

   Connected to mqtt.thingsboard.cloud
   Sent T=28.50 C RH=62.00 %
   Sent T=28.52 C RH=61.95 %
   Sent T=28.49 C RH=62.10 %

.. END:code:0:5:14

The application publishes telemetry every 10 seconds.

.. START:section:0:6
Verify Received Telemetry
=========================

.. END:section:0:6

.. START:list:0:6:0

.. LIST_META: {"type": "bullet", "head": "", "items": ["Log in to ThingsBoard Cloud.", "Open Devices.", "Select ES1351X_PHYBOARD_WEGA.", "Open Latest telemetry.", "Verify the temperature and humidity values."]}

- Log in to ThingsBoard Cloud.
- Open Devices.
- Select ES1351X_PHYBOARD_WEGA.
- Open Latest telemetry.
- Verify the temperature and humidity values.

.. END:list:0:6:0

The application publishes telemetry in JSON format:

.. START:code:0:6:2

.. code-block:: console

   {
     "temperature": 28.5,
     "humidity": 62.0
   }

.. END:code:0:6:2

If the values appear and update in ThingsBoard Cloud, telemetry transmission is working.

.. START:section:0:7
Troubleshooting
===============

.. END:section:0:7

.. START:table:0:7:0

.. csv-table::
   :header: "Issue", "Possible Cause", "Recommended Action"
   :widths: 25, 35, 40
   :align: center

   "I²C device unavailable", "Incorrect bus or disabled interface", "Verify the I²C configuration and device node."
   "Sensor read error", "Wiring, address, or communication issue", "Check the connections and sensor address."
   "CRC error", "Invalid sensor response", "Check I²C communication and measurement timing."
   "MQTT connection refused", "Invalid access token or connection settings", "Verify the token, broker, port, and network access."
   "Telemetry not visible", "Failed publish or incorrect device", "Check the connection and the device's Latest telemetry."

.. END:table:0:7:0

.. START:section:0:8
Expected Outcome
================

.. END:section:0:8

The phyBOARD-Wega reads temperature and humidity measurements from the ES1351X sensor and sends the data to ThingsBoard Cloud using MQTT. The received telemetry can be monitored through the device's Latest telemetry section and displayed on dashboards.

.. START:section:0:9
References
==========

.. END:section:0:9

| ThingsBoard Cloud
| ThingsBoard MQTT API Documentation
| ThingsBoard Device Configuration
