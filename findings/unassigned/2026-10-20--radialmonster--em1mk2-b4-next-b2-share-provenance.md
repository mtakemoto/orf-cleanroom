# E-M1MarkII: b4 carries most of the H-to-next-L information

Author: @radialmonster
Verified by: @mtakemoto
Lead: #11
Variant: unassigned
Builds on: 2026-10-19--radialmonster--em1mk2-token-dependence-vertical-lag2-differs
Partial: only the b4(t-1) to b2(t) share of H(t-1) to L(t) mutual information

## Claim
In the q-zero, stop-bit, 5-bit-suffix parse, b4 of a token carries about 95–98% of the baseline-adjusted lag-1 mutual information between H=b4b3 and the next L=b2b1b0 on raw.pixls.us ids 1993 and 1994. This verifies the bounded “about 97%” dependence claim of lead #11 on these files and extents. The absolute H-to-next-L information varies: 0.0507–0.0515 bit on id 1993, 0.0899–0.1125 bit on id 1994. The ~0.12-bit figure in #11 is close to the 1994 prefix, but does not describe the other three measurements.

## Original evidence
Lead #11 by @radialmonster reported that about 97% of H-to-next-L information was carried by b4 predicting b2, with H-to-next-L information around 0.12 bit on the original studied body. Its later comment names id 1994 and says “about 0.95” there. The original record cites only private research notes dated 2026-10-14..18, says they are not yet reproducible with public tools, and its Reproduce section says nothing is public yet. It publishes no original script or tool commit, and no complete original input file list or hashes. The exact ~0.12-bit result cannot be reproduced from that original record; proximity to a later measurement is not exact reproduction of the private run. The existing finding `2026-10-19--radialmonster--em1mk2-token-dependence-vertical-lag2-differs` reports a 0.97 share for the 400-row prefix of id 1993 and a 0.95 share for the 400-row prefix of id 1994. Id 1993 and id 1994 are separate files.

## Verification
@mtakemoto ran the repository's `tools/orf_tokens.py` after lead #11 was posted, on 2026-10-20 UTC (HEAD `18d6a0add3e29468b86ab10c7e65f8647e29e21d`, Python 3.14.5). Both raw.pixls.us files passed `tools/pixls_samples.py check` as CC0. The tool locates the largest-strip image IFD, parses tokens MSB-first, leaves q>=17 escapes out of H/L statistics, and reports plug-in mutual information with a rotated-pair baseline. The adjusted share is `(MI(b4(t-1);b2(t)) - baseline) / (MI(H(t-1);L(t)) - baseline)`. This repository tool at the stated commit is the verification tool, not an identified copy of the finder's original private script. This is a separate run of the same deterministic repository tool used by the earlier public finding, not an independent estimator. The whole payload of id 1994 extends beyond the 400-row prefix in the existing finding; whether it overlaps #11's private original measurements cannot be determined.

The verification measure follows the earlier public finding's baseline-adjusted b4-to-b2 share. The 400-row extents were chosen for direct comparison with that finding, and whole-payload extents to extend the comparison beyond those prefixes. This records the comparison rationale, not a claim that the measure or extent choices were locked before results were seen. The overlap of either file and extent with #11's private run is unknown; these runs are not established as held out from that run.

| raw.pixls.us id, SHA-256 | Extent | Payload | Tokens | Bits consumed / payload bits | Escapes | b4→b2 MI (baseline), bit | H→L MI (baseline), bit | Adjusted share |
| --- | --- | --- | ---: | --- | ---: | --- | --- | ---: |
| 1993, `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8` | 400 rows | 5240×3912 | 2,096,000 | 12,771,565 / 126,081,000 | 1 | 0.0498 (0.0000) | 0.0515 (0.0000) | 0.97 |
| 1993, same file | whole payload | 5240×3912 | 20,525,511 | 126,080,996 / 126,081,000 | 13 | 0.0495 (0.0000) | 0.0507 (0.0000) | 0.98 |
| 1994, `f8d04ca777b3cd4d1eed4c2971d713d6ac7397bf1254929b4097c4b619f49c23` | 400 rows | 10400×7792 | 4,160,000 | 24,997,002 / 487,951,184 | 588 | 0.1064 (0.0000) | 0.1125 (0.0001) | 0.95 |
| 1994, same file | whole payload | 10400×7792 | 81,065,363 | 487,951,180 / 487,951,184 | 5,864 | 0.0860 (0.0000) | 0.0899 (0.0000) | 0.96 |

The displayed mutual information and baseline values are rounded to four decimals and the adjusted share to two decimals by the tool. The 400-row extent is the first `400 × payload width` parsed tokens; row boundaries are not established by this parse. The unknown escape layout is a limit on interpretation, especially for id 1994 with many escapes.

## Reproduce
From the repository root:

    python tools/pixls_samples.py download ../orf-samples --model E-M1MarkII
    python tools/pixls_samples.py check ../orf-samples/1993_* ../orf-samples/1994_*
    sha256sum ../orf-samples/1993_* ../orf-samples/1994_*
    python tools/orf_tokens.py ../orf-samples/1993_* --rows 400
    python tools/orf_tokens.py ../orf-samples/1993_* --all
    python tools/orf_tokens.py ../orf-samples/1994_* --rows 400
    python tools/orf_tokens.py ../orf-samples/1994_* --all
