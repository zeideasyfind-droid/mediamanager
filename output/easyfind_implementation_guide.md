# EasyFind Property Formatter — Final Implementation Guide

This guide combines the implementation plan, Cloud Run responsibilities, and the two core artifacts you asked for: WhatsApp reply format standardization and field format normalization. The current repository already uses a canonical property normalizer and WhatsApp formatter as the single source of truth for message generation, which this guide preserves. [cite:31][cite:32]

## Architecture goal

Build a web application where an operator submits raw property text and property photos, and the system produces a ready-to-share WhatsApp message with normalized property details, a Google Maps link, and a Google Drive gallery link. The current repository already centers formatting around a single normalization layer and a WhatsApp caption builder, so the new system should keep that same pattern rather than splitting formatting logic across multiple places. [cite:31][cite:34]

## Phase-by-phase implementation

### Phase 1 — Input and property linking

The web app should have one section for raw property details and another for raw property images. As soon as both are submitted, Cloud Run should create one linked property record so the text dump and the uploaded image batch are always treated as one unit of work. This matches the current repo’s operator-first admin workflow where a single property submission moves through all downstream steps together. [cite:34]

### Phase 2 — Property extraction and normalization

Cloud Run should receive the raw property dump and pass it through the EasyFind normalization layer. The first line remains the source of truth for furnishing, BHK, bathrooms, balconies, and utility, while labeled lines handle rent, deposit, maintenance, area, floor, availability, tenant preference, pets, community, and location. The final normalized structure must remain aligned to the repo’s current canonical formatter behavior so the output stays consistent across all future channels. [cite:31][cite:32]

### Phase 3 — Maps and missing detail recovery

If a Google Maps link is present, the system should use it directly and treat it as the strongest source for property name or locality recovery when those values are missing. If no Maps link is present but a society name is given, the AI layer may resolve the best matching Google Maps entry and attach that link to the property record. If neither a society name nor a Maps link exists, the system should fall back to the provided location text and treat the property as non-gated or standalone for formatting purposes. This approach follows your final rule set for flexible gated versus non-gated handling. [cite:31]

### Phase 4 — Image enhancement and storage staging

Cloud Run should coordinate the uploaded image batch and assign enhancement work to the image AI layer asynchronously. Final enhanced images should be staged into cloud storage before being organized into a Drive folder, which fits an event-driven workflow pattern well because Pub/Sub is designed for asynchronous decoupled processing and Cloud Run can consume Pub/Sub-driven work safely. [web:35][web:41]

### Phase 5 — Resizing and padding ownership in Cloud Run

Cloud Run should own all deterministic image reshaping work after AI enhancement is complete. That means Cloud Run should resize images to the portal or output dimensions you define, and when padding is needed it should create the padding using a blurred, scaled version of the original image so the result still looks premium and consistent. This kind of stateless image resizing flow is a natural fit for Cloud Run, and Google Cloud examples show Cloud Run being used as the image resizing layer over cloud storage assets. [web:39][web:45]

### Phase 6 — Google Drive gallery creation

After enhancement and resizing are complete, the system should upload the final image set into a dedicated Google Drive folder for that property batch and produce a shareable gallery link. That Drive link becomes the official gallery link inserted into the WhatsApp output and should always represent the enhanced, final image set rather than the raw uploaded photos. This preserves your requirement that the gallery link correspond to the processed image batch, not the originals. [cite:34]

### Phase 7 — WhatsApp output assembly

Once normalized text, maps data, and Drive gallery link are ready, Cloud Run should trigger the WhatsApp formatting step using the EasyFind standard. The output should be one final ready-to-copy WhatsApp message, with line omissions handled cleanly for missing fields and with gated versus standalone closing logic applied consistently. The repo already has a dedicated WhatsApp caption builder and sender flow, so the new app should keep output assembly centralized in one formatter stage before any sending or copy action happens. [cite:29][cite:31]

### Phase 8 — Final delivery and review

The frontend output panel should show the final WhatsApp message, the Google Maps link, and the Google Drive gallery link together. Operators should be able to copy the message in one click, and any warning state such as missing location should be surfaced before the final copy action. This preserves the current success-and-verification style used in the repo, where the generated result is explicitly shown after processing. [cite:34]

## Cloud Run responsibility summary

Cloud Run is the main orchestrator and should do the following:

