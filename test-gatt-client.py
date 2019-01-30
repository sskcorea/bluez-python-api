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
	device_list = []
	if len(sys.argv) <= 1:
		print('put target addr')
		sys.exit()

	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bpb = BPB(cb)
	device_list = bpb.get_device_list()

	if not device_list:
		print('unkwon device')
		sys.exit()

	for d in device_list:
		if (sys.argv[1] == d['Address']):
			bpb.connect(sys.argv[1])
		else:
			print('unkown device')
			sys.exit()

	mainloop = GObject.MainLoop()
	mainloop.run()

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		bpb.disconnect(sys.argv[1])
		pass