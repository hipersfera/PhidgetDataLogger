Introduction
************************

Overview
=========
The Phidget Data Logger application is designed for the real time viewing of
sensor data from a range of Phidget sensors. In addition to real time viewing the
application also offers functionality for the recording, viewing and analysis
of recorded data. Finally the app offers a way to calibrate load cells in real
time and save and apply the results for calibration.

Code Layout
===========
The code for the application is broadly split into two categories. Sensor classes
and UI classes. The sensor classes are all derived from the "Sensor" class and
provide a way to connect to and retrieve data from a range of Phidget sensors.
The UI classes provide separate interfaces for: viewing live data, viewing recorded
data and calibrating strain sensors.
