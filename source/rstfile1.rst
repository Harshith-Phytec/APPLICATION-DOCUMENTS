V4L2-CTL – Video4Linux2 Device Configuration and Testing
========================================================


Introduction
------------

Video4Linux2 (V4L2) is the standard Linux framework used to access video devices such as USB cameras, MIPI CSI-2 cameras, video capture interfaces, and other multimedia hardware supported by Linux drivers.

The `v4l2-ctl` utility is a command-line application provided by the `v4l-utils` package. It allows developers and system engineers to inspect, configure, and test V4L2-compatible devices directly from a Linux terminal.

Using this utility, developers can:

- Identify available video devices.
- Check camera and driver capabilities.
- List supported image formats and resolutions.
- Configure image width, height, and pixel format.
- Read and modify supported camera controls.
- Capture image frames.
- Test video streaming.
- Inspect frame intervals and streaming parameters.
- Collect diagnostic information when camera operations fail.

The utility communicates with Linux V4L2 drivers through the V4L2 userspace API. It does not directly control every camera sensor register or every internal Image Signal Processing (ISP) parameter. The available operations depend on the camera hardware, kernel driver, and the capabilities exposed by the device.

This document explains how to use `v4l2-ctl` for camera-device inspection, configuration, image capture, streaming, and troubleshooting on Linux-based embedded systems.

Objectives
----------

The main objectives of this document are:

1. Understand the role of V4L2 in Linux camera applications.
2. Understand the purpose and functionality of the `v4l2-ctl` utility.
3. Install and verify the required V4L2 command-line tools.
4. Identify camera devices available in the Linux system.
5. Inspect device capabilities and supported formats.
6. Configure resolution, pixel format, and frame rate where supported.
7. Read and modify camera controls exposed by the driver.
8. Capture image frames and perform video streaming tests.
9. Identify common camera configuration and streaming problems.
10. Establish a repeatable procedure for validating camera functionality.

Scope
-----

This document covers the application-side usage of `v4l2-ctl` on Linux-based systems.

The scope includes:

- V4L2 device discovery.
- Device capability inspection.
- Video format enumeration.
- Resolution and pixel-format configuration.
- Frame interval inspection.
- Camera control management.
- Single-frame and continuous-stream capture.
- Media device topology inspection.
- Diagnostic commands and troubleshooting.

The examples use `/dev/video0` as the camera device. This is only an example device node. The actual camera node must be identified on the target system.

The document does not cover kernel driver development, sensor register programming, device-tree configuration, or hardware-specific ISP tuning.

V4L2 Architecture Overview
--------------------------

V4L2 provides a standard interface between Linux userspace applications and video device drivers.

A typical camera data flow is:

.. code-block:: console

          Camera Sensor
                |
                | Image Data
                v
          Camera Interface
          (CSI / USB / Other)
                |
                v
          ISP / Video Pipeline
          (If supported by hardware)
                |
                v
          Linux V4L2 Driver
                |
                v
          /dev/videoX
                |
                v
            v4l2-ctl
                |
                v
       Image / Video Application

The exact hardware pipeline depends on the platform. Some cameras connect through USB, while embedded camera sensors commonly use a MIPI CSI-2 interface. Some systems also include an ISP between the camera sensor and the video capture interface.

Camera Sensor
~~~~~~~~~~~~~

The camera sensor captures light and converts it into digital image data.

Depending on the sensor, the output may use formats such as:

- RAW Bayer.
- YUV.
- RGB.
- JPEG or another compressed format, if supported.

The sensor's available resolutions, frame rates, and output formats depend on its hardware specifications and driver configuration.

Camera Interface
~~~~~~~~~~~~~~~~

The camera interface transfers image data from the sensor or camera device into the system.

Common interfaces include:

- MIPI CSI-2.
- USB Video Class (UVC).
- Parallel camera interfaces.

The interface and driver must be correctly configured before applications can access the camera.

ISP and Video Processing
~~~~~~~~~~~~~~~~~~~~~~~~

