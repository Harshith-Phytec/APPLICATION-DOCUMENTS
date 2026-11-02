.. START:section:0:0
Writing systemd Service Files: A Complete Learning Guide
========================================================

.. END:section:0:0

.. START:main_content:0:0
A general, hardware-independent guide to writing, installing, managing and debugging Linux service files.

.. END:main_content:0:0

.. START:section:0:1
Service File and Need
=====================

.. END:section:0:1

.. START:main_content:0:1
| On almost every modern Linux system (Ubuntu, Debian, Yocto-based embedded Linux), the first process started by the kernel is systemd (PID 1). It starts everything else: networking, logging, SSH, and your own programs.
| A **service file** (formally a unit file with the extension .service) is a small text file that tells systemd:

.. END:main_content:0:1

.. START:list:0:1:0

.. LIST_META: {"type": "bullet", "head": "", "items": ["What to run (the command).", "When to run it (at boot, after networking, after another service).", "How to run it (which user, which folder, which environment variables).", "What to do if it fails (restart it, wait, give up)."]}

- What to run (the command).
- When to run it (at boot, after networking, after another service).
- How to run it (which user, which folder, which environment variables).
- What to do if it fails (restart it, wait, give up).

.. END:list:0:1:0

Without a service file you would start your program manually (./myapp), and it would die when you close the terminal or reboot. With a service file, your program starts automatically at boot, restarts if it crashes, and writes logs to a central place.

.. START:note:0:1:2

.. note::

   **Note on other init systems:** Older systems used SysV init scripts (/etc/init.d). Some minimal embedded images (BusyBox) still do. This guide covers systemd, which is the standard today.

.. END:note:0:1:2

.. START:section:0:2
Types of Unit Files
===================

.. END:section:0:2

systemd manages several kinds of units. The file extension tells systemd what kind it is.

.. START:table:0:2:1

.. csv-table::
   :header: "Extension", "Purpose"
   :widths: 25, 75
   :align: center

   "``.service``", "A program or daemon (what this guide focuses on)."
   "``.timer``", "Runs a service on a schedule (like cron)."
   "``.socket``", "Starts a service when a connection arrives."
   "``.target``", "A group of units, like a boot stage (``multi-user.target``)."
   "``.mount``", "A filesystem mount point."
   "``.path``", "Starts a service when a file or folder changes."

.. END:table:0:2:1

.. START:section:0:3
Where Service Files Live
========================

.. END:section:0:3

.. START:table:0:3:0

.. csv-table::
   :header: "Directory", "Meaning", "Priority"
   :widths: 40, 45, 15
   :align: center

   "``/etc/systemd/system/``", "Files written by **you** (the administrator).", "Highest"
   "``/run/systemd/system/``", "Runtime-generated units.", "Medium"
   "``/usr/lib/systemd/system/`` (or ``/lib/systemd/system/``)", "Files installed by packages.", "Lowest"

.. END:table:0:3:0

| **Rule:** put your own services in /etc/systemd/system/. Never edit files in /usr/lib/systemd/system/, because package updates will overwrite your changes. To modify a packaged service, use an override (Section 12).
| Check where a unit is loaded from:

.. START:code:0:3:2

.. code-block:: console

   systemctl status ssh
   systemctl cat ssh

.. END:code:0:3:2

.. START:section:0:4
Anatomy of a Service File
=========================

.. END:section:0:4

A service file is an INI-style file with three main sections:

.. START:code:0:4:1

.. code-block:: console

   [Unit]
   Description=Short human-readable description
   After=network.target
   
   [Service]
   ExecStart=/usr/local/bin/myapp
   Restart=on-failure
   
   [Install]
   WantedBy=multi-user.target

.. END:code:0:4:1

.. START:list:0:4:2

.. LIST_META: {"type": "bullet", "head": "", "items": ["[Unit] describes the service and its relationship to other units (ordering and dependencies).", "[Service] describes how to run the program.", "[Install] describes what happens when you run systemctl enable (which boot stage pulls this service in)."]}

- [Unit] describes the service and its relationship to other units (ordering and dependencies).
- [Service] describes how to run the program.
- [Install] describes what happens when you run systemctl enable (which boot stage pulls this service in).