- Accept raw property details and uploaded images.
- Create and maintain the linked property job record.
- Trigger normalization and missing-detail recovery.
- Dispatch image enhancement tasks asynchronously.
- Perform deterministic resizing and blurred-background padding after enhancement.
- Stage processed files for Drive upload.
- Collect the Drive gallery link and Maps link.
- Assemble the final WhatsApp message using the EasyFind formatter rules.
- Return the final copy-ready output to the frontend.

This division keeps AI focused on extraction, enhancement, and formatting polish, while Cloud Run owns workflow control and deterministic business operations. That separation mirrors the central-orchestrator design you proposed and fits Cloud Run plus Pub/Sub well. [web:35][web:41][cite:34]

---

# Artifact 1 — WhatsApp Reply Format Standardization

```text
EASYFIND WHATSAPP REPLY FORMAT STANDARD

1. TITLE LINE
Format:
*👉{Furnishing} {BHK} BHK, {bath phrase} with {balcony phrase}{utility}*

Examples:
*👉Semi Furnished 3 BHK, 3 Bathrooms with 1 Balcony + Utility*
*👉Fully Furnished 3 BHK, 3 Attached Bathrooms with 5 Balconies + Utility*
*👉Semi Furnished 2 BHK, 2 Bathrooms with 1 Balcony*

Rules:
- Entire title line must be bold.
- 👉 appears only at the start of the title line.
- “+ Utility” appears only if utility is present.
- 1 bathroom → “1 Bath” or “1 Attached Bath”
- 2 or more bathrooms → “N Bathrooms” or “N Attached Bathrooms”
- 1 balcony → “1 Balcony”
- 2 or more balconies → “N Balconies”

2. BODY FIELD ORDER
Use this exact field order:
Rent
Maintenance
Deposit
Sq. Ft.
Floor
Available From
Preferred Tenant
Diet Preference
Pets
Community
Location

3. BODY FIELD FORMAT
Rent: ₹{amount}
Maintenance: {₹amount or text}
Deposit: ₹{amount}
Sq. Ft.: {number}
Floor: {floor}
Available From: {full date or Ready to occupy}
Preferred Tenant: {value}
Diet Preference: {value}
Pets: {value}
Community: {value}
Location: *{full location}*

Rules:
- Location value only must be bold.
- Diet Preference line must be omitted if the normalized value is “No preference”, “None”, or “Any”.
- Any empty field must be omitted entirely.
- Do not print placeholders like N/A or blank labels.

4. GALLERY LINE
Format:
*📸 Gallery:* {google drive folder link}

Rules:
- Gallery label must be bold.
- Gallery line appears only if a Drive gallery link exists.
- The Drive link must represent the enhanced final image batch.

5. CLOSING BLOCK — GATED / SEMI GATED WITH PROPERTY NAME
Format:
*{Property Name}*
📍 Map: {google maps link}

Rules:
- Property name must be bold.
- Map line must use the 📍 emoji and the “Map:” label.
- Use this closing block when a real property or society name is known.

6. CLOSING BLOCK — STANDALONE / NO PROPERTY NAME
Format:
📍 Near {Location}
{google maps link}

Rules:
- Do not invent a society name.
- Use the locality or landmark as the closing reference.
- Use this format when the property is standalone, independent, open, or unnamed.

7. SPACING RULES
- One blank line after the title.
- No blank lines between body fields.
- One blank line before the Gallery line block.
- One blank line before the closing block.
- No trailing decorative text.

8. FINAL OUTPUT PRINCIPLE
The WhatsApp message must be clean, premium, and ready to send without edits.
```

---

# Artifact 2 — Field Format Normalization

