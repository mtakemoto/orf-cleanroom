# E-M1MarkII: sequential suffix association alternates by lag and changes with extent

Author: @radialmonster
Verified by: @mtakemoto
Lead: #11
Variant: unassigned
Builds on: 2026-10-19--radialmonster--em1mk2-token-dependence-vertical-lag2-differs, 2026-10-20--radialmonster--em1mk2-b4-next-b2-share-provenance
Partial: measured alternating sequential H/L lag association on raw.pixls.us ids 1995 and 1997, at the first 2,096,000 candidate tokens and whole payload; not exclusive cross-/same-field dependence, exact within-token independence, or the lead's geometry, CFA, value or escape interpretations

## Claim

Under the candidate q-zero, stop-1, five-bit-suffix parse, the measured association between suffix labels `H=b4b3` and `L=b2b1b0` has the qualitative lag pattern reported in #11 on these fixed files and extents: cross-field MI dominates at sequential lags 1 and 3, and same-field MI dominates at lag 2. This is a statement about the reported associations, not proof of two exclusive chains or a decoder interpretation.

The full tables below do **not** verify the literal word “only.” Smaller off-pattern cells are nonzero at the tool's precision. Within-token H/L MI is 0.0005 bit in both prefixes and 0.0007 in both whole payloads, against displayed 0.0000 rotated baselines; small MI does not establish exact independence. The measured b1/b0 marginals are not exactly 0.5, and their balance does not establish independent fair-coin trials. No significance threshold or equivalence margin is applied.

Lag-1 H→L MI falls from 0.0390/0.0394 bit in the two prefixes to 0.0280/0.0281 over their whole payloads. The original approximate 0.12-bit H→L and 0.07-bit L→H figures are not stream constants. These extent differences do not correct the earlier finding's measurements of its fixed prefixes.

## Original evidence