.. END:list:0:4:2

Syntax rules:

.. START:list:0:4:4

.. LIST_META: {"type": "bullet", "head": "", "items": ["Each line is Key=Value. Keys are case-sensitive.", "Lines starting with # or ; are comments.", "Use \\ at the end of a line to continue onto the next line.", "Do not put inline comments after a value on the same line.", "ExecStart needs an absolute path to the program (/usr/bin/python3, not python3)."]}

- Each line is Key=Value. Keys are case-sensitive.
- Lines starting with # or ; are comments.
- Use \ at the end of a line to continue onto the next line.
- Do not put inline comments after a value on the same line.
- ExecStart needs an absolute path to the program (/usr/bin/python3, not python3).

.. END:list:0:4:4

.. START:section:0:5
Your First Service: Step by Step
================================

.. END:section:0:5

We will create a small script and run it as a service.

Step 1: Create the program

.. START:code:0:5:2

.. code-block:: console

   sudo mkdir -p /opt/hello
   sudo nano /opt/hello/hello.sh

.. END:code:0:5:2

Paste:

.. START:code:0:5:4

.. code-block:: console

   #!/bin/bash
   while true; do
       echo Hello from my service at $(date)
       sleep 5
   done

.. END:code:0:5:4

Make it executable:

.. START:code:0:5:6

.. code-block:: console

   sudo chmod +x /opt/hello/hello.sh

.. END:code:0:5:6

Test it manually first (press Ctrl+C to stop). Always confirm the program works by hand before wrapping it in a service:

.. START:code:0:5:8

.. code-block:: console

   /opt/hello/hello.sh

.. END:code:0:5:8

Step 2: Create the service file
-------------------------------

.. START:code:0:5:10

.. code-block:: console

   sudo nano /etc/systemd/system/hello.service

.. END:code:0:5:10

.. START:code:0:5:11

.. code-block:: console

   [Unit]
   Description=Hello demo service
   After=network.target
   
   [Service]
   Type=simple
   ExecStart=/opt/hello/hello.sh
   Restart=on-failure
   RestartSec=5
   
   [Install]
   WantedBy=multi-user.target

.. END:code:0:5:11

Step 3: Tell systemd about the new file
---------------------------------------

.. START:code:0:5:13

.. code-block:: console

   sudo systemctl daemon-reload

.. END:code:0:5:13

Why: systemd caches unit files in memory. You must run daemon-reload every time you create or edit a unit file, otherwise systemd keeps using the old version.

Step 4: Start it and check
--------------------------

.. START:code:0:5:16

.. code-block:: console

   sudo systemctl start hello.service
   systemctl status hello.service

.. END:code:0:5:16

Expected output includes Active: active (running).

.. START:section:0:6
Step 5: Watch its logs
======================

.. END:section:0:6

.. START:code:0:6:0

.. code-block:: console

   journalctl -u hello.service -f

.. END:code:0:6:0

Step 6: Enable it at boot
-------------------------

.. START:code:0:6:2

.. code-block:: console

   sudo systemctl enable hello.service

.. END:code:0:6:2

This creates a symlink from

/etc/systemd/system/multi-user.target.wants/hello.service to your file. Use enable --now to enable and start in one command:

.. START:code:0:6:4

.. code-block:: console

   sudo systemctl enable --now hello.service

.. END:code:0:6:4

Step 7: Stop and disable
------------------------

.. START:code:0:6:6

.. code-block:: console

   sudo systemctl stop hello.service
   sudo systemctl disable hello.service

.. END:code:0:6:6

.. START:section:0:7
The [Unit] Section in Detail
============================

.. END:section:0:7

.. START:table:0:7:0

.. csv-table::
   :header: "Directive", "Meaning"
   :widths: 35, 65
   :align: center

   "``Description=``", "Text shown in ``systemctl status`` and logs. Keep it short."
   "``Documentation=``", "URLs or man pages, e.g. `https://example.com/docs <https://example.com/docs>`_."
   "``After=``", "Start **after** the listed units. Controls order only."
   "``Before=``", "Start **before** the listed units."
   "``Wants=``", "Soft dependency: try to start these too, but continue if they fail."
   "``Requires=``", "Hard dependency: if they fail to start, this service fails too."
   "``BindsTo=``", "Like ``Requires=``, but also stops this service if the other stops."
   "``Conflicts=``", "Starting this unit stops the listed units."
   "``ConditionPathExists=``", "Only start if the path exists; otherwise skip silently."
   "``StartLimitIntervalSec=`` / ``StartLimitBurst=``", "Rate limit for restarts (see Section 8)."

.. END:table:0:7:0

| The most important idea: ordering vs dependency
| After= and Wants=/Requires= do different jobs:
|     • After=network.target only says if both are starting, wait for network first. It does not start the network.
|     • Wants=network-online.target says please also start this.
| You usually need both:

.. START:code:0:7:2

.. code-block:: console

   [Unit]
   Wants=network-online.target
   After=network-online.target

.. END:code:0:7:2

**network.target vs network-online.target**

.. START:list:0:7:5

.. LIST_META: {"type": "bullet", "head": "", "items": ["network.target: the networking software has been started. An IP address may not exist yet.", "network-online.target: a network connection is actually up. Use this when your program connects to a server (MQTT, HTTP, database) at startup."]}

- network.target: the networking software has been started. An IP address may not exist yet.
- network-online.target: a network connection is actually up. Use this when your program connects to a server (MQTT, HTTP, database) at startup.

.. END:list:0:7:5

Common targets
--------------

.. START:table:0:7:7

.. csv-table::
   :header: "Target", "Meaning"
   :widths: 35, 65
   :align: center

   "``basic.target``", "Basic system is up."
   "``multi-user.target``", "Normal text-mode system (the usual target for services)."
   "``graphical.target``", "Desktop/GUI system."
   "``network-online.target``", "Network is connected."
   "``time-sync.target``", "Clock has been synchronized."

.. END:table:0:7:7

List the order systemd used on your machine:

.. START:code:0:7:9

.. code-block:: console

   systemd-analyze critical-chain hello.service

.. END:code:0:7:9

.. START:section:0:8
The [Service] Section in Detail
===============================

.. END:section:0:8

Type= (how systemd decides the service has started)

.. START:table:0:8:1

.. csv-table::
   :header: "Type", "Behavior", "When to use"
   :widths: 20, 50, 30
   :align: center

   "``simple`` (default)", "The process in ``ExecStart`` is the main process and stays in the foreground. systemd treats it as started immediately.", "Most programs: Python, Node, Go, shell loops."
   "``exec``", "Like ``simple``, but systemd waits until the program is actually executed.", "Better error reporting for invalid executable paths."
   "``forking``", "The program forks and the parent exits (classic daemon). Needs ``PIDFile=``.", "Old-style daemons."
   "``oneshot``", "Runs once and exits. systemd waits for it to finish.", "Setup scripts and initialisation."
   "``notify``", "The program tells systemd when it is ready (via ``sd_notify``).", "Programs that support readiness notifications."
   "``idle``", "Like ``simple``, but delayed until other jobs finish.", "Keeping console output tidy."

.. END:table:0:8:1

**Important:** Do not make a program daemonize itself (&, --daemon) when using Type=simple. systemd expects the process to stay in the foreground, and it will think the service died.

Commands: ExecStart and friends
-------------------------------

.. START:table:0:8:4

.. csv-table::
   :header: "Directive", "Meaning"
   :widths: 25, 75
   :align: center

   "``ExecStartPre=``", "Run before the main command (check files, create folders). If it fails, the service does not start. Prefix with ``-`` to ignore failure."
   "``ExecStart=``", "The main command. **Absolute path required.**"
   "``ExecStartPost=``", "Run after the main command has started."
   "``ExecReload=``", "Command run on ``systemctl reload``, e.g. ``/bin/kill -HUP $MAINPID``."
   "``ExecStop=``", "Custom stop command. If omitted, systemd sends SIGTERM."
   "``ExecStopPost=``", "Cleanup after the service stops, even if it failed."

.. END:table:0:8:4

Example:

.. START:code:0:8:6

.. code-block:: console

   ExecStartPre=/bin/mkdir -p /var/lib/myapp
   ExecStartPre=-/bin/rm -f /tmp/myapp.lock
   ExecStart=/usr/bin/python3 /opt/myapp/main.py --config /etc/myapp/config.json
   ExecReload=/bin/kill -HUP $MAINPID

.. END:code:0:8:6

**Gotcha:** systemd does not run commands through a shell. Pipes (|), redirects (>), && and $(...) do not work directly. If you need them, call a shell explicitly:

.. START:code:0:8:8

.. code-block:: console

   ExecStart=/bin/bash -c 'echo started >> /var/log/myapp.log && /opt/myapp/run'

7.3 Who and where: User, Group, WorkingDirectory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These settings control the account and directory used to run the program:

.. code-block:: ini

   User=appuser
   Group=appuser
   WorkingDirectory=/opt/myapp

Create a dedicated system account instead of running the service as root:

.. code-block:: console

   sudo useradd --system --no-create-home --shell /usr/sbin/nologin appuser

If the program needs serial-port or GPIO access, add the account to the required
group rather than running it as root:

.. code-block:: console

   sudo usermod -aG dialout appuser

7.4 Environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~

Set a small number of variables directly in the unit:

.. code-block:: ini

   Environment=MODE=production
   Environment="LOG_LEVEL=info" "PORT=8080"

For several settings, put them in a separate environment file:

.. code-block:: ini

   EnvironmentFile=/etc/myapp/myapp.env

The file contains one ``KEY=value`` entry per line; do not use ``export``:

.. code-block:: console

   MODE=production
   PORT=8080
   MQTT_HOST=192.168.1.10

Prefix the path with ``-`` to allow the file to be absent:
``EnvironmentFile=-/etc/myapp/myapp.env``. Restrict access when the file
contains secrets:

.. code-block:: console

   sudo chmod 600 /etc/myapp/myapp.env

Services do not inherit your terminal's ``PATH`` or environment. If a program
works interactively but fails as a service, check its environment first.

7.5 Logging
~~~~~~~~~~~

By default, the service's standard output and error are sent to the journal:

.. code-block:: ini

   StandardOutput=journal
   StandardError=journal
   SyslogIdentifier=myapp

To append output to a file instead:

.. code-block:: ini

   StandardOutput=append:/var/log/myapp.log
   StandardError=append:/var/log/myapp.log

Python output may be delayed because of buffering. Use ``python3 -u`` or set
``Environment=PYTHONUNBUFFERED=1``.

7.6 Timeouts and kill behavior
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

   TimeoutStartSec=60
   TimeoutStopSec=30
   KillMode=control-group
   KillSignal=SIGTERM

When stopping the service, systemd sends ``SIGTERM`` and waits for
``TimeoutStopSec``. If the service has not exited by then, systemd sends
``SIGKILL``.

8. Restart Policies
===================

Use ``Restart=`` to decide when systemd should restart a service, and
``RestartSec=`` to set the delay before each attempt:

.. code-block:: ini

   Restart=on-failure
   RestartSec=5

.. csv-table::
   :header: "Value", "Restarts when..."
   :widths: 25, 75
   :align: center

   "``no`` (default)", "Never."
   "``on-success``", "The process exits with a successful status."
   "``on-failure``", "The process exits unsuccessfully, is killed by a signal, or times out."
   "``on-abnormal``", "The process is killed by a signal or times out, but not when it exits with a non-zero status."
   "``on-abort``", "The process exits because of an uncaught signal."
   "``always``", "Whenever the process exits, including after a clean exit."

``Restart=on-failure`` is a sensible default for most long-running programs.
Use ``Restart=always`` only when a clean exit should also cause another start.

To prevent a crash loop from causing constant restarts, set a start limit in
the ``[Unit]`` section:

.. code-block:: ini

   [Unit]
   StartLimitIntervalSec=60
   StartLimitBurst=5

After five start attempts in 60 seconds, systemd stops trying and marks the
unit failed. Clear that state with:

.. code-block:: console

   sudo systemctl reset-failed myapp.service

