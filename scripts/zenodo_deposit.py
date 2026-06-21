#!/usr/bin/env python3
"""
zenodo_deposit.py - Prepare a Zenodo deposition (DRAFT) for the Blue Thumb
chloride reproducibility archive, and STOP before the irreversible publish.

It builds a git archive of the current commit (tracked files only, so no
gitignored OCC raw data is uploaded), targets a Zenodo deposition, uploads the
archive, and sets the metadata. It NEVER publishes: you review the draft and
click Publish in the Zenodo UI. Publishing is the irreversible step that mints
the permanent DOI and cannot be undone.

VERSIONING (why updating the repo later is not a problem):
  - A DRAFT is disposable. Nothing is frozen until you publish, so you can edit
    or delete a draft and re-run freely.
  - Publishing FREEZES that snapshot to a permanent version DOI. To update the
    repo after publishing, you do NOT make a fresh record; you cut a linked
    "new version" (--new-version) which gets its own version DOI under a stable
    concept DOI that always resolves to the latest version.
  - The paper cites the DOI but the DOI archives the paper. Resolve this with
    the reserved DOI: run once (a draft reserves a DOI, printed below), paste it
    into the paper, then re-run with --deposition <id> to refresh that SAME
    draft's archive so the frozen copy cites its own DOI, then publish.

MODES:
  (default)            create a new deposition draft (first time only)
  --deposition <id>    update an existing DRAFT in place (re-upload + metadata)
  --new-version <id>   create a linked new-version draft of a PUBLISHED record

SECURITY: the API token is read from the ZENODO_TOKEN environment variable, or
from a local token file if that is unset. Never pass the token on the command
line and never paste it into a chat. It is a secret with write access to your
Zenodo account.

Usage (run it yourself so the token stays in your terminal):
    export ZENODO_TOKEN='your-token'
    python scripts/zenodo_deposit.py                       # new draft
    python scripts/zenodo_deposit.py --deposition 123456   # refresh that draft
    python scripts/zenodo_deposit.py --new-version 123456 --version 1.1.0
    python scripts/zenodo_deposit.py --sandbox             # dry-run on sandbox

Token scopes required: deposit:write and deposit:actions.
After publishing, paste the DOI into paper/main_v2.tex (Data Availability + S4).
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
TOKEN_FILE = Path.home() / ".config" / "zenodo" / "token"

parser = argparse.ArgumentParser(description="Prepare a Zenodo deposition draft (does not publish).")
parser.add_argument("--sandbox", action="store_true", help="use sandbox.zenodo.org")
parser.add_argument("--deposition", help="update an existing DRAFT deposition in place")
parser.add_argument("--new-version", dest="new_version",
                    help="create a linked new-version draft of a PUBLISHED deposition id")
parser.add_argument("--version", default="1.0.0", help="version string for the metadata")
ARGS = parser.parse_args()

BASE = "https://sandbox.zenodo.org" if ARGS.sandbox else "https://zenodo.org"
API = BASE + "/api/deposit/depositions"


def metadata(version):
    return {"metadata": {
        "upload_type": "software",
        "title": "Blue Thumb volunteer chloride validation: analysis code and data",
        "version": version,
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
        "keywords": ["citizen science", "water quality", "chloride", "volunteer monitoring",
                     "mixed-effects model", "reproducibility", "Blue Thumb",
                     "EPA Water Quality Portal"],
        "related_identifiers": [
            {"relation": "isSupplementTo",
             "identifier": "https://github.com/Black-Box-Research-Labs/ok-blue-thumb-data-validation",
             "scheme": "url"},
        ],
    }}


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


def resolve_target(params):
    """Return the deposition (dict) we will upload to, per the chosen mode."""
    if ARGS.new_version:
        # newversion requires a PUBLISHED record; it returns a fresh editable draft.
        r = requests.post(f"{API}/{ARGS.new_version}/actions/newversion", params=params)
        r.raise_for_status()
        draft_url = r.json()["links"]["latest_draft"]
        dep = requests.get(draft_url, params=params)
        dep.raise_for_status()
        print(f"created new-version draft from published record {ARGS.new_version}")
        return dep.json()
    if ARGS.deposition:
        r = requests.get(f"{API}/{ARGS.deposition}", params=params)
        r.raise_for_status()
        print(f"updating existing draft {ARGS.deposition} in place")
        return r.json()
    r = requests.post(API, params=params, json={})
    r.raise_for_status()
    print("created a new draft deposition")
    return r.json()


def main():
    params = {"access_token": get_token()}

    archive = ROOT / "dist" / "bluestream-reproducibility.tar.gz"
    archive.parent.mkdir(exist_ok=True)
    sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT).decode().strip()
    subprocess.check_call(["git", "archive", "--format=tar.gz", "-o", str(archive), "HEAD"], cwd=ROOT)
    print(f"built archive of commit {sha}: {archive} ({archive.stat().st_size:,} bytes)")

    dep = resolve_target(params)
    dep_id = dep["id"]
    bucket = dep["links"]["bucket"]

    # Clear any existing/inherited files so the deposit holds exactly this commit.
    for f in dep.get("files", []):
        requests.delete(f"{API}/{dep_id}/files/{f['id']}", params=params)

    with open(archive, "rb") as fh:
        up = requests.put(f"{bucket}/{archive.name}", data=fh, params=params)
    up.raise_for_status()
    print(f"uploaded {archive.name}")

    md = requests.put(f"{API}/{dep_id}", params=params, json=metadata(ARGS.version))
    md.raise_for_status()
    print(f"metadata set (version {ARGS.version})")

    j = md.json()
    links = dep.get("links", {})
    edit_url = links.get("html") or f"{BASE}/deposit/{dep_id}"
    reserved = j.get("metadata", {}).get("prereserve_doi", {})
    concept = j.get("conceptdoi")
    print("\nDRAFT READY (not published).")
    print(f"  Deposition id:   {dep_id}")
    print(f"  Review and edit: {edit_url}")
    if reserved:
        print(f"  Reserved DOI (final only when you publish): {reserved.get('doi')}")
    if concept:
        print(f"  Concept DOI (stable across versions):       {concept}")
    print("  Confirm title, authors, and license, and that the co-authors approve, then click")
    print("  Publish in the Zenodo UI. Publishing is IRREVERSIBLE.")
    print("  To refresh this same draft after editing the paper:  --deposition", dep_id)
    print("  To version it after a prior publish:                 --new-version <published_id>")


if __name__ == "__main__":
    main()
