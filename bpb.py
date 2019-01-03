from __future__ import absolute_import, print_function, unicode_literals

import dbus
import bluezutils

# Bluez Python Bindings
class BPB:
	devices = {}
	data = {}
	
	def __init__(self, callback):
		self.bus = dbus.SystemBus()
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

	def scan(self):
		adapter = bluezutils.find_adapter(0)

		om = dbus.Interface(self.bus.get_object("org.bluez", "/"),
					"org.freedesktop.DBus.ObjectManager")
		objects = om.GetManagedObjects()
		for path, interfaces in objects.iteritems():
			if "org.bluez.Device1" in interfaces:
				self.devices[path] = interfaces["org.bluez.Device1"]

		adapter.StartDiscovery()