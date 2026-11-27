#!/usr/bin/env python3
"""Read-only inventory for C2 historical ZIP archives. No implicit data conversion."""
import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path, PurePosixPath


def inspect_archive(path, expected_sha256=None):
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected_sha256 and digest.lower() != expected_sha256.lower():
        raise ValueError('ZIP SHA-256 mismatch; aborting before inspection')
    files = []
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError('ZIP CRC failure: ' + bad)
        for item in archive.infolist():
            name = item.filename
            parts = PurePosixPath(name).parts
            if name.startswith('/') or '..' in parts or '\\' in name:
                raise ValueError('Unsafe ZIP entry path: ' + name)
            if item.is_dir():
                continue
            info = {'path': name, 'bytes': item.file_size, 'crc32': f'{item.CRC:08x}'}
            if name.lower().endswith('.csv'):
                with archive.open(item) as handle:
                    text = io.TextIOWrapper(handle, encoding='utf-8-sig', newline='')
                    try:
                        reader = csv.reader(text)
                        info['columns'] = next(reader, [])
                        info['data_rows'] = sum(1 for _ in reader)
                    except UnicodeError as exc:
                        info['csv_parse_error'] = str(exc)
            files.append(info)
    return {'archive': path.name, 'sha256': digest, 'crc_passed': True,
            'files': files, 'csv_count': sum(x['path'].lower().endswith('.csv') for x in files),
            'note': 'Read-only metadata inventory; not independent data provenance validation.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--sha256', help='Expected known ZIP SHA-256')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = inspect_archive(args.archive, args.sha256)
    payload = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding='utf-8')
    print(payload, end='')


if __name__ == '__main__':
    main()
