#!/usr/bin/python

import sys
import dbus.mainloop.glib
import argparse
import pprint
from gi.repository import GObject
from bpb import BPB
from random import randint

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

filter = {
	'uuids' : None,
	# only pathloss or rssi can be set, never both
	'rssi': -80,
	'pathloss': None, # MAX 137
	'transport': 'auto', # auto, bredr, le
	'duplicate': True
}

app = {
	'service': [{
		'uuid': '0000180d-0000-1000-8000-00805f9b34fb',
		'primary': True,
		'characteristic': [{
			'uuid': '00002a37-0000-1000-8000-00805f9b34fb',
			'flags': ['notify']
		}, {
			'uuid': '00002a38-0000-1000-8000-00805f9b34fb',
			'flags': ['read']
		}]
	}, {
		'uuid': '180f',
		'primary': True,
		'characteristic': [{
			'uuid': '2a19',
			'flags': ['read', 'notify']
		}]
	}, {
		'uuid': '12345678-1234-5678-1234-56789abcdef0',
		'primary': True,
		'characteristic': [{
			'uuid': '12345678-1234-5678-1234-56789abcdef1',
			'flags': ['read', 'write', 'writable-auxiliaries'],
			'descriptor': [{
				'uuid': '12345678-1234-5678-1234-56789abcdef2',
				'flags': ['read', 'write']
			}]
		}]
	}]
}

hr_ee_count = 0
energy_expended = 0
notifying = False

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('-addr', help='get address', action='store_true')
group.add_argument('-name', help='get name', action='store_true')
group.add_argument('-alias', help='get alias', action='store_true')
group.add_argument('-info', help='get adapter info', action='store_true')
group.add_argument('-discoverable', help='get discoverable',
	action='store_true')
group.add_argument('-timeout', help='get discoverable timeout',
	action='store_true')
group.add_argument('-discovering', help='get discovering',
	action='store_true')
group.add_argument('-set', help='set alias, discoverable, discoverable timeout',
	action='store', nargs=2, metavar=('key', 'value'))
parser.add_argument('-scan', help='start discovery', action='store_true')
parser.add_argument('-adv', help='start advertising', action='store_true')
parser.add_argument('-agent', help='register agent', action='store_true')
parser.add_argument('-server', help='register gatt server', action='store_true')
parser.add_argument('-capa', help='set capability',
	action='store', choices=['KeyboardDisplay', 'DisplayOnly',
	'DisplayYesNo', 'KeyboardOnly', 'NoInputNoOutput'])

def hr_msrmt_cb():
	global hr_ee_count, energy_expended, notifying
	value = []
	value.append(dbus.Byte(0x06))
	value.append(dbus.Byte(randint(90, 130)))

	if hr_ee_count % 10 == 0:
		value[0] = dbus.Byte(value[0] | 0x08)
		value.append(dbus.Byte(energy_expended & 0xff))
		value.append(dbus.Byte((energy_expended >> 8) & 0xff))

	energy_expended = min(0xffff, energy_expended + 1)
	hr_ee_count += 1

	print('Updating value: ' + repr(value))

	bpb.notify(value)

	return notifying

def cb(evt):
	global notifying

	print(evt['id'])

	if (evt['id'] == 'device'):
		pprint.pprint(evt['data'])
		pass
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
	elif (evt['id'] == 'startnotify'):
		notifying = True
		GObject.timeout_add(1000, hr_msrmt_cb)
	elif (evt['id'] == 'stopnotify'):
		notifying = False
	elif (evt['id'] == 'readvalue'):
		if (evt['uuid'] == '12345678-1234-5678-1234-56789abcdef1'):
			evt['response'] = [ 0x01 ]
		elif (evt['uuid'] == '12345678-1234-5678-1234-56789abcdef2'):
			evt['response'] = [ 0x02 ]
		else:
			evt['response'] = [ 0xff ]
	elif (evt['id'] == 'writevalue'):
		print(evt['uuid'])
		print(evt['value'])
	elif (evt['id'] == 'mediacontrol' or evt['id'] == 'mediaplayer' or
		evt['id'] == 'mediaitem'):
		print(evt['data'])

def main():
	global bpb

	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bpb = BPB(cb)

	args = parser.parse_args()
	if (args.scan):
		bpb.set_scan_filter(filter)
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
		pprint.pprint(bpb.get_info())
		sys.exit()
	elif (args.discoverable):
		print(bpb.get_discoverable())
		sys.exit()
	elif (args.timeout):
		print(bpb.get_discoverable_timeout())
		sys.exit()
	elif (args.discovering):
		print(bpb.get_discovering())
		sys.exit()
	elif (args.set):
		if (args.set[0] == 'alias'):
			bpb.set_alias(args.set[1])
		elif (args.set[0] == 'discoverable'):
			bpb.set_discoverable(args.set[1])
		elif (args.set[0] == 'timeout'):
			bpb.set_discoverable_timeout(args.set[1])
		else:
			pass
		sys.exit()
	elif (args.server):
		bpb.register_app(app)
	else:
		sys.exit()

	mainloop = GObject.MainLoop()
	mainloop.run()

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass