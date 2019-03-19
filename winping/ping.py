import ctypes
import ctypes.wintypes
import socket
import struct
import os

from .errors import *

__all__ = ['ping', 'IcmpHandle', 'IpOptionInformation', 'IcmpEchoReply']


INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


class IPAddr(ctypes.Structure):
    _fields_ = [ ("S_addr", ctypes.c_ulong),
                 ]

    def __str__(self):
        return socket.inet_ntoa(struct.pack("L", self.S_addr))


class IP_OPTION_INFORMATION(ctypes.Structure):
    _fields_ = [ ("Ttl", ctypes.c_ubyte),
                 ("Tos", ctypes.c_ubyte),
                 ("Flags", ctypes.c_ubyte),
                 ("OptionsSize", ctypes.c_ubyte),
                 ("OptionsData", ctypes.POINTER(ctypes.c_ubyte)),
                 ]


class ICMP_ECHO_REPLY(ctypes.Structure):
    _fields_ = [ ("Address", IPAddr),
                 ("Status", ctypes.c_ulong),
                 ("RoundTripTime", ctypes.c_ulong),
                 ("DataSize", ctypes.c_ushort),
                 ("Reserved", ctypes.c_ushort),
                 ("Data", ctypes.c_void_p),
                 ("Options", IP_OPTION_INFORMATION),
                 ]


class IpOptionInformation(object):
    def __init__(s, r):
        s.Ttl = r.Ttl
        s.Tos = r.Tos
        s.Flags = r.Flags
        s.OptionsData = ctypes.string_at(r.OptionsData, r.OptionsSize)


class IcmpEchoReply(object):
    def __init__(s, r):
        s.Address = str(r.Address)
        s.Status = r.Status
        s.RoundTripTime = r.RoundTripTime
        s.Data = ctypes.string_at(r.Data, r.DataSize)
        s.Options = IpOptionInformation(r.Options)
    

icmp = ctypes.windll.iphlpapi
kernel = ctypes.windll.kernel32


GetLastError = ctypes.WINFUNCTYPE(ctypes.wintypes.DWORD,
                                  use_last_error=True)(("GetLastError", kernel))


def IcmpCreateFile_errcheck(res, func, args):
    if res == INVALID_HANDLE_VALUE:
        errno = GetLastError()
        raise OSError(0, "IcmpCreateFile failed", None, errno)
    return args


IcmpCreateFile = ctypes.WINFUNCTYPE(ctypes.wintypes.HANDLE,
                                    use_last_error=True)(("IcmpCreateFile", icmp))
IcmpCreateFile.errcheck = IcmpCreateFile_errcheck


def IcmpCloseHandle_errcheck(res, func, args):
    if not res:
        errno = GetLastError()
        raise OSError(0, "IcmpCloseHandle failed", None, errno)
    return args


IcmpCloseHandle = (ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL,
                                      ctypes.wintypes.HANDLE,
                                      use_last_error=True)(
                                          ("IcmpCloseHandle", icmp), (
                                              (1,"IcmpHandle"),)))
IcmpCloseHandle.errcheck = IcmpCloseHandle_errcheck


def IcmpSendEcho_errcheck(res, func, args):
    if res == 0:
        errno = GetLastError()
        if errno in errno_map:
            raise errno_map[errno](0, "IcmpSendEcho failed", None, errno)
        else:
            raise OSError(0, "IcmpSendEcho failed", None, errno)
    return args


IcmpSendEcho = (ctypes.WINFUNCTYPE(ctypes.wintypes.DWORD,
                                   ctypes.wintypes.HANDLE,
                                   IPAddr,
                                   ctypes.wintypes.LPVOID,
                                   ctypes.wintypes.WORD,
                                   ctypes.POINTER(IP_OPTION_INFORMATION),
                                   ctypes.wintypes.LPVOID,
                                   ctypes.wintypes.DWORD,
                                   ctypes.wintypes.DWORD,
                                   use_last_error=True)(
                                       ("IcmpSendEcho", icmp), (
                                           (1, "IcmpHandle"),
                                           (1, "DestinationAddress"),
                                           (1, "RequestData"),
                                           (1, "RequestSize"),
                                           (1, "RequestOptions"),
                                           (1, "ReplyBuffer"),
                                           (1, "ReplySize"),
                                           (1, "Timeout"))))
IcmpSendEcho.errcheck = IcmpSendEcho_errcheck


class IcmpHandle(object):
    def __init__(self):
        self.handle = IcmpCreateFile()

    def __enter__(self):
        return self.handle

    def __exit__(self, exc_type, exc_value, exc_tb):
        IcmpCloseHandle(self.handle)


def inet_addr(ip):
    return IPAddr(struct.unpack("L", socket.inet_aton(ip))[0])


def ping(handle, address, *, timeout=1000, data=None, expected_count=10):
    address = inet_addr(address)
    if data is None:
        data = os.urandom(32)
    bufsize = (ctypes.sizeof(ICMP_ECHO_REPLY) +
               len(data) + 8) * expected_count
    buf = ctypes.create_string_buffer(bufsize)
    
    count = IcmpSendEcho(IcmpHandle=handle,
                         DestinationAddress=address,
                         RequestData=data,
                         RequestSize=len(data),
                         RequestOptions=None,
                         ReplyBuffer=buf,
                         ReplySize=bufsize,
                         Timeout=timeout)
    
    replies = ctypes.cast(buf, ctypes.POINTER(ICMP_ECHO_REPLY * count)).contents
    replies = [ IcmpEchoReply(r) for r in replies ]
    
    return replies
