from config.config import (
    freq_to_band,
    LA_PARISHES_FILE, WVE_ABBREVS_FILE,
    US_PREFIXES, CANADIAN_PREFIXES,
    PHONE_QSO_POINTS, CW_DIGITAL_QSO_POINTS,
    N5LCC_BONUS, ROVER_PARISH_BONUS,
    PHONE_MODES, CW_DIGITAL_MODES, PROVINCES, CONTEST_YEAR,
    LEADERBOARDS
)
for section in LEADERBOARDS:
    print('{')
    for sub in section[1:]:
        print(f"""'': '{sub["title"]}',""")
    print('}')