Some embedded platforms contain an Image Signal Processor (ISP). It can perform operations such as demosaicing, noise reduction, color correction, and image enhancement.

The ISP pipeline is hardware- and driver-dependent. Not every camera device exposes all ISP functions through the standard V4L2 interface.

V4L2 Driver
~~~~~~~~~~~

The V4L2 driver provides a standard userspace interface to the video hardware.

It exposes device nodes, commonly named:

.. code-block:: console

   /dev/video0
   /dev/video1
   /dev/video2

A system can contain multiple video nodes. These nodes do not necessarily represent separate physical cameras. Some may represent capture interfaces, processing blocks, metadata streams, or other video functions.

v4l2-ctl Utility
~~~~~~~~~~~~~~~~

The `v4l2-ctl` application sends V4L2 requests to the selected device node.

It can query device information, enumerate formats, configure supported parameters, capture frames, and inspect camera controls.

It is primarily a diagnostic and configuration tool. Applications can also access the same V4L2 API using libraries or system calls.

Installing V4L2 Utilities
-------------------------

The `v4l2-ctl` command is normally installed through the `v4l-utils` package.

Ubuntu and Debian
~~~~~~~~~~~~~~~~~

Run:

.. code-block:: console

   sudo apt update
   sudo apt install v4l-utils


Verify Installation
~~~~~~~~~~~~~~~~~~~

Check the installed version:

.. code-block:: console

   v4l2-ctl --version

Display the available command options:

.. code-block:: console

   v4l2-ctl --help

For streaming-related options:

.. code-block:: console

   v4l2-ctl --help-streaming

For input and output options:

.. code-block:: console

   v4l2-ctl --help-io

The available help categories can vary with the installed version.

Embedded Linux Systems
~~~~~~~~~~~~~~~~~~~~~~

On an embedded Linux target, the package may already be included in the root filesystem.

Check whether the command exists:

.. code-block:: console

   which v4l2-ctl

Alternatively:

.. code-block:: console

   command -v v4l2-ctl

If the command is missing, the required package must be included in the system image or installed using the package manager supported by that distribution.

The presence of the utility alone does not guarantee that a camera driver or camera hardware is available.

Identifying Connected Video Devices
-----------------------------------

Before configuring a camera, identify the available video devices.

List All Video Devices
~~~~~~~~~~~~~~~~~~~~~~

Run:

.. code-block:: console

   v4l2-ctl --list-devices

Example output:

.. code-block:: console

   USB Camera (usb-0000:00:14.0-1):
           /dev/video0
           /dev/video1

The output identifies video devices registered with the V4L2 subsystem.

A single physical camera may expose more than one video node. Therefore, each node should be inspected before selecting it for capture.

List Video Device Nodes
~~~~~~~~~~~~~~~~~~~~~~~

Run:

.. code-block:: console

   ls -l /dev/video*

Example output:

.. code-block:: console

   crw-rw----+ 1 root video 81, 0 Oct 30 10:00 /dev/video0
   crw-rw----+ 1 root video 81, 1 Oct 30 10:00 /dev/video1

The device numbers identify the available character-device nodes.

If no video device nodes are present, investigate camera detection, driver registration, and kernel logs.

Check Device Information
~~~~~~~~~~~~~~~~~~~~~~~~

To inspect the driver information for `/dev/video0`, run:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --all

This command requests the device information, current format, and other information supported by the selected node.

To query the driver information specifically:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --info

The output may include:

- Driver name.
- Card name.
- Bus information.
- Driver version.
- Device capabilities.
- Current video format.
- Supported controls.

Example output:

.. code-block:: console

   Driver Info:
           Driver name      : uvcvideo
           Card type        : USB Camera
           Bus info         : usb-0000:00:14.0-1
           Driver version   : 6.x.x

   Video input : 0

   Format Video Capture:
           Width/Height      : 640/480
           Pixel Format      : 'YUYV'
           Field             : None

This is an illustrative output. Actual values depend on the device and driver.

Checking Device Capabilities
----------------------------

Device capabilities describe the functions supported by a V4L2 device.

