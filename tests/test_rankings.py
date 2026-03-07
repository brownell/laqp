# Test rankings generation
from leaderboards import generate_leaderboards
from database import get_result
from config import LEADERBOARDS, RANKINGS

# Generate
sections = generate_leaderboards('2024', LEADERBOARDS, RANKINGS)

# Check a user
result = get_result('2024', 'K5ABC')
print(f"Rankings: {result['rankings']}")
# {'NQ': 1, 'NS': 2, 'NL': 5}

# Verify ranking count
for code, rank in result['rankings'].items():
    print(f"  {RANKINGS[code]}: Rank {rank}")