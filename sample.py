#!/usr/bin/python

import sys
import dbus.mainloop.glib
import argparse
from gi.repository import GObject
from bpb import BPB

def print_compact(address, properties):
	name = ""
	address = "<unknown>"

	for key, value in properties.iteritems():
		if type(value) is dbus.String:
			value = unicode(value).encode('ascii', 'replace')
		if (key == "Name"):
			name = value
		elif (key == "Address"):
			address = value

	if "Logged" in properties:
		flag = "*"
	else:
		flag = " "

	print("%s%s %s" % (flag, address, name))

	properties["Logged"] = True

def print_normal(address, properties):
	print("[ " + address + " ]")

	for key in properties.keys():
		value = properties[key]
		if type(value) is dbus.String:
			value = unicode(value).encode('ascii', 'replace')
		if (key == "Class"):
			print("    %s = 0x%06x" % (key, value))
		else:
			print("    %s = %s" % (key, value))

	print()

	properties["Logged"] = True

def cb(key, value):
	if (key == 'PROPERTY' or key == 'SCAN'):
		print_compact(value['address'], value['devices'])
	elif (key == 'ADVERTISEMENT'):
		print(value['message'])

def main():
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bpb = BPB(cb)

	parser = argparse.ArgumentParser()
	parser.add_argument('-s', '--scan', help='start discovery', action='store_true')
	parser.add_argument('-a', '--advertise', help='start advertising', action='store_true')
	args = parser.parse_args()
	if (args.scan):
		bpb.start_scan()
	elif (args.advertise):
		adv = {
			'type': 'peripheral',
			'service_uuid': ['180D', '180F'],
			'manufacturer_data': {
				'code': 0xffff,
				'data': [0x00, 0x01, 0x02, 0x03, 0x04]
			},
			'service_data': {
				'uuid': '9999',
				'data': [0x00, 0x01, 0x02, 0x03, 0x04]
			},
			'local_name': 'bpb',
			'tx_power': True,
			'data': [0x26, [0x01, 0x01, 0x00]],
		}
		bpb.start_adv(adv)

	mainloop = GObject.MainLoop()
	mainloop.run()

if __name__ == "__main__":
	main()