9. The [Install] Section
========================

.. code-block:: ini

   [Install]
   WantedBy=multi-user.target

Common install directives:

* ``WantedBy=`` specifies which target should pull in the service when it is
  enabled. For ordinary system services this is usually
  ``multi-user.target``.
* ``RequiredBy=`` creates a stronger dependency from the target.
* ``Alias=`` defines an alternative name for the unit.

The ``[Install]`` section is used by ``systemctl enable`` and
``systemctl disable``. It does not affect a direct ``systemctl start``.

10. Complete Example: A Real-World Service
==========================================

This example shows a Python application that needs the network, runs under its
own account, reads settings from a file, and restarts after failure:

.. code-block:: ini

   [Unit]
   Description=My Sensor Gateway
   Documentation=https://example.com/docs
   Wants=network-online.target
   After=network-online.target
   StartLimitIntervalSec=120
   StartLimitBurst=5

   [Service]
   Type=simple
   User=appuser
   Group=appuser
   WorkingDirectory=/opt/gateway
   EnvironmentFile=-/etc/gateway/gateway.env
   Environment=PYTHONUNBUFFERED=1
   ExecStart=/usr/bin/python3 /opt/gateway/main.py
   ExecReload=/bin/kill -HUP $MAINPID
   Restart=on-failure
   RestartSec=5
   TimeoutStopSec=20
   SyslogIdentifier=gateway

   [Install]
   WantedBy=multi-user.target

Install and start it:

.. code-block:: console

   sudo cp gateway.service /etc/systemd/system/gateway.service
   sudo chmod 644 /etc/systemd/system/gateway.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now gateway.service
   systemctl status gateway.service

11. Other Service Patterns
==========================

11.1 oneshot: a setup task that runs once at boot
-------------------------------------------------

.. code-block:: ini

   [Unit]
   Description=Initialise data folders
   After=local-fs.target

   [Service]
   Type=oneshot
   ExecStart=/opt/setup/init.sh
   RemainAfterExit=yes

   [Install]
   WantedBy=multi-user.target

``RemainAfterExit=yes`` keeps the unit shown as ``active (exited)`` after the
script finishes, so other units can depend on it.

11.2 Ordering one service after another
---------------------------------------

.. code-block:: ini

   [Unit]
   Description=Dashboard uploader
   Requires=gateway.service
   After=gateway.service

11.3 Forking daemon
-------------------

Use ``Type=forking`` only for programs that fork into the background. A PID
file helps systemd track the daemon:

.. code-block:: ini

   [Service]
   Type=forking
   PIDFile=/run/olddaemon.pid
   ExecStart=/usr/sbin/olddaemon --daemon

11.4 Template units: many instances from one file
-------------------------------------------------

A template unit named ``worker@.service`` can be started multiple times with
different instance names. ``%i`` is replaced by the instance name:

.. code-block:: ini

   [Unit]
   Description=Worker for %i

   [Service]
   ExecStart=/opt/worker/run.sh %i

Start two instances:

.. code-block:: console

   sudo systemctl start worker@ttyUSB0.service
   sudo systemctl start worker@ttyUSB1.service

11.5 Timers: schedule a service
-------------------------------

Timer units can schedule a service, for example as a replacement for cron.
Create ``backup.service``:

.. code-block:: ini

   [Unit]
   Description=Nightly backup

   [Service]
   Type=oneshot
   ExecStart=/opt/backup/backup.sh

Then create ``backup.timer``:

.. code-block:: ini

   [Unit]
   Description=Run backup every night

   [Timer]
   OnCalendar=*-*-* 02:00:00
   Persistent=true

   [Install]
   WantedBy=timers.target

Load and enable the timer:

.. code-block:: console

   sudo systemctl daemon-reload
   sudo systemctl enable --now backup.timer
   systemctl list-timers

Other timer options include ``OnBootSec=5min`` (five minutes after boot) and
``OnUnitActiveSec=1h`` (one hour after the last activation). Validate calendar
expressions with:

.. code-block:: console

   systemd-analyze calendar '*-*-* 02:00:00'

