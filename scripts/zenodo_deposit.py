#!/usr/bin/env python3
"""
zenodo_deposit.py - Prepare a Zenodo deposition (DRAFT) for the Blue Thumb
chloride reproducibility archive, and STOP before the irreversible publish.

It builds a git archive of the current commit (tracked files only, so no
gitignored OCC raw data is uploaded), creates a Zenodo draft, uploads the
archive, and sets the metadata. It NEVER publishes: you review the draft and
click Publish in the Zenodo UI. Publishing is the irreversible step that mints
the permanent DOI and cannot be undone.

SECURITY: the API token is read from the ZENODO_TOKEN environment variable, or
from a local token file if that is unset. Never pass the token on the command
line and never paste it into a chat. It is a secret with write access to your
Zenodo account.

Usage (run it yourself so the token stays in your terminal):
    export ZENODO_TOKEN='your-token'
    python scripts/zenodo_deposit.py            # real Zenodo
    python scripts/zenodo_deposit.py --sandbox  # test on sandbox.zenodo.org first

Token scopes required: deposit:write and deposit:actions.
After publishing, paste the DOI into paper/main_v2.tex (the Data Availability
section and Supplemental S4).
"""
import os
import sys
import subprocess
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
SANDBOX = "--sandbox" in sys.argv
BASE = "https://sandbox.zenodo.org" if SANDBOX else "https://zenodo.org"
API = BASE + "/api/deposit/depositions"
TOKEN_FILE = Path.home() / ".config" / "zenodo" / "token"

METADATA = {
    "metadata": {
        "upload_type": "software",
        "title": "Blue Thumb volunteer chloride validation: analysis code and data",
        "creators": [
            {"name": "Ingram, Miguel", "affiliation": "Black Box Research Labs LLC"},
            {"name": "Dyer, Joseph J.", "affiliation": "Oklahoma Conservation Commission"},
            {"name": "Shaw, Kim", "affiliation": "Oklahoma Conservation Commission"},
        ],
        "description": (
            "Reproducibility archive for the manuscript validating Oklahoma Blue Thumb "
            "volunteer chloride measurements against professional agency data. Includes the "
            "analysis pipeline, the regional mixed-effects model and the stratified-subsampling "
            "geographic-confound test, the indoor-QA and variance-decomposition analyses, and a "
            "one-command verifier (verify.py) that recomputes every headline claim from the "
            "committed data. See README.md and QUICKSTART.md."
        ),
        "license": "cc-by-4.0",
        "version": "1.0.0",
        "keywords": ["citizen science", "water quality", "chloride", "volunteer monitoring",
                     "mixed-effects model", "reproducibility", "Blue Thumb",
                     "EPA Water Quality Portal"],
        "related_identifiers": [
            {"relation": "isSupplementTo",
             "identifier": "https://github.com/Black-Box-Research-Labs/ok-blue-thumb-data-validation",
             "scheme": "url"},
        ],
    }
}


def get_token():
    tok = os.environ.get("ZENODO_TOKEN")
    if tok:
        return tok.strip()
    if TOKEN_FILE.exists():
        return TOKEN_FILE.read_text().strip()
    sys.exit(
        "ZENODO_TOKEN is not set and no token file exists at " + str(TOKEN_FILE) + ".\n"
        "Set it in your own terminal:  export ZENODO_TOKEN='...'  then re-run.\n"
        "Do not paste the token into a chat."
    )


def main():
    token = get_token()
    params = {"access_token": token}

    archive = ROOT / "dist" / "bluestream-reproducibility.tar.gz"
    archive.parent.mkdir(exist_ok=True)
    sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT).decode().strip()
    subprocess.check_call(["git", "archive", "--format=tar.gz", "-o", str(archive), "HEAD"], cwd=ROOT)
    print(f"built archive of commit {sha}: {archive} ({archive.stat().st_size:,} bytes)")

    r = requests.post(API, params=params, json={})
    r.raise_for_status()
    dep = r.json()
    dep_id = dep["id"]
    bucket = dep["links"]["bucket"]
    print(f"created draft deposition {dep_id} on {BASE}")

    with open(archive, "rb") as fh:
        up = requests.put(f"{bucket}/{archive.name}", data=fh, params=params)
    up.raise_for_status()
    print(f"uploaded {archive.name}")

    md = requests.put(f"{API}/{dep_id}", params=params, json=METADATA)
    md.raise_for_status()
    print("metadata set")

    links = dep.get("links", {})
    edit_url = links.get("html") or f"{BASE}/deposit/{dep_id}"
    reserved = md.json().get("metadata", {}).get("prereserve_doi", {})
    print("\nDRAFT READY (not published).")
    print(f"  Review and edit:  {edit_url}")
    if reserved:
        print(f"  Reserved DOI (becomes final only when you publish): {reserved.get('doi')}")
    print("  Confirm title, authors, and license, and that the co-authors approve, then click")
    print("  Publish in the Zenodo UI. Publishing is IRREVERSIBLE.")
    print("  Finally paste the DOI into paper/main_v2.tex (Data Availability and Supplemental S4).")


if __name__ == "__main__":
    main()
