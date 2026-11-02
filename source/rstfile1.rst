Application-Side Technical Documentation
========================================

| **Document category:** Application Development
| **Platform:** Linux-based embedded systems
| **Programming language:** Python 3
| **Storage format:** CSV (Comma-Separated Values)

Introduction
------------

Local data storage is an application-level mechanism for saving measurement
data, application records, and operational information directly to the local
filesystem.

In embedded Linux applications, sensors, communication interfaces, and
application processes generate data that can be stored in local files for
future reference, monitoring, analysis, and troubleshooting.

This guide explains how to implement file-based data storage using Python on
Linux-based embedded systems. It covers file creation, data recording,
timestamp management, data retrieval, storage organization, error handling,
and backup procedures. The implementation is designed to be adaptable across
embedded Linux platforms without depending on a specific processor, board, or
hardware architecture.

Objectives
^^^^^^^^^^

The main objectives of local data storage are to:

* Store application-generated data in local files.
* Maintain measurement records with timestamps.
* Organize stored information for easy access.
* Retrieve previously saved records.
* Handle file access and storage errors.
* Monitor storage capacity and file integrity.
* Support data backup and maintenance.

Scope
^^^^^

This guide focuses on application-level data storage using the Linux
filesystem, Python standard-library modules, and CSV files. It does not
require a database server, cloud connection, or external storage service.

The same approach can be adapted for sensor measurements, application data,
device monitoring information, communication logs, and operational or
diagnostic records.

Local Data Storage Architecture
-------------------------------

Local data storage consists of three main operations:

#. **Data acquisition:** Receive data from an application, sensor, or
   communication interface.
#. **Data storage:** Process the received information and save it in local
   files.
#. **Data retrieval:** Read previously stored records for monitoring,
   analysis, or reporting.

The data flow is:

.. code-block:: text

   Data source -> Application -> Data processing -> Local filesystem -> Retrieval

The application receives information from its configured source, processes
it, and stores it in local files. Stored records can subsequently be accessed
using Python applications or standard Linux utilities.

Storage Format
^^^^^^^^^^^^^^

CSV (Comma-Separated Values) is used as the storage format in this
implementation. CSV is suitable for simple application records because it is
human-readable, supports tabular data, can be opened in spreadsheet
applications, can be processed using Python, and requires no database
installation.

Example records (illustrative):

.. list-table::
   :header-rows: 1

   * - Timestamp (UTC)
     - Application
     - Parameter
     - Value
   * - 2026-10-30T04:00:00+00:00
     - Monitoring_App
     - Temperature
     - 28.50
   * - 2026-10-30T04:00:10+00:00
     - Monitoring_App
     - Temperature
     - 28.52
   * - 2026-10-30T04:00:20+00:00
     - Monitoring_App
     - Temperature
     - 28.49

Storage Directory Configuration
-------------------------------

A dedicated directory should be used for application-generated data.
Separating application files from stored data makes maintenance, backup, and
retrieval easier.

Create a storage directory:

.. code-block:: console

   sudo mkdir -p /var/lib/application-data/records

The resulting directory structure is:

.. code-block:: text

   /var/lib/application-data/
   └── records/
       ├── application_data_2026-10-30.csv
       ├── application_data_2026-10-31.csv
       └── application_data_2026-11-01.csv

Each CSV file stores records for one UTC calendar day.

Directory Permissions
^^^^^^^^^^^^^^^^^^^^^

The application must have permission to create and update files. For an
application running under the current Linux user, configure ownership and
permissions as appropriate:

.. code-block:: console

   sudo chown -R "$USER":"$USER" /var/lib/application-data
   chmod 750 /var/lib/application-data
   chmod 750 /var/lib/application-data/records
   ls -ld /var/lib/application-data/records

The directory owner must match the Linux account used to execute the
application. Avoid providing unrestricted write access to all users.

Verify available filesystem capacity before starting data collection:

.. code-block:: console

   df -h

Application Implementation
--------------------------

