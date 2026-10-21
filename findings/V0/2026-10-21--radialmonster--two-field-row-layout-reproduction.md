# Two-field row layout reproduced on six IIRS packed-12 files

Author: @radialmonster
Verified by: @mtakemoto
Lead: #77
Variant: V0
Builds on: #75, 2026-10-19--radialmonster--packed-12-msb-two-values-per-three-bytes
Partial: Six-file two-field strip geometry and row-continuity evidence, with eleven natural-order controls; excludes the historical decoder/hash defect and general header-versus-gap selector rules.

## Claim

A new run reproduces the six-file evidence for storing the first `ceil(height/2)` rows as even image rows, followed by odd image rows. For each of these six IIRS packed-12 files, the strip-table gap and a stored-row discontinuity occur exactly at that split. Strip byte counts cover the complete fixed-size payload. Interleaving the two parts restores lower distance-two than distance-one row differences over every eligible interior row of the 400 centre columns. Natural interpretation has the reverse ordering. All eleven published V0 controls have no strip gap, no detected discontinuity, and lower stored distance-two than distance-one differences.

This supports the bounded layout observations in #77, not a universal layout selector or proof of physical CFA origin. The natural/field hypotheses use the lead's existing byte-unpacking method, rather than an independent decoder implementation.

## Original evidence

@radialmonster published #77 on 2026-10-18 using `tools/layout_probe.py` and the repository's original `decoder/orf_decode.py` at `683842a`. The lead identified six CC0 IIRS packed-12 files and eleven V0 controls from #75. Its six gap sizes/split rows were 1224/975, 1464/1155, 1464/1155, 1464/1155, 1624/1371, and 1624/1371 (ordered C5060WZ, C7070WZ, SP510UZ, SP550UZ, SP565UZ, SP570UZ). It scored about 200 interior image-row starts over 400 centre columns. See #77 for all original scores and pairing counts; public sample identities for this new run are below.

## Verification

New runs by @mtakemoto on 2026-10-20, after publication of the lead, on base `1887ba3637b98dd7e5b3b56561274cd939b0d4a4` with Python 3.14.7. All 17 files were freshly downloaded using `pixls_samples.py`, checked CC0 using `pixls_samples.py check`, and matched to the manifest by SHA-256. Every input already has an @mtakemoto measurement row, so no duplicate manifest rows were appended.

A fresh raw.pixls.us public listing contained exactly one CC0 file for each of the six target models: the same six files used by the lead. No additional CC0 file for those models was available. To widen the validation rather than merely repeat the prefix/sample, the second run used every eligible interior row start: `range(10,h-10)` for stored lags and `range(20,h-20)` for hypothesis scores. It still uses only the centre 400 columns, not the full raster width. Gap/discontinuity detection already scans the full stored-row series. Pairing and shift-curve sampling were unchanged.

The metric and ranges were fixed before this run: for two rows over the selected columns, `D = sum(abs(a-b)) / (sum(a+b)/2)`, with zero when the denominator is zero. Scores are means of these per-row-pair normalized differences. Discontinuities use the existing threshold, above four times the median of the twelve neighbouring differences and above 0.3; split selection uses the existing first peak within 10% of half-height. No thresholds, inputs, or exclusions were changed after observing results.

First, the unchanged published tool was run on all 17 inputs. The six hypothesis-score triples, gap boundaries, discontinuity summaries and pairing summaries reproduce #77 to its published precision. Then the new tool's default run reproduced all 17 original outputs byte-for-byte after excluding only added row-count lines. The widened `--all-rows` run was frozen at tool commit `fe4ec45712ed656528a254324dd515424b5268de`, before reading its outcomes. The small CLI change is a separate tool contribution, not part of this finding-only change.

### Wider target scores

D2 and D1 mean image rows two and one apart, respectively. F01 maps image row `2k` to stored row `k`, and image row `2k+1` to stored row `split+k`; F10 exchanges these roles.

| ID / model | Height | Gap bytes / split row | Scored hypothesis rows | Natural D2 / D1 | F01 D2 / D1 | F10 D2 / D1 |
|---|---:|---:|---:|---:|---:|---:|
| 1799 / C5060WZ | 1949 | 1224 / 975 | 1909 | 0.1616 / 0.1170 | 0.1162 / 0.4743 | 0.1162 / 0.4806 |
| 780 / C7070WZ | 2309 | 1464 / 1155 | 2269 | 0.2019 / 0.1214 | 0.1211 / 0.5603 | 0.1211 / 0.5706 |
| 2420 / SP510UZ | 2309 | 1464 / 1155 | 2269 | 0.3713 / 0.2595 | 0.2593 / 0.5206 | 0.2593 / 0.5645 |
| 8609 / SP550UZ | 2309 | 1464 / 1155 | 2269 | 0.2083 / 0.1438 | 0.1432 / 0.4772 | 0.1432 / 0.4924 |
| 3438 / SP565UZ | 2741 | 1624 / 1371 | 2701 | 0.1255 / 0.0938 | 0.0932 / 0.5536 | 0.0932 / 0.5587 |
| 5491 / SP570UZ | 2741 | 1624 / 1371 | 2701 | 0.1441 / 0.1119 | 0.1114 / 0.5329 | 0.1114 / 0.5353 |

