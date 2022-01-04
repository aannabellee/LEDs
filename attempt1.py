import bluetooth
import btaps.libbtaps as libbtaps
import time
import random


# Locate local bluetooth devices and list Plugable BT switches
# Returns a dictionary of btaddr's for local Plugable switches
# and their device names

def findSwitches():
    switchDict = {}
    print
    "\nSearching for switches nearby..."
    nearby = bluetooth.discover_devices()
    for btaddr in nearby:
        if bluetooth.lookup_name(btaddr) == 'Plugable':
            print
            "Connecting...",
            checkSwitch = libbtaps.BTaps(btaddr)
            checkSwitch.connect()
            switchDict[btaddr] = checkSwitch.get_dev_name()
            print
            "Found: " + btaddr + " -- " + switchDict[btaddr]
            checkSwitch.disconnect()
    return switchDict


# Report switches found. Takes switch dict in form {btaddr:deviceName}
# and lists the names and addresss

def listSwitches(switchDict):
    count = 1
    for btaddr in switchDict:
        print
        str(count) + ": " + switchDict[btaddr], btaddr
        count += 1


# Refresh list of found switches with ones not previously discovered

def refreshList(switchDict):
    nearby = bluetooth.discover_devices()
    for btaddr in nearby:
        if btaddr not in switchDict and bluetooth.lookup_name(btaddr) == 'Plugable':
            print
            "Connecting...",
            checkSwitch = libbtaps.BTaps(btaddr)
            checkSwitch.connect()
            switchDict[btaddr] = checkSwitch.get_dev_name()
            print
            "Found: " + btaddr + " -- " + switchDict[btaddr]
            checkSwitch.disconnect()
    return switchDict


# Ask user if this was all the expected switches. Refresh list if not.

def enufSwitches(switchDict):
    enuf = ''
    count = 0
    while not (enuf == 'y' or enuf == 'Y'):
        print
        "\nA total of " + str(len(switchDict)) + " switches were found nearby:"
        listSwitches(switchDict)
        enuf = raw_input('\nWere all the local switches listed? (y/n) ')
        if (enuf == 'n' or enuf == 'N'):
            if count > 0:
                print
                "Try moving the Bluetooth adapter closer to the switches."
                print
                "Make sure all switches are plugged in."
                raw_input("Press any key")
            print
            "Looking for more..."
            switchDict = refreshList(switchDict)
            count += 1
    return switchDict


# Gives the user a chance to name or rename switches with handles. Press 'q' to skip it all.

def nameSwitches(switchDict):
    rename = ''
    count = 1
    find = {}
    for btaddr in switchDict:
        find[str(count)] = btaddr
        count += 1

    print
    "\n\nYou can check the operation of your switches or rename them here."
    while (True):
        print
        "Here are the names and addresses of your switches."
        listSwitches(switchDict)
        rename = raw_input("Enter the number next to the switch you want to check or name (q to quit): ")
        if rename == 'q' or rename == 'Q':
            break
        else:
            if rename in find:
                print
                "Connecting..."
                btaddr = find[rename]
                checkSwitch = libbtaps.BTaps(btaddr)
                checkSwitch.connect()
                print
                "\nThis switch is named " + switchDict[btaddr]
                print
                "The switch will flash for 10 seconds, then ask if you want to rename it."
                while (True):
                    raw_input("Press any key when ready for light to flash.")
                    for i in range(1, 5):
                        checkSwitch.set_switch(True)
                        time.sleep(2)
                        checkSwitch.set_switch(False)
                    change = raw_input(
                        "\nDo you want to rename this switch? (y/n, press any other key to flash again.)")
                    if change == 'n' or change == 'N':
                        checkSwitch.disconnect()
                        break
                    elif change == 'y' or change == 'Y':
                        name = ''
                        print
                        'The current name is: ' + switchDict[btaddr]
                        while not (len(name) < 17 and len(name) > 0):
                            name = raw_input('Enter new name (16 characters or less, type no to keep current name): ')
                        if name != 'no':
                            switchDict[btaddr] = name
                            checkSwitch.set_dev_name(name)
                        checkSwitch.disconnect()
                        break
            else:
                print
                "\nInvalid entry.\n"
    return switchDict


# Strip useless null characters from end of name

def nullstrip(s):
    try:
        s = s[:s.index('\x00')]
    except ValueError:  # No nulls were found, which is okay.
        pass
    return s


# Connect all switches by name, returns a tuple containing a list of instances that can be used to call
# the switches, and a lookup list of the switch names that can be accessed numerically.