The implementation uses two Python files:

.. list-table::
   :header-rows: 1

   * - File
     - Purpose
   * - ``store_data.py``
     - Generates or receives application data and saves records in daily CSV files.
   * - ``read_data.py``
     - Retrieves and displays previously stored records.

The examples use generated measurements to demonstrate local storage. In an
actual application, replace the sample data-generation function with data
received from the required sensor, communication interface, or application
module.

Data Storage Application: ``store_data.py``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create ``store_data.py``. The application creates the storage directory,
generates measurement data, creates a UTC timestamp, selects a daily CSV file,
appends records, flushes buffered data, and repeats at the configured
interval.

.. code-block:: python

   #!/usr/bin/env python3
   """Store application measurements in daily CSV files."""

   import csv
   import os
   import random
   import time
   from datetime import datetime, timezone
   from pathlib import Path

   APPLICATION_NAME = "Monitoring_App"
   INTERVAL = 10
   STORAGE_DIR = Path("/var/lib/application-data/records")
   CSV_FIELDS = [
       "timestamp_utc",
       "application",
       "parameter",
       "value",
   ]


   def create_storage_directory():
       """Create the storage directory if it does not exist."""
       STORAGE_DIR.mkdir(parents=True, exist_ok=True)


   def get_storage_file():
       """Return the daily CSV filename for the current UTC date."""
       today = datetime.now(timezone.utc).date()
       filename = "application_data_%s.csv" % today.isoformat()
       return STORAGE_DIR / filename


   def get_application_data():
       """Generate example measurements; replace with real data acquisition."""
       temperature = round(random.uniform(25.0, 35.0), 2)
       humidity = round(random.uniform(40.0, 80.0), 2)
       return [
           ("Temperature", temperature),
           ("Humidity", humidity),
       ]


   def save_measurement(parameter, value):
       """Append an application record to the current daily CSV file."""
       timestamp = datetime.now(timezone.utc)
       storage_file = get_storage_file()
       file_exists = storage_file.exists() and storage_file.stat().st_size > 0

       with open(storage_file, "a", newline="", encoding="utf-8") as file:
           writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
           if not file_exists:
               writer.writeheader()

           writer.writerow({
               "timestamp_utc": timestamp.isoformat(timespec="seconds"),
               "application": APPLICATION_NAME,
               "parameter": parameter,
               "value": value,
           })
           file.flush()
           os.fsync(file.fileno())

       print("Stored: %s = %s" % (parameter, value))
       print("Storage file:", storage_file)


   def main():
       try:
           create_storage_directory()
           print("Storage directory:", STORAGE_DIR)
           print("Application started:", APPLICATION_NAME)

           while True:
               try:
                   measurements = get_application_data()
                   for parameter, value in measurements:
                       save_measurement(parameter, value)
               except OSError as error:
                   print("Storage error:", error)

               time.sleep(INTERVAL)
       except KeyboardInterrupt:
           print("\nApplication stopped.")


   if __name__ == "__main__":
       main()

How the Storage Application Works
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* ``STORAGE_DIR`` defines where application records are stored.
* ``INTERVAL`` sets the time between collection cycles; this example collects
  data every 10 seconds.
* ``get_application_data()`` generates sample temperature and humidity
  values. Replace this function with the actual data-acquisition method.
* ``get_storage_file()`` creates a filename using the current UTC date, so a
  new file is selected automatically when the UTC date changes.
* ``save_measurement()`` writes the timestamp, application name, parameter,
  and value as a CSV record.
* ``file.flush()`` and ``os.fsync()`` flush Python's buffered data and request
  that the operating system synchronize the file with the storage device.
  These operations improve durability but cannot guarantee protection from
  every power failure or hardware failure.

Data Retrieval Application
--------------------------

The retrieval application supports reading the latest stored records, reading
records for a specific date, displaying timestamps and measurement values,
and selecting how many records to display.

Create ``read_data.py`` with the following code:

