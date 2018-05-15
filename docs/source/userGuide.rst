User Guide
***********

In this sections a brief overview of the Sensor and UI elements which make up the
Phidget Display app will be given along with a full example program.

The base Sensor Class
=======================

There exist a large number of Phidget sensors each with their own API.
In order to make connecting to each new kind of sensor as easy as possible each
sensor type inherits from the same base sensor class :py:mod:`Sensor`.

The  :py:mod:`Sensor` class's main role is to set up the event listener which detects
when a connected phidget is disconnected unexpectedly. It also handles the :py:meth:`Sensor.Sensor.getData`
method which is used by the plotting UI to get the time values and sensor outputs needed for
plotting.

Inherited Classes
=================

There are a number of classes implemented to deal with specific kinds of sensor which
inherit from :py:mod:`Sensor. These include: :py:mod:`DummySensor`,  :py:mod:`IRTemperatureSensor`,
:py:mod:`StrainSensor`,  :py:mod:`VoltageInputSensor`, :py:mod:`VoltageRatioSensor`.
As a rule these classes implement two functions which are not present in  :py:mod:`Sensor`.
These are the :py:func:`attachSensor` method which is responsible for connecting to the sensor
and connecting it to the rest of the application and the :py:func:`activateDataListener`
method which is responsible for setting up the events which trigger when the
sensor acquires new data. The exception to this rule is the :py:mod:`DummySensor`
module which overrides :py:meth:`Sensor.Sensor.getData` to allow it to simulate an
actual sensor.

UI Classes
===========

There are three classes used to provide a grphical user interface for interacting
with Phidget Sensors and the data they produce. The :py:mod:`PhidgetDisplayApp`
is the main GUI display and handles the majority of functionality including
displaying live data, saving and loading sensor data and setting and monitoring
alarm values. The examining of saved data is handled by the :py:mod:`StoredDataPlotter`
which opens the data in a separate window which can be used concurrently with
live data monitoring. Finally the :py:mod:`StrainCalibrator` module allows the
user to quickly and easily measure values in order to perform calibration of load
cell sensors. The calibration data can then be saved to a file and loaded in
the main application to convert the strain sensor output from volts to Kg.
