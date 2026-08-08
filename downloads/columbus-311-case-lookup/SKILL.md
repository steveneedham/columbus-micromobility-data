---
name: columbus-311-case-lookup
description: Look up a Columbus, Ohio 311 case by address and CAS ID, then report status, description, micromobility vendor evidence, ADA obstruction evidence, and timestamps.
---

# Columbus 311 case lookup

Use this workflow when a user provides a Columbus 311 case number such as `CAS-3089579-L6N6Q9` and an address or nearby intersection.

## Source and access

Use the public, read-only CBUS 311 portal:

`https://columbusoh.oneviewcrm.cc/servicerequests/nearby`

No login is required. Do not submit, edit, or comment on a request.

## Important search constraint

The portal does not search by the human-readable CAS ID. Its search field treats a CAS ID as an address and fails. Search by the supplied street address or intersection, then scan the nearby results for the exact CAS ID. Detail-page URLs use an internal UUID and cannot be guessed from the CAS ID.

If the user supplies only a case ID, ask for the address, intersection, or general area before proceeding.

## Lookup procedure

1. Open the nearby-requests page in a fresh browser tab or session.
2. Wait for the initial request list to finish loading.
3. Search the supplied address or intersection with `Columbus, OH` appended.
4. Wait for the geocoded address and nearby results.
5. Find the row whose `ID #CAS-...` exactly matches the requested case.
6. Open that row and read the request type, status, full address, description, created time, updated time, comments, and available photos.
7. If the page hangs on a loading spinner, start a fresh tab or browser session instead of repeatedly retrying the same page.

## Vendor and device evidence

Apply this section only to micromobility requests such as “Shared Electric Bike & Scooters.”

Prefer evidence in this order:

1. The description explicitly names a vendor or device number.
2. A usable attached photo shows readable branding or a recognizable vehicle color scheme.
3. Otherwise report `Unknown / not stated`.

Common public-fleet cues include:

- Veo: teal-and-black branded scooter or bike.
- Spin: orange or blue branded scooter or bike.
- Other named vendors: report the name exactly as shown.

List every vendor and device mentioned. State the evidence method as `from text` or `from photo`. Do not infer a vendor from a broken image or generic placeholder.

## ADA and accessibility evidence

Report `Yes` when the description or photo indicates obstruction of a sidewalk, curb ramp, crosswalk, bus stop, entrance, or an accessible clear path. Language about insufficient wheelchair clearance is direct supporting evidence.

Report `No` only when the available evidence affirmatively shows or describes proper parking without an obstruction.

Report `Unclear` when the case merely describes a device’s presence, location, duration, or improper parking without enough evidence to determine whether an accessible route was blocked. Include the supporting phrase and do not guess.

## Response format

Return:

- Case ID
- Request type
- Current status, including both the portal status and status reason when available
- Full address
- Description
- Vendor(s) and device(s), with evidence method
- ADA blocking: Yes, No, or Unclear, with supporting evidence
- Created timestamp
- Updated timestamp
- Direct public case link

Use absolute timestamps and include the time zone. Clearly distinguish portal-confirmed facts from interpretation.

