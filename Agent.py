import dbus.service

def ask(prompt):
	try:
		return raw_input(prompt)
	except:
		return input(prompt)

class Rejected(dbus.DBusException):
	_dbus_error_name = "org.bluez.Error.Rejected"

class Agent(dbus.service.Object):
	# exit_on_release = True
	bus = None

	def _set_trusted(self, path):
		props = dbus.Interface(self.bus.get_object("org.bluez", path),
						"org.freedesktop.DBus.Properties")
		props.Set("org.bluez.Device1", "Trusted", True)

	def _dev_connect(self, path):
		dev = dbus.Interface(self.bus.get_object("org.bluez", path),
								"org.bluez.Device1")
		dev.Connect()

	def __init__(self, bus, path):
		self.bus = bus
		dbus.service.Object.__init__(self, bus, path)

	# def set_exit_on_release(self, exit_on_release):
	# 	self.exit_on_release = exit_on_release

	@dbus.service.method('org.bluez.Agent1',
					in_signature="", out_signature="")
	def Release(self):
		print("Release")
		# if self.exit_on_release:
		# 	mainloop.quit()

	@dbus.service.method('org.bluez.Agent1',
					in_signature="os", out_signature="")
	def AuthorizeService(self, device, uuid):
		print("AuthorizeService (%s, %s)" % (device, uuid))
		authorize = ask("Authorize connection (yes/no): ")
		if (authorize == "yes"):
			return
		raise Rejected("Connection rejected by user")

	@dbus.service.method('org.bluez.Agent1',
					in_signature="o", out_signature="s")
	def RequestPinCode(self, device):
		print("RequestPinCode (%s)" % (device))
		self._set_trusted(device)
		return ask("Enter PIN Code: ")

	@dbus.service.method('org.bluez.Agent1',
					in_signature="o", out_signature="u")
	def RequestPasskey(self, device):
		print("RequestPasskey (%s)" % (device))
		self._set_trusted(device)
		passkey = ask("Enter passkey: ")
		return dbus.UInt32(passkey)

	@dbus.service.method('org.bluez.Agent1',
					in_signature="ouq", out_signature="")
	def DisplayPasskey(self, device, passkey, entered):
		print("DisplayPasskey (%s, %06u entered %u)" %
						(device, passkey, entered))

	@dbus.service.method('org.bluez.Agent1',
					in_signature="os", out_signature="")
	def DisplayPinCode(self, device, pincode):
		print("DisplayPinCode (%s, %s)" % (device, pincode))

	@dbus.service.method('org.bluez.Agent1',
					in_signature="ou", out_signature="")
	def RequestConfirmation(self, device, passkey):
		print("RequestConfirmation (%s, %06d)" % (device, passkey))
		confirm = ask("Confirm passkey (yes/no): ")
		if (confirm == "yes"):
			self._set_trusted(device)
			return
		raise Rejected("Passkey doesn't match")

	@dbus.service.method('org.bluez.Agent1',
					in_signature="o", out_signature="")
	def RequestAuthorization(self, device):
		print("RequestAuthorization (%s)" % (device))
		auth = ask("Authorize? (yes/no): ")
		if (auth == "yes"):
			return
		raise Rejected("Pairing rejected")

	@dbus.service.method('org.bluez.Agent1',
					in_signature="", out_signature="")
	def Cancel(self):
		print("Cancel")
