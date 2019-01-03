#!/usr/bin/python

import dbus.mainloop.glib
try:
  from gi.repository import GObject
except ImportError:
  import gobject as GObject

from bpb import BPB

def print_compact(address, properties):
	name = ""
	address = "<unknown>"

	for key, value in properties.iteritems():
		if type(value) is dbus.String:
			value = unicode(value).encode('ascii', 'replace')
		if (key == "Name"):
			name = value
		elif (key == "Address"):
			address = value

	if "Logged" in properties:
		flag = "*"
	else:
		flag = " "

	print("%s%s %s" % (flag, address, name))

	properties["Logged"] = True

def print_normal(address, properties):
	print("[ " + address + " ]")

	for key in properties.keys():
		value = properties[key]
		if type(value) is dbus.String:
			value = unicode(value).encode('ascii', 'replace')
		if (key == "Class"):
			print("    %s = 0x%06x" % (key, value))
		else:
			print("    %s = %s" % (key, value))

	print()

	properties["Logged"] = True

def cb(key, value):
	print(key)
	print_normal(value['address'], value['devices'])


def main():
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	bpb = BPB(cb)
	bpb.scan()

	mainloop = GObject.MainLoop()
	mainloop.run()

if __name__ == "__main__":
	main()