.. code-block:: python

   #!/usr/bin/env python3
   """Retrieve application measurement records from local CSV storage."""

   import argparse
   import csv
   import sys
   from collections import deque
   from datetime import date
   from pathlib import Path

   STORAGE_DIR = Path("/var/lib/application-data/records")


   def read_records(target_date=None, last=20):
       if target_date:
           files = [
               STORAGE_DIR / ("application_data_%s.csv" % target_date)
           ]
       else:
           files = sorted(STORAGE_DIR.glob("application_data_*.csv"))

       if not files:
           print("No application data files found.")
           return

       records = deque(maxlen=last)
       for storage_file in files:
           if not storage_file.is_file():
               continue

           try:
               with open(
                   storage_file,
                   "r",
                   newline="",
                   encoding="utf-8",
               ) as file:
                   reader = csv.DictReader(file)
                   for row in reader:
                       if row.get("timestamp_utc"):
                           records.append(row)
           except (OSError, csv.Error) as error:
               print(
                   "Unable to read %s: %s" % (storage_file, error),
                   file=sys.stderr,
               )

       if not records:
           print("No measurement records available.")
           return

       print("\nStored Application Records\n")
       print(
           "{:<27} {:<20} {:<18} {:<12}".format(
               "Timestamp (UTC)",
               "Application",
               "Parameter",
               "Value",
           )
       )
       print("-" * 80)

       for row in records:
           print(
               "{:<27} {:<20} {:<18} {:<12}".format(
                   row.get("timestamp_utc", ""),
                   row.get("application", ""),
                   row.get("parameter", ""),
                   row.get("value", ""),
               )
           )

       print("\nTotal records displayed:", len(records))


   def main():
       parser = argparse.ArgumentParser(
           description="Retrieve locally stored application data."
       )
       parser.add_argument(
           "--date",
           help="Retrieve records for a UTC date (YYYY-MM-DD).",
       )
       parser.add_argument(
           "--last",
           type=int,
           default=20,
           help="Number of latest records to display.",
       )
       args = parser.parse_args()

       if args.last <= 0:
           parser.error("--last must be greater than zero")

       if args.date:
           try:
               date.fromisoformat(args.date)
           except ValueError:
               parser.error("Invalid date. Use YYYY-MM-DD.")

       read_records(target_date=args.date, last=args.last)


   if __name__ == "__main__":
       main()

Retrieve the latest 20 records:

.. code-block:: console

   python3 read_data.py

Display the latest 50 records:

.. code-block:: console

   python3 read_data.py --last 50

Retrieve records for a particular UTC date, such as 30 October 2026:

.. code-block:: console

   python3 read_data.py --date 2026-10-30

For a date query, the application reads the corresponding daily CSV file and
displays up to the requested number of records.

Application Deployment and Execution
------------------------------------

The application files must be available on the target Linux system before
execution. Keep scripts separate from stored measurement files:

.. code-block:: text

   application/
   ├── store_data.py
   └── read_data.py

.. code-block:: text

   /var/lib/application-data/records/
   ├── application_data_2026-10-30.csv
   └── application_data_2026-10-31.csv

This separation makes application maintenance and data management easier.

Check the installed Python version:

.. code-block:: console

   python3 --version

The scripts use Python standard-library modules and do not require additional
Python packages.

Create the storage directory and configure ownership for the account that
will run the application:

.. code-block:: console

   sudo mkdir -p /var/lib/application-data/records
   sudo chown -R "$USER":"$USER" /var/lib/application-data

Start the data storage application:

.. code-block:: console

   python3 store_data.py

The application generates example records and stores them in the daily CSV
file. Press ``Ctrl+C`` to stop data collection.

List the generated CSV files and inspect a file:

.. code-block:: console

   ls -lh /var/lib/application-data/records/
   cat /var/lib/application-data/records/application_data_2026-10-30.csv

The filename should match the UTC date on which the data was recorded.

Expected Output and Validation
------------------------------

After starting the application, the terminal should display output similar to
the following. The values are randomly generated examples.

.. code-block:: text

   Storage directory: /var/lib/application-data/records
   Application started: Monitoring_App
   Stored: Temperature = 29.45
   Storage file: /var/lib/application-data/records/application_data_2026-10-30.csv
   Stored: Humidity = 61.25
   Storage file: /var/lib/application-data/records/application_data_2026-10-30.csv
   Stored: Temperature = 30.12
   Storage file: /var/lib/application-data/records/application_data_2026-10-30.csv

An example CSV file contains:

.. code-block:: text

   timestamp_utc,application,parameter,value
   2026-10-30T04:00:00+00:00,Monitoring_App,Temperature,29.45
   2026-10-30T04:00:00+00:00,Monitoring_App,Humidity,61.25
   2026-10-30T04:00:10+00:00,Monitoring_App,Temperature,30.12
   2026-10-30T04:00:10+00:00,Monitoring_App,Humidity,60.85

Each row represents one application measurement. Verify retrieval with:

.. code-block:: console

   python3 read_data.py --last 10

Example retrieval output:

.. code-block:: text

   Stored Application Records

   Timestamp (UTC)           Application          Parameter          Value
   --------------------------------------------------------------------------------
   2026-10-30T04:00:00+00:00 Monitoring_App       Temperature        29.45
   2026-10-30T04:00:00+00:00 Monitoring_App       Humidity           61.25
   2026-10-30T04:00:10+00:00 Monitoring_App       Temperature        30.12
   2026-10-30T04:00:10+00:00 Monitoring_App       Humidity           60.85

   Total records displayed: 4

Use this checklist to validate a deployment:

.. list-table::
   :header-rows: 1

   * - Test case
     - Expected result
   * - Storage directory creation
     - Directory is created successfully.
   * - Application initialization
     - Application starts without errors.
   * - Data acquisition
     - Example measurement values are generated.
   * - CSV file creation
     - A daily CSV file is created.
   * - Record insertion
     - Each measurement is appended as a new row.
   * - Timestamp generation
     - Each record contains a UTC timestamp.
   * - Data retrieval
     - Previously stored records are displayed.
   * - Date-based retrieval
     - Records for the selected date are retrieved.
   * - Application termination
     - Application exits using ``Ctrl+C``.
   * - File permissions
     - Application can read and write its storage files.

Error Handling and Data Integrity
---------------------------------

Local storage applications must handle errors to prevent unexpected
termination and avoid treating unsuccessful writes as successfully stored
measurements.

File Access Errors
^^^^^^^^^^^^^^^^^^

File access errors can occur when the storage directory cannot be created,
the application lacks write permission, the filesystem is mounted as
read-only, or the storage device becomes unavailable. The example reports
write errors and reports retrieval errors to standard error.

Disk Space Limitations
^^^^^^^^^^^^^^^^^^^^^^

Measurement files continue to grow while the application is running. Monitor
available storage and the size of the data directory:

.. code-block:: console

   df -h
   du -sh /var/lib/application-data/records

If available storage becomes low, review the stored files and apply an
approved retention or backup policy.

Data Integrity
^^^^^^^^^^^^^^

The implementation uses CSV headers and structured records to maintain a
consistent file format. After writing each record, it calls
``file.flush()`` and ``os.fsync(file.fileno())`` to request synchronization
with the filesystem. Sudden power loss, storage hardware failure, or
filesystem corruption can still result in incomplete or lost records.
Applications requiring stronger reliability may need recovery checks,
redundant storage, or power-failure protection.

Timestamp Management
^^^^^^^^^^^^^^^^^^^^

The application uses UTC timestamps to avoid ambiguity when the system's
local timezone changes. For example:

.. code-block:: text

   2026-10-30T04:00:00+00:00

Ensure that the Linux system clock is configured correctly; incorrect system
time results in inaccurate measurement timestamps.

Storage Maintenance and Backup
------------------------------

Define a maintenance strategy as the application continues to collect data.
Monitor filesystem capacity, inspect individual files, and check total
directory usage:

.. code-block:: console

   df -h
   ls -lh /var/lib/application-data/records/
   du -sh /var/lib/application-data/records/

Create a compressed backup using the Linux ``tar`` utility:

.. code-block:: console

   tar -czf application_data_backup.tar.gz \
       -C /var/lib/application-data records

Verify the archive:

.. code-block:: console

   ls -lh application_data_backup.tar.gz

Restore Stored Records
^^^^^^^^^^^^^^^^^^^^^^

Create the destination directory and restore the archive:

.. code-block:: console

   sudo mkdir -p /var/lib/application-data
   sudo tar -xzf application_data_backup.tar.gz \
       -C /var/lib/application-data
   ls -lh /var/lib/application-data/records/

Restore backups into a separate location or verify existing files before
restoring. Extracting into an active storage directory may overwrite files
with matching names.

Data Retention
^^^^^^^^^^^^^^

A retention policy defines how long application records should be maintained.
For example, an application may retain records for 90 days and archive older
files. Select the retention period according to available storage capacity,
application requirements, customer data retention requirements, and backup
and recovery requirements.

The example implementation does not automatically delete old files.
Automatic cleanup should only be introduced after the retention policy has
been approved.

Troubleshooting
---------------

.. list-table::
   :header-rows: 1

   * - Issue
     - Possible cause
     - Recommended action
   * - Storage directory not created
     - Insufficient permissions
     - Check directory ownership and permissions.
   * - Permission denied
     - Application user lacks write access
     - Configure the correct directory ownership.
   * - CSV file not generated
     - Invalid storage path or filesystem issue
     - Verify the configured directory and filesystem status.
   * - No measurement records
     - Data acquisition function not working
     - Check the application data source.
   * - Incorrect timestamps
     - System clock not configured correctly
     - Verify the system date and time.
   * - Storage space exhausted
     - Too many stored records
     - Check filesystem usage and apply the retention policy.
   * - Unable to retrieve records
     - Incorrect filename or missing file
     - Verify the daily CSV file and storage path.
   * - Incomplete final record
     - Unexpected shutdown or storage failure
     - Inspect the CSV file and check filesystem health.

Useful Linux diagnostic commands:

.. code-block:: console

   date -u
   df -h
   ls -lh /var/lib/application-data/records/
   dmesg | tail -50

These commands help identify filesystem, storage, and system-level issues.

Security and Operational Considerations
---------------------------------------

Application-generated files may contain operational information that should
be protected from unauthorized access. Recommended practices include:

* Store application data in a dedicated directory.
* Restrict file permissions to authorized users.
* Do not store passwords, access tokens, or credentials in measurement files.
* Monitor available filesystem capacity.
* Maintain backups of important records.
* Validate retrieved records before using them for further processing.
* Check backup and retention requirements before deleting stored records.
* Run applications under an appropriate Linux service account instead of
  using root privileges unnecessarily.

For production deployments, access to stored records should follow the
security policies of the target system.

Conclusion
----------

Local data storage provides a simple and effective mechanism for maintaining
application-generated records on Linux-based embedded systems. Using Python
and CSV files, applications can generate records, attach timestamps, organize
data into daily files, and retrieve previously stored information without
requiring a database server or continuous network connectivity.

The implementation in this guide provides a basic file-based storage
solution that can be adapted to different application requirements and
Linux-based embedded platforms.

References
----------

* `Python CSV Module Documentation <https://docs.python.org/3/library/csv.html>`_
* `Python pathlib Documentation <https://docs.python.org/3/library/pathlib.html>`_
* `Python File I/O Documentation <https://docs.python.org/3/tutorial/inputoutput.html>`_
* `Python datetime Documentation <https://docs.python.org/3/library/datetime.html>`_
* `Linux Filesystem Documentation <https://www.kernel.org/doc/html/latest/filesystems/index.html>`_