12. Modifying Services Safely: Overrides and Drop-ins
=====================================================

Change a packaged service without editing its original unit file:

.. code-block:: console

   sudo systemctl edit ssh.service

This creates a drop-in such as
``/etc/systemd/system/ssh.service.d/override.conf``. For example:

.. code-block:: ini

   [Service]
   Restart=always
   RestartSec=3

To replace a list-valued setting such as ``ExecStart``, clear the old value
before assigning the replacement:

.. code-block:: ini

   [Service]
   ExecStart=
   ExecStart=/usr/sbin/sshd -D -e

Edit the complete unit file with ``systemctl edit --full``. Revert local
changes with ``systemctl revert``, and inspect the merged unit with
``systemctl cat``:

.. code-block:: console

   sudo systemctl edit --full ssh.service
   sudo systemctl revert ssh.service
   systemctl cat ssh.service

13. The Complete systemctl Command Reference
============================================

Replace ``NAME`` with the unit name, with or without the ``.service`` suffix.

.. csv-table::
   :header: "Task", "Command"
   :widths: 45, 55
   :align: center

   "Reload unit files after editing", "``sudo systemctl daemon-reload``"
   "Start", "``sudo systemctl start NAME``"
   "Stop", "``sudo systemctl stop NAME``"
   "Restart (stop then start)", "``sudo systemctl restart NAME``"
   "Reload configuration without restarting", "``sudo systemctl reload NAME``"
   "Reload if supported, otherwise restart", "``sudo systemctl reload-or-restart NAME``"
   "Show status and recent log lines", "``systemctl status NAME``"
   "Enable at boot", "``sudo systemctl enable NAME``"
   "Enable and start now", "``sudo systemctl enable --now NAME``"
   "Disable at boot", "``sudo systemctl disable NAME``"
   "Disable and stop now", "``sudo systemctl disable --now NAME``"
   "Check whether it is running", "``systemctl is-active NAME``"
   "Check whether it is enabled", "``systemctl is-enabled NAME``"
   "Check whether it has failed", "``systemctl is-failed NAME``"
   "List running services", "``systemctl list-units --type=service``"
   "List failed units", "``systemctl --failed``"
   "List installed service unit files", "``systemctl list-unit-files --type=service``"
   "Clear failed state", "``sudo systemctl reset-failed NAME``"
   "Show the unit file", "``systemctl cat NAME``"
   "Show all unit properties", "``systemctl show NAME``"
   "Show unit dependencies", "``systemctl list-dependencies NAME``"
   "Prevent any start (mask)", "``sudo systemctl mask NAME``"
   "Undo a mask", "``sudo systemctl unmask NAME``"
   "Reboot or power off", "``sudo systemctl reboot`` or ``sudo systemctl poweroff``"

14. Reading Logs with journalctl
================================

.. csv-table::
   :header: "Task", "Command"
   :widths: 45, 55
   :align: center

   "All logs for a service", "``journalctl -u NAME``"
   "Follow logs live", "``journalctl -u NAME -f``"
   "Show the last 50 lines", "``journalctl -u NAME -n 50``"
   "Print without a pager", "``journalctl -u NAME --no-pager``"
   "Show logs from the current boot", "``journalctl -u NAME -b``"
   "Show logs from the previous boot", "``journalctl -u NAME -b -1``"
   "Show logs since a time", "``journalctl -u NAME --since '2026-10-29 09:00'``"
   "Show logs from the last hour", "``journalctl -u NAME --since '1 hour ago'``"
   "Show errors only", "``journalctl -u NAME -p err``"
   "Show kernel messages", "``journalctl -k``"
   "Show journal disk usage", "``journalctl --disk-usage``"
   "Remove journal entries older than seven days", "``sudo journalctl --vacuum-time=7d``"

On embedded boards with limited flash storage, the journal may be stored only
in RAM. To persist it across reboots, configure ``Storage=persistent`` in
``/etc/systemd/journald.conf`` and set a limit such as ``SystemMaxUse=50M``.
Then restart ``systemd-journald``.

15. Security Hardening Options
==============================

systemd can restrict a service with sandboxing and resource-control settings.
Add suitable options to ``[Service]`` and test the application after each
change; restrictions may prevent legitimate access.

