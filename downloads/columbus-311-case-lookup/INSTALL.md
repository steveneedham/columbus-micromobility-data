# Install the Columbus 311 case lookup workflow

This package contains a public, read-only address-first workflow for finding a Columbus 311 case and evaluating micromobility vendor and accessibility evidence.

## Claude

1. Download `columbus-311-case-lookup.zip` from the dashboard.
2. In Claude, enable **Code execution and file creation** under **Settings > Capabilities** if needed.
3. Open **Customize > Skills**.
4. Select **+**, then **+ Create skill**, then **Upload a skill**.
5. Upload the ZIP and enable the skill.
6. Ask Claude to use `columbus-311-case-lookup`, supplying both the CAS ID and address.

Claude supports this package as a native custom skill.

## ChatGPT

1. Download `columbus-311-case-lookup.txt` from the dashboard.
2. Create a new ChatGPT Project.
3. Upload the Markdown file to the Project as a source.
4. In **Project settings**, add: `Follow the uploaded Columbus 311 case lookup workflow whenever I provide a Columbus CAS ID and address.`
5. Start a Project chat and provide the CAS ID and address. Allow web access when prompted.

This is Project context, not a native Claude-style skill installation.

## Gemini

1. Download `columbus-311-case-lookup.txt` from the dashboard.
2. In the Gemini web app, open **Gems > New Gem**.
3. Name it `Columbus 311 Case Lookup`.
4. Paste the workflow purpose into the Gem instructions.
5. Under **Knowledge**, select **Add files** and upload the Markdown file.
6. Save the Gem, then provide the CAS ID and address in a Gem chat.

This is a reusable Gem with a knowledge file, not a native Claude-style skill installation.

## Test prompt

`Use the Columbus 311 case lookup workflow to look up case CAS-3089579-L6N6Q9 at E COMO AVE & INDIANOLA AVE, Columbus, OH. Return the request type, status, full address, description, vendor and device evidence, ADA blocking evidence, and created and updated timestamps.`

## Safety

Review downloaded AI instructions before installing them. This workflow uses a public portal and requires no login. It should not submit, edit, or comment on a 311 request.
