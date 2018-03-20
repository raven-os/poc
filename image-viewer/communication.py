
import os
import errno
from time import sleep
from threading import Thread

import config

def createFifo():
    try:
        os.mkfifo("/raven_com/fifo")
    except OSError as oe:
        if (oe.errno != errno.EEXIST):
            return -1
    return 0

def readFifo(app):
    fd = -1
    while (not stop):
        try:
            if fd == -1:
                print("Open fifo")
                fd = os.open("/raven_com/fifo", os.O_RDONLY | os.O_NONBLOCK)
            data = os.read(fd, 1)
            if not stop and len(data) > 0:
                print("Read: {0}".format(data))
                if (b'1' in data):
                    app.updateConfig(config.Config(config = "configs/config1.json"))
                elif (b'2' in data):
                    app.updateConfig(config.Config(config = "configs/config2.json"))

            sleep(0.1)
        except OSError as oe:
            print(oe)
    print("Close fifo")
    os.close(fd)

def startCom(app):
    global ret
    global th
    global stop

    ret = createFifo()
    if ret != 0:
        print("Cannot create communication channel for profile:")
        print("sudo mkdir /raven_com && sudo chmod 777 /raven_com")
    else:
        stop = False
        th = Thread(target = readFifo, args=[app])
        th.start()

def stopCom():
    global stop
    stop = True

    if ret == 0:
        th.join()
        os.remove("/raven_com/fifo")
