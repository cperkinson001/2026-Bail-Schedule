# LA County Bail Schedule Search

A single-page, static web app for searching the Los Angeles County Superior Court's
**Felony Bail Schedule** and **Misdemeanor Bail Schedule** (effective January 1, 2026).

Search by **code section** (e.g. `273.5`, `459`) or by **offense description**
(e.g. `burglary`, `domestic battery`) and instantly see:

- The code section
- The offense description
- The **Pre-Arraignment Release Protocol** — Cite and Release (CR), Book and Release (BR),
  Magistrate Review (MR), a required dollar bail amount, or "ineligible for release"

## Live demo

Enable GitHub Pages for this repo (Settings → Pages → Deploy from branch → `main` / root),
then visit `https://<your-username>.github.io/<repo-name>/`.

## Files

| File | Purpose |
|---|---|
| `index.html` | The entire app — search UI, styling, and logic (no build step, no dependencies) |
| `data.js` | The bail schedule dataset as a JS array (`BAIL_DATA`), loaded by `index.html` |
| `scripts/build_felony.py` | Python script that generated the felony portion of the dataset |
| `scripts/build_misd1.py` / `scripts/build_misd2.py` | Python scripts that generated the misdemeanor portion of the dataset |

## Keeping the data current

A scheduled GitHub Action (`.github/workflows/check-bail-schedule-updates.yml`)
runs automatically on the **1st of every month** (and can be triggered manually
from the Actions tab):

1. It downloads both official source PDFs fresh from lacourt.ca.gov's storage.
2. It hashes them and compares against the hashes recorded in `meta.json`.
3. If nothing changed, it just updates the "last checked" date — silent, no action needed.
4. If either PDF changed, it:
   - saves the new PDFs to `pending-review/` in the repo,
   - sets `update_pending: true` in `meta.json` (which makes a warning banner appear
     at the top of the live app),
   - opens a GitHub Issue linking to the new PDFs so it's easy to review and update.

**What it deliberately does *not* do:** automatically re-parse the PDF and overwrite
`data.js` with no human review. The bail amounts and release protocols in this dataset
carry real consequences if wrong, and PDF table parsing is error-prone — so a genuine
schedule change is surfaced for a person (or an assistant, working from the diff) to
transcribe carefully, the same way the original dataset was built, rather than applied
silently. To complete an update once the issue fires:

1. Diff the new PDF in `pending-review/` against the previous version.
2. Update the entry lists in `scripts/build_felony.py` / `build_misd1.py` / `build_misd2.py`.
3. Regenerate `data.js` (see "Regenerating the dataset" below).
4. Update `schedule_effective_date` in `meta.json` and set `update_pending: false`.
5. Commit, push, and close the issue.

## Data source

Transcribed from the official Superior Court of California, County of Los Angeles
bail schedules:

- Felony Bail Schedule, Eff. Jan 1, 2026 —
  `https://lascpubstorage.blob.core.windows.net/cpw/LIBOPSCriminal-32-FelonyBailSchedule.pdf`
- Misdemeanor Bail Schedule, Eff. Jan 1, 2026 —
  `https://lascpubstorage.blob.core.windows.net/cpw/LIBOPSCriminal-54-MisdemeanorBailSchedule.pdf`

Current/interim amendments are always posted at `https://www.lacourt.ca.gov`.

## Regenerating the dataset

The dataset (`data.js`) was built with the scripts in `scripts/`. To rebuild:

```bash
cd scripts
python3 build_felony.py      # writes felony.json
python3 build_misd1.py       # writes misd_part1.json
python3 build_misd2.py       # writes misdemeanor.json and bail_data.json
python3 -c "
import json
data = json.load(open('bail_data.json'))
with open('../data.js', 'w') as f:
    f.write('const BAIL_DATA = ')
    json.dump(data, f)
    f.write(';')
"
```

## Disclaimer

This tool is provided for **quick reference only**. Bail amounts and pre-arraignment
release protocols change; always verify against the current official schedule at
lacourt.ca.gov before relying on this information operationally. This is not legal advice.

## License

MIT — see `LICENSE`.
