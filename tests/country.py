import os
from pyhamtools import LookupLib, Callinfo
import pycountry

my_lookuplib = LookupLib(lookuptype='countryfile', filename='./reference_data/cty.plist', username='KJ5BYZ', pwd='rLM@$*2RFIBnaARG')
cic = Callinfo(my_lookuplib)

def get_iso2(country_name: str) -> str:
    try:
        results = pycountry.countries.search_fuzzy(country_name)
        print(results)
        return results[0].alpha_2
    except LookupError:
        print(f"no 2-digit name: {country_name}")
        return country_name
    
def lookup_callsign(callsign: str) -> dict:
    print(f"callsign: {callsign}")
    data = cic.get_all(callsign)
    data["iso2"] = get_iso2(data.get("country", ""))
    # return data['country'], data['iso2']
    return data
    

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


print(lookup_callsign("GM4XYZ"))   # Scotland → "GB"
print(lookup_callsign("KL7ABC"))   # Alaska   → "US"
print(lookup_callsign("EA6XYZ"))   # Balearic → "ES"
print(lookup_callsign("DL2XYZ"))   # Germany  → "DE"  (via pycountry fallback)
print(lookup_callsign("JA1ABC"))   # Japan    → "JP" 