def connectAll(switchDict):
    connected = {}
    lookup = []
    print
    "\nConnecting all local switches.\n"
    for btaddr in switchDict:
        print
        "Connecting " + switchDict[btaddr]
        handle = nullstrip(switchDict[btaddr])
        lookup.append(handle)
        connected[handle] = libbtaps.BTaps(btaddr)
        connected[handle].connect()
        connected[handle].set_datetime_now()
        connected[handle].set_switch(True)
        time.sleep(2)
        connected[handle].set_switch(False)
    print
    "\nAll connected"
    return connected


# Disconnect all switches
def disconnectAll(connectedDict):
    print
    "\nDisconnecting all local switches"
    for handle in connectedDict:
        print
        "Disconnecting" + connectedDict[handle]
        connectedDict[handle].disconnect()
    print
    "\nAll disconnected."


# Create lookup list
def makeLookup(connectedDict):
    lookup = []
    for key in connectedDict.keys():
        lookup.append(key)
    return lookup


# Set it all up!

def setUpSwitches():
    myDict = findSwitches()
    myDict = enufSwitches(myDict)
    myDict = nameSwitches(myDict)
    connectedSwitches = connectAll(myDict)
    lookup = makeLookup(connectedSwitches)
    return (connectedSwitches, lookup, myDict)


# use to quickly reconnect switches after initial connection
def quickReconnect(switches):
    connectedSwitches = connectAll(switches[2])
    lookup = makeLookup(connectedSwitches)
    return (connectedSwitches, lookup, myDict)


###Light Show function examples###

def allOn(switches, delay):
    for key in switches[0].keys():
        switches[0][key].set_switch(True)
        time.sleep(delay)


def allOff(switches, delay):
    for key in switches[0].keys():
        switches[0][key].set_switch(False)
        time.sleep(delay)


# Turn each switch on in turn, then each switch off


def onOff(switches, delay, reps):
    for i in range(0, reps):
        for key in switches[0].keys():
            switches[0][key].set_switch(True)
            time.sleep(delay)
        for key in switches[0].keys():
            switches[0][key].set_switch(False)
            time.sleep(delay)


# Turn each switch on then off in sequence

def seq(switches, delay, reps):
    for i in range(0, reps):
        for key in switches[0].keys():
            switches[0][key].set_switch(True)
            time.sleep(delay)
            switches[0][key].set_switch(False)


# Turns all on in sequence, then turns them off and back on one by one, then turns them off is sequence

def backSeq(switches, delay, reps):
    for i in range(0, reps):
        for key in switches[0].keys():
            switches[0][key].set_switch(True)
            time.sleep(delay)
        for key in switches[0].keys():
            switches[0][key].set_switch(False)
            time.sleep(delay)
            switches[0][key].set_switch(True)
        for key in switches[0].keys():
            switches[0][key].set_switch(True)
            time.sleep(delay)


# Does onOff for a specified number of reps


def cool(switches, delay, reps):
    for i in range(0, reps):
        for key in switches[0].keys():
            switches[0][key].set_switch(True)
            time.sleep(delay)
        for i in range(5, random.randint(7, 12)):
            key = switches[1][random.randint(0, (len(switches[1]) - 1))]
            wait = random.randint(2, 6) / 2
            for i in range(0, random.randint(2, 6)):
                switches[0][key].set_switch(False)
                time.sleep(wait)
                switches[0][key].set_switch(True)
                time.sleep(wait)
        for key in switches.keys():
            switches[0][key].set_switch(False)
            time.sleep(delay)

        # Turns switches on and off with random time intervals between


def rand(switches, reps):
    for i in range(reps):
        for key in switches[0].keys():
            switches[0][key].set_switch(True)
            time.sleep((random.random() / 2))
        for key in switches[0].keys():
            switches[0][key].set_switch(False)
            time.sleep((random.random() / 2))


# Random lights on and off at random interval


def crazy(switches, reps):
    for i in range(1, reps):
        key = switches[1][random.randint(0, (len(switches[1]) - 1))]
        switches[0][key].set_switch(True)
        time.sleep(random.random() / 2)
        switches[0][key].set_switch(False)
        time.sleep(random.random() / 2)
        switches[0][key].set_switch(True)


# Loops through different sequences randomly

def allOverThePlace(switches, reps):
    for i in range(0, reps):
        thisTime = random.randint(0, 5)
        reps = random.randint(10, 50)
        if thisTime == 0:
            crazy(switches, switches[1], reps)
        elif thisTime == 1:
            rand(switches, reps)
        elif thisTime == 2:
            cool(switches, random.randint(1, 4), switches[1], reps)
        elif thisTime == 3:
            backSeq(switches, random.randint(1, 4), reps)
        elif thisTime == 4:
            seq(switches, random.randint(1, 4), reps)
        else:
            onOff(switches, random.randint(1, 4), reps)