Run:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --all

Look for the capabilities section.

Common capability types include:

* **Video Capture** — Supports video capture using the single-planar interface.
* **Video Capture Multiplanar** — Supports video capture using the multi-planar interface.
* **Video Output** — Supports video output.
* **Streaming** — Supports streaming I/O.
* **Read/Write** — Supports read/write I/O, if implemented.
* **Metadata Capture** — Supports metadata capture, where implemented.

Not every device supports every capability.

For example, a capture device may support streaming but not the traditional read/write method.

The capability information helps determine which capture and configuration methods are appropriate.

Listing Supported Pixel Formats
-------------------------------

A camera may support several pixel formats. Before selecting a format, check the formats advertised by the driver.

Run:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --list-formats

For more detailed information:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --list-formats-ext

The extended listing can include:

- Pixel format.
- Supported frame sizes.
- Discrete resolutions.
- Continuous or stepwise size ranges.
- Supported frame intervals.

Example output:

.. code-block:: console

   ioctl: VIDIOC_ENUM_FMT

   Type: Video Capture

   [0]: 'YUYV' (YUYV 4:2:2)
           Size: Discrete 640x480
           Size: Discrete 1280x720

   [1]: 'MJPG' (Motion-JPEG)
           Size: Discrete 640x480
           Size: Discrete 1280x720

This is an illustrative example. A real camera may expose different formats and resolutions.

Common Pixel Formats
~~~~~~~~~~~~~~~~~~~~

Common pixel formats include:

* **YUYV** — Uncompressed YUV 4:2:2 format.
* **UYVY** — Uncompressed YUV 4:2:2 format with a different byte order.
* **MJPG** — Motion-JPEG compressed video frames.
* **NV12** — YUV 4:2:0 format with a semi-planar layout.
* **RGB24** — 24-bit RGB pixel format.
* **GREY** — 8-bit grayscale format.
* **Bayer formats** — Raw sensor data arranged in a Bayer pattern.

The availability of these formats is device-dependent.

A format advertised by a camera is not necessarily supported by every application or processing pipeline.

Understanding Pixel Format Selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pixel format determines how image data is represented in memory.

For example:

- YUYV stores luma and chroma values in an interleaved arrangement.
- NV12 stores luma in one plane and chroma in another plane.
- MJPG stores compressed JPEG image data.
- Bayer formats contain raw sensor samples before full color reconstruction.

Selecting the correct format is important for compatibility with downstream applications and processing components.

Checking Supported Resolutions
------------------------------

A camera may support multiple image resolutions.

Use:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --list-formats-ext

The output shows the supported resolutions for each pixel format.

Example:

.. code-block:: console

   Pixel Format: 'YUYV'

   Size: Discrete 640x480
   Size: Discrete 1280x720
   Size: Discrete 1920x1080

This example does not imply that all cameras support these resolutions.

Before configuring a resolution, verify that the selected pixel format and resolution combination is listed by the device.

Why Resolution Matters
~~~~~~~~~~~~~~~~~~~~~~

Resolution determines the number of pixels in each captured frame.

For example:

Example resolutions and pixel counts:

* **640 × 480** — 307,200 pixels.
* **1280 × 720** — 921,600 pixels.
* **1920 × 1080** — 2,073,600 pixels.

Higher resolutions generally require more memory bandwidth and processing resources.

The actual performance also depends on the pixel format, frame rate, interface bandwidth, and processing pipeline.

Configuring Video Format
------------------------

After identifying a supported pixel format and resolution, configure the device.

For example, to request 640 × 480 using YUYV:

.. code-block:: console

   v4l2-ctl -d /dev/video0 \
   --set-fmt-video=width=640,height=480,pixelformat=YUYV

To check the configured format:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --get-fmt-video

Example output:

.. code-block:: console

   Format Video Capture:
           Width/Height      : 640/480
           Pixel Format      : 'YUYV'
           Field             : None

The driver may adjust the requested settings to a supported configuration. Therefore, always read back the format after setting it.

Configure MJPEG Format
~~~~~~~~~~~~~~~~~~~~~~

If the camera advertises MJPG support for the selected resolution, it can be requested as follows:

.. code-block:: console

   v4l2-ctl -d /dev/video0 \
   --set-fmt-video=width=640,height=480,pixelformat=MJPG

Check the result:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --get-fmt-video

Do not assume that MJPG is supported. Check the format enumeration first.

Important Configuration Note
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The format-setting operation configures the selected video node. It does not automatically configure every upstream sensor, ISP, or media-controller entity.

On media-controller-centric hardware, additional pipeline configuration may be required before the video node can stream.

Checking Frame Intervals and Frame Rate
---------------------------------------

Frame rate describes how many frames are captured per second.

Use the following command to enumerate supported frame intervals:

.. code-block:: console

   v4l2-ctl -d /dev/video0 \
   --list-frameintervals=width=640,height=480,pixelformat=YUYV

The selected width, height, and pixel format must correspond to a supported combination.

Example output:

.. code-block:: console

   ioctl: VIDIOC_ENUM_FRAMEINTERVALS

   Size: Discrete 640x480
           Interval: Discrete 0.033s (30.000 fps)
           Interval: Discrete 0.067s (15.000 fps)

These values are examples only.

Configure Frame Rate
~~~~~~~~~~~~~~~~~~~~

If the driver supports frame interval configuration, a frame rate can be requested using:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --set-parm=30

Read the current value:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --get-parm

The driver may reject or adjust the requested frame rate based on the active format and hardware capabilities.

Always verify the returned value.

Reading Camera Controls
-----------------------

V4L2 supports controls for adjusting camera parameters.

The controls available depend on the camera and its driver.

List all supported controls:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --list-ctrls

To display controls with menu information:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --list-ctrls-menus

Example output:

.. code-block:: console

   brightness 0x00980900 (int) : min=0 max=255 step=1 default=128 value=128

   contrast 0x00980901 (int) : min=0 max=255 step=1 default=128 value=128

   saturation 0x00980902 (int) : min=0 max=255 step=1 default=128 value=128

The example values are illustrative and are not standard values for every camera.

Common Camera Controls
~~~~~~~~~~~~~~~~~~~~~~

Common controls include:

* **Brightness** — Adjusts image brightness.
* **Contrast** — Adjusts the difference between light and dark regions.
* **Saturation** — Adjusts color intensity.
* **Gain** — Controls sensor or processing gain where exposed.
* **Exposure** — Controls exposure time or exposure-related settings.
* **White Balance** — Adjusts color balance.
* **Sharpness** — Adjusts image sharpness where supported.
* **Focus** — Controls focus on cameras with supported focus mechanisms.

Some controls may be unavailable, read-only, or dependent on other settings.

Change Brightness
~~~~~~~~~~~~~~~~~

If the device exposes a writable brightness control, use:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --set-ctrl=brightness=150

Read the brightness value:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --get-ctrl=brightness


Change Contrast
~~~~~~~~~~~~~~~


.. code-block:: console

   v4l2-ctl -d /dev/video0 --set-ctrl=contrast=140

Verify:

.. code-block:: console

   v4l2-ctl -d /dev/video0 --get-ctrl=contrast


Set Multiple Controls
~~~~~~~~~~~~~~~~~~~~~

Multiple controls can be requested in one command:

.. code-block:: console

   v4l2-ctl -d /dev/video0 \
   --set-ctrl=brightness=140,contrast=130,saturation=120

Only use control names and values reported by the selected device.

A failed control operation may indicate that the control is unsupported, read-only, inactive, or outside its allowed range.

Capturing a Single Image Frame
------------------------------

One of the most useful functions of `v4l2-ctl` is capturing image data directly from a camera.

Before capturing, check:

1. The correct video node is selected.
2. The camera supports the requested format.
3. The requested resolution is supported.
4. The device supports the required streaming method.
5. No other application is using the camera.

Capture a YUYV Frame
~~~~~~~~~~~~~~~~~~~~

Configure the camera:

.. code-block:: console

   v4l2-ctl -d /dev/video0 \
   --set-fmt-video=width=640,height=480,pixelformat=YUYV

Capture one frame:

.. code-block:: console

   v4l2-ctl -d /dev/video0 \
   --stream-mmap=3 \
   --stream-count=1 \
   --stream-to=frame.yuyv

Here:

- `--stream-mmap=3` requests streaming with three memory-mapped buffers.
- `--stream-count=1` requests one frame.
- `--stream-to=frame.yuyv` saves the captured frame to a file.

The output file contains raw YUYV image data. It is not a JPEG or PNG image and may require conversion before it can be viewed using a normal image viewer.

Capture an MJPEG Frame
~~~~~~~~~~~~~~~~~~~~~~

If the camera supports MJPG at the selected resolution:

.. code-block:: console

   v4l2-ctl -d /dev/video0 \
   --set-fmt-video=width=640,height=480,pixelformat=MJPG

Capture one frame:

.. code-block:: console

   v4l2-ctl -d /dev/video0 \
   --stream-mmap=3 \
   --stream-count=1 \
   --stream-to=frame.jpg

For a single MJPEG frame, the resulting file may be viewable as a JPEG image if the device returns a complete JPEG frame.

Verify the file:

.. code-block:: console

   file frame.jpg

If the output is not identified as JPEG, inspect the negotiated format and captured data. Do not rely only on the filename extension.

Capturing Multiple Frames
-------------------------

For continuous capture, specify a larger frame count.

Example:

.. code-block:: console

   v4l2-ctl -d /dev/video0 \
   --stream-mmap=3 \
   --stream-count=100 \
   --stream-to=capture.raw

This requests 100 frames and writes the captured data to the output file.

The file contains a sequence of frame data. Its structure depends on the negotiated pixel format and the data returned by the driver.

For uncompressed formats, the expected size can be estimated from the image dimensions and bytes per pixel, but actual buffer sizes and padding should be checked rather than assumed.

For compressed formats such as MJPG, frame sizes can vary.

Monitor Capture Statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~

To display streaming information while capturing:

.. code-block:: console

   v4l2-ctl -d /dev/video0 \
   --stream-mmap=3 \
   --stream-count=100 \
   --stream-to=capture.raw \
   --verbose

The exact diagnostic information depends on the installed utility version.

This test can help identify capture failures, incomplete streams, and performance issues.

Testing Continuous Video Streaming
----------------------------------

A streaming test verifies whether the camera can continuously deliver frames to userspace.

Run:

.. code-block:: console

   v4l2-ctl -d /dev/video0 \
   --stream-mmap=3 \
   --stream-count=300

This requests 300 frames using memory-mapped streaming.

The test does not necessarily display video on the screen. It is primarily useful for checking whether frames can be received successfully.

For example, at a stable 30 frames per second, 300 frames would take approximately 10 seconds to capture.

Actual capture duration depends on the negotiated frame rate and device behavior.

Streaming Methods
~~~~~~~~~~~~~~~~~

V4L2 supports different methods of exchanging frame data between drivers and applications.

Common methods include:

* **Read/Write** — Transfers data using standard read and write operations, if supported.
* **Memory Mapping (MMAP)** — Maps driver-allocated buffers into userspace.
* **User Pointer (USERPTR)** — Uses userspace-allocated buffers, if supported.
* **DMA-BUF** — Allows buffer sharing between supported devices and applications.

The `v4l2-ctl` utility supports streaming tests using available methods. Hardware and driver support determine which methods can be used.

MMAP is a common starting point for camera streaming tests.

Inspecting the Media Controller Topology
----------------------------------------

Some embedded camera systems use the Linux Media Controller framework to manage connected camera components and processing pipelines.

These systems may contain:

- Camera sensor entities.
- CSI receiver entities.
- ISP entities.
- Video processing entities.
- Video capture nodes.
- Media links and pads.

The `media-ctl` utility, normally provided by `v4l-utils`, can be used to inspect the media topology.

