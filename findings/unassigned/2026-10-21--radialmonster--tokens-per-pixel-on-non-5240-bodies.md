# Tokens per pixel on five CC0 bodies that are not 5240 wide

Author: @radialmonster
Verified by: @radialmonster
Lead: #29
Variant: unassigned
Builds on: #11
Partial: item 2 only (tokens per pixel), on bodies 4080, 4040, 4640 and 5200 wide; items 1 and 3 to 9 not verified

## Claim

Parsing a whole compressed payload as tokens (q zero bits, a stop bit, a 5-bit suffix; an escape is parsed like any other token) gives about one token per pixel on most bodies and more on busy ones. On five CC0 files from bodies not named in the lead, the token count divided by payload width times height is 1.027 to 1.036 on four of them and 1.155 on the fifth (TG-7, the busiest by bits per pixel).

## Original evidence

Lead #29, item 2, opened by @radialmonster on 2026-10-18: 1.0001, 1.0013 and 1.0036 tokens per pixel on three 5240-wide class bodies, 1.025 to 1.034 on the 4640-wide class, 1.154 on the 5220x3912 body. The lead cites private notes and no public script; it builds on #11.

## Verification

New run on 2026-10-21 UTC, after the lead was posted, with `tools/orf_tokens.py` at `e07ad95` (repository head `6ad67a6`), `python -I tools/orf_tokens.py --all FILE`, which parses the whole payload and prints "tokens parsed". Ratio = tokens parsed / (payload_w x payload_h). The tool's own "tokens per pixel (estimated from bits per token)" line agrees to four digits. None of these five bodies is a 5240-wide body, and none was among the lead's named size classes except the 4640-wide E-M1; the 5240-wide "calm" claim (1.0001 to 1.0036) was not tested here.

| raw.pixls.us id | Model | Payload | SHA-256 | Tokens parsed | Tokens per pixel | Escapes |
| --- | --- | --- | --- | ---: | ---: | ---: |
| 241 | E-P3 | 4080x3040 | `540edabdd9d4e6ef8602f56443730cc3133d714dc4d3d2c607e2f0aa6be5cbcd` | 12739341 | 1.0271 | 2282 |
| 1079 | E-PM1 | 4080x3040 | `db8a564def35efaadf72cf74de92fa3959b2ab44bee4e0ec7876305830c59765` | 12759714 | 1.0287 | 6611 |
| 1051 | E-M1 | 4640x3472 | `19ba17e778ae802d4039f0e88bb1cd68825780788b8058c479067e32b9a63eda` | 16694598 | 1.0363 | 2225 |
| 4126 | E-M10 Mark IV | 5200x3904 | `ce03e936cb2e8131343e7045a3249f78477bd2ae944e121ace72058b89fef509` | 20882428 | 1.0287 | 1606 |
| 6946 | TG-7 | 4040x3016 | `4f7344c67bfcfcfec45f754195ba612fc2ad6312f5fab87812bf04b9e9e7d46a` | 14075268 | 1.1552 | 25462 |

Against the lead: the four ordinary bodies sit at 1.027 to 1.036, just above the lead's 4640-wide range (1.025 to 1.034; the E-M1 at 1.0363 is slightly outside it), so "more than one token per pixel on non-calm bodies" holds and the exact range does not carry over. TG-7 at 1.155 matches the lead's 1.154 for a busy body. The count includes escapes (0.008% to 0.18% of tokens); they do not change the ratio at the third decimal except on TG-7.

Item 1 (only k=5 gives zero change in bits per row) is not verified: the tool has no suffix-width option and rows cannot be delimited. As a different measure, a whole-payload parse with suffix width k = 2 to 8 and both stop-bit conventions (script in Reproduce) gives tokens per pixel nearest 1 at k=5 on four of the five files, with stop=1 1.027 to 1.036; on TG-7 it is k=6 that gives 1.0006 (k=5: 1.155). That measure does not single out the stop-bit convention either (k=5 with stop=0 gives 0.973 to 0.999 on the four ordinary files). So it neither confirms nor contradicts item 1 as the lead states it.

## Reproduce

```sh
python -I tools/pixls_samples.py download ../orf-samples --model E-P3 --max 1   # likewise E-PM1, E-M1, "E-M10 Mark IV", TG-7
python -I tools/orf_tokens.py --all FILE      # "tokens parsed" divided by payload w x h
```

Match files to the table by SHA-256. `--all` on a 100 MB-class payload needs several GB of memory; the files above are 10 to 18 MB. The k-scan used a short stdlib script (`bin()` of the payload, `str.find("1")` for the stop bit, advance k bits, count tokens until the payload ends) and is not part of this finding.
