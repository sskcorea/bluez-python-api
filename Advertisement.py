import dbus.service

class Advertisement(dbus.service.Object):
	PATH_BASE = '/bpb/advertisement'

	def __init__(self, bus, index, advertising_type):
		self.path = self.PATH_BASE + str(index)
		self.bus = bus
		self.ad_type = advertising_type
		self.service_uuids = None
		self.manufacturer_data = None
		self.solicit_uuids = None
		self.service_data = None
		self.include_tx_power = None
		dbus.service.Object.__init__(self, bus, self.path)

	def get_properties(self):
		properties = dict()
		properties['Type'] = self.ad_type
		if self.service_uuids is not None:
			properties['ServiceUUIDs'] = dbus.Array(self.service_uuids,
													signature='s')
		if self.solicit_uuids is not None:
			properties['SolicitUUIDs'] = dbus.Array(self.solicit_uuids,
													signature='s')
		if self.manufacturer_data is not None:
			properties['ManufacturerData'] = dbus.Dictionary(
				self.manufacturer_data, signature='qay')
		if self.service_data is not None:
			properties['ServiceData'] = dbus.Dictionary(self.service_data,
														signature='say')
		if self.include_tx_power is not None:
			properties['IncludeTxPower'] = dbus.Boolean(self.include_tx_power)
		return {'org.bluez.LEAdvertisement1': properties}

	def get_path(self):
		return dbus.ObjectPath(self.path)

	def add_service_uuid(self, uuid):
		if not self.service_uuids:
			self.service_uuids = []
		self.service_uuids.append(uuid)

	def add_solicit_uuid(self, uuid):
		if not self.solicit_uuids:
			self.solicit_uuids = []
		self.solicit_uuids.append(uuid)

	def add_manufacturer_data(self, manuf_code, data):
		if not self.manufacturer_data:
			self.manufacturer_data = dict()
		self.manufacturer_data[manuf_code] = data

	def add_service_data(self, uuid, data):
		if not self.service_data:
			self.service_data = dict()
		self.service_data[uuid] = data

	@dbus.service.method('org.freedesktop.DBus.Properties',
						 in_signature='s',
						 out_signature='a{sv}')
	def GetAll(self, interface):
		print 'GetAll'
		if interface != 'org.bluez.LEAdvertisement1':
			raise InvalidArgsException()
		print 'returning props'
		return self.get_properties()['org.bluez.LEAdvertisement1']

	@dbus.service.method('org.bluez.LEAdvertisement1',
						 in_signature='',
						 out_signature='')
	def Release(self):
		print '%s: Released!' % self.path