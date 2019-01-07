from __future__ import absolute_import, print_function, unicode_literals

import dbus
import bluezutils
from Advertisement import Advertisement

# Bluez Python Bindings
class BPB:
	# Class variables
	devices = {}
	data = {}
	
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

	def _skip_dev(old_dev, new_dev):
		if not "Logged" in old_dev:
			return False
		if "Name" in old_dev:
			return True
		if not "Name" in new_dev:
			return True
		return False

	def _interfaces_added(self, path, interfaces):
		properties = interfaces["org.bluez.Device1"]
		if not properties:
			return

		if path in self.devices:
			dev = self.devices[path]

			if compact and _skip_dev(dev, properties):
				return
			self.devices[path] = dict(self.devices[path].items() + properties.items())
		else:
			self.devices[path] = properties

		if "Address" in self.devices[path]:
			address = properties["Address"]
		else:
			address = "<unknown>"

		data = {
			'address': address,
			'devices': self.devices[path]
		}
		self.callback('SCAN', data)

	def _properties_changed(self, interface, changed, invalidated, path):
		if interface != "org.bluez.Device1":
			return

		if path in self.devices:
			dev = self.devices[path]

			# if compact and _skip_dev(dev, changed):
			# 	return
			self.devices[path] = dict(self.devices[path].items() + changed.items())
		else:
			self.devices[path] = changed

		if "Address" in self.devices[path]:
			address = self.devices[path]["Address"]
		else:
			address = "<unknown>"

		data = {
			'address': address,
			'devices': self.devices[path]
		}
		self.callback('PROPERTY', data)

	def start_scan(self):
		proxy = self.bus.get_object("org.bluez", "/")
		om_interface = dbus.Interface(proxy, "org.freedesktop.DBus.ObjectManager")
		objects = om_interface.GetManagedObjects()

		for path, interfaces in objects.iteritems():
			if "org.bluez.Device1" in interfaces:
				self.devices[path] = interfaces["org.bluez.Device1"]

		self.adapter.StartDiscovery()

	def _register_ad_cb(self):
		data = {
			'message': 'Advertisement registered',
		}
		self.callback('ADVERTISEMENT', data)


	def _register_ad_error_cb(self, error):
		data = {
			'message': 'Failed to register advertisement: ' + str(error), 
		}
		self.callback('ADVERTISEMENT', data)

	def start_adv(self, adv):
		advertisement = Advertisement(self.bus, 0, adv['type'])
		advertisement.add_service_uuid('180D')
		advertisement.add_service_uuid('180F')
		# advertisement.add_manufacturer_data(0xffff, [0x00, 0x01, 0x02, 0x03, 0x04])
		# advertisement.add_service_data('9999', [0x00, 0x01, 0x02, 0x03, 0x04])
		advertisement.include_tx_power = adv['tx_power']

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
