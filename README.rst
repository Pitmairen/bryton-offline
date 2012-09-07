=============
BrytonOffline
=============

This is a simple application for accessing Bryton GPS devices.

**Features:**

* Works without internet access.
* Upload history to strava.com and brytonsport.com.
* Save you history localy in .tcx and .bdx format.
* Show short summary of you rides.


Binary files for Windows
========================

Binary files for windows can be downloaded from here:
https://docs.google.com/folder/d/0B9_cvlT9lotxOGJwamFqMTB5WTQ/edit

*When using the brytonoffline.exe the output is not visible
in the console so you will not se the error messages if something goes wrong.
If you want to see debug messages you have to run it from source.*


Commandline arguments
=====================

*All arguments are optional.*


**Strava.com:**

\--strava-email EMAIL
  Your strava.com email address.
\--strava-password PASSWORD
  Your strava.com password.
\--strava-auth-token TOKEN
  A valid strava.com auth token can be used
  instead of email and password.

**Brytonsport.com:**

\--bryton-email EMAIL
  Your brytonsport.com email address.
\--bryton-password PASSWORD
  Your brytonsport.com password.
\--bryton-session-id SESSION_ID
  A valid brytonsport.com session id can be used
  instead of email and password.


**Other:**

\--server-host ADDRESS:
  This can be used to specify the address of the internal server.
  This is only usefull if the you are running BrytonBridge on a different
  host, e.g on a virtual machine.

\-v, --verbose:
  Enable debugging output.


Requirements to run from source
===============================

* BrytonBridge2
* Python 2.7
* PyQt4
* WebOb


Screenshots
===========

.. image:: https://github.com/pitmairen/bryton-offline/raw/master/screenshots/brytonoffline.png
   :height: 423px
   :width: 600px
   :scale:  100%

.. image:: https://github.com/pitmairen/bryton-offline/raw/master/screenshots/laps.png
   :height: 444px
   :width: 600px
   :scale:  100%

.. image:: https://github.com/pitmairen/bryton-offline/raw/master/screenshots/upload.png
   :height: 464px
   :width: 600px
   :scale:  100%

.. image:: https://github.com/pitmairen/bryton-offline/raw/master/screenshots/export.png
   :height: 463px
   :width: 600px
   :scale:  100%