All six heights are odd; the first part has one more row than the second. F01 is count-consistent and F10 is not, for all six files. Their very similar D2 scores alone do not distinguish first-even from first-odd placement. The gap/split equality, row counts, continuity and the existing near-zero-shift pairing evidence support the bounded F01 interpretation together.

The original full stored-row scan finds just the gap-boundary discontinuity in five targets. C7070WZ has eight detected boundaries, including the gap at 1155; scene-edge boundaries prevent using its gap jump alone as conclusive evidence. The retained pairing samples reproduce the lead's offset-0-or-minus-1 counts: C5060WZ 6, C7070WZ 19, SP510UZ 30, SP550UZ 25, SP565UZ 8 and SP570UZ 21. Repeating texture makes this check weak on C5060WZ and SP565UZ. The shift-curve minimum is at -1 or 0 in each target, at the tool's printed precision.

### Wider natural-row controls

All have zero strip gaps and zero detected discontinuities. Every payload equals height times row bytes, and strip byte counts sum to that payload. D2 below D1 supports the lead's natural-row contrast; the tool does not exhaustively test all possible row permutations for controls.

| ID / model | Packing | Scored stored-row starts | Stored D2 | Stored D1 |
|---|---|---:|---:|---:|
| 792 / SH-2 | packed-12 | 3450 | 0.0814 | 0.3987 |
| 1432 / XZ-2 | packed-12 | 2966 | 0.0389 | 0.3935 |
| 1800 / E-1 | packed-16 | 1946 | 0.0908 | 0.2645 |
| 2151 / E-400 | packed-16 | 2820 | 0.0402 | 0.4263 |
| 2431 / XZ-10 | packed-12 | 2970 | 0.0220 | 0.5012 |
| 2856 / E-M5MarkII | packed-12.8 | 6912 | 0.0498 | 0.1086 |
| 2878 / E-300 | packed-12.8 | 2484 | 0.0736 | 0.3296 |
| 2977 / PEN-F | packed-12.8 | 7776 | 0.0178 | 0.1952 |
| 3540 / E-500 | packed-12.8 | 2484 | 0.0539 | 0.3401 |
| 3624 / E-330 | packed-12.8 | 2430 | 0.0653 | 0.2947 |
| 5424 / E-10 | packed-16 | 1664 | 0.0561 | 0.6834 |

### Identities and source provenance

All samples below are raw.pixls.us CC0, not private or decoder-generated data. No sample files, pixel arrays, or images are included.

