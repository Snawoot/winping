winping
=======

Ping implementation which utilizes Windows ICMP API

## Installation

Standard Python package installation.

## Usage

### Utility

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

### Library

```python3
from winping.ping import *
with IcmpHandle() as h:
    resp = ping(h, '8.8.8.8')
print(resp[0].RoundTripTime)
```

For example of working ping utility see [winping/main.py](winping/main.py).
