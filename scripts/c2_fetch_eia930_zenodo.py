#!/usr/bin/env python3
"""Audited PUDL/Zenodo archive fallback for authentic raw EIA-930 BALANCE.

Pinned Zenodo record and published archive MD5; data are original EIA files
re-archived by Catalyst Cooperative, not a live EIA API pull.
"""
import argparse
import hashlib
import json
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from scripts.c2_fetch_eia930_bulk import csv_to_month

RECORD_URL = "https://zenodo.org/records/22215263/files/eia930-2025half2.zip?download=1"
PUBLISHED_MD5 = "48cf49085d90c80c60d9fd38a65caa49"
BALANCE_MEMBER = "eia930-2025half2-balance.csv"
MAX_ARCHIVE_BYTES = 40 * 1024 * 1024
MAX_BALANCE_BYTES = 100 * 1024 * 1024

def acquire_archive(zip_path, url=RECORD_URL, opener=None):
    opener = opener or urllib.request.urlopen
    zip_path = Path(zip_path)
    digest = hashlib.md5()
    total = 0
    req = urllib.request.Request(url, headers={"User-Agent":"C2-Research-Archive/0.1"})
    try:
        with opener(req, timeout=90) as response, zip_path.open("xb") as out:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk: break
                total += len(chunk)
                if total > MAX_ARCHIVE_BYTES: raise ValueError("archive exceeds compressed size limit")
                digest.update(chunk)
                out.write(chunk)
        if digest.hexdigest() != PUBLISHED_MD5:
            raise ValueError("Zenodo archive MD5 differs from published record")
    except Exception:
        zip_path.unlink(missing_ok=True)
        raise
    return {"zenodo_archive_md5":digest.hexdigest(),"bytes":total,"url":url}

def extract_balance(archive_path, balance_path):
    with zipfile.ZipFile(archive_path) as zf:
        names=zf.namelist()
        if len(names)!=len(set(names)) or BALANCE_MEMBER not in names:
            raise ValueError("unexpected or duplicate archive members")
        item=zf.getinfo(BALANCE_MEMBER)
        if item.file_size>MAX_BALANCE_BYTES:
            raise ValueError("uncompressed balance CSV exceeds permitted size")
        if zf.testzip() is not None:
            raise ValueError("archive CRC verification failed")
        with zf.open(item) as source, Path(balance_path).open("xb") as dest:
            shutil.copyfileobj(source,dest)

def fetch_zenodo(outdir,year=2025,month=7,ba="SRP",url=RECORD_URL,opener=None):
    if year!=2025 or month<7 or month>12:
        raise ValueError("pinned Zenodo half2 archive supports July-December 2025 only")
    outdir=Path(outdir)
    if outdir.exists():
        raise ValueError("destination already exists")
    outdir.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="c2_zenodo_",dir=outdir.parent) as temp:
        work=Path(temp)
        archive=work/"eia930-2025half2.zip"
        meta=acquire_archive(archive,url,opener)
        balance=work/BALANCE_MEMBER
        extract_balance(archive,balance)
        report=csv_to_month(balance,outdir,ba,year,month,source_url=url)
        # Preserve both the exact archived original CSV and its source ZIP.
        archived_copy=outdir/archive.name
        shutil.copyfile(archive,archived_copy)
        manifest_file=outdir/"source_manifest.json"
        manifest=json.loads(manifest_file.read_text(encoding="utf-8"))
        manifest["origin"]="pudl_zenodo_raw"
        manifest["archive_provenance"]={
            "record":"22215263","published_md5":PUBLISHED_MD5,
            "download_md5":meta["zenodo_archive_md5"],
            "archive_sha256":hashlib.sha256(archived_copy.read_bytes()).hexdigest(),
            "archive_file":archive.name,"member":BALANCE_MEMBER,
            "interpretation":"EIA original CSV archived by PUDL; snapshot, not EIA live API"}
        manifest_file.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("output_dir",type=Path)
    p.add_argument("--ba",default="SRP");p.add_argument("--year",type=int,default=2025)
    p.add_argument("--month",type=int,default=7)
    a=p.parse_args()
    report=fetch_zenodo(a.output_dir,a.year,a.month,a.ba)
    print(json.dumps({"origin":report["origin"],"rows":report["row_count"],
                      "archive":report["archive_provenance"]},indent=2))

if __name__=="__main__":
    main()
