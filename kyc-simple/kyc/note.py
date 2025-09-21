from typing import Dict, Any

TEMPLATE = """# KYC Risk Note (Demo)

## Summary
This customer appears to be **{name}** (DOB: **{dob}**). We found an ID with passport number **{passport_no}** and a proof of address: **{address}**, {city}, {country}.

## Facts (with citations)
- Name: **{name}** [source: {name_source}]
- DOB: **{dob}** [source: mixed]
- Passport No: **{passport_no}** [source: {id_source}]
- Address: **{address}**, {city}, {country} [source: {addr_source}]

## Ownership
{owners_block}

## Checks
- ID present: **{id_present}**
- Address present: **{address_present}**
- Owners sum to 100%: **{owners_sum_to_100}**

> Notes: This is a demo. All claims must be backed by the cited file names above.
"""

def owners_md(owners):
    if not owners:
        return "- (none provided)\n"
    lines = []
    for o in owners:
        lines.append(f"- {o.get('name','?')}: {o.get('percent','?')}% [source: ownership.pdf]")
    return "\n".join(lines) + "\n"

def draft_note(profile: Dict[str, Any], checks: Dict[str, Any]) -> str:
    name = profile.get("name") or "(unknown)"
    dob = profile.get("dob") or "(unknown)"
    passport_no = profile.get("id", {}).get("passport_no") or "(missing)"
    id_source = profile.get("id", {}).get("source") or "(unknown)"
    addr = profile.get("address", {}).get("address") or "(missing)"
    city = profile.get("address", {}).get("city") or "(missing)"
    country = profile.get("address", {}).get("country") or "(missing)"
    addr_source = profile.get("address", {}).get("source") or "(unknown)"
    name_source = profile.get("name_source", "(unknown)")

    return TEMPLATE.format(
        name=name,
        dob=dob,
        passport_no=passport_no,
        id_source=id_source,
        address=addr,
        city=city,
        country=country,
        addr_source=addr_source,
        name_source=name_source,
        owners_block=owners_md(profile.get("owners")),
        id_present=checks.get("id_present"),
        address_present=checks.get("address_present"),
        owners_sum_to_100=checks.get("owners_sum_to_100"),
    )
