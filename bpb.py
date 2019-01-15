from __future__ import absolute_import, print_function, unicode_literals

import dbus
from Advertisement import Advertisement
from Agent import Agent

# Bluez Python Bindings
class BPB:
	devices = {}
	data = {}
	advertisements = []

	def __init__(self, callback):
		self.bus = dbus.SystemBus()
		self.callback = callback

		self.bus.add_signal_receiver(self._interfaces_added,
			dbus_interface = "org.freedesktop.DBus.ObjectManager",
			signal_name = "InterfacesAdded")

		self.bus.add_signal_receiver(self._properties_changed,
			dbus_interface = "org.freedesktop.DBus.Properties",
			signal_name = "PropertiesChanged",
			path_keyword = "path")

		p1 = self.bus.get_object('org.bluez', '/')
		self.if_obj_mgr = dbus.Interface(p1, 'org.freedesktop.DBus.ObjectManager')

		o = self.if_obj_mgr.GetManagedObjects()
		for path, interfaces in o.iteritems():
			if ('org.bluez.Adapter1' in interfaces
				and 'org.bluez.LEAdvertisingManager1' in interfaces):
				hcix = path # ex, /org/bluez/hci0

		p2 = self.bus.get_object('org.bluez', '/org/bluez')
		self.if_agent_mgr = dbus.Interface(p2, 'org.bluez.AgentManager1')

		p3 = self.bus.get_object('org.bluez', hcix)
		self.if_prop = dbus.Interface(p3, 'org.freedesktop.DBus.Properties')
		self.if_adapter = dbus.Interface(p3, 'org.bluez.Adapter1')
		self.if_le_mgr = dbus.Interface(p3, 'org.bluez.LEAdvertisingManager1')

		self.advertisements = [None] * self._get_support_inst()

	def _interfaces_added_device1(self, path, interfaces):
		print("_interfaces_added_device1")
		properties = interfaces["org.bluez.Device1"]
		if not properties:
			return

		if path in self.devices:
			self.devices[path] = dict(self.devices[path].items()
				+ properties.items())
		else:
			self.devices[path] = properties

		event = {
			'id': 'device',
			'data': self.devices[path],
			'instance': self
		}
		self.callback(event)

	def _interfaces_added_gatt_server1(self, path, interfaces):
		print('_interfaces_added_gatt_server1')
		properties = interfaces["org.bluez.GattService1"]
		if not properties:
			return

		event = {
			'id': 'device',
			'data': properties,
			'instance': self
		}
		self.callback(event)

	def _interfaces_added(self, path, interfaces):
		print('_interfaces_added')
		for interface in interfaces.items():
			for obj in interface:
				if type(obj) != str:
					pass

				if (obj == 'org.bluez.Device1'):
					self._interfaces_added_device1(path, interfaces)
				elif (obj == "org.bluez.GattService1"):
					self._interfaces_added_gatt_server1(path, interfaces)
				else:
					pass

	def _properties_changed(self, interface, changed, invalidated, path):
		print('_properties_changed')
		print(interface)

		event = None

		if (interface == 'org.bluez.Device1'):
			if path in self.devices:
				self.devices[path] = dict(self.devices[path].items()
					+ changed.items())
			else:
				self.devices[path] = changed

			event = {
				'id': 'device',
				'data': self.devices[path],
				'instance': self
			}
		elif (interface == 'org.bluez.MediaControl1'):
			event = {
				'id': 'mediacontrol',
				'data': changed,
				'instance': self
			}
		elif (interface == 'org.bluez.MediaPlayer1'):
			event = {
				'id': 'mediaplayer',
				'data': changed,
				'instance': self
			}
		elif (interface == 'org.bluez.MediaItem1'):
			event = {
				'id': 'mediaitem',
				'data': changed,
				'instance': self
			}
		else:
			return

		self.callback(event)

	def _register_ad_cb(self):
		event = {
			'id': 'start_adv',
			'message': 'Advertisement registered',
			'error': None,
			'instance': self
		}
		self.callback(event)

	def _register_ad_error_cb(self, error):
		event = {
			'id': 'start_adv',
			'message': 'Failed to register advertisement',
			'error': str(error),
			'instance': self
		}
		self.callback(event)

	def _unregister_ad_cb(self):
		event = {
			'id': 'stop_adv',
			'message': 'Advertisement unregistered',
			'error': None,
			'instance': self
		}
		self.callback(event)


	def _unregister_ad_error_cb(self, error):
		event = {
			'id': 'stop_adv',
			'message': 'Failed to unregister advertisement',
			'error': str(error),
			'instance': self
		}
		self.callback(event)

	def _get_active_adv(self):
		ai = self.if_prop.Get('org.bluez.LEAdvertisingManager1',
			'ActiveInstances')
		return ai if ai else 0

	def _get_support_inst(self):
		return self.if_prop.Get('org.bluez.LEAdvertisingManager1'
			, 'SupportedInstances')

	def get_addr(self):
		return self.if_prop.Get('org.bluez.Adapter1', 'Address')

	def get_name(self):
		return self.if_prop.Get('org.bluez.Adapter1', 'Name')

	def get_alias(self):
		return self.if_prop.Get('org.bluez.Adapter1', 'Alias')

	def set_alias(self, alias):
		return self.if_prop.Set('org.bluez.Adapter1', 'Alias', alias)

	def get_info(self):
		o = self.if_obj_mgr.GetManagedObjects()
		for _, interfaces in o.iteritems():
			if "org.bluez.Adapter1" not in interfaces:
				continue

			return interfaces["org.bluez.Adapter1"]

	def get_discoverable(self):
		return 'true' if self.if_prop.Get('org.bluez.Adapter1', 'Discoverable') \
			else 'false'

	def set_discoverable(self, onoff):
		if (onoff == "on"):
			value = dbus.Boolean(1)
		elif (onoff == "off"):
			value = dbus.Boolean(0)
		else:
			value = dbus.Boolean(onoff)

		self.if_prop.Set('org.bluez.Adapter1', 'Discoverable', value)

	def start_adv(self, adv):
		index = self._get_active_adv()

		advertisement = Advertisement(self.bus, index, adv['type'])
		for uuid in adv['service_uuid']:
			advertisement.add_service_uuid(uuid)
		advertisement.add_manufacturer_data(
			adv['manufacturer_data']['code'],
			adv['manufacturer_data']['data'])
		advertisement.add_service_data(
			adv['service_data']['uuid'],
			adv['service_data']['data'])
		advertisement.include_tx_power = adv['tx_power']

		self.advertisements[index] = advertisement

		self.if_le_mgr.RegisterAdvertisement(advertisement.get_path(), {},
			reply_handler=self._register_ad_cb,
			error_handler=self._register_ad_error_cb)

		return index

	def stop_adv(self, index):
		self.if_le_mgr.UnregisterAdvertisement(
			self.advertisements[index].get_path(),
			reply_handler=self._unregister_ad_cb,
			error_handler=self._unregister_ad_error_cb)

	def register_agent(self, capability):
		Agent(self.bus, '/bpb/agent')

		self.if_agent_mgr.RegisterAgent('/bpb/agent', capability)
		self.if_agent_mgr.RequestDefaultAgent('/bpb/agent')

	def start_scan(self):
		o = self.if_obj_mgr.GetManagedObjects()
		for path, interfaces in o.iteritems():
			if "org.bluez.Device1" in interfaces:
				self.devices[path] = interfaces["org.bluez.Device1"]

		self.if_adapter.StartDiscovery()

	def set_scan_filter(self, filter):
		f = dict()

		if filter['uuids'] is not None:
			f['UUIDs'] = dbus.Array(filter['uuids'], signature='s')
		if filter['rssi'] is not None and filter['pathloss'] is None:
			f['RSSI'] = dbus.Int16(filter['rssi'])
		if filter['pathloss'] is not None and filter['rssi'] is None:
			f['Pathloss'] = dbus.UInt16(filter['pathloss'])
		if filter['transport'] is not None:
			f['Transport'] = dbus.String(filter['transport'])
		if filter['duplicate'] is not None:
			f['DuplicateData'] = dbus.Boolean(filter['duplicate'])

		self.if_adapter.SetDiscoveryFilter(f)