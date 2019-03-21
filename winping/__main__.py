import sys
import time
import argparse
import socket
import os

from . import *
from .errors import *


def parse_args():
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

    parser = argparse.ArgumentParser(
        description="Ping implementation which utilizes Windows ICMP API",
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
                        help="number of data bytes to be sent",
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

    proto_group = parser.add_mutually_exclusive_group()
    proto_group.add_argument("-4",
                             help="force using IPv4",
                             dest="force_ipv4",
                             action="store_true")
    proto_group.add_argument("-6",
                             help="force using IPv6",
                             dest="force_ipv6",
                             action="store_true")
    
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    ai_list = socket.getaddrinfo(args.address, 0)
    if (args.force_ipv4 or args.force_ipv6):
        target_af = socket.AF_INET if args.force_ipv4 else socket.AF_INET6
        ai_list = [ai for ai in ai_list if ai[0] == target_af]
    if not ai_list:
        print("Ping request could not find host %s. "
              "Please check the name and try again." % (args.address),
              file=sys.stderr)
        sys.exit(3)
    ip = ai_list[0][4][0]
    af = ai_list[0][0]
    ping_fun, Handle = ((ping, IcmpHandle) if af == socket.AF_INET
                        else (ping6, Icmp6Handle))
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
        with Handle() as handle:
            while True:
                count -= 1
                try:
                    res = ping_fun(handle, ip, timeout=args.timeout, data=data)
                except RequestTimedOut:
                    requests += 1
                    lost += 1
                except OSError as e:
                    print("Error: ", (e,), file=sys.stderr)
                else:
                    requests += 1
                    for rep in res:
                        if rep.Status == 0:
                            rtt = rep.RoundTripTime
                            max_rtt = max(max_rtt, rtt)
                            min_rtt = min(min_rtt, rtt)
                            sum_rtt += rtt
                            if af == socket.AF_INET:
                                print("Reply from %s: bytes=%d time=%dms TTL=%d" %
                                    (rep.Address,
                                     len(rep.Data),
                                     rtt,
                                     rep.Options.Ttl))
                                if rep.Data != data:
                                    print("Corrupted packet!", file=sys.stderr)
                            else:
                                print("Reply from %s: time=%dms" %
                                      (rep.Address, rtt))
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

if __name__ == '__main__':
    main()
