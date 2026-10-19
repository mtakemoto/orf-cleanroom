# Independent V0 hash agreement on all 17 fixed-size CC0 files

Author: @radialmonster
Verified by: @mtakemoto
Lead: #75
Variant: V0
Builds on: #77, #78, #79
Partial: All 17 corrected output hashes and exact payload ends; excludes the lead's 793 "out of 12-bit range" wording and any proof of physical pixel order or general selector rules.

## Claim

A second, independently written V0 payload implementation agrees with all 17 output SHA-256 hashes in the corrected post-#80 conformance table. All 17 payloads end exactly. The explicit header, strip-gap-position and TIFF-endian candidate selectors produce hash agreement on this cohort. The result does not establish those selectors on other files or prove first/second physical pixel order.

## Original evidence

@radialmonster published lead #75 using original reference decoder/conformance tooling at `ce123cc`. Six two-field packed-12 hashes were superseded by #80 (`b3082b3`). This verification targets `samples/conformance-V0.csv` at `bf56d394c97d8c51dd1c7be6aa491c681004dc23`, SHA-256 `abdcad7514572edc23d150c6c75efef5c2d998a48219c0810121adf6321665c6`, containing those corrected hashes. The lead identifies the public sample names and input hashes.

## Verification

New whole-frame run by @mtakemoto on 2026-10-19, after the lead was posted. The lead already used every fixed-size CC0 file in the available collection; a fresh `pixls_samples.py list --missing samples/manifest.csv` returned no missing files. No additional fixed-size CC0 input was available in that listing. This is a separate independent implementation and measurement of the complete existing 17-file cohort, rather than an additional camera/file or a wider region. All 17 licences were freshly checked CC0 and all input identities match existing @mtakemoto manifest rows by SHA-256.

