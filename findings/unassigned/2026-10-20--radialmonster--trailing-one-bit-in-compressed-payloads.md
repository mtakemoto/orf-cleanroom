# Trailing 1 bits in a preselected compressed-payload cohort

Author: @radialmonster
Verified by: @mtakemoto
Lead: #87
Variant: unassigned
Builds on: #11
Partial: elevated frequency of a final 1 bit in 16 preselected CC0 files; the 87-file histogram and token-padding question remain open

## Claim

In a preselected sample of 16 CC0 files, one per camera model, 15 compressed payloads ended in a 1 bit. Under an independent fair-last-bit null, the one-sided exact binomial probability of 15 or more successes in 16 files is 17/65,536 (about 0.0002594). This verifies the lead's narrow observation in a subset. It does not establish that the bits are padding or reproduce the lead's full-cohort histogram.

## Original evidence

Lead #87, opened by @radialmonster on 2026-10-19, reports 82 of 87 CC0 variable-size payloads ending in at least one 1 bit. Its inline reproduction uses `tools/orf_tokens.py` to locate each payload and counts trailing low-order 1 bits in the last byte. A contemporaneous 87-file cohort matching the lead's stated filter is enumerated by the [original repository's manifest at `ad566d4`](https://github.com/radialmonster/orf-cleanroom/blob/ad566d4c5820716efb47a02d20fe9e4444b272e8/samples/manifest.csv), committed before the lead was posted: it has exactly 87 distinct SHA-256 values among rows with `source=pixls`, `licence=CC0`, and `size_class=variable`. The lead says it used every then-listed CC0 variable-size file, so no newly listed CC0 file was available for this verification. The lead itself does not pin a tools commit; repository history shows `tools/orf_tokens.py` last changed at [`e07ad95`](https://github.com/radialmonster/orf-cleanroom/commit/e07ad95e65b926c92ede1e26018046da3d18f338) before the lead was posted. This does not establish the finder's exact checkout state. Its separately reported eight-byte histogram sums to 106, whereas the last-byte histogram sums to 87; that discrepancy remains unresolved. The lead builds on #11.

## Verification

On 2026-10-20 UTC, @mtakemoto made a new run on a cohort fixed before downloading or seeing target results. From unique SHA-256 rows with `source=pixls`, `licence=CC0`, and `size_class=variable`, Python's `random.Random('AVA-20 lead87 sampling v1')` selected 16 distinct model names and then one SHA-sorted row per model. The run used repository base `96e35326aefafd830240054fc339df86b041e49f`, `tools/orf_tokens.py` at `e07ad95`, and `tools/orf_signature.py` at `8318921`. Every downloaded file matched its manifest and raw.pixls.us catalog SHA-256 and passed `tools/pixls_samples.py check` as CC0. Every measured file had an ORF-RO signature, compression tag 1, and a variable-size payload. Matching rows measured by @mtakemoto were appended to `samples/manifest.csv` without changing prior rows.

The final 1-bit run was counted three ways: within the last byte, within the last eight bytes, and backward through the whole payload. All three counts agreed for every file. A count of 8 means exactly eight trailing 1 bits here, since the whole-payload scan also returned 8. The prespecified primary threshold was at least 14 of 16 files ending in a 1 bit; 15 met it. The run-length histogram was 0:1, 1:3, 3:1, 4:3, 5:1, 6:6, 8:1. The fair-bit calculation assumes independent file outcomes; one file per model limits duplicate-model dependence but cannot establish independence of shared encoders. This model-weighted sample does not estimate the file-weighted 87-file rate.

