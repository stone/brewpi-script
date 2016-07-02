# wraps a tcp socket stream in a object that looks like a serial port
# this allows seemless integration with exsiting brewpi-script code
import BrewPiUtil
import socket
# import dbus, gobject, avahi
# from dbus import DBusException
# from dbus.mainloop.glib import DBusGMainLoop


class TCPSerial(object):
    def __init__(self, host=None, port=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # find BrewPi's via mdns lookup
        self.host=host
        self.port=port
        self.retries=10 # max reconnect attempts to try when doing a read or write operation
        self.retryCount=0 # count of reconnect attempts performed
        BrewPiUtil.logMessage("Connecting to BrewPi " + host + " on port " + str(port))
        self.sock.connect((host, port))
        self.timeout=self.sock.gettimeout()
        self.name=host + ':' + str(port) 
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
        bytes=None
        try: 
            bytes=self.sock.recv(size)
        except socket.timeout: # timeout on receive just means there is nothing in the buffer.  This is not an error
            return None
        except socket.error: # other socket errors probably mean we lost our connection.  try to recover it.
            if self.retryCount < self.retries:
                self.retryCount=self.retryCount+1
                self.sock.close()
                self.sock.connect((self.host, self.port))
                bytes=self.read(size)
            else:
                self.sock.close()
                return None
        if bytes is not None:
            self.retryCount=0
        return bytes

    
    def readline(self,size=None, eol='\n'):
        #Parameters:    
        #Read a line which is terminated with end-of-line (eol) character (\n by default) or until timeout.
        buf=self.read(1)
        line=buf
        while buf!='\n':
            buf=self.read(1)
            if buf is not None and buf!='\n':
                line+=buf
        return line
            
   
    def write(self, data):
        #Returns:    Number of bytes written.
        #Raises SerialTimeoutException:
        #     In case a write timeout is configured for the port and the time is exceeded.
        #Write the string data to the port.
        try:
            bytes=self.sock.sendall(data)
        except socket.timeout: # A write timeout is probably a connection issue
            if self.retryCount < self.retries:
                self.retryCount=self.retryCount+1
                self.sock.close()
                self.sock.connect((self.host, self.port))
                bytes=self.write(data)
            else:
                self.sock.close()
                return -1
        except socket.error: # general errors are most likely to be a timeout disconnect from BrewPi, so try to recover.
            if self.retryCount < self.retries:
                self.retryCount=self.retryCount+1
                self.sock.close()
                self.sock.connect((self.host, self.port))
                bytes=self.write(data)
            else:
                self.sock.close()
                return -1
        if bytes>=0:
            self.retryCount=0
        return bytes
    
    def inWaiting(self):
        #Return the number of chars in the receive buffer.
        # Note: the value returned by inWaiting should be greater than the send buffer size on BrewPi firmware
        # If not, brewpi.py may not grab the next whole buffered message.
        return 4096  #tcp socket doesnt give us a way to know how much is in the buffer, so we assume there is always something
    
        
    def setTimeout(self, value=0.1):
        if value:
            self.sock.settimeout(value)
            self.timeout=self.sock.gettimeout()
        return self.sock.gettimeout()
    
    def flush(self):
        #Flush of file like objects. In this case, wait until all data is written.
        # this has no meaning to tcp
        return

    
    def close(self):
        #close port immediately
        return self.sock.close()
    
    
# class MDNSBrowser(object):
#
#     def __init__(self):
#         # Avahi global configs
#         self.Avahi_loop = DBusGMainLoop(set_as_default=True)
#         self.Avahi_busloop = gobject.MainLoop()
#         gobject.threads_init()
#         self.Avahi_bus = dbus.SystemBus(mainloop=self.Avahi_loop)
#         self.Avahi_server = dbus.Interface( self.Avahi_bus.get_object(avahi.DBUS_NAME, '/'), 'org.freedesktop.Avahi.Server')
#         self.Avahi_TYPE = '_brewpi._tcp'
#         self.tcpHost=None
#         self.tcpPort=None
#
#     def _service_resolved(self,*args):
#         #global tcpHost
#         #global tcpPort
#         BrewPiUtil.logMessage('\taddress:' + args[7])
#         BrewPiUtil.logMessage( '\tport:' + str(args[8]))
#         self.tcpHost=args[7]
#         self.tcpPort=args[8]
#         self.Avahi_busloop.quit()
#
#     def _print_error(self,*args):
#         BrewPiUtil.logMessage('error_handler:' + args[0])
#         self.Avahi_busloop.quit()
#
#     def _myhandler(self,interface, protocol, name, stype, domain, flags):
#         BrewPiUtil.logMessage("Found BrewPi service '" + name +"' type '" +stype+"' domain '"+domain+"' ") #% (name, stype, domain)
#
#         if flags & avahi.LOOKUP_RESULT_LOCAL:
#                 # local service, skip
#                 pass
#
#         self.Avahi_server.ResolveService(interface, protocol, name, stype,
#             domain, avahi.PROTO_UNSPEC, dbus.UInt32(0),
#             reply_handler=self._service_resolved, error_handler=self._print_error)
#
#
#     def discoverBrewpis(self):
#         BrewPiUtil.logMessage("Running discovery...")
#         sbrowser = dbus.Interface(self.Avahi_bus.get_object(avahi.DBUS_NAME,
#                                   self.Avahi_server.ServiceBrowserNew(avahi.IF_UNSPEC,
#                                   avahi.PROTO_UNSPEC, self.Avahi_TYPE, 'local', dbus.UInt32(0))),
#                                   avahi.DBUS_INTERFACE_SERVICE_BROWSER)
#
#         sbrowser.connect_to_signal("ItemNew", self._myhandler)
#         self.Avahi_busloop.run()
#         return (self.tcpHost,self.tcpPort)
#