The method and selector choices were [posted before implementation and target outcomes](https://github.com/radialmonster/orf-cleanroom/issues/75#issuecomment-6273059887). Original payload code and synthetic tests were written from `specs/V0.md` at `bf56d39`, without reading the reference decoder, its conformance tool/tests, existing payload probes, target bytes or reference output hashes. Shared original `orf_signature.Tiff` code supplies only header/endian and integer primitives; original descriptor validation and payload code are separate. This verifies payload agreement, not independent TIFF-parser agreement.

Independent Astra review and focused repair review passed; 25 original synthetic tests passed on actual Python 3.8.20 and 3.12.14 before targets. Source was frozen at `12d43336a264a4e7948bc27cbb5046e5f786e3c3`. Tool SHA-256 is `1e9116a5c9a2ecfd076ec836552f9fdae006ca39cca3b52d18ccbaf8ad4de92a`; tests SHA-256 is `596b20e4ca7344d4ea9466c87f3c40caf6f9bb5ed4a8406f3b0d31f7447b9868`; shared-container SHA-256 is `b1b6f091bfb986ab7aca3ad1f513202acfaaccc424272523589142444d025afb`. The tool is published in PR #93, whose public integration commit `56ae05485155495c1da074c29755ba5a6d070637` has byte-identical tool/tests and the same shared-container dependency.

All predictions were saved and sealed at 17:38:16 UTC before the reference CSV was first opened at 17:38:31 UTC. Prediction JSONL SHA-256: `011930060fb404c9f1973304b5698e2a842de502ddde59503bc5e4972c3948f4`. All 17 output hashes match by input SHA-256 and all 17 independently report exact end. No oracle-dependent decoder changes followed the comparison.

The stored packed-16 words remain unchanged, including low nibbles. The lead's 793 count agrees with E-400's nonzero-low-nibble count. It is not the count of stored words greater than 4095: independently that count is 9,587,334 on E-400, 3,944,270 on E-1 and 2,807,536 on E-10. E-1 and E-10 have zero nonzero low nibbles. That terminology is excluded from this partial verification. Smoothness scores and general physical-format correctness are also outside scope.

The table lists raw.pixls.us IDs, input hashes and matching independent output hashes. Public names are in the manifest and lead #75. These are aggregate hashes only.

| raw.pixls.us ID | Input SHA-256 | Independent output SHA-256 |
|---|---|---|
| 1432 | `675fefe7c9e99281783b987889d723b5f46692f5c20e19fed5e422c7c6d2636b` | `a8cedb760320786303436515140aba5406a36598e9df841ac706c7b8ecf38a4d` |
| 1799 | `3fc12bc3f6320cfab456111d7805b446e329fdd1907680be55e2e163e5e084bd` | `1e6a220bfa5fbdced0bc9acf6c62cecc3cf287ad3df527e3fe980f154534ab37` |
| 1800 | `042286653fbae5b085bef4a4e626145385ea6e82e817f166b4904abcef64457c` | `63c910928a97106d8102f571d4a52ee6f044088e4a6e8ab9bbbbf78bdf31018d` |
| 2151 | `1354e0ac98ea90820227650031d8215637a2aaabd15de995c5a1e00b1986261b` | `90bc69a504e06a54fc5635581e16320417b9fdd9ace3cd2e283f2247834e9d0c` |
| 2420 | `f0737d78bb2e588963a3d5038fab493cdff1c9c48475704de96d797bbb81e62a` | `cfca8bfd4489355e98a9acd3ca40ba83e89b60267d5ef6197e9f14e758cd9f3d` |
| 2431 | `a25383acad9b5bb0bb404715e0957f2eb80aa1aaad6c448a71025c03cfa631be` | `96e57e497f18092664831bb4d9d11d1bdbc1d97f841d4c1e5be91fff464fe697` |
| 2856 | `5c42fa75d6b549514b722e2c50726c03e34fac4909ec3640e147ea7fa825fc8d` | `79aa165b0c74e88ff6c3e3e027e86aad30a6957d9b7d3d8990668aafbb393ef4` |
| 2878 | `6d818dbff78b3e2efa4835f568d04733052b9211e6bc65b0a3748a841170e95b` | `09736a0cc45c4834a89b3b606e58d80caa3772549e2dabe3bb1a8a6304b04315` |
| 2977 | `f87a5f3295aeb4d6ab27bb5b41c5e0f3a211ec9b4e3b1d9f105a650bee1a2f13` | `32c3bc92092bc11e7d854d08dc9c151bd5525262072a3dc32f88b4b941ad80c6` |
| 3438 | `5088771f83ce08a001b44672e1dd9f013e603933c37ce1bfb7030a02abbe801c` | `8efdaba481cd470cde37b2db535a9d4439faa14db13f2e332363395d62b4efff` |
| 3540 | `fa5a4759b2de2b573f59629ad1baf64ad04a85fb8fe1fb3cbf68e08a42fff4f0` | `bd231fd8c50e85f774fe142e9633c64f6844ae4b8758889f2befedf2ffc944f6` |
| 3624 | `ba11eb970ab32e1e9cf3d0176041e4bd11c501d445720c0a344217e785ad65a6` | `36f8e058e2b1c6da64746254b7e9af8d5574d33867035382546a4764b54a548b` |
| 5424 | `2bfdade72439017a60a47aad1e5bbcb1aca36f2be7a21e94a4257a678fb6f4da` | `b05f48502e9ff5107ac93f72478d7d52092e5f389d1025ad25576c664761ca47` |
| 5491 | `baab92391834076b427e406e98da79aaba48fb87243d6ccae60e08e299cfccf7` | `3ade5df7552bafd57992e27d06d98484de2e7866eb4de30e2286fcbc28dde77c` |
| 780 | `9d55506f9d6ee31d2d4c4b6df0dcd1d016d358b3e5eb4ed31edd7227dfefd5f8` | `3b0807cf04a79b9740e912702eb043dd738e442f39098f9e3584f712e05c51f5` |
| 792 | `6e6b9b7dd9ded7c4b364b83116c817ca2d6daac15f2e9ef7796159b08c3288a1` | `21fe65f6975d951b83aba92818339d915c9b76d927810d35b7f7f05fc5b89752` |
| 8609 | `05f49918e1b1894c3abd2b5451b356f7a00adb1c8568abc5babff33fcade1bb2` | `75f2379b923a8df7a2ee8c60f75270aa820c5fb074cb91e7df3b328619fa2d45` |

## Reproduce

Fetch the public integration commit containing the checker and current dependencies:

```sh
git fetch origin refs/pull/93/merge
git checkout --detach 56ae05485155495c1da074c29755ba5a6d070637
python -I tools/v0_spec_check.py --self-test
python tools/pixls_samples.py download /tmp/orf-v0-cc0
```

The download command retrieves the CC0 collection; only the 17 IDs below are measured. With that directory already populated, run this one-off count over the new tool's output (the reference CSV is first opened after all outputs are saved):

```python
import csv, hashlib, json, pathlib, subprocess, sys
root = pathlib.Path('/tmp/orf-v0-cc0')
ids = '1432 1799 1800 2151 2420 2431 2856 2878 2977 3438 3540 3624 5424 5491 780 792 8609'.split()
manifest = list(csv.DictReader(open('samples/manifest.csv', newline='')))
cmd = [sys.executable, '-I', 'tools/v0_spec_check.py', '--measured-by', 'mtakemoto']
for sid in ids:
    candidates = [p for p in root.iterdir() if p.is_file() and p.name.startswith(sid + '_')]
    assert len(candidates) == 1, sid
    path = candidates[0]
    subprocess.run([sys.executable, 'tools/pixls_samples.py', 'check', str(path)], check=True)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    row = next(r for r in manifest if r['pixls_id'] == sid and r['sha256'] == sha)
    cmd += ['--sample', sid, row['pixls_name'], str(path)]
run = subprocess.run(cmd, stdout=subprocess.PIPE, check=True)
pathlib.Path('/tmp/v0-independent.jsonl').write_bytes(run.stdout)
actual = [json.loads(line) for line in run.stdout.splitlines()]
reference_bytes = pathlib.Path('samples/conformance-V0.csv').read_bytes()
assert hashlib.sha256(reference_bytes).hexdigest() == 'abdcad7514572edc23d150c6c75efef5c2d998a48219c0810121adf6321665c6'
expected = {r['input_sha256']: r for r in csv.DictReader(reference_bytes.decode().splitlines())}
assert len(actual) == len(expected) == 17
assert {r['input_sha256'] for r in actual} == set(expected)
print('hash matches', sum(r['output_sha256'] == expected[r['input_sha256']]['output_sha256'] for r in actual))
print('exact ends', sum(r['exact_end'] for r in actual))
for r in actual:
    if r['packing'] == 'packed-16':
        print(r['sample_id'], 'above4095', r['above4095_count'], 'nonzero_low_nibble', r['nonzero_low_nibble_count'])
```

The tool's declared selectors and limits must stay fixed. It preserves stored packed-16 words, emits canonical uint16LE values in image row order, and saves no decoded raster. Header/gap/endian generalizations and unit-order conventions remain unverified outside this measured cohort. File measurement requires nonblocking descriptor-open support; platforms without it report an explicit unsupported category.
