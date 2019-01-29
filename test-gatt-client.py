#!/usr/bin/python

import sys
import dbus.mainloop.glib
from gi.repository import GObject
from bpb import BPB

bpb = None

def print_device(properties):
	for key in properties.keys():
		value = properties[key]
		if type(value) is dbus.String:
			value = unicode(value).encode('ascii', 'replace')
		if (key == "Class"):
			print("    %s = 0x%06x" % (key, value))
		else:
			print("    %s = %s" % (key, value))

def cb(evt):
	print(evt['id'])

	if (evt['id'] == 'device'):
		print_device(evt['data'])

def main():
	global bpb

	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bpb = BPB(cb)
	bpb.connect('A0:E6:F8:B7:20:01')

	mainloop = GObject.MainLoop()
	mainloop.run()

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		bpb.disconnect('A0:E6:F8:B7:20:01')
		pass