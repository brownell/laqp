"""
Cabrillo format utilities
"""

def parse_cabrillo_line(line):
    """Parse a Cabrillo QSO line"""
    parts = line.strip().split()
    if parts[0] != "QSO:":
        return None
    
    return {
        'freq_khz': int(parts[1]),
        'mode': parts[2],
        'date': parts[3],
        'time': parts[4],
        'sent_call': parts[5],
        'sent_rst': parts[6],
        'sent_qth': parts[7],
        'rcvd_call': parts[8],
        'rcvd_rst': parts[9],
        'rcvd_qth': parts[10]
    }
