import platform

def detect_arch():
    """
    Returns a string describing the CPU architecture.
    """
    return platform.machine()