| raw.pixls.us id | Model | SHA-256 | Trailing 1 bits |
| --- | --- | --- | ---: |
| 1051 | E-M1 | `19ba17e778ae802d4039f0e88bb1cd68825780788b8058c479067e32b9a63eda` | 1 |
| 1135 | TG-4 | `a056d3fad56762d8a125806a0a4857341f115bc6303085b7297758be8d93b20a` | 5 |
| 1331 | E-M10 | `d7f6ac99ee1f824e81ec0e71599f0f87f9b2e2675f7ddfdb21202281b8bdc5e0` | 6 |
| 1430 | E-PL6 | `38d3750abbcf847bba58e254b2ab8c57d8c9f3fc48490c29ae2b55c4e84d5f64` | 6 |
| 1431 | E-PL7 | `e0e138e9d33b0d2a16c0a9378582ddaac71d0b2cf07bc9ed459df275aa025c60` | 0 |
| 1723 | TG-5 | `1fd6d09b8c93a9bb629e1871859c18a6763397301396844c34217330de094453` | 6 |
| 1803 | E-3 | `ba4605bbd9fe9b77971da444bcdb1698904c0ad4ebdf9dd42dd45ab255f3f6d4` | 4 |
| 2978 | PEN-F | `156bf12075c4f69a3e475518f67db9d4010972d8123bdd27ae8c9177b443c374` | 8 |
| 3041 | E-M1X | `ab171cedfe3a65438dd47c2df704a7d3001f45f5ab43e67b7f96cfe30b6ebbcf` | 1 |
| 4927 | E-M10MarkIIIS | `8bc0009eaacdbeacc72606581665702a1242bc6d4b405d1f0b3f149fe6c85e55` | 6 |
| 5782 | E-450 | `ce44576886d214d194896c32bdd05881f25a23053455decc3da18c46fee96fad` | 6 |
| 5980 | E-P7 | `391b7a28d088f093a93d05c43b82bc8e9403579dea8cdc066d28af53a773d9c5` | 4 |
| 6946 | TG-7 | `4f7344c67bfcfcfec45f754195ba612fc2ad6312f5fab87812bf04b9e9e7d46a` | 3 |
| 7266 | OM-1MarkII | `1c994e4bf5aa4e48d6ec97a1f83558184a866f71bca2b5b1bf914a159927e199` | 4 |
| 7804 | OM-3 | `bcc05bd57e78cbbb308a596f97987975f7167b17768d8c2d536c87e0c34298e0` | 6 |
| 8553 | OM-5MarkII | `6c34d583e2c98840828fa500e54e47f270f138dfc697a9a7cd084575305d3c9f` | 1 |

## Reproduce

Extract the original cohort's raw.pixls.us IDs and SHA-256 values from the immutable pre-lead manifest:

```sh
git show ad566d4:samples/manifest.csv |
python -c 'import csv, sys
by_sha = {r["sha256"]: r["pixls_id"] for r in csv.DictReader(sys.stdin)
          if (r["source"], r["licence"], r["size_class"]) == ("pixls", "CC0", "variable")}
assert len(by_sha) == 87
for sha, pixls_id in sorted(by_sha.items(), key=lambda item: int(item[1])):
    print(pixls_id, sha)'
```

Run from repository base `96e35326aefafd830240054fc339df86b041e49f`. Download the listed CC0 files outside the repository, using the exact id/SHA matches above:

```sh
PYTHONPATH=tools python - <<'PY'
import csv, hashlib, urllib.parse
from pathlib import Path
import pixls_samples as ps

ids = {1051, 1135, 1331, 1430, 1431, 1723, 1803, 2978,
       3041, 4927, 5782, 5980, 6946, 7266, 7804, 8553}
with open('samples/manifest.csv', newline='', encoding='utf-8') as f:
    manifest = {int(r['pixls_id']): r for r in csv.DictReader(f)
                if r['source'] == 'pixls' and r['pixls_id'].isdigit()
                and int(r['pixls_id']) in ids}
catalog = {int(r['id']): r for r in ps.rows() if int(r['id']) in ids}
assert set(manifest) == set(catalog) == ids
dest = Path('/path/to/orf-samples-ava20')
dest.mkdir(parents=True, exist_ok=True)
for i in sorted(ids):
    m, c = manifest[i], catalog[i]
    assert m['sha256'] == c['sha256'] and m['licence'] == c['licence'] == 'CC0'
    assert m['size_class'] == 'variable'
    path = dest / c['local_name']
    if path.exists() and ps.sha256_file(path) == c['sha256']:
        continue
    data = ps.fetch(urllib.parse.quote(c['url'], safe=':/'))
    assert hashlib.sha256(data).hexdigest() == c['sha256']
    path.write_bytes(data)
PY
```

