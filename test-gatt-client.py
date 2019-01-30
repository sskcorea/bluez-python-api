#!/usr/bin/python

import sys
import pprint
import dbus.mainloop.glib
from gi.repository import GObject
from bpb import BPB

bpb = None

def cb(evt):
	print(evt['id'])

	if (evt['id'] == 'device'):
		pprint.pprint(evt['data'])

def main():
	global bpb

	if len(sys.argv) <= 1:
		print('put target addr')
		sys.exit()

	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bpb = BPB(cb)
	bpb.connect(sys.argv[1])

	mainloop = GObject.MainLoop()
	mainloop.run()

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		bpb.disconnect(sys.argv[1])
		pass