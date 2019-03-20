winping
=======

Ping implementation which utilizes Windows ICMP API

## Installation

Standard Python package installation.

## Usage

### Utility

#### Synopsis

```
C:\>winping --help
usage: winping [-h] [-w TIMEOUT] [-l SIZE] [-t | -n COUNT] address

Ping implementation which utilizes Windows ICMP API

positional arguments:
  address     specifies the host name or IP address of the destination

optional arguments:
  -h, --help  show this help message and exit
  -w TIMEOUT  timeout in milliseconds to wait for each reply (default: 1000)
  -l SIZE     timeout in seconds to wait for each reply (default: 32)
  -t          ping the specified host until stopped (default: False)
  -n COUNT    number of echo requests to send (default: 4)

```

#### Example

```
C:\>winping google.com

Pinging google.com [172.217.20.206] with 32 bytes of data:
Reply from 172.217.20.206: bytes=32 time=29ms TTL=57
Reply from 172.217.20.206: bytes=32 time=25ms TTL=57
Reply from 172.217.20.206: bytes=32 time=24ms TTL=57
Reply from 172.217.20.206: bytes=32 time=25ms TTL=57

Ping statistics for 172.217.20.206:
    Packets: Sent = 4, Received = 4, Lost = 0 (0.00% loss),
Approximate round trip times in milli-seconds:
    Minimum = 24ms, Maximum = 29ms, Average = 26ms

```

Also, if python scripts are not in your system path, you may run it like this: `python -m winping`

### Library

```python3
import winping
with winping.IcmpHandle() as h:
    resp = winping.ping(h, '8.8.8.8')
print(resp[0].RoundTripTime)
```

For example of working ping utility see [winping/\_\_main\_\_.py](winping/__main__.py).

## Limitations

* Works only on Windows XP and newer.
* No asyncio support at this moment, but you may run ping in thread executor.
* Only IPv4 supported at this moment.
* Alpha-software: library API may change.