| raw.pixls.us ID | Public name | Input SHA-256 |
|---|---|---|
| 780 | Olympus - C7070WZ - 12bit (4:3).ORF | `9d55506f9d6ee31d2d4c4b6df0dcd1d016d358b3e5eb4ed31edd7227dfefd5f8` |
| 792 | Olympus - SH-2 - 12bit (4:3).ORF | `6e6b9b7dd9ded7c4b364b83116c817ca2d6daac15f2e9ef7796159b08c3288a1` |
| 1432 | Olympus - XZ-2 - 12bit (4:3).orf | `675fefe7c9e99281783b987889d723b5f46692f5c20e19fed5e422c7c6d2636b` |
| 1799 | Olympus - C5060WZ - 12bit (4:3).ORF | `3fc12bc3f6320cfab456111d7805b446e329fdd1907680be55e2e163e5e084bd` |
| 1800 | Olympus - E-1 - 16bit (4:3).ORF | `042286653fbae5b085bef4a4e626145385ea6e82e817f166b4904abcef64457c` |
| 2151 | Olympus - E-400 - 16bit (4:3).ORF | `1354e0ac98ea90820227650031d8215637a2aaabd15de995c5a1e00b1986261b` |
| 2420 | Olympus - SP510UZ - 12bit (4:3).ORF | `f0737d78bb2e588963a3d5038fab493cdff1c9c48475704de96d797bbb81e62a` |
| 2431 | Olympus - XZ-10 - 12bit (4:3).ORF | `a25383acad9b5bb0bb404715e0957f2eb80aa1aaad6c448a71025c03cfa631be` |
| 2856 | Olympus - E-M5 Mark II - 16bit 16bit "high-res" (4:3).ORF | `5c42fa75d6b549514b722e2c50726c03e34fac4909ec3640e147ea7fa825fc8d` |
| 2878 | Olympus - E-300 - 16bit (4:3).ORF | `6d818dbff78b3e2efa4835f568d04733052b9211e6bc65b0a3748a841170e95b` |
| 2977 | Olympus - PEN-F - 16bit (4:3).orf | `f87a5f3295aeb4d6ab27bb5b41c5e0f3a211ec9b4e3b1d9f105a650bee1a2f13` |
| 3438 | Olympus - SP565UZ - 12bit (4:3).ORF | `5088771f83ce08a001b44672e1dd9f013e603933c37ce1bfb7030a02abbe801c` |
| 3540 | Olympus - E-500 - 16bit (4:3).ORF | `fa5a4759b2de2b573f59629ad1baf64ad04a85fb8fe1fb3cbf68e08a42fff4f0` |
| 3624 | Olympus - E-330 - 16bit (4:3).ORF | `ba11eb970ab32e1e9cf3d0176041e4bd11c501d445720c0a344217e785ad65a6` |
| 5424 | Olympus - E-10 - 16bit (4:3).ORF | `2bfdade72439017a60a47aad1e5bbcb1aca36f2be7a21e94a4257a678fb6f4da` |
| 5491 | Olympus - SP570UZ - 12bit (4:3).ORF | `baab92391834076b427e406e98da79aaba48fb87243d6ccae60e08e299cfccf7` |
| 8609 | Olympus - SP550UZ - 12bit (4:3).ORF | `05f49918e1b1894c3abd2b5451b356f7a00adb1c8568abc5babff33fcade1bb2` |

Source SHA-256 values:

- Original `tools/layout_probe.py` at the base: `eef3ac4386fcee5aaa6489f1c1c9b196f4538f338c37078c25ae011162e8d1b6`.
- Widened `tools/layout_probe.py`: `dd3294e65994e52080e7fc10b89de18a5fad15477e61bfe9ed35314cbc39bac5`.
- Shared original `decoder/orf_decode.py`: `4d6f8baed6079c56e13d5da612b1627f9d0926337a63383a2324c9f7278e6d77`.
- Shared original `tools/orf_signature.py`: `b1b6f091bfb986ab7aca3ad1f513202acfaaccc424272523589142444d025afb`.
- `tools/pixls_samples.py`: `96bc348acbc8d6f883ca099a58a215ac6e3a065ca0832ba348c80a13a88f8951`.

All three measurement runs exited zero, with no stderr or failed/excluded inputs. The widened aggregate text output SHA-256 is `651ab34dab9b7493b6d40dfb1a7b74228c6ebef9fe42b0e330bf07ae8e251198`. Synthetic metric checks covered equal rows, normalization, selected columns, a zero denominator and the upper normalized-difference boundary. These check arithmetic, not the physical layout interpretation.

## Reproduce

Fetch the separate tool contribution through upstream PR #122 and select its frozen measurement commit:

```sh
git fetch origin refs/pull/122/head
git checkout --detach fe4ec45712ed656528a254324dd515424b5268de
python -I tools/layout_probe.py --help
```

Download only the required CC0 models to a directory outside the contribution repository:

```sh
for model in C5060WZ C7070WZ SP510UZ SP550UZ SP565UZ SP570UZ SH-2 XZ-2 XZ-10 E-1 E-400 E-10 E-300 E-500 E-330 PEN-F 'E-M5 Mark II'; do
    python tools/pixls_samples.py download ../orf-samples-lead77 --model "$model" --max 1
done
python tools/pixls_samples.py check ../orf-samples-lead77/*
python -I tools/layout_probe.py ../orf-samples-lead77/*
python -I tools/layout_probe.py --all-rows ../orf-samples-lead77/*
```

Use a clean sample directory. Match the 17 files by their full input hashes above, not basenames. The download listing can change: if `--max 1` chooses a different file for a model, select the table's ID and hash instead of treating it as the same cohort. Local filenames use underscores for colons, as documented in samples/README.md.

The last command yields the widened tables above; output order follows shell filename order. The original sampled numerical results can also be reproduced by checking out the base commit and running its unchanged `layout_probe.py` command.

## Limits

This is a new wider run by another contributor, not a new estimator or an unseen camera cohort. It does not decide whether header magic or strip-gap geometry is the general selector, nor which rule wins if gap position differs from `ceil(height/2)`. It does not establish a CFA phase or absolute physical row origin from continuity alone. The historical decoder defect in #77 had already been addressed before this base commit and is not re-verified here; no decoder or conformance hashes are changed by this finding. Generalization beyond these measured files remains open.