Check every file before measuring:

```sh
python tools/pixls_samples.py check /path/to/orf-samples-ava20/*
python tools/orf_signature.py /path/to/orf-samples-ava20/*
```

This short script reproduces the deterministic ID selection from the base manifest (before this finding's append-only rows):

```sh
python - <<'PY'
import csv, random
rows = list(csv.DictReader(open('samples/manifest.csv', newline='', encoding='utf-8')))
by_sha = {r['sha256']: r for r in rows if r['source'] == 'pixls' and r['licence'] == 'CC0' and r['size_class'] == 'variable'}
models = sorted({r['model'] for r in by_sha.values()})
rng = random.Random('AVA-20 lead87 sampling v1')
chosen = []
for model in rng.sample(models, 16):
    choices = sorted((r for r in by_sha.values() if r['model'] == model), key=lambda r: r['sha256'])
    chosen.append(rng.choice(choices))
print(sorted(r['pixls_id'] for r in chosen))
PY
```

From the base checkout, after checking the files and reproducing the selection, append the verified rows:

```sh
python tools/manifest_rows.py --by @mtakemoto --append samples/manifest.csv /path/to/orf-samples-ava20/*
```

Count trailing low-order 1 bits; `locate()` selects the image IFD with the largest total strip byte count. The signature and manifest SHA checks pin the input files:

```sh
PYTHONPATH=tools python - <<'PY'
import csv, glob, math
from collections import Counter
from orf_signature import signature
from orf_tokens import locate

expected = {r['sha256']: r for r in csv.DictReader(open('samples/manifest.csv', newline='', encoding='utf-8')) if r['source'] == 'pixls' and r['licence'] == 'CC0' and r['size_class'] == 'variable'}
selected_ids = {1051, 1135, 1331, 1430, 1431, 1723, 1803, 2978,
                3041, 4927, 5782, 5980, 6946, 7266, 7804, 8553}
def trailing(data):
    n = 0
    for b in reversed(data):
        k = 0
        while k < 8 and (b >> k) & 1:
            k += 1
        n += k
        if k < 8:
            break
    return n

hist = Counter()
seen = set()
paths = sorted(glob.glob('/path/to/orf-samples-ava20/*'))
assert len(paths) == 16
for path in paths:
    s = signature(path)
    assert s['sha256'] in expected and s['size_class'] == 'variable' and s['compression_tag'] == 1
    seen.add(int(expected[s['sha256']]['pixls_id']))
    w, h, buf = locate(path)
    assert (w, h, len(buf)) == (s['payload_w'], s['payload_h'], s['payload_bytes'])
    one, eight, full = trailing(buf[-1:]), trailing(buf[-8:]), trailing(buf)
    assert one == eight == full
    hist[one] += 1
    print(expected[s['sha256']]['pixls_id'], s['sha256'], one, eight, full)
assert seen == selected_ids
positive = sum(count for length, count in hist.items() if length > 0)
print('histogram', sorted(hist.items()), 'positive', positive, 'total', len(paths))
print('fair-bit one-sided p', sum(math.comb(len(paths), k) for k in range(positive, len(paths)+1)) / (2 ** len(paths)))
PY
```

Expected aggregate output from the verified run:

```text
histogram [(0, 1), (1, 3), (3, 1), (4, 3), (5, 1), (6, 6), (8, 1)] positive 15 total 16
fair-bit one-sided p 0.0002593994140625
```
