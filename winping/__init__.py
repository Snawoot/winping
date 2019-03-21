import ctypes
import ctypes.wintypes
import socket
import struct
import os

from .errors import *

__all__ = [
    'ping',
    'ping6',
    'IcmpHandle',
    'Icmp6Handle',
    'IpOptionInformation',
    'IcmpEchoReply',
    'Icmp6EchoReply',
]


INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
ERROR_IO_PENDING = 997


class IPAddr(ctypes.Structure):
    _fields_ = [ ("S_addr", ctypes.c_ulong),
                 ]

    def __str__(self):
        return socket.inet_ntoa(struct.pack("L", self.S_addr))


class in6_addr(ctypes.Structure):
    _fields_ = [ ("Byte", ctypes.c_ubyte * 16),
                 ]

    def __str__(self):
        return socket.inet_ntop(socket.AF_INET6, bytes(self.Byte))


class sockaddr_in6(ctypes.Structure):
    _fields_ = [
        ("sin6_family", ctypes.c_short),
        ("sin6_port", ctypes.c_ushort),
        ("sin6_flowinfo", ctypes.c_ulong),
        ("sin6_addr", in6_addr),
        ("sin6_scope_id", ctypes.c_ulong)
    ]


class IPV6_ADDRESS_EX(ctypes.Structure):
    _fields_ = [
        ("sin6_port", ctypes.c_ushort),
        ("sin6_flowinfo", ctypes.c_ulong),
        ("sin6_addr", in6_addr),
        ("sin6_scope_id", ctypes.c_ulong)
    ]
    _pack_ = 1


class ICMPV6_ECHO_REPLY(ctypes.Structure):
    _fields_ = [
        ("Address", IPV6_ADDRESS_EX),
        ("Status", ctypes.c_ulong),
        ("RoundTripTime", ctypes.c_uint)
    ]


class IP_OPTION_INFORMATION(ctypes.Structure):
    _fields_ = [ ("Ttl", ctypes.c_ubyte),
                 ("Tos", ctypes.c_ubyte),
                 ("Flags", ctypes.c_ubyte),
                 ("OptionsSize", ctypes.c_ubyte),
                 ("OptionsData", ctypes.c_uint32),
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


class DUMMYUNION(ctypes.Union):
    _fields_ = [
        ("Status", ctypes.c_long),
        ("Pointer", ctypes.c_void_p),
    ]


class IO_STATUS_BLOCK(ctypes.Structure):
    _fields_ = [
        ("DUMMYUNIONNAME", DUMMYUNION),
        ("Information", ctypes.POINTER(ctypes.c_ulong))
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


class Icmp6EchoReply(object):
    def __init__(s, r):
        s.Address = str(r.Address.sin6_addr)
        s.Status = r.Status
        s.RoundTripTime = r.RoundTripTime
    

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

Icmp6CreateFile = ctypes.WINFUNCTYPE(ctypes.wintypes.HANDLE,
                                     use_last_error=True)(("Icmp6CreateFile", icmp))
Icmp6CreateFile.errcheck = IcmpCreateFile_errcheck


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


def Icmp6SendEcho2_errcheck(res, func, args):
    if res == 0:
        errno = GetLastError()
        if errno == ERROR_IO_PENDING:
            pass
        elif errno in errno_map:
            raise errno_map[errno](0, "Icmp6SendEcho2 failed", None, errno)
        else:
            raise OSError(0, "Icmp6SendEcho2 failed", None, errno)
    return args


Icmp6SendEcho2 = (ctypes.WINFUNCTYPE(ctypes.wintypes.DWORD,
                                     ctypes.wintypes.HANDLE,
                                     ctypes.wintypes.HANDLE,
                                     ctypes.wintypes.LPVOID,
                                     ctypes.wintypes.LPVOID,
                                     ctypes.POINTER(sockaddr_in6),
                                     ctypes.POINTER(sockaddr_in6),
                                     ctypes.wintypes.LPVOID,
                                     ctypes.wintypes.WORD,
                                     ctypes.POINTER(IP_OPTION_INFORMATION),
                                     ctypes.wintypes.LPVOID,
                                     ctypes.wintypes.DWORD,
                                     ctypes.wintypes.DWORD,
                                     use_last_error=True)(
                                         ("Icmp6SendEcho2", icmp), (
                                             (1, "IcmpHandle"),
                                             (1, "Event"),
                                             (1, "ApcRoutine"),
                                             (1, "ApcContext"),
                                             (1, "SourceAddress"),
                                             (1, "DestinationAddress"),
                                             (1, "RequestData"),
                                             (1, "RequestSize"),
                                             (1, "RequestOptions"),
                                             (1, "ReplyBuffer"),
                                             (1, "ReplySize"),
                                             (1, "Timeout"))))
Icmp6SendEcho2.errcheck = Icmp6SendEcho2_errcheck


def Icmp6ParseReplies_errcheck(res, func, args):
    if res != 1:
        errno = GetLastError()
        raise OSError(0, "Icmp6ParseReplies failed", None, errno)
    return args


Icmp6ParseReplies = (ctypes.WINFUNCTYPE(ctypes.wintypes.DWORD,
                                        ctypes.wintypes.LPVOID,
                                        ctypes.wintypes.DWORD)(
                                            ("Icmp6ParseReplies", icmp), (
                                                (1, "ReplyBuffer"),
                                                (1, "ReplySize"))))
Icmp6ParseReplies.errcheck = Icmp6ParseReplies_errcheck


class IcmpHandle(object):
    def __init__(self):
        self.handle = IcmpCreateFile()

    def __enter__(self):
        return self.handle

    def __exit__(self, exc_type, exc_value, exc_tb):
        IcmpCloseHandle(self.handle)


class Icmp6Handle(object):
    def __init__(self):
        self.handle = Icmp6CreateFile()

    def __enter__(self):
        return self.handle

    def __exit__(self, exc_type, exc_value, exc_tb):
        IcmpCloseHandle(self.handle)


def inet_addr(ip):
    return IPAddr(struct.unpack("L", socket.inet_aton(ip))[0])


def inet6_addr(ip):
    return sockaddr_in6(socket.AF_INET6.value,
                        0,
                        0,
                        in6_addr.from_buffer_copy(socket.inet_pton(socket.AF_INET6, ip)),
                        0)


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


def ping6(handle, address, *, timeout=1000, data=None, expected_count=10):
    address = inet6_addr(address)
    source = inet6_addr('::')
    options = IP_OPTION_INFORMATION(128, 0, 0, 0, 0)
    if data is None:
        data = os.urandom(32)
    bufsize = (ctypes.sizeof(ICMPV6_ECHO_REPLY) + len(data) + 8 +
               ctypes.sizeof(IO_STATUS_BLOCK)) * expected_count
    buf = ctypes.create_string_buffer(bufsize)
    
    count = Icmp6SendEcho2(IcmpHandle=handle,
                           Event=None,
                           ApcRoutine=None,
                           ApcContext=None,
                           SourceAddress=source,
                           DestinationAddress=ctypes.byref(address),
                           RequestData=data,
                           RequestSize=len(data),
                           RequestOptions=ctypes.byref(options),
                           ReplyBuffer=buf,
                           ReplySize=bufsize,
                           Timeout=timeout)
    Icmp6ParseReplies(ReplyBuffer=buf, ReplySize=bufsize)

    replies = ctypes.cast(buf, ctypes.POINTER(ICMPV6_ECHO_REPLY * count)).contents
    replies = [ Icmp6EchoReply(r) for r in replies ]
    
    return replies
