import select
import functools
import errno
import evdev
import pyudev

context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='input')
# NB: Start monitoring BEFORE we query evdev initially, so that if
# there is a plugin after we evdev.list_devices() we'll pick it up
monitor.start()

# Modify this predicate function for whatever you want to match against


def pred(d):
    keyboards = "mouse" not in d.name.lower()
    return keyboards


# Populate the "active devices" map, mapping from /dev/input/eventXX to
# InputDevice
devices = {}
for d in map(evdev.InputDevice, evdev.list_devices()):
    if pred(d):
        devices[d.fn] = d

# "Special" monitor device
devices['monitor'] = monitor

while True:
    rs, _, _ = select.select(devices.values(), [], [])
    # Unconditionally ping monitor; if this is spurious this
    # will no-op because we pass a zero timeout.  Note that
    # it takes some time for udev events to get to us.
    for udev in iter(functools.partial(monitor.poll, 0), None):
        if not udev.device_node:
            break
        if udev.action == 'add':
            if udev.device_node not in devices:
                print("Device added: %s" % udev)
                try:
                    devices[udev.device_node] = evdev.InputDevice(
                        udev.device_node)
                except IOError as e:
                    # udev reports MORE devices than are accessible from
                    # evdev; a simple way to check is see if the devinfo
                    # ioctl fails
                    if e.errno != errno.ENOTTY:
                        raise
                    pass
        elif udev.action == 'remove':
            # NB: This code path isn't exercised very frequently,
            # because select() will trigger a read immediately when file
            # descriptor goes away, whereas the udev event takes some
            # time to propagate to us.
            if udev.device_node in devices:
                print("Device removed (udev): %s" % devices[udev.device_node])
                del devices[udev.device_node]
    for r in rs:
        # You can't read from a monitor
        if r.fileno() == monitor.fileno():
            continue
        if r.fn not in devices:
            continue
        # Select will immediately return an fd for read if it will
        # ENODEV.  So be sure to handle that.
        try:
            for event in r.read():
                if event.type == evdev.ecodes.EV_KEY:
                    print(evdev.categorize(event))
        except IOError as e:
            if e.errno != errno.ENODEV:
                raise
            print("Device removed: %s" % r)
            del devices[r.fn]
