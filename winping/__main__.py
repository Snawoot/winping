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


def main():
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
                except RequestTimedOut:
                    requests += 1
                    lost += 1
                except OSError as e:
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

if __name__ == '__main__':
    main()
