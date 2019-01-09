from __future__ import absolute_import, print_function, unicode_literals

import dbus
import bluezutils
from Advertisement import Advertisement

# Bluez Python Bindings
class BPB:
	# Class variables
	devices = {}
	data = {}
	advertisements = []

	def __init__(self, callback):
		# Instance variables
		self.bus = dbus.SystemBus()
		self.adapter = bluezutils.find_adapter(0)
		self.callback = callback

		self.bus.add_signal_receiver(self._interfaces_added,
			dbus_interface = "org.freedesktop.DBus.ObjectManager",
			signal_name = "InterfacesAdded")

		self.bus.add_signal_receiver(self._properties_changed,
			dbus_interface = "org.freedesktop.DBus.Properties",
			signal_name = "PropertiesChanged",
			arg0 = "org.bluez.Device1",
			path_keyword = "path")
		self.advertisements = [None] * self._get_support_inst()

	def _interfaces_added(self, path, interfaces):
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

	def _properties_changed(self, interface, changed, invalidated, path):
		if interface != "org.bluez.Device1":
			return

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
		self.callback(event)

	def start_scan(self):
		proxy = self.bus.get_object("org.bluez", "/")
		om_interface = dbus.Interface(proxy, "org.freedesktop.DBus.ObjectManager")
		objects = om_interface.GetManagedObjects()

		for path, interfaces in objects.iteritems():
			if "org.bluez.Device1" in interfaces:
				self.devices[path] = interfaces["org.bluez.Device1"]

		self.adapter.StartDiscovery()

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
		proxy = self.bus.get_object('org.bluez', '/org/bluez/hci0')
		interface = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
		a = interface.Get('org.bluez.LEAdvertisingManager1', 'ActiveInstances')
		if (a):
			return a
		else:
			return 0

	def _get_support_inst(self):
		proxy = self.bus.get_object('org.bluez', '/org/bluez/hci0')
		interface = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
		return interface.Get('org.bluez.LEAdvertisingManager1', 'SupportedInstances')

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

		proxy = self.bus.get_object('org.bluez', '/')
		om_interface = dbus.Interface(proxy, 'org.freedesktop.DBus.ObjectManager')
		objects = om_interface.GetManagedObjects()

		for path, interfaces in objects.iteritems():
			if 'org.bluez.LEAdvertisingManager1' in interfaces:
				hcix = path # /org/bluez/hci0

		hci_proxy = self.bus.get_object('org.bluez', hcix)
		ad_interface = dbus.Interface(hci_proxy, 'org.bluez.LEAdvertisingManager1')

		ad_interface.RegisterAdvertisement(advertisement.get_path(), {},
			reply_handler=self._register_ad_cb,
			error_handler=self._register_ad_error_cb)

		return index

	def stop_adv(self, index):
		proxy = self.bus.get_object('org.bluez', '/')
		om_interface = dbus.Interface(proxy, 'org.freedesktop.DBus.ObjectManager')
		objects = om_interface.GetManagedObjects()

		for path, interfaces in objects.iteritems():
			if 'org.bluez.LEAdvertisingManager1' in interfaces:
				hcix = path # /org/bluez/hci0

		hci_proxy = self.bus.get_object('org.bluez', hcix)
		ad_interface = dbus.Interface(hci_proxy, 'org.bluez.LEAdvertisingManager1')

		# print(self.advertisements[index].get_path())
		ad_interface.UnregisterAdvertisement(self.advertisements[index].get_path(),
			reply_handler=self._unregister_ad_cb,
			error_handler=self._unregister_ad_error_cb)
