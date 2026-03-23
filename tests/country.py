import os
from pyhamtools import LookupLib, Callinfo
import pycountry

my_lookuplib = LookupLib(lookuptype='countryfile', filename='./reference_data/cty.plist', username='KJ5BYZ', pwd='rLM@$*2RFIBnaARG')
cic = Callinfo(my_lookuplib)

def get_iso2(country_name: str) -> str:
    try:
        results = pycountry.countries.search_fuzzy(country_name)
        return results[0].alpha_2
    except LookupError:
        print(country_name)
        return country_name
    
def lookup_callsign(callsign: str) -> dict:
    data = cic.get_all(callsign)
    data["iso2"] = get_iso2(data.get("country", ""))
    return data['country'], data['iso2']
    

print(lookup_callsign("DL2XYZ"))
print(lookup_callsign("JA1ABC"))
print(lookup_callsign("W5XYZ"))
print(lookup_callsign("kj5byz"))
print(lookup_callsign("VA3CJZ"))
print(lookup_callsign("VE3RGO"))
print(lookup_callsign("ZF2MA"))
print(lookup_callsign("KD5YS"))
print(lookup_callsign("IW9FFI"))
print(lookup_callsign("HP6LEF"))
print(lookup_callsign("DL3DXX"))
print(lookup_callsign("HP6LEF"))

def dxcc_to_iso2(dxcc_number: int, country_name: str) -> str | None:
    """Convert a DXCC entity number (or name fallback) to ISO 3166-1 alpha-2."""

    # Step 1: Check manual overrides for sub-national DXCC entities
    if dxcc_number in DXCC_TO_ISO2:
        return DXCC_TO_ISO2[dxcc_number]
    
def get_iso2_for_callsign(callsign: str) -> str | None:
    data = cic.get_all(callsign)
    return dxcc_to_iso2(
        dxcc_number=data.get("adif"),
        country_name=data.get("country", "")
    )

get_iso2_for_callsign("GM4XYZ")   # Scotland → "GB"
get_iso2_for_callsign("KL7ABC")   # Alaska   → "US"
get_iso2_for_callsign("EA6XYZ")   # Balearic → "ES"
get_iso2_for_callsign("DL2XYZ")   # Germany  → "DE"  (via pycountry fallback)
get_iso2_for_callsign("JA1ABC")   # Japan    → "JP" 
