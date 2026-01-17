"""
Callsign utilities
"""

def get_prefix(callsign):
    """Extract prefix from callsign"""
    for i, char in enumerate(callsign):
        if char.isdigit():
            return callsign[:i]
    return callsign

def is_us_call(callsign):
    """Check if callsign is US"""
    prefix = get_prefix(callsign)
    return prefix and prefix[0] in ('K', 'N', 'W')

def is_canadian_call(callsign):
    """Check if callsign is Canadian"""
    from config.config import CANADIAN_PREFIXES
    prefix = get_prefix(callsign)
    return prefix in CANADIAN_PREFIXES

def is_dx_call(callsign):
    """Check if callsign is DX (not US or VE)"""
    return not (is_us_call(callsign) or is_canadian_call(callsign))