```text
EASYFIND FIELD NORMALIZATION STANDARD

A. TITLE LINE FIELDS
These fields must be extracted from the first line only:
- Furnishing
- BHK
- Bathrooms
- Bathroom Type
- Balconies
- Utility

Furnishing normalization:
- fully furnished / fully permitted → Fully Furnished
- semi furnished / semi-furnished / semi permitted → Semi Furnished
- unfurnished / bare shell → Unfurnished
- partially furnished / well furnished → Semi Furnished

BHK normalization:
- 2 BHK / 2BHK / 2bhk → 2
- 2.5 BHK / 2.5BHK → 2.5
- WhatsApp display always becomes: {BHK} BHK

Bathrooms normalization:
- 1 Bathroom / 1 Bath → 1 Bath
- 2 Bathrooms / 2 Bath / 2 Baths → 2 Bathrooms
- 3 Attached Bathroom / 3 Attached Bath → 3 Attached Bathrooms

Balcony normalization:
- 1 Balcony / 1 balcony / 1 Baicony → 1 Balcony
- 2 Balcony / 2 Balconies → 2 Balconies

Utility normalization:
- If “utility” appears in title → append “ + Utility” in title output
- If absent → omit utility suffix

B. MONEY FIELDS
Rent and Deposit:
- 10k / ₹10k / Rs 10k → ₹10,000
- 40k → ₹40,000
- 42k → ₹42,000
- 43k → ₹43,000
- 45k → ₹45,000
- 60k → ₹60,000
- 90k → ₹90,000
- 1L / 1 lakh → ₹1,00,000
- 1.2L / 1.2 lakh → ₹1,20,000
- 1.5L / 1.5 lakh → ₹1,50,000
- 2L / 2 lakh → ₹2,00,000
- 2.5L / 2.5 lakh / 2 lakh 50 thousand → ₹2,50,000
- 3L → ₹3,00,000
- 3.6L → ₹3,60,000
- 4L → ₹4,00,000
- 50000 / 50,000 → ₹50,000
- 100000 / 1,00,000 → ₹1,00,000
- 250000 / 2,50,000 → ₹2,50,000

Maintenance:
Numeric:
- 5k / 5000 / 5,000 → ₹5,000
- 5.5k → ₹5,500
- 4.5k → ₹4,500
- 5.1k → ₹5,100
- 6.7k → ₹6,700
- 3750 → ₹3,750
- 3826 → ₹3,826
- 3996 → ₹3,996

Text:
- Inclusive → Inclusive
- Water charges → Water charges
- Society charges → Society charges
- Included in rent → Included in rent
- Nil / NA / N/A / none → Nil

C. AREA
Normalize all to a plain number with no commas and no units:
- 1200 sqft / 1,200 sqft / 1200 sq ft → 1200
- 1726 Sq.Ft. → 1726
- 1800 → 1800
- 2320 → 2320
- 1143 / 1,143 → 1143
- 1110 → 1110
- 1166 → 1166
- 1100 → 1100
- 1280 → 1280
- 1775 → 1775

Display format:
Sq. Ft.: {number}

D. FLOOR
Output exactly as intended for display:
- 12/14
- 6/14
- 1/5
- 3/4
- 13/14
- 5/8
- 2/3
- 1/14
- Ground
- G/5
- Top floor
- Basement

E. AVAILABLE FROM
Always normalize to full readable output:
- Aug 1 / Aug. 1 / 01 Aug / 1 Aug → August 1
- Aug 10 → August 10
- Aug 16 → August 16
- Sep 1 / Sept 1 / 01 Sep → September 1
- Oct 1 → October 1
- Nov 15 → November 15
- Jan 1 → January 1
- Jul 15 → July 15

Immediate occupancy normalization:
- Immediately / Vacant / Today / Now / Ready → Ready to occupy

F. PREFERRED TENANT
Always Title Case:
- anyone / no preference → Anyone
- family → Family
- working professionals → Working Professionals
- bachelors → Bachelors
- bachelors/family → Bachelors/Family
- single → Single

G. DIET PREFERENCE
Normalize:
- Veg only / Veg / Vegetarian → Veg
- Non Veg / Non-Veg / nonveg → Non-Veg
- No preference / None / Any → omit this line entirely from WhatsApp output

H. PETS
Normalize:
- Allowed / Yes / ok / Pets ok → Allowed
- Not Allowed / No → Not Allowed

I. COMMUNITY
Normalize:
- Gated / Gated Community → Gated
- Semi Gated → Semi Gated
- Open → Open
- Independent → Independent
- Society → Society

J. LOCATION
- Preserve the full location text for WhatsApp display.
- In WhatsApp output, display as: Location: *{full location}*
- If missing but Maps link exists, recover locality from Maps.
- If missing and no Maps link exists, flag for manual review.

K. PROPERTY NAME
- Extract from the named property or society if available.
- If a Maps link reveals a real property name, use it.
- If no valid property name exists, do not invent one.
- Standalone properties must fall back to a landmark-style closing.

L. GOOGLE MAPS LINK
Priority order:
1. Use provided Google Maps link if available.
2. If absent but society/property name exists, AI may resolve the best matching Google Maps link.
3. If absent and only location exists, treat as standalone/non-gated and use location text.

M. GALLERY LINK
- Always use the Google Drive folder containing the final enhanced image batch.
- If absent, omit the Gallery line entirely.
```