List media devices:

.. code-block:: console

   ls -l /dev/media*

Display media topology:

.. code-block:: console

   media-ctl -d /dev/media0 -p

Example topology:

.. code-block:: console

   Media controller API version ...

   - entity 1: Camera Sensor
     pad0: Source

   - entity 2: CSI Receiver
     pad0: Sink
     pad1: Source

   - entity 3: Video Capture
     pad0: Sink

This is a conceptual example. Actual entity names and connections depend on the hardware and driver.

Why Media Topology Is Important
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A camera can be detected by the kernel but still fail to stream if the upstream media pipeline is not correctly configured.

For example:

- The sensor may not be connected to the expected CSI receiver.
- A media link may be disabled.
- The pipeline may use incompatible pad formats.
- The required ISP or capture entity may not be configured.

In these cases, inspecting only `/dev/video0` may not provide enough information.

Use `media-ctl` and the platform's camera documentation to investigate the complete pipeline.

Practical Camera Validation Procedure
-------------------------------------

The following procedure provides a repeatable method for testing a V4L2 camera.

Step 1: Verify Utility Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code-block:: console

   v4l2-ctl --version

Expected result: The installed `v4l2-ctl` version is displayed.

Step 2: Identify Video Devices
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code-block:: console

   v4l2-ctl --list-devices

Expected result: Registered V4L2 devices and their device nodes are listed.

Step 3: Inspect Camera Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code-block:: console

   v4l2-ctl -d /dev/video0 --all

Expected result: The selected node's supported capabilities and available configuration information are displayed.

Step 4: Check Supported Formats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code-block:: console

   v4l2-ctl -d /dev/video0 --list-formats-ext

Expected result: Supported formats and their available frame sizes and intervals are displayed.

Step 5: Configure Resolution and Format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code-block:: console

   v4l2-ctl -d /dev/video0 \
   --set-fmt-video=width=640,height=480,pixelformat=YUYV


Step 6: Verify Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code-block:: console

   v4l2-ctl -d /dev/video0 --get-fmt-video

Expected result: The driver reports the active format. It may differ from the requested format if the driver adjusted the configuration.

Step 7: Capture a Frame
~~~~~~~~~~~~~~~~~~~~~~~


.. code-block:: console

   v4l2-ctl -d /dev/video0 \
   --stream-mmap=3 \
   --stream-count=1 \
   --stream-to=frame.yuyv

Expected result: The command completes and writes captured data to the specified file if streaming succeeds.

Step 8: Check the Captured File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code-block:: console

   ls -lh frame.yuyv
   file frame.yuyv

Expected result: The file exists and has a non-zero size when a frame was successfully captured.

The `file` command may identify raw image data as generic data. This is normal for many uncompressed formats.

Step 9: Run a Streaming Test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code-block:: console

   v4l2-ctl -d /dev/video0 \
   --stream-mmap=3 \
   --stream-count=300

Expected result: The device delivers the requested frames without a streaming error.

Review Kernel Messages
~~~~~~~~~~~~~~~~~~~~~~


.. code-block:: console

   dmesg | tail -n 50

Expected result: Recent kernel messages can be reviewed for camera, sensor, CSI, USB, or driver errors.

This procedure verifies device discovery, format negotiation, capture, and basic streaming. It does not by itself verify image quality, color accuracy, or the complete ISP processing pipeline.

Troubleshooting
---------------

The following table describes common problems encountered when using `v4l2-ctl`.

Common problems and recommended actions:

