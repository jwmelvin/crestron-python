# crestron-python

This is a framework for exchanging data with Crestron systems using the xsig protocol. 
It is currently in an early state of development, but has working methods for changing 
Crestron digital, analog, or serial signals into Python objects holding the corresponding
boolean, integer, or string object and xsig index.

The module has the start of an asynchronous server that allows TCP connections on a port
and processes signals received from a connected Crestron system.
