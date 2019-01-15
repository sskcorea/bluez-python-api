#!/usr/bin/python

import sys
import dbus.mainloop.glib
import argparse
from gi.repository import GObject
from bpb import BPB

bpb = None

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
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-addr', help='get address', action='store_true')
	group.add_argument('-name', help='get name', action='store_true')
	group.add_argument('-alias', help='get alias', action='store_true')
	group.add_argument('-info', help='get adapter info', action='store_true')
	group.add_argument('-discoverable', help='get discoverable',
		action='store_true')
	group.add_argument('-set', help='set alias, discoverable',
		action='store', nargs=2, metavar=('key', 'value'))
	parser.add_argument('-scan', help='start discovery', action='store_true')
	parser.add_argument('-adv', help='start advertising', action='store_true')
	parser.add_argument('-agent', help='register agent', action='store_true')
	parser.add_argument('-capa', help='set capability',
		action='store', choices=['KeyboardDisplay', 'DisplayOnly',
		'DisplayYesNo', 'KeyboardOnly', 'NoInputNoOutput'])
	args = parser.parse_args()

	if (args.scan):
		bpb.start_scan()
	elif (args.adv):
		bpb.set_discoverable('on')
		adv_id = bpb.start_adv(adv)
	elif (args.agent):
		if args.capa:
			capability = args.capa
		bpb.register_agent(capability)
	elif (args.addr):
		print(bpb.get_addr())
		sys.exit()
	elif (args.name):
		print(bpb.get_name())
		sys.exit()
	elif (args.alias):
		print(bpb.get_alias())
		sys.exit()
	elif (args.info):
		print_device(bpb.get_info())
		sys.exit()
	elif (args.discoverable):
		print(bpb.get_discoverable())
		sys.exit()
	elif (args.set):
		if (args.set[0] == 'alias'):
			bpb.set_alias(args.set[1])
		elif (args.set[0] == 'discoverable'):
			bpb.set_discoverable(args.set[1])
		else:
			pass
		sys.exit()
	else:
		sys.exit()

	mainloop = GObject.MainLoop()
	mainloop.run()

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass