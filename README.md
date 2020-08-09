winping
=======

Ping implementation which utilizes Windows ICMP API

---

:heart: :heart: :heart:

You can say thanks to the author by donations to these wallets:

- ETH: `0xB71250010e8beC90C5f9ddF408251eBA9dD7320e`
- BTC:
  - Legacy: `1N89PRvG1CSsUk9sxKwBwudN6TjTPQ1N8a`
  - Segwit: `bc1qc0hcyxc000qf0ketv4r44ld7dlgmmu73rtlntw`

---

## Installation

Standard Python package installation.

## Usage

### Utility

#### Synopsis

```
C:\>winping --help
usage: winping [-h] [-w TIMEOUT] [-l SIZE] [-t | -n COUNT] [-4 | -6] address

Ping implementation which utilizes Windows ICMP API

positional arguments:
  address     specifies the host name or IP address of the destination

optional arguments:
  -h, --help  show this help message and exit
  -w TIMEOUT  timeout in milliseconds to wait for each reply (default: 1000)
  -l SIZE     number of data bytes to be sent (default: 32)
  -t          ping the specified host until stopped (default: False)
  -n COUNT    number of echo requests to send (default: 4)
  -4          force using IPv4 (default: False)
  -6          force using IPv6 (default: False)

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

C:\>winping -6 google.com

Pinging google.com [2a00:1450:401b:804::200e] with 32 bytes of data:
Reply from 2a00:1450:401b:804::200e: time=79ms
Reply from 2a00:1450:401b:804::200e: time=77ms
Reply from 2a00:1450:401b:804::200e: time=76ms
Reply from 2a00:1450:401b:804::200e: time=75ms

Ping statistics for 2a00:1450:401b:804::200e:
    Packets: Sent = 4, Received = 4, Lost = 0 (0.00% loss),
Approximate round trip times in milli-seconds:
    Minimum = 75ms, Maximum = 79ms, Average = 77ms

```

Also, if python scripts are not in your system path, you may run it like this: `python -m winping`

### Library

```python3
import winping
with winping.IcmpHandle() as h:
    resp = winping.ping(h, '8.8.8.8')
print(resp[0].RoundTripTime)
with winping.Icmp6Handle() as h:
    resp = winping.ping6(h, '2a00:1450:401b:804::200e')
print(resp[0].RoundTripTime)
```

For example of working ping utility see [winping/\_\_main\_\_.py](winping/__main__.py).

## Limitations

* Works only on Windows XP / Windows Server 2003 and newer.
* No asyncio support at this moment, but you may run ping in thread executor.
