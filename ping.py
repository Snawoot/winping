import ctypes
import ctypes.wintypes
import argparse
import socket
import struct
import os


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
    def __enter__(self):
        self.handle = IcmpCreateFile()
        return self.handle
    def __exit__(self, exc_type, exc_value, exc_tb):
        IcmpCloseHandle(self.handle)


def inet_addr(ip):
    return IPAddr(struct.unpack("L", socket.inet_aton(ip))[0])


def check_positive_int(value):
    value = int(value)
    if value <= 0:
         raise argparse.ArgumentTypeError(
             "%s is an invalid positive number value" % value)
    return value


def check_nonnegative_int(value):
    value = int(value)
    if value < 0:
         raise argparse.ArgumentTypeError(
             "%s is an invalid non-negative number value" % value)
    return value


def check_size(value):
    value = int(value)
    if not (0 <= value <= 65500):
         raise argparse.ArgumentTypeError(
             "Bad data size, valid range is from 0 to 65500)")
    return value


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("address",
                        help="specifies the host name or IP address of the "
                        "destination")
    parser.add_argument("-w",
                        help="timeout in milliseconds to wait for each reply",
                        type=check_positive_int,
                        dest="timeout",
                        default=1000)
    parser.add_argument("-l",
                        help="timeout in seconds to wait for each reply",
                        type=check_size,
                        dest="size",
                        default=32)
    
    count_group = parser.add_mutually_exclusive_group()
    count_group.add_argument("-t",
                             help="ping the specified host until stopped",
                             dest="infinite",
                             action="store_true")
    count_group.add_argument("-n",
                             help="number of echo requests to send",
                             type=check_positive_int,
                             dest="count",
                             default=4)
    
    args = parser.parse_args()
    return args


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


def main():
    import sys
    import time
    args = parse_args()
    ip = socket.gethostbyname(args.address)
    data = os.urandom(args.size)
    count = args.count
    
    print("\nPinging %s [%s] with %d bytes of data:" %
              (args.address, ip, len(data)))

    requests = 0
    responses = 0
    lost = 0
    min_rtt = float("+inf")
    max_rtt = float("-inf")
    sum_rtt = 0
    
    try:
        with IcmpHandle() as handle:
            while True:
                count -= 1
                try:
                    res = ping(handle, ip, timeout=args.timeout, data=data)
                except OSError as e:
                    if e.errno == 11010:
                        requests += 1
                        lost += 1
                    else:
                        print("Error: %s", (e,), file=sys.stderr)
                else:
                    requests += 1
                    for rep in res:
                        if rep.Status == 0:
                            rtt = rep.RoundTripTime
                            max_rtt = max(max_rtt, rtt)
                            min_rtt = min(min_rtt, rtt)
                            sum_rtt += rtt
                            print("Reply from %s: bytes=%d time=%dms TTL=%d" %
                                (rep.Address,
                                 len(rep.Data),
                                 rtt,
                                 rep.Options.Ttl))
                            if rep.Data != data:
                                print("Corrupted packet!", file=sys.stderr)
                            responses += 1
                        else:
                            lost += 1
                finally:
                    if not args.infinite and count <= 0:
                        break
                time.sleep(1)
    except KeyboardInterrupt:
        pass

    if requests:
        print("\nPing statistics for %s:" % (ip,))
        print("    Packets: Sent = %d, Received = %d, Lost = %d (%.2f%% loss)," % (
            requests,
            responses,
            lost,
            100 * lost / requests))
    if responses:
        print("Approximate round trip times in milli-seconds:")
        print("    Minimum = %dms, Maximum = %dms, Average = %sms" %
              (min_rtt,
               max_rtt,
               int(round(sum_rtt / responses))))
        


if __name__=='__main__':
    main()
