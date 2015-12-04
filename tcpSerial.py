# wraps a tcp socket stream in a object that looks like a serial port
# this allows seemless integration with exsiting brewpi-script code

import socket
import serial
from zeroconf import ServiceBrowser, Zeroconf, ServiceStateChange


class TCPSerial(object):
    def __init__(self, host=None, port=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # find BrewPi's via mdns lookup

        
        self.sock.connect((host, port))
        return
        
    def flushInput(self):
        # this has no meaning to tcp
        return
    
    def flushOutput(self):
        #Clear output buffer, aborting the current output and discarding all that is in the buffer.
        # this has no meaning to tcp
        return

    
    def read(self, size=1):
        #Returns:    Bytes read from the port.
        #Read size bytes from the serial port. If a timeout is set it may return less characters as requested. With no timeout it will block until the requested number of bytes is read.
        return self.sock.recv(size)

    
    def readline(self,size=None, eol='\n'):
        #Parameters:    
        #Read a line which is terminated with end-of-line (eol) character (\n by default) or until timeout.
        buf=self.sock.recv(1)
        line=buf
        while buf!='\n':
            buf=self.sock.recv(1)
            if buf!='\n':
                line+=buf
        
        return line
            
   
    def write(self, data):
        #Returns:    Number of bytes written.
        #Raises SerialTimeoutException:
        #     In case a write timeout is configured for the port and the time is exceeded.
        #Write the string data to the port.
        return self.sock.sendall(data)
    
    def inWaiting(self):
        #Return the number of chars in the receive buffer.
        return 1  #tcp socket doesnt give us a way to know how much is in the buffer, so we assume there is always something
    
    def name(self):
        #Device name. This is always the device name even if the port was opened by a number. (Read Only).
        return sock.getpeername()
    
    def timeout(self, value=0.1):
        #Read or write current read timeout setting.
        return setTimeout(value)
    
    def setTimeout(self, value=0.1):
        if value:
            self.sock.settimeout(value)
        return self.sock.gettimeout()
    
    def flush(self):
        #Flush of file like objects. In this case, wait until all data is written.
        # this has no meaning to tcp
        return

    
    def close(self):
        #close port immediately
        return self.sock.close()
    
    
    
 


class MDNSListener(object):

    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))
        
def on_service_state_change(zeroconf, service_type, name, state_change):
    print("Service %s of type %s state changed: %s" % (name, service_type, state_change))

    if state_change is ServiceStateChange.Added:
        info = zeroconf.get_service_info(service_type, name)
        if info:
            print("  Address: %s:%d" % (socket.inet_ntoa(info.address), info.port))
            print("  Weight: %d, priority: %d" % (info.weight, info.priority))
            print("  Server: %s" % (info.server,))
            if info.properties:
                print("  Properties are:")
                for key, value in info.properties.items():
                    print("    %s: %s" % (key, value))
            else:
                print("  No properties")
        else:
            print("  No info")
        print('\n')

def discoverBrewpis():
    print "Discovering WiFi connected BrewPis..."
    zeroconf = Zeroconf()
    listener = MDNSListener()
    browser = ServiceBrowser(zeroconf, "_brewpi._tcp.local", None,listener)   
    print "Listener established"
    try:
        input("Press enter to exit...\n\n")
    finally:
        zeroconf.close() 
    
