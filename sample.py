#!/usr/bin/python

import sys
import dbus.mainloop.glib
import argparse
from gi.repository import GObject
from bpb import BPB

capability = 'KeyboardDisplay'

adv_id = 0
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
	elif (evt['id'] == 'start_adv'):
		if (evt['error'] is not None):
			print(evt['error'])
			sys.exit()
		else:
			print(evt['message'])
			# evt['instance'].stop_adv(adv_id)
	elif (evt['id'] == 'stop_adv'):
		if (evt['error'] is not None):
			print(evt['error'])
		else:
			print(evt['message'])
	elif (evt['id'] == 'mediacontrol' or evt['id'] == 'mediaplayer' or
		evt['id'] == 'mediaitem'):
		print(evt['data'])

def main():
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bpb = BPB(cb)

	parser = argparse.ArgumentParser()
	parser.add_argument('-s', '--scan', help='start discovery',
		action='store_true')
	parser.add_argument('-a', '--advertise', help='start advertising',
		action='store_true')
	parser.add_argument('-r', '--agent', help='register agent',
		action='store_true')
	parser.add_argument("-c", "--capability", action="store",
		help="set capability", choices=['KeyboardDisplay', 'DisplayOnly',
		'DisplayYesNo', 'KeyboardOnly', 'NoInputNoOutput'])
	args = parser.parse_args()

	if (args.scan):
		bpb.start_scan()
	elif (args.advertise):
		adv_id = bpb.start_adv(adv)
	elif (args.agent):
		if args.capability:
			capability = args.capability
		bpb.register_agent(capability)
	else:
		sys.exit()

	mainloop = GObject.MainLoop()
	mainloop.run()

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass