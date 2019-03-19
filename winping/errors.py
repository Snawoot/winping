class IcmpException(OSError):
    pass

class BufferTooSmall(IcmpException):
    pass

class DestinationNetUnreachable(IcmpException):
    pass

class DestinationHostUnreachable(IcmpException):
    pass

class DestinationProtocolUnreachable(IcmpException):
    pass

class DestinationPortUnreachable(IcmpException):
    pass

class NoResources(IcmpException):
    pass

class BadOption(IcmpException):
    pass

class HardwareError(IcmpException):
    pass

class PacketTooBig(IcmpException):
    pass

class RequestTimedOut(IcmpException):
    pass

class BadRequest(IcmpException):
    pass

class BadRoute(IcmpException):
    pass

class TTLExpiredInTransit(IcmpException):
    pass

class TTLExpiredOnReassembly(IcmpException):
    pass

class ParameterProblem(IcmpException):
    pass

class SourceQuench(IcmpException):
    pass

class OptionTooBig(IcmpException):
    pass

class BadDestination(IcmpException):
    pass

class GeneralFailure(IcmpException):
    pass

errno_map = {
    11001: BufferTooSmall,
    11002: DestinationNetUnreachable,
    11003: DestinationHostUnreachable,
    11004: DestinationProtocolUnreachable,
    11005: DestinationPortUnreachable,
    11006: NoResources,
    11007: BadOption,
    11008: HardwareError,
    11009: PacketTooBig,
    11010: RequestTimedOut,
    11011: BadRequest,
    11012: BadRoute,
    11013: TTLExpiredInTransit,
    11014: TTLExpiredOnReassembly,
    11015: ParameterProblem,
    11016: SourceQuench,
    11017: OptionTooBig,
    11018: BadDestination,
    11050: GeneralFailure,
}
