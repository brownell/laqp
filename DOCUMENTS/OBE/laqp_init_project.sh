#!/bin/bash
# Louisiana QSO Party Processor - Project Initialization Script
# This creates all necessary directories and placeholder files

echo "Initializing Louisiana QSO Party Processor project structure..."

# Create main directories
mkdir -p config
mkdir -p data
mkdir -p laqp/{models,core,utils,cli}
mkdir -p web/{routes,templates,static}
mkdir -p logs/{incoming,validated,prepared,problems,reports}
mkdir -p output/{scores,statistics}
mkdir -p tests/sample_logs
mkdir -p scripts

# Create .gitkeep files to preserve empty directories in git
touch logs/incoming/.gitkeep
touch logs/validated/.gitkeep
touch logs/prepared/.gitkeep
touch logs/problems/.gitkeep
touch logs/reports/.gitkeep
touch output/scores/.gitkeep
touch output/statistics/.gitkeep
touch tests/sample_logs/.gitkeep

# Create __init__.py files for Python packages
touch config/__init__.py
touch laqp/__init__.py
touch laqp/models/__init__.py
touch laqp/core/__init__.py
touch laqp/utils/__init__.py
touch laqp/cli/__init__.py
touch web/__init__.py
touch web/routes/__init__.py
touch tests/__init__.py

# Create placeholder files for modules to be implemented
cat > laqp/core/preparation.py << 'EOF'
"""
Louisiana QSO Party Log Preparation

TODO: Adapt from TX preparation.py
- Convert frequency to band
- Split multi-parish QSOs
- Determine categories
"""

def prepare_log(log_path, output_path):
    """Prepare a validated log for scoring"""
    raise NotImplementedError("Preparation module not yet implemented")
EOF

cat > laqp/core/scoring.py << 'EOF'
"""
Louisiana QSO Party Scoring

TODO: Adapt from TX scoring.py
- Calculate QSO points (2 for phone, 4 for CW/digital)
- Calculate multipliers (per band/mode)
- Apply bonuses (N5LCC, rover activation)
"""

def score_log(log_path):
    """Score a prepared log"""
    raise NotImplementedError("Scoring module not yet implemented")
EOF

cat > laqp/core/statistics.py << 'EOF'
"""
Louisiana QSO Party Statistics

TODO: Adapt from TX statistics.py
- Aggregate contest statistics
- Parish activity
- Band/mode breakdown
"""

def generate_statistics(log_paths):
    """Generate contest statistics from all logs"""
    raise NotImplementedError("Statistics module not yet implemented")
EOF

cat > laqp/utils/file_ops.py << 'EOF'
"""
File operation utilities
"""
import shutil
from pathlib import Path

def safe_copy(src, dst):
    """Safely copy a file"""
    shutil.copy2(str(src), str(dst))

def safe_move(src, dst):
    """Safely move a file"""
    shutil.move(str(src), str(dst))

def ensure_dir(path):
    """Ensure directory exists"""
    Path(path).mkdir(parents=True, exist_ok=True)
EOF

cat > laqp/utils/cabrillo.py << 'EOF'
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
EOF

cat > laqp/utils/callsign.py << 'EOF'
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
EOF

# Copy data files from TX if they exist, otherwise create placeholders
if [ -f "WVE_Abbrevs.txt" ]; then
    cp WVE_Abbrevs.txt data/
    echo "Copied WVE_Abbrevs.txt to data/"
else
    cat > data/WVE_Abbrevs.txt << 'EOF'
AL
AK
AZ
AR
CA
CO
CT
DE
FL
GA
HI
ID
IL
IN
IA
KS
KY
LA
ME
MD
MA
MI
MN
MS
MO
MT
NE
NV
NH
NJ
NM
NY
NC
ND
OH
OK
OR
PA
RI
SC
SD
TN
TX
UT
VT
VA
WA
WV
WI
WY
DC
AB
BC
MB
NB
NL
NS
NT
NU
ON
PE
QC
SK
YT
EOF
    echo "Created placeholder WVE_Abbrevs.txt"
fi

# Create sample test log
cat > tests/sample_logs/TEST.log << 'EOF'
START-OF-LOG: 3.0
CALLSIGN: TEST123
CONTEST: LA-QSO-PARTY
CATEGORY-OPERATOR: SINGLE-OP
CATEGORY-POWER: LOW
CATEGORY-STATION: FIXED
EMAIL: test@example.com
QSO: 7040 CW 2025-04-05 1430 TEST123 599 GA W5TEST 599 ORLE
QSO: 14255 PH 2025-04-05 1445 TEST123 59 GA W5TEST 59 JEFF
END-OF-LOG:
EOF

echo ""
echo "Project structure created successfully!"
echo ""
echo "Next steps:"
echo "1. Install dependencies: pip install -r requirements.txt"
echo "2. Initialize database: python -c \"from laqp.models.database import Database; from config.config import DATABASE_URL; Database(DATABASE_URL).create_tables()\""
echo "3. Place logs in logs/incoming/"
echo "4. Run validator: python scripts/process_all_logs.py --validate-only"
echo ""
echo "The project is ready for development!"