[Lead #11](https://github.com/radialmonster/orf-cleanroom/issues/11), by @radialmonster, reports the H/L split and alternating lag association from private notes dated 2026-10-14..18. It supplies no original script/commit or complete original input list and hashes. The exact private figures and overlap with these public files cannot be reproduced from that provenance.

The first finding in `Builds on` supplies the public candidate-parse method and prefix comparison: its id 1995/1997 lag-1 H→L values are 0.0390/0.0394, L→H 0.0219/0.0218, and lag-2 L→L 0.0407/0.0415. It credits #11 and #37 and identifies `tools/orf_tokens.py`, last changed in `8e5dc0e`. The second finding independently credits @mtakemoto's bounded verification of the b4→b2 information share on ids 1993/1994 and documents the private-provenance limits. This finding builds on those tools and findings; it is not a new verification of that share.

## Verification

@mtakemoto's separate run on 2026-10-21 UTC used the existing, unchanged `tools/orf_tokens.py` at repository commit `71b6e96065564357e601a861fb37a118ff96c724`. The two files, both already public, freshly passed `tools/pixls_samples.py check` as CC0:

| raw.pixls.us id | Exact public name | SHA-256 |
| --- | --- | --- |
| 1995 | `Olympus - E-M1MarkII - 16bit (4:3).ORI` | `8af918366ed969c6dddf5a48b8810fec1024858d22c75c5f1ac1a5c750a57a1f` |
| 1997 | `Olympus - E-M1MarkII - 16bit (4:3).ORI` | `89138ccc958509ca1beb7028452400ab7f42061c0fc56e35c8a7d7a4a808dd0a` |

Both signatures are ORF-RO, payload dimensions 5240×3912, BitsPerSample 16, Compression tag 1, payload offset 1,500,160, variable size (6.154 bits per payload pixel by the signature tool). These signatures do not assign a bitstream variant.

Before these results, the run fixed the files, prefix and whole extents, within-token comparison, all four field pairings at lags 1/2/3, and the default parse/escape handling. All six CC0 E-M1MarkII files had already been used publicly. The whole-payload dependence measurements here widen the earlier 400-block dependence measurements on 1995/1997; they are not held-out files, a new body, or established non-overlap with the private historical run. The prefixes overlap their whole extents and are not independent replicates.

The tool locates the largest-strip image IFD and scans MSB-first from its payload start. Each candidate consumes q zeros, one stop bit and five suffix bits, with no extra escape skip. Candidates with q≥17 retain their sequential positions but are excluded from H/L statistics. A pair is accepted only when both endpoints are ordinary; gaps are not closed. `--rows 400` means `400 × 5240 = 2,096,000` candidate tokens, **not demonstrated physical rows**. `--all` scans the payload rather than stopping at width×height tokens.

### Counts and endpoints

Consumed-bit positions are relative to payload start. Ordinary counts are candidate tokens minus q≥17 candidates; “escape” below is this measurement convention, not a verified escape layout.

| Id | Extent | Payload bytes | Candidate tokens | Ordinary tokens | Escapes | Bits consumed / payload bits |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 1995 | 400 blocks | 15,768,425 | 2,096,000 | 2,095,999 | 1 | 12,760,459 / 126,147,400 |
| 1995 | whole payload | 15,768,425 | 20,513,176 | 20,513,126 | 50 | 126,147,398 / 126,147,400 |
| 1997 | 400 blocks | 15,767,553 | 2,096,000 | 2,095,999 | 1 | 12,759,401 / 126,140,424 |
| 1997 | whole payload | 15,767,553 | 20,513,308 | 20,513,256 | 52 | 126,140,420 / 126,140,424 |

### Within-token MI and suffix bit balance

Probabilities use ordinary suffixes only. MI is in bits. Every within-token rotated baseline is **0.0000 at tool precision**, not established exact zero. The within-token pair count is the ordinary-token count above.

| Id | Extent | MI(H;L) | P(b4=1) | P(b3=1) | P(b2=1) | P(b1=1) | P(b0=1) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1995 | 400 blocks | 0.0005 | 0.2904 | 0.4066 | 0.3242 | 0.4795 | 0.4955 |
| 1995 | whole payload | 0.0007 | 0.3162 | 0.4151 | 0.3417 | 0.4761 | 0.4935 |
| 1997 | 400 blocks | 0.0005 | 0.2903 | 0.4064 | 0.3234 | 0.4794 | 0.4951 |
| 1997 | whole payload | 0.0007 | 0.3161 | 0.4149 | 0.3414 | 0.4761 | 0.4935 |

### Complete sequential-lag tables

`A→B` at lag k means MI between `A[t-k]` and `B[t]`, not causal direction. All four cells are retained, including small and displayed-zero outcomes. Each row's count applies to every observed field pairing in that row. **Every cell's rotated baseline is 0.0000 at tool precision.**

| Id | Extent | Lag | Ordinary endpoint pairs | H→L | L→H | L→L | H→H |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1995 | 400 blocks | 1 | 2,095,998 | 0.0390 | 0.0219 | 0.0004 | 0.0008 |
| 1995 | 400 blocks | 2 | 2,095,997 | 0.0001 | 0.0008 | 0.0407 | 0.0020 |
| 1995 | 400 blocks | 3 | 2,095,996 | 0.0010 | 0.0164 | 0.0001 | 0.0003 |
| 1995 | whole payload | 1 | 20,513,076 | 0.0280 | 0.0141 | 0.0006 | 0.0019 |
| 1995 | whole payload | 2 | 20,513,075 | 0.0001 | 0.0011 | 0.0297 | 0.0017 |
| 1995 | whole payload | 3 | 20,513,074 | 0.0009 | 0.0126 | 0.0000 | 0.0002 |
| 1997 | 400 blocks | 1 | 2,095,998 | 0.0394 | 0.0218 | 0.0004 | 0.0008 |
| 1997 | 400 blocks | 2 | 2,095,997 | 0.0002 | 0.0007 | 0.0415 | 0.0021 |
| 1997 | 400 blocks | 3 | 2,095,996 | 0.0010 | 0.0165 | 0.0001 | 0.0003 |
| 1997 | whole payload | 1 | 20,513,204 | 0.0281 | 0.0141 | 0.0007 | 0.0019 |
| 1997 | whole payload | 2 | 20,513,203 | 0.0001 | 0.0011 | 0.0298 | 0.0017 |
| 1997 | whole payload | 3 | 20,513,202 | 0.0010 | 0.0126 | 0.0000 | 0.0002 |

MI is the plug-in estimate printed to four decimals. The diagnostic baseline rotates the lagged target by `len(target)//2 + 12345` before excluding escape endpoints; rotated and observed accepted-pair counts need not agree. A single rotation is not a null distribution, a significance test, or proof of independence.

Reusing the deterministic repository CLI is not itself an independent estimator. The verifier also cross-checked with a separately implemented scanner and contingency/MI calculation sharing the repository TIFF locator: exact token/escape counts, consumed endpoints, ordinary suffix histograms, and all 52 observed plus 52 rotated contingency tables (within-token plus twelve lag/field comparisons per extent) agreed. All reported CLI MI and bit-balance values agreed at displayed precision. This implementation cross-check adds no extra human verifier and establishes no decoder semantics. The public values above are reproducible with the existing CLI alone; no private oracle is required for the reproduction below.

The supported scope is the measured alternating sequential association and its extent dependence. Exact H/L independence and exclusive cross-/same-field dependence are not verified. Physical rows, one token per pixel, row/column parity, byte alignment, preview geometry, CFA identity, signed/residual values, prediction/value assembly, initial/escape framing and larger-sensor ordinary codes are not established here. Lead #11 remains open for its remaining claims.

## Reproduce

From the repository root at commit `71b6e96065564357e601a861fb37a118ff96c724`, use the unchanged tools. Download outside the repository, then check the two selected inputs:

```sh
python -I -B tools/pixls_samples.py download ../orf-samples --model E-M1MarkII
python -I -B tools/pixls_samples.py check ../orf-samples/1995_* ../orf-samples/1997_*
```

Each glob must select exactly one file: `1995_Olympus - E-M1MarkII - 16bit (4_3).ORI` and `1997_Olympus - E-M1MarkII - 16bit (4_3).ORI`, respectively. The downloader replaces `:` in the public name with `_`. Confirm the check reports CC0 and the exact public names above; it identifies files by SHA-256. Use the exact hashes above as the input identities, not model/name alone.

The four measurement commands are:

```sh
python -I -B tools/orf_tokens.py ../orf-samples/1995_* --rows 400
python -I -B tools/orf_tokens.py ../orf-samples/1995_* --all
python -I -B tools/orf_tokens.py ../orf-samples/1997_* --rows 400
python -I -B tools/orf_tokens.py ../orf-samples/1997_* --all
```