* **`v4l2-ctl: command not found`** — V4L2 utilities are not installed or not in `PATH`. Install the `v4l-utils` package and verify the command path.
* **No `/dev/video*` node** — The camera driver may not be registered, the hardware may not be detected, or device creation may have failed. Check hardware connections, driver status, and kernel logs.
* **`No such file or directory`** — The video device path may be incorrect. Run `v4l2-ctl --list-devices` and select the correct node.
* **`Permission denied`** — The current user may not have permission to access the video node. Check device permissions and the user's video-group membership.
* **`Device or resource busy`** — Another application may be using the device. Check processes using the node with `fuser` or `lsof`.
* **Unsupported pixel format** — The requested format is not advertised by the driver. Check `--list-formats-ext` and select a supported format.
* **Unsupported resolution** — The requested dimensions are unavailable for the selected format. Select a listed resolution.
* **Unexpected frame rate** — The driver or hardware may not support the requested interval. Check supported frame intervals and read back the configured parameters.
* **Streaming fails** — The format may be incorrect, the pipeline may be incomplete, or there may be a driver or hardware issue. Verify the format and inspect kernel logs and media topology.
* **Captured file is empty** — Capture may not have completed or valid data may not have been written. Check the command result, camera connection, and streaming support.
* **Raw image cannot be opened** — The file contains raw pixel data rather than a standard image file. Use a compatible raw-image conversion or processing tool.
* **Control cannot be changed** — The control may be unsupported, read-only, inactive, or outside its allowed range. Inspect `--list-ctrls` and use a supported value.
* **Camera is detected but does not stream** — The upstream media pipeline or sensor configuration may be incomplete. Inspect media topology and platform-specific camera configuration.

Check Device Permissions
~~~~~~~~~~~~~~~~~~~~~~~~

Run:

.. code-block:: console

   ls -l /dev/video0

Check the current user:

.. code-block:: console

   id

If the device belongs to the `video` group and the user is not a member, an administrator can add the user:

.. code-block:: console

   sudo usermod -aG video "$USER"

Log out and log back in for the new group membership to take effect.

Avoid changing device permissions to world-writable as a permanent workaround.

Check Whether Another Process Is Using the Camera
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run:

.. code-block:: console

   fuser -v /dev/video0

Alternatively:

.. code-block:: console

   lsof /dev/video0

If another application owns the device, stop that application gracefully before performing the test.

Inspect Kernel Messages
~~~~~~~~~~~~~~~~~~~~~~~

Run:

.. code-block:: console

   dmesg | grep -Ei 'video|camera|v4l2|sensor|csi|uvc'

This can help identify:

- Sensor detection failures.
- USB camera connection issues.
- CSI receiver errors.
- Driver registration problems.
- Buffer allocation failures.
- Streaming errors.

Some systems restrict access to kernel logs. Administrative permissions may be required.

Important Considerations for Embedded Linux Systems
---------------------------------------------------

When using `v4l2-ctl` on an embedded platform, several additional points should be considered.

Camera Driver Support
~~~~~~~~~~~~~~~~~~~~~

The camera sensor and interface must be supported by the Linux kernel and the relevant platform drivers.

Installing `v4l-utils` does not automatically add support for an unsupported camera sensor.

Device Node Selection
~~~~~~~~~~~~~~~~~~~~~

Do not assume that `/dev/video0` is always the camera capture node.

Inspect the available nodes and their capabilities before running capture commands.

Media Pipeline Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some embedded camera platforms require media-controller configuration before streaming can start.

The sensor, CSI receiver, ISP, and capture node may need compatible formats and enabled links.

Follow the platform-specific camera integration documentation when additional setup is required.

Memory and Bandwidth
~~~~~~~~~~~~~~~~~~~~

Higher resolutions and frame rates increase data-transfer and memory-bandwidth requirements.

For example, an uncompressed YUYV stream at 1920 × 1080 and 30 frames per second requires approximately:

.. code-block:: console

   1920 × 1080 × 2 × 30
   = 124,416,000 bytes/second

This is approximately 124.4 MB/s before considering additional system overhead.

Actual requirements can vary based on buffer layout, alignment, and the negotiated format.

Pixel Format Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~

The selected pixel format must be supported by both the camera driver and the application that consumes the image.

For example, an application expecting NV12 cannot necessarily process YUYV data without conversion.

Driver and Utility Version
~~~~~~~~~~~~~~~~~~~~~~~~~~

The available command-line options and supported V4L2 features depend on the installed `v4l-utils` version and the kernel driver.

For reliable testing, record both versions:

