from typing import Dict, Any

def run_checks(profile: Dict[str, Any]) -> Dict[str, Any]:
    present_id = bool(profile.get("id", {}).get("passport_no"))
    present_addr = bool(profile.get("address", {}).get("address"))
    owners = profile.get("owners", [])
    owners_sum_ok = None
    if owners:
        s = sum(o.get("percent", 0) for o in owners)
        owners_sum_ok = abs(s - 100.0) < 0.001

    return {
        "id_present": present_id,
        "address_present": present_addr,
        "owners_sum_to_100": owners_sum_ok,
        "all_required_docs_present": present_id and present_addr,
    }