.. code-block:: ini

   NoNewPrivileges=true
   PrivateTmp=true
   ProtectSystem=full
   ProtectHome=true
   ReadWritePaths=/var/lib/myapp
   PrivateDevices=true
   RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
   CapabilityBoundingSet=
   LimitNOFILE=4096
   MemoryMax=200M

.. csv-table::
   :header: "Option", "Effect"
   :widths: 35, 65
   :align: center

   "``NoNewPrivileges=true``", "Prevents the process from gaining additional privileges."
   "``PrivateTmp=true``", "Gives the service a private ``/tmp`` directory."
   "``ProtectSystem=full``", "Makes ``/usr``, ``/boot``, and ``/etc`` read-only to the service; ``strict`` makes almost the entire filesystem read-only."
   "``ProtectHome=true``", "Hides ``/home`` from the service."
   "``ReadWritePaths=``", "Specifies paths that remain writable when filesystem protections are enabled."
   "``PrivateDevices=true``", "Hides physical devices. Omit or set to ``false`` if the service needs serial ports or GPIO."
   "``MemoryMax=``", "Sets a memory limit; the service may be terminated if it exceeds the limit."

Review the service's security exposure (a lower score is safer):

.. code-block:: console

   systemd-analyze security myapp.service

16. Validating and Debugging
============================

Check a unit file for syntax and other issues:

.. code-block:: console

   systemd-analyze verify /etc/systemd/system/myapp.service

A useful debugging routine is:

.. code-block:: console

   systemctl status myapp.service
   journalctl -u myapp.service -n 100 --no-pager
   systemctl cat myapp.service
   sudo -u appuser /usr/bin/python3 /opt/myapp/main.py

The last command runs the application as the service account, which can
reproduce permission and path problems.

.. csv-table::
   :header: "Status", "Meaning"
   :widths: 35, 65
   :align: center

   "``active (running)``", "The service is running."
   "``active (exited)``", "A oneshot service finished successfully."
   "``activating (auto-restart)``", "The service exited and is waiting to restart."
   "``failed``", "The service exited with an error or reached its restart limit."
   "``inactive (dead)``", "The service is not running."

Common exit codes in logs:

.. csv-table::
   :header: "Code", "Typical cause"
   :widths: 30, 70
   :align: center

   "``status=200/CHDIR``", "The ``WorkingDirectory`` does not exist."
   "``status=203/EXEC``", "The ``ExecStart`` path is wrong or the file is not executable; check its shebang too."
   "``status=217/USER``", "The configured ``User=`` account does not exist."
   "``status=1/FAILURE``", "The program failed; inspect its own log lines."
   "``status=127``", "A command could not be found inside a shell invocation."
   "``status=137``", "The process was killed with ``SIGKILL``, often because of memory pressure or a stop timeout."

17. Common Mistakes Checklist
=============================

Before enabling a new service, check that you have not:

#. Forgotten ``sudo systemctl daemon-reload`` after editing the unit.
#. Used a relative path in ``ExecStart``; use an absolute path such as
   ``/usr/bin/python3`` and locate executables with ``which python3``.
#. Forgotten ``chmod +x`` on a script or used an incorrect shebang such as
   ``#!/bin/bash``.
#. Put shell features (pipes, ``&&``, or ``>``) directly in ``ExecStart``
   without invoking a shell explicitly.
#. Used ``Type=simple`` for a program that backgrounds itself.
#. Put ``StartLimitIntervalSec`` in ``[Service]`` instead of ``[Unit]``.
#. Assumed the service inherits your terminal's environment or working
   directory.
#. Run the program as root when a dedicated account and group would suffice.
#. Used ``After=network.target`` when the program needs an actual network
   connection; consider ``network-online.target``.
#. Forgotten to enable the service, so it will not start after reboot.
#. Used Windows line endings (CRLF) in the unit or script. Convert the file
   with ``sed -i 's/\r$//' FILE``.
#. Set incorrect unit-file ownership or permissions; system unit files should
   normally be owned by root with mode ``644``.

.. END:code:0:8:8