.. code-block:: console

   v4l2-ctl --version
   uname -r


Application Access
~~~~~~~~~~~~~~~~~~

Only one application may be able to configure or stream from a device at a time, depending on driver behavior and hardware support.

If a camera test fails because the device is busy, check for background camera services and multimedia applications.

Useful Commands Reference
-------------------------

The following commands provide a quick reference for common V4L2 operations.

Common commands:

* **Display version** — `v4l2-ctl --version`
* **Display help** — `v4l2-ctl --help`
* **List devices** — `v4l2-ctl --list-devices`
* **Inspect device** — `v4l2-ctl -d /dev/video0 --all`
* **Display driver information** — `v4l2-ctl -d /dev/video0 --info`
* **List formats** — `v4l2-ctl -d /dev/video0 --list-formats`
* **List extended formats** — `v4l2-ctl -d /dev/video0 --list-formats-ext`
* **Read current format** — `v4l2-ctl -d /dev/video0 --get-fmt-video`
* **Set video format** — `v4l2-ctl -d /dev/video0 --set-fmt-video=width=640,height=480,pixelformat=YUYV`
* **List controls** — `v4l2-ctl -d /dev/video0 --list-ctrls`
* **Read brightness** — `v4l2-ctl -d /dev/video0 --get-ctrl=brightness`
* **Set brightness** — `v4l2-ctl -d /dev/video0 --set-ctrl=brightness=150`
* **List frame intervals** — `v4l2-ctl -d /dev/video0 --list-frameintervals=width=640,height=480,pixelformat=YUYV`
* **Read frame rate** — `v4l2-ctl -d /dev/video0 --get-parm`
* **Request frame rate** — `v4l2-ctl -d /dev/video0 --set-parm=30`
* **Capture one frame** — `v4l2-ctl -d /dev/video0 --stream-mmap=3 --stream-count=1 --stream-to=frame.yuyv`
* **Capture multiple frames** — `v4l2-ctl -d /dev/video0 --stream-mmap=3 --stream-count=100 --stream-to=capture.raw`
* **Test continuous capture** — `v4l2-ctl -d /dev/video0 --stream-mmap=3 --stream-count=300`
* **Inspect media topology** — `media-ctl -d /dev/media0 -p`

Conclusion
----------

The `v4l2-ctl` utility is an important command-line tool for inspecting and testing video devices on Linux-based systems.

It provides access to many V4L2 operations without requiring developers to write a dedicated application for every basic camera test.

By using `v4l2-ctl`, developers can identify video devices, inspect driver capabilities, enumerate supported formats, configure resolutions, examine camera controls, capture image frames, and test streaming functionality.

For embedded camera applications, it is especially useful during initial camera validation and application-level debugging.

However, successful execution of a `v4l2-ctl` command does not guarantee that the complete camera and ISP pipeline is correctly configured. Hardware-specific pipeline setup, driver support, and image-quality validation may still be required.

A systematic validation process should therefore include device discovery, capability inspection, format negotiation, frame capture, streaming verification, and review of kernel diagnostics.

References
----------

The following documentation provides additional technical information:

1. Linux Kernel – Video4Linux2 API documentation:
`https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/v4l2.html <https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/v4l2.html>`_
2. Linux Kernel – Video Capture Interface:
`https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/dev-capture.html <https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/dev-capture.html>`_
3. Linux Kernel – V4L2 Input/Output Methods:
`https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/io.html <https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/io.html>`_
4. Debian Manual – `v4l2-ctl`:
`https://manpages.debian.org/unstable/v4l-utils/v4l2-ctl.1.en.html <https://manpages.debian.org/unstable/v4l-utils/v4l2-ctl.1.en.html>`_
5. Linux Kernel – V4L2 Device Opening and Capabilities:
`https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/open.html <https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/open.html>`_
6. Linux Kernel – V4L2 Driver Framework:
`https://www.kernel.org/doc/html/latest/driver-api/media/v4l2-core.html <https://www.kernel.org/doc/html/latest/driver-api/media/v4l2-core.html>`_
