"""Acquire original BPA 2020-2025 FERC-714 XLSX and inventory raw workbook evidence.

Only fetches original operator files and audits workbook sheet headers.
No EIA-930 comparison, modelling or BA geography approval is implied.
Uses Python stdlib ZIP/XML only; does not alter the original XLSX bytes.
"""
import argparse
import csv
import hashlib
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

BASE = "https://transmission.bpa.gov/business/operations/ferc714/"
YEARS = tuple(range(2020, 2026))
S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
P = "{http://schemas.openxmlformats.org/package/2006/relationships}"
KEYWORDS = ("pt iii", "schedule", "balancing", "load", "demand", "interchange")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def extract_inventory(raw):
    """Inspect the immutable workbook ZIP: workbook sheet names plus early cells."""
    from io import BytesIO
    with zipfile.ZipFile(BytesIO(raw)) as z:
        names = set(z.namelist())
        required = {"xl/workbook.xml", "xl/_rels/workbook.xml.rels"}
        if not required <= names:
            raise ValueError("Invalid XLSX: workbook index or relationships missing")
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        destinations = {}
        for e in rels:
            target = e.attrib.get("Target", "")
            if target.startswith("/"):
                location = target.lstrip("/")
            elif target.startswith("xl/"):
                location = target
            else:
                location = "xl/" + target
            destinations[e.attrib.get("Id")] = location
        strings = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            strings = ["".join(t.text or "" for t in si.iter(S + "t"))
                       for si in root.findall(S + "si")]
        output = []
        for sheet in wb.findall(".//" + S + "sheet"):
            label = sheet.attrib.get("name", "")
            rid = sheet.attrib.get(R + "id")
            member = destinations.get(rid, "")
            if member not in names:
                raise ValueError("Missing XLSX worksheet part: " + member)
            data = ET.fromstring(z.read(member))
            sampled = []
            for row in data.findall(".//" + S + "sheetData/" + S + "row")[:35]:
                cells = []
                for cell in row.findall(S + "c")[:22]:
                    v = cell.find(S + "v")
                    inline = cell.find(S + "is")
                    value = v.text if v is not None and v.text else ""
                    if cell.attrib.get("t") == "s" and value:
                        idx = int(value)
                        if idx < 0 or idx >= len(strings):
                            raise ValueError("Invalid shared string index")
                        value = strings[idx]
                    elif inline is not None:
                        value = "".join(t.text or "" for t in inline.iter(S + "t"))
                    if value.strip():
                        cells.append((cell.attrib.get("r", ""), value[:250]))
                if cells:
                    sampled.append({"row": row.attrib.get("r", ""),
                                    "cells": [{"cell": k, "value": v} for k, v in cells]})
            output.append({"sheet_name": label, "original_sheet_part": member,
                           "sample_first_35_rows": sampled,
                           "name_relevant": any(k in label.lower() for k in KEYWORDS)})
        if not output:
            raise ValueError("No XLSX worksheets")
        return output


def acquire(out, years=YEARS, opener=None):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for year in years:
        if year not in YEARS:
            raise ValueError("Year outside BPA audit period")
        url = BASE + "FERC714_" + str(year) + "_Masterx.xlsx"
        target = out / ("BPA_FERC714_" + str(year) + "_ORIGINAL.xlsx")
        item = {"year": year, "official_url": url, "raw_file": target.name,
                "status": "not_retrieved", "source_is_operator_original": True,
                "data_metric_definition_authenticated": False,
                "EIA930_comparison_permitted": False}
        try:
            if target.exists():
                # Never replace a frozen original on a runner re-run.
                raw = target.read_bytes()
                source_status = "existing_original_reverified"
            elif opener is None:
                request = urllib.request.Request(url, headers={
                    "User-Agent": "C2-BPA-FERC714-Original-Source-Audit/1.0"})
                with urllib.request.urlopen(request, timeout=100) as response:
                    raw = response.read(50000001)
                source_status = "original_downloaded_workbook_inventory_pass"
            else:
                raw = opener(url)
                source_status = "original_downloaded_workbook_inventory_pass"
            if len(raw) > 50000000 or len(raw) < 1000 or not zipfile.is_zipfile(__import__("io").BytesIO(raw)):
                raise ValueError("Original source is not a bounded valid XLSX ZIP")
            inventory = extract_inventory(raw)
            if not target.exists():
                target.write_bytes(raw)
            item.update({"status": source_status,
                         "sha256": sha(raw), "original_file_bytes": len(raw),
                         "worksheet_count": len(inventory)})
            (out / ("BPA_FERC714_" + str(year) + "_SHEET_INVENTORY.json")).write_text(
                json.dumps({"original_sha256": sha(raw), "worksheets": inventory},
                           indent=2) + "\n", encoding="utf-8")
        except Exception as exc:
            item["status"] = ("existing_original_invalid" if target.exists()
                              else "source_not_verified")
            item["error"] = type(exc).__name__ + ": " + str(exc)[:450]
        manifest.append(item)
    (out / "BPA_FERC714_2020_2025_ORIGINAL_SOURCE_MANIFEST.json").write_text(
        json.dumps({"source_type": "BPA original FERC-714 operator-submitted XLSX",
                    "reports": manifest, "all_original_sources_obtained": all(
                        x["status"] in ("original_downloaded_workbook_inventory_pass", "existing_original_reverified")
                        for x in manifest),
                    "historical_BA_geography_approved": False,
                    "model_training_permitted": False,
                    "actual_EIA930_source_comparison_completed": False},
                   indent=2) + "\n", encoding="utf-8")
    with (out / "BPA_FERC714_2020_2025_DOWNLOAD_STATUS.csv").open(
            "w", newline="", encoding="utf-8") as f:
        fields = ("year", "official_url", "status", "sha256", "original_file_bytes",
                  "worksheet_count", "error")
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows({key: item.get(key, "") for key in fields} for item in manifest)
    return manifest


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    result = acquire(args.out)
    print(json.dumps({"originals_verified": sum(x["status"] in ("original_downloaded_workbook_inventory_pass", "existing_original_reverified")
                                                 for x in result), "of": len(result),
                      "model_training_permitted": False}))
    if not all(x["status"] in ("original_downloaded_workbook_inventory_pass", "existing_original_reverified") for x in result):
        raise SystemExit("Original BPA XLSX retrieval/inventory INCOMPLETE; no model admission")


if __name__ == "__main__":
    main()
