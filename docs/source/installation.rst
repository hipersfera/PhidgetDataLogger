Installation
*************

The Phidget Data Logger app is written in pure python and therefore can be run on
any environment which is capable of running python. It does however rely on
a number of standard python packages as well as one package unique to the phidget
sensors. The full list of dependent packages is shown below as well as information
on how to install them. It is highly recommended to use a fresh python 3.6.x
`virtual environment <https://virtualenv.pypa.io/en/stable/>`_ throughout.

Dependencies
============

* `numpy <http://www.numpy.org/>`_
* `pyqtgraph <http://www.pyqtgraph.org/documentation/index.html>`_
* `PyQt5 <http://pyqt.sourceforge.net/Docs/PyQt5/>`_
* `Phidget22 <https://www.phidgets.com/docs/Language_-_Python>`_

Numpy, PyQtGraph and PyQt, which are used for handling arrays, real time plotting and
GUIs respectively can all be installed through pythons package manager Pip with the
following commands:

.. code-block:: bash

  $ pip install numpy
  $ pip install pyqtgraph
  $ pip install pyqt5

The remaining package Phidget22 needs to be installed by downloading the zip file
and running the Setup.py script. Instructions for doing this can be found `here <https://www.phidgets.com/docs/Language_-_Python#Install_Phidget_Python_Module_for_Windows>`_.
