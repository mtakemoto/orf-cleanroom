# Independent reproduction: compression tag is 1 across the CC0 ORF set

Author: @radialmonster
Verified by: @mtakemoto
Lead: #10
Variant: container
Builds on: #28
Reproduces: 2026-10-19--radialmonster--compression-tag-is-1-on-every-orf

## Claim

The container measurements in the reproduced finding match a new run on the same complete CC0 Olympus / OM System ORF and ORI set: 104 distinct files, spanning 63 model spellings in their own tags. The raw IFD's Compression tag is 1 in every file, including both variable-size payloads and fixed packings, so this tag does not distinguish those classes in this set.

| Size class | Files | BitsPerSample | Compression tag |
| --- | ---: | ---: | ---: |
| packed-12 | 9 | 12 | 1 |
| packed-12.8 | 5 | 16 | 1 |
| packed-16 | 3 | 16 | 1 |
| variable | 87 | 16 | 1 |

The variable-size files range from 6.021 to 8.794 bits per pixel, as rounded by the measuring tool. File 7269 is the only one above 8.5. There are 21 payloads wider than 6000 pixels: 19 variable-size and 2 fixed-size. The magic values are ORF-RO on 98 files and ORF-RS on 6. These reproduce the original counts and bounds; they establish no compressed bitstream grammar or decoded sensor values.

## Original evidence

Lead #10 was opened by @radialmonster on 2026-10-18 from `tools/orf_signature.py` on 17 CC0 files, without recording their IDs. The self-verified finding `2026-10-19--radialmonster--compression-tag-is-1-on-every-orf` records the later whole-set run, with every raw.pixls.us ID and SHA-256. Its measuring tool was `tools/orf_signature.py`, last changed in `62c368a`.

## Verification

Independent reproduction by @mtakemoto on 2026-10-19 UTC, after both the lead and the self-verified finding were posted. The signature run began at 01:32:14 UTC and finished at 01:32:15 UTC, using Python 3.14.7 on repository commit `cb4a062`; `tools/orf_signature.py` was still at `62c368a02bc15df595aa482488f69e0ac5a548c5`.

All files were obtained with `tools/pixls_samples.py download`, which verified their SHA-256 hashes, and checked again immediately before measurement with `tools/pixls_samples.py check`: every file was CC0. The current CC0 listing has exactly the IDs and hashes in the original whole-set finding. That finding already used every CC0 file in this set, so no previously unused CC0 file was available; this is a new execution by a different contributor on the same complete cohort.

The inline comparison below matched every original per-file table entry in eight fields: model, payload width, payload height, rounded bits per pixel, size class, BitsPerSample, Compression, and SHA-256. There were no mismatches. The aggregate counts and bounds above also match. Public sample names, IDs, hashes, and measured signatures are appended to `samples/manifest.csv` in rows beginning `@mtakemoto tools/orf_signature.py 62c368a`; existing rows and findings are unchanged. Variable-size files remain `unassigned`, and exact fixed packings are V0 under the existing variant rule.

Both runs use the same original container tool. This checks computational reproducibility and the stated file cohort; it is not an independent implementation of TIFF parsing. No image data was decoded or compared with any other decoder.

## Reproduce

Run from the repository root. Keep samples outside the repository, in a directory containing only files obtained and checked as below. The CSV contains container measurements and hashes, not pixel data. The original finding pins the dated cohort; a changed or incomplete cohort causes the comparison to stop rather than silently change the verification scope.

```bash
set -e
python tools/pixls_samples.py download ../orf-samples
python tools/pixls_samples.py check ../orf-samples/*
python tools/orf_signature.py ../orf-samples/* > sig.csv
python - sig.csv findings/container/2026-10-19--radialmonster--compression-tag-is-1-on-every-orf.md <<'PY'
"""One-off counts and per-file comparison over original tool CSV output."""
import collections
import csv
import json
from pathlib import Path
import re
import sys

rows = list(csv.DictReader(Path(sys.argv[1]).open(newline='')))
reference = Path(sys.argv[2]).read_text()
pattern = re.compile(
    r'^- (\d+) (.*?) (\d+)x(\d+), ([0-9.]+) bpp, '
    r'(variable|packed-[0-9.]+), bits/sample (\d+), tag (\d+), `([0-9a-f]{64})`$',
    re.M,
)
fields = ('model', 'payload_w', 'payload_h', 'bpp', 'size_class',
          'bits_per_sample', 'compression_tag', 'sha256')
expected = {m[0]: dict(zip(fields, m[1:])) for m in pattern.findall(reference)}
actual = {r['file'].split('_', 1)[0]: r for r in rows}
assert expected, 'Reference table was not recognized'
assert len(actual) == len(rows), 'Duplicate sample IDs in CSV'
assert set(actual) == set(expected), 'CSV coverage differs from original finding'
mismatches = [
    {'id': sample_id, 'field': field, 'expected': expected[sample_id][field],
     'actual': actual[sample_id][field]}
    for sample_id in sorted(expected, key=int)
    for field in fields
    if actual[sample_id][field] != expected[sample_id][field]
]
groups = collections.Counter((r['compression_tag'], r['bits_per_sample'],
                              r['size_class']) for r in rows)
variable = [r for r in rows if r['size_class'] == 'variable']
wide = [r for r in rows if int(r['payload_w']) > 6000]
values = [float(r['bpp']) for r in variable]
summary = {
    'files': len(rows), 'unique_sha256': len({r['sha256'] for r in rows}),
    'model_spellings': len({r['model'] for r in rows}),
    'reference_files': len(expected), 'compared_fields_per_file': len(fields),
    'per_file_mismatches': mismatches,
    'compression_tag_counts': dict(collections.Counter(r['compression_tag'] for r in rows)),
    'groups': [dict(compression_tag=tag, bits_per_sample=bits, size_class=kind,
                    files=n) for (tag, bits, kind), n in sorted(groups.items())],
    'variable': {'files': len(variable), 'bpp_min': min(values), 'bpp_max': max(values),
                 'above_8_5_ids': [r['file'].split('_', 1)[0] for r in variable
                                   if float(r['bpp']) > 8.5]},
    'width_above_6000': {'files': len(wide),
                         'variable': sum(r['size_class'] == 'variable' for r in wide),
                         'fixed': sum(r['size_class'] != 'variable' for r in wide)},
    'magic_counts': dict(collections.Counter(r['magic'] for r in rows)),
}
print(json.dumps(summary, indent=2, sort_keys=True))
raise SystemExit(1 if mismatches else 0)
PY
```
