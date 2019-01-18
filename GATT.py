import dbus.service

class Application(dbus.service.Object):
	"""
	org.bluez.GattApplication1 interface implementation
	"""
	def __init__(self, bus):
		self.path = '/bpb/app'
		self.services = []
		dbus.service.Object.__init__(self, bus, self.path)

	def get_path(self):
		return dbus.ObjectPath(self.path)

	def add_service(self, service):
		self.services.append(service)

	def get_services(self):
		return self.services

	@dbus.service.method('org.freedesktop.DBus.ObjectManager',
		out_signature='a{oa{sa{sv}}}')
	def GetManagedObjects(self):
		response = {}
		print('GetManagedObjects')

		for service in self.services:
			response[service.get_path()] = service.get_properties()
			chrcs = service.get_characteristics()
			for chrc in chrcs:
				response[chrc.get_path()] = chrc.get_properties()
				descs = chrc.get_descriptors()
				for desc in descs:
					response[desc.get_path()] = desc.get_properties()

		return response

class Service(dbus.service.Object):
	"""
	org.bluez.GattService1 interface implementation
	"""
	PATH_BASE = '/org/bluez/example/service'

	def __init__(self, bus, index, uuid, primary):
		self.path = self.PATH_BASE + str(index)
		self.bus = bus
		self.uuid = uuid
		self.primary = primary
		self.characteristics = []
		dbus.service.Object.__init__(self, bus, self.path)

	def get_properties(self):
		return {
				'org.bluez.GattService1': {
						'UUID': self.uuid,
						'Primary': self.primary,
						'Characteristics': dbus.Array(
								self.get_characteristic_paths(),
								signature='o')
				}
		}

	def get_path(self):
		return dbus.ObjectPath(self.path)

	def add_characteristic(self, characteristic):
		self.characteristics.append(characteristic)

	def get_characteristic_paths(self):
		result = []
		for chrc in self.characteristics:
			result.append(chrc.get_path())
		return result

	def get_characteristics(self):
		return self.characteristics

	@dbus.service.method('org.freedesktop.DBus.Properties',
						 in_signature='s',
						 out_signature='a{sv}')
	def GetAll(self, interface):
		if interface != 'org.bluez.GattService1':
			raise Exception()

		return self.get_properties()['org.bluez.GattService1']


class Characteristic(dbus.service.Object):
	"""
	org.bluez.GattCharacteristic1 interface implementation
	"""
	def __init__(self, bus, index, uuid, flags, service, callback):
		self.path = service.path + '/char' + str(index)
		self.bus = bus
		self.uuid = uuid
		self.service = service
		self.flags = flags
		self.descriptors = []
		self.callback = callback
		dbus.service.Object.__init__(self, bus, self.path)

	def get_properties(self):
		return {
				'org.bluez.GattCharacteristic1': {
						'Service': self.service.get_path(),
						'UUID': self.uuid,
						'Flags': self.flags,
						'Descriptors': dbus.Array(
								self.get_descriptor_paths(),
								signature='o')
				}
		}

	def get_path(self):
		return dbus.ObjectPath(self.path)

	def add_descriptor(self, descriptor):
		self.descriptors.append(descriptor)

	def get_descriptor_paths(self):
		result = []
		for desc in self.descriptors:
			result.append(desc.get_path())
		return result

	def get_descriptors(self):
		return self.descriptors

	@dbus.service.method('org.freedesktop.DBus.Properties',
						 in_signature='s',
						 out_signature='a{sv}')
	def GetAll(self, interface):
		if interface != 'org.bluez.GattCharacteristic1':
			raise Exception()

		return self.get_properties()['org.bluez.GattCharacteristic1']

	@dbus.service.method('org.bluez.GattCharacteristic1',
						in_signature='a{sv}',
						out_signature='ay')
	def ReadValue(self, options):
		print('Default ReadValue called')
		event = {
			'id': 'readvalue',
			'uuid': self.uuid,
			'response': None
		}
		self.callback(event)

		print(event['response'])
		if event['response'] is not None:
			return event['response']
		else:
			return None

	@dbus.service.method('org.bluez.GattCharacteristic1', in_signature='aya{sv}')
	def WriteValue(self, value, options):
		print('Default WriteValue called')
		event = {
			'id': 'writevalue',
			'uuid': self.uuid,
			'value': value
		}
		self.callback(event)

	@dbus.service.method('org.bluez.GattCharacteristic1')
	def StartNotify(self):
		print('Default StartNotify called')
		event = {
			'id': 'startnotify',
		}
		self.callback(event)

	@dbus.service.method('org.bluez.GattCharacteristic1')
	def StopNotify(self):
		print('Default StopNotify called')
		event = {
			'id': 'stopnotify',
		}
		self.callback(event)

	@dbus.service.signal('org.freedesktop.DBus.Properties',
						 signature='sa{sv}as')
	def PropertiesChanged(self, interface, changed, invalidated):
		pass


class Descriptor(dbus.service.Object):
	"""
	org.bluez.GattDescriptor1 interface implementation
	"""
	def __init__(self, bus, index, uuid, flags, characteristic, callback):
		self.path = characteristic.path + '/desc' + str(index)
		self.bus = bus
		self.uuid = uuid
		self.flags = flags
		self.chrc = characteristic
		self.callback = callback
		dbus.service.Object.__init__(self, bus, self.path)

	def get_properties(self):
		return {
				'org.bluez.GattDescriptor1': {
						'Characteristic': self.chrc.get_path(),
						'UUID': self.uuid,
						'Flags': self.flags,
				}
		}

	def get_path(self):
		return dbus.ObjectPath(self.path)

	@dbus.service.method('org.freedesktop.DBus.Properties',
						 in_signature='s',
						 out_signature='a{sv}')
	def GetAll(self, interface):
		if interface != 'org.bluez.GattDescriptor1':
			raise Exception()

		return self.get_properties()['org.bluez.GattDescriptor1']

	@dbus.service.method('org.bluez.GattDescriptor1',
						in_signature='a{sv}',
						out_signature='ay')
	def ReadValue(self, options):
		print ('Default ReadValue called')
		event = {
			'id': 'readvalue',
			'uuid': self.uuid,
			'response': None
		}
		self.callback(event)

		print(event['response'])
		if event['response'] is not None:
			return event['response']
		else:
			return None

	@dbus.service.method('org.bluez.GattDescriptor1', in_signature='aya{sv}')
	def WriteValue(self, value, options):
		event = {
			'id': 'writevalue',
			'uuid': self.uuid,
			'value': value
		}
		self.callback(event)
