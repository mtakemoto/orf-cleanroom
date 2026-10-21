# Lead #29 item 4: six-file public held-out context transfer

Tool: `tools/token_context_probe.py` at immutable repository commit
`53698db2f91e00d7b269f48fd438e352a9849150` (unchanged).
Public raw.pixls.us IDs: 241, 1079, 1051, 4126, 4132, 6946.
Exact public names, SHA-256 identities and the complete aggregate report are in
[lead29-context-public-cohort.json](lead29-context-public-cohort.json).
Measured by: @mtakemoto, 2026-10-21 UTC.
Original lead and tool credit: @radialmonster.
Builds on: [#11](https://github.com/radialmonster/orf-cleanroom/issues/11),
[#29 item 4](https://github.com/radialmonster/orf-cleanroom/issues/29),
[#166](https://github.com/radialmonster/orf-cleanroom/pull/166) and
[#169](https://github.com/radialmonster/orf-cleanroom/pull/169).

The predeclared primary criterion holds on **4 of 6 prefixes**: E-PM1 id1079,
E-M1 id1051, and E-M10 Mark IV ids4126 and 4132. It fails on E-P3 id241
because `b4_one` has a negative gain, and on TG-7 id6946 because `b2_two`
has a negative gain. The fixed public pattern therefore does not transfer
uniformly to this availability-selected cohort. Larger models have mixed
incremental results and cannot rescue either primary failure.

This is a public explanatory study, not a finding. It extends a fixed public
estimator to an additional cohort; it neither replicates nor refutes the
historical smoothed private figures under their unspecified estimator.
No independent human verification is claimed. This contribution is **Part of
#29**, not a resolution of that issue.

## Fixed design and prior context

The [predeclared claim](https://github.com/radialmonster/orf-cleanroom/issues/29#issuecomment-6310675273)
fixed the six files, estimator, split and decision before outcomes. There
was no outcome-driven replacement of files, tuning of taps or smoothing,
change of split, or extension beyond the declared cohort.

[#166](https://github.com/radialmonster/orf-cleanroom/pull/166) supplied
pairwise lag-MI background, not conditional feature ordering.
[#169](https://github.com/radialmonster/orf-cleanroom/pull/169) introduced
this multivariate held-out estimator on the earlier public smoke cohort
1993/5283/6343. Its extra-context results were already nonuniform: the
five-tap b2 model worsened on 5283, and the b4 one-tap gain on 6343 was below
its own permutation mean. The present study asks whether those unchanged
fixed models transfer to six additional public prefixes; it is not a new
estimator or the first public item4 measurement.

These files are outside that context smoke cohort, but are **not pristine
held-out research samples**. They have already been used for other public
measurements, including the item6
[#172](https://github.com/radialmonster/orf-cleanroom/pull/172) lag-MI study
and item7 [#177](https://github.com/radialmonster/orf-cleanroom/pull/177)
scale study; five also occur in the earlier item2 report. Selection was by
public availability, not random sampling of files, camera bodies or scenes.
The two E-M10 Mark IV files are not assumed to be independent scene
replicates. Here, “held-out” refers to the within-prefix train/test split,
not to a previously untouched research cohort.

### Candidate parse and block split

The unchanged parser starts at payload bit zero and reads the first 262144
complete candidate tokens, MSB-first: q zero bits, a one stop bit, then five
suffix bits. A candidate q>=17 escape consumes q+6 bits, with no additional
escape skip. This is a candidate token interpretation, not established
post-escape framing.

Complete consecutive 128-token blocks are numbered from zero **before**
omission. Entire blocks containing any q>=17 token are omitted, as is an
incomplete tail. Retained original even-numbered blocks train; retained
original odd-numbered blocks test. Omitted blocks are not renumbered.
Original block parity is a split rule, not a test of even/odd token-position
invariance.

All six models use exactly the same target positions: zero-based within-block
`t>=5`, giving 123 targets per retained block. No context crosses a block
boundary. In a suffix integer `s`, `b2=(s>>2)&1` and `b4=(s>>4)&1`; bit
numbers count from the least-significant suffix bit. A lag is a previous
candidate token within the same block.

| Model | Target | Context taps, in packing order |
|---|---|---|
| `b2_empty` | b2 at t | Empty context |
| `b2_two` | b2 at t | b4 at t-1; b2 at t-2 |
| `b2_five` | b2 at t | b4 at t-1; b2 at t-2; b4 at t-3; b2 at t-4; b4 at t-5 |
| `b4_empty` | b4 at t | Empty context |
| `b4_one` | b4 at t | b2 at t-1 |
| `b4_two` | b4 at t | b2 at t-1; b2 at t-3 |

The first listed tap is packed as the most-significant context bit.
Train/test tables contain counts for each packed context and binary outcome.
For each context, the training-fitted probability of outcome y is
`(n_y + 0.5) / (n_0 + n_1 + 1)`: Jeffreys half-count smoothing per outcome.
An unseen training context predicts 0.5. The measured loss is mean held-out
`-log2(predicted probability of the test outcome)`, in bits per target,
not empirical conditional entropy. Every observed model here has training
and test targets, and all observed unseen-training-context test counts are
zero; those counts remain explicit in the JSON.

### Gains, controls and the decision

`gain_vs_empty_bits` is **same-target empty-model loss minus current-model
loss**. A positive gain improves on the fitted empty baseline; a negative
gain worsens it. The two target bits have separate baselines.

The primary descriptive criterion is applied separately to each file:

- `b2_two.gain_vs_empty_bits` must be strictly positive and strictly greater
  than its own mean gain over the sixteen permutations; **and**
- `b4_one.gain_vs_empty_bits` must meet those same two conditions against
  its own permutation mean.

Both models must pass. Being above a negative permutation mean does not
rescue a negative observed gain. Missing or null gains would not pass.
There is no significance threshold.

The larger models are secondary. Their signed incremental improvement is
`gain_vs_previous_bits`: **previous-model loss minus larger-model loss**.
For `b2_five` this is `loss(b2_two) - loss(b2_five)`; for `b4_two` it is
`loss(b4_one) - loss(b4_two)`. Thus a positive value means that adding taps
helps; a negative value means it hurts. This is not the reverse loss
subtraction that an informal “five minus two” label might suggest. For the
first nonempty model the previous gain equals its empty gain; empty models
have zero empty gain and null previous gain. Secondary results do not alter
the primary criterion.

Each of sixteen controls independently shuffles whole suffix tokens within
each retained block, preserving within-token structure and block marginals,
not temporal order. Replicate 0..15 uses one Python
`Random(20261021 + replicate)` generator, consumed across retained blocks
in original order. The original block indices and train/test split remain
fixed; every model is refitted and rescored for every replicate. Target
positions remain `t>=5`, so shuffling can change the scored target marginal
by changing which tokens occupy the excluded initial positions. Every model
is compared with its **own** mean permutation gain, not a shared null value.
These controls are descriptive comparators, not p-values or uncertainty
intervals.

## Cohort identity and selection

All six files passed a fresh `tools/pixls_samples.py check`. All six public
ID/name/SHA-256 identities matched existing `samples/manifest.csv` rows
attributed to @mtakemoto. Existing manifest rows and attribution were not
changed. Exact names and full hashes are retained in the JSON; the names in
the rerun command below are exact, including extension case. All payloads
have variable-size signatures and remain `unassigned`; body names do not
assign a codec variant.

| raw.pixls.us ID | Public body | Payload dimensions |
|---|---|---|
| 241 | Olympus E-P3 | 4080x3040 |
| 1079 | Olympus E-PM1 | 4080x3040 |
| 1051 | Olympus E-M1 | 4640x3472 |
| 4126 | Olympus E-M10 Mark IV | 5200x3904 |
| 4132 | Olympus E-M10 Mark IV | 5200x3904 |
| 6946 | OM System TG-7 | 4040x3016 |

Every file returned all 262144 requested tokens and 2048 complete blocks,
with zero prefix shortfall, tail tokens or tail escapes. The endpoints below
are consumed bits relative to payload bit zero, not physical row endpoints.
Train/test pairs always retain the original parity split.

| ID | Retained blocks train / test | Escape-omitted blocks train / test | Targets train / test | Candidate escapes | Bit endpoint |
|---|---:|---:|---:|---:|---:|
| 241 | 1022 / 1023 | 2 / 1 | 125706 / 125829 | 3 | 1737004 |
| 1079 | 997 / 1002 | 27 / 22 | 122631 / 123246 | 55 | 1756598 |
| 1051 | 1023 / 1023 | 1 / 1 | 125829 / 125829 | 3 | 1775448 |
| 4126 | 1023 / 1024 | 1 / 0 | 125829 / 125952 | 1 | 1737857 |
| 4132 | 1023 / 1023 | 1 / 1 | 125829 / 125829 | 3 | 1788524 |
| 6946 | 531 / 540 | 493 / 484 | 65313 / 66420 | 2235 | 1946399 |

TG-7 loses **977 of 2048 blocks**, retaining only 1071. Its results therefore
have a particularly strong selective-omission limitation. Omitted blocks
are not silently included in any training or test denominator. Omission
also does not repair unknown framing after an earlier escape: later retained
blocks still depend on the candidate parse.

## Results

The following baseline losses and signed gains reproduce the JSON values
without decimal-place rounding. All losses and gains are bits per held-out
target. The linked JSON is the complete numerical record: `report` contains
the unchanged CLI output, including every model's observed loss, both gains,
exact train/test tables, target and unseen-context counts, and all sixteen
permutation score triples. `model_comparison_means` contains every model's
own mean permutation loss and both mean gains; `decisions` records the
predeclared per-file decision. The tables here select complementary views
rather than duplicating all of those scores.

### Empty-model baseline losses

| ID | `b2_empty` loss | `b4_empty` loss |
|---|---:|---:|
| 241 | 0.9973645354231939 | 0.995427873193755 |
| 1079 | 0.9970910979196896 | 0.9944273083094956 |
| 1051 | 1.0000144427238808 | 0.9980938220729344 |
| 4126 | 0.9959640196817844 | 0.9941509086871613 |
| 4132 | 0.9900991221683013 | 0.9269473734686028 |
| 6946 | 0.9989546621781173 | 0.9977491836207358 |

### Primary models: gains over their own empty baseline

Each permutation column is the mean `gain_vs_empty_bits` for the model
immediately to its left, not a mean shared across models.

| ID | `b2_two` gain | Own permutation mean | `b4_one` gain | Own permutation mean | Primary criterion |
|---|---:|---:|---:|---:|---|
| 241 | 0.002438282618001608 | -2.7978574952354507e-05 | -1.0020036897984141e-06 | -4.770906599171898e-06 | fails |
| 1079 | 0.0006291836009549856 | -8.244944927543463e-06 | 2.3420028803289306e-05 | -4.23921721137005e-06 | holds |
| 1051 | 0.00031155455909370744 | -1.926195405745068e-05 | 4.425465181312482e-06 | -1.0664449238612095e-05 | holds |
| 4126 | 0.0028109067763409934 | 9.67642294680271e-07 | 0.0002871385831403339 | -1.039387389364932e-06 | holds |
| 4132 | 0.007569882595879651 | 0.0009179392622194402 | 0.0019889307931268974 | 0.0008223199640830445 | holds |
| 6946 | -6.478745147853182e-05 | -4.804041512399687e-05 | 7.625392552945698e-07 | -1.0907580160306185e-05 | fails |

On E-P3, `b4_one` is above its own negative permutation mean but still has
negative gain: it is worse than the empty baseline and the file fails.
TG-7's `b2_two` is both negative and below its own mean. Its small positive
`b4_one` gain cannot compensate. Neither failure is removed by a favorable
secondary score or by reporting only gain relative to a permutation mean.

### Secondary models: signed incremental gains from adding taps

These are `gain_vs_previous_bits`, not gains over the empty baseline.
Their own permutation means use the same previous-versus-larger subtraction
in each replicate. The larger models' empty-baseline gains and losses are
also preserved in the JSON, including all negative values.

| ID | `b2_five` increment over `b2_two` | Own permutation mean | `b4_two` increment over `b4_one` | Own permutation mean |
|---|---:|---:|---:|---:|
| 241 | 6.933351199767124e-05 | -0.0001682073634235795 | 0.0001826521282103366 | -7.317612797735906e-06 |
| 1079 | -4.8459253886634635e-05 | -0.00018339590109056614 | 4.642559628698084e-05 | -9.888095140138387e-06 |
| 1051 | -0.00016767911112836043 | -0.00012466644901931723 | -3.202166458660116e-06 | -2.251955687315732e-06 |
| 4126 | 0.0002501710352685871 | -0.00015552792762613815 | 0.0003213560513625202 | -3.1531011302904366e-06 |
| 4132 | 0.007628652729633423 | 0.001234767226843743 | 0.005099770889610333 | 0.0008380216366103629 |
| 6946 | -0.00045667370515833916 | -0.0003288979339346118 | -3.1475103203781885e-05 | -1.870676116070419e-05 |

Adding the three extra b2 taps worsens held-out loss on 1079, 1051 and 6946.
On 1079 that negative increment is nevertheless above its own more negative
permutation mean; this does not turn it into an improvement. On 1051 and
6946 the increments are also below their own means. Adding the second b4
tap worsens loss on 1051 and 6946, again below the corresponding means.
Positive primary transfer on 1051 therefore does not imply that more taps
help. Conversely, the positive b4 increment on 241 does not change its
predeclared primary failure.

On 4132, both primary gains and both secondary increments exceed their
**positive** own permutation means. Those positive comparison baselines
matter: the observed gains cannot all be attributed to the temporal ordering
that the shuffle removes, and comparing only with zero would omit the
control's nonzero predictive gains. The shuffles retain within-token
structure and block marginals; they are not a guarantee of independent
observations or a causal isolation of a codec mechanism. The positive
primary permutation mean for `b2_two` on 4126 also remains in the table;
negative null means are not assumed by the criterion.

## Reproduce the report and decision

Read the full unchanged `tools/token_context_probe.py`, its repository
imports `tools/suffix_joint_probe.py` and `tools/orf_signature.py`, and
`tools/test_token_context_probe.py` at the immutable commit above first.
Read `tools/pixls_samples.py` before its licence check. Obtain the exact
public CC0 files through that downloader, respecting its refusal to save
inside a repository. Substitute each FILE token with the corresponding
local sample path; no sample path is published here.

Run from the repository root with Python 3.14.7 to match the recorded Python
environment and seeded permutation behavior. The actual measurement used
Python **3.14.7, CPU only**. No GPU was required.

```sh
python -I -B tools/pixls_samples.py check FILE241 FILE1079 FILE1051 FILE4126 FILE4132 FILE6946
python -I -B tools/test_token_context_probe.py
python -I -B tools/suffix_joint_probe.py --self-test
python -I -B tools/token_context_probe.py --sample 241 "Olympus - E-P3 - 16bit (4:3).ORF" FILE241 --sample 1079 "Olympus - E-PM1 - 16bit (4:3).ORF" FILE1079 --sample 1051 "Olympus - E-M1 - 16bit (4:3).orf" FILE1051 --sample 4126 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4126 --sample 4132 "Olympus - E-M10 Mark IV - 16bit (4:3).ORF" FILE4132 --sample 6946 "OM System - TG-7 - 16bit (4:3).ORF" FILE6946
```

The tool prints aggregate JSON only, not sample bytes, token streams or
previews. Its complete CLI report is retained in the committed study JSON's
`report` member, separate from the surrounding study and audit metadata.
The source hashes in `report.source_sha256` pin the estimator,
parser and locator:

| Source under `tools/` | SHA-256 |
|---|---|
| `token_context_probe.py` | `09c1db54ddef6455c87ea874508ae79c0a134d8282ad708f602e8e41fe5deb7f` |
| `suffix_joint_probe.py` | `c16c0f55bff91897a949cd94cc8c64d8117568d7ce215a735c6f1ae04d092f18` |
| `orf_signature.py` | `b1b6f091bfb986ab7aca3ad1f513202acfaaccc424272523589142444d025afb` |

The following reads only the committed aggregate report and recomputes the
fixed primary decision and each nonempty model's relevant own permutation mean.
For secondary models it prints the signed incremental gain, not the
empty-baseline gain. It introduces no new estimator or threshold.

```sh
python -I -B - <<'PY'
import json
import math

with open("stats/lead29-context-public-cohort.json", encoding="utf-8") as handle:
    report = json.load(handle)["report"]
if report["failures"]:
    raise SystemExit("Report contains failed samples")
for sample in report["samples"]:
    models = {model["name"]: model for model in sample["models"]}
    comparisons = {}
    for name in ("b2_two", "b4_one", "b2_five", "b4_two"):
        model = models[name]
        key = ("gain_vs_empty_bits" if name in ("b2_two", "b4_one")
               else "gain_vs_previous_bits")
        values = [score[key] for score in model["permuted_scores"]]
        mean = math.fsum(values) / len(values)
        comparisons[name] = (model[key], mean)
    holds = all(gain is not None and gain > 0 and gain > mean
                for gain, mean in (comparisons["b2_two"],
                                   comparisons["b4_one"]))
    print(sample["pixls_id"], "holds" if holds else "fails", comparisons)
PY
```

Expected decisions in the declared order are: 241 fails, 1079 holds,
1051 holds, 4126 holds, 4132 holds, 6946 fails. Full model losses and both
kinds of gain remain available directly in the report rather than being
replaced by this summary.

### Verification actually completed

The recorded measurement checks comprise six fresh CC0 checks, six exact
existing manifest user/ID/name/hash matches, six context synthetic tests,
and the scanner self-test. A separate original implementation also passed
sixteen synthetic oracle checks. It independently located the container and
parsed the candidate tokens, without importing or calling the repository
estimator or scanner, and used Counter tables and log-difference arithmetic
to audit the result.

That computational audit confirmed **414 metadata checks, 36 observed
train/test table pairs, 36 observed score triples, and 576 permutation
score triples**, with zero mismatches at an absolute score tolerance of
`1e-12`. The score triples comprise loss, empty gain and previous gain,
retaining nulls where applicable. Metadata checks include selection and bit
endpoints, target counts and observed unseen-context counts. The audit covers
every permutation's scores, not merely the first replicate. It does **not**
compare exact permutation train/test tables or permutation unseen counts:
the unchanged CLI does not export them. No such exact-table comparison is
claimed. The audit implementation's source hash and the complete audit
counts are recorded under `verification` in the JSON.

This is an independent implementation and computational run, **not
independent human verification**. The earlier static evidence review alone
was not a numerical audit; the scope above describes the subsequently
completed run. No external decoder material, decoder output or previews
were used: the sources were original repository code, lawful public CC0
inputs and original analysis.

## Interpretation limits

These blocks are not established physical camera rows. Adjacent training
and test blocks can remain dependent, so the held-out split does not
establish independent samples. Selective escape omission, prefix-only
measurement, unknown post-escape framing, cohort reuse and availability
selection limit generality. A permutation mean is not a significance test,
an uncertainty bound, an independence guarantee or a causal control.

The measurements establish only the reported predictive associations under
this fixed candidate parse, selection, split and estimator. They do not
establish physical rows, a codec mechanism, causal adaptation, a universal
interleaved binary chain, parity invariance, GF(2) rank, a deeper b2/b4 law,
or conditional feature ordering. Nor do they justify a decoder/spec change,
a model-based variant assignment, or automatic follow-on promotion.

The historical private input identities and complete estimator were not
supplied. Reproducing the historical smoothed figures requires identified
lawful inputs and the original outcome/context definition, row split,
smoothing, selection and scoring protocol. This different public estimator
and cohort neither replicate nor refute those figures. Physical-row tests
also require established boundaries and escape/framing interpretation.
Any wider untouched windows or cohorts need a separate declaration, not an
outcome-driven addition to this run.

## Status

The bounded six-file study and its computational audit are complete. The
primary descriptive criterion holds on 1079/1051/4126/4132 and fails on
241/6946. All signed secondary outcomes are retained. This mixed result is
a completed study, not an unsupported finding or completion of historical
item4. Existing findings and manifest rows remain unchanged; no new tool,
code, decoder/spec change or documentation promotion is part of this study.
The numbered claim dispositions for #29 remain:

1. **Unique k=5 row exactness — not tested.** Fixed k=5 prefix parsing is not
   a k=2..8 or stop-convention comparison. Physical row endpoints remain
   unresolved.
2. **Tokens/pixel — existing Partial findings, not reverified here.**
   [#118](https://github.com/radialmonster/orf-cleanroom/pull/118) and
   [#129](https://github.com/radialmonster/orf-cleanroom/pull/129) cover
   separate evidence. No new ratio, calm/busy rule or causal bpp claim is made.
3. **Within-token correlations and conditionals — not tested here.**
   [#152](https://github.com/radialmonster/orf-cleanroom/pull/152) measures
   a different public metric with mixed cross-file generality; historical
   smoothed estimates remain open.
4. **Alternating contexts — bounded public transfer measured, mixed.**
   The declared primary criterion holds on four of six prefixes, with signed
   secondary gains and own permutation means reported. This does not test
   the historical .15/.14/.016-bit gains, greedy conditional ordering,
   parity invariance, GF(2) rank, a four-tap comparison or a binary-chain law.
5. **Greedy approximately 340-feature search — not tested.** Fixed selected
   taps cannot show that other features lose or that row-position features
   are absent.
6. **q lag3 versus low3 — not tested here.**
   [#164](https://github.com/radialmonster/orf-cleanroom/pull/164) and
   [#172](https://github.com/radialmonster/orf-cleanroom/pull/172) provide
   separate plug-in MI studies; the latter's largest-lag criterion holds
   on only two of six files. Historical smoothed values, stationarity and
   magnitude-scale interpretation remain open.
7. **Slow scale — not tested here; no overlap with
   [#173](https://github.com/radialmonster/orf-cleanroom/pull/173) or
   [#177](https://github.com/radialmonster/orf-cleanroom/pull/177).**
   Binary-q running-count transfer is not historical full-q entropy or
   causal adaptation.
8. **Donor pattern — not tested here; no overlap with
   [#180](https://github.com/radialmonster/orf-cleanroom/pull/180).**
   Nominal width-lag/parity correlations do not establish physical rows,
   CFA/donor structure, magnitude peaks or invariance.
9. **Row-start block — not tested.** This requires established physical row
   starts and a declared early-versus-later measure on more bodies.

All four historical **Next steps** remain open:

1. **Parser/MI/held-out reproduction on other files.** This run adds scoped
   public item4 evidence only; row exactness and the historical estimators
   and lawful identified input files are still missing.
2. **Every item across other CC0 size classes.** Six additional item4
   prefixes are not all-items coverage or population generality.
3. **Check items7/9 on more bodies.** Item7 has separate #177 evidence;
   this contribution settles neither historical claim and does not test
   item9. Physical-row boundaries and declared row-start comparisons remain
   prerequisites for item9.
4. **Deeper b2/b4 law.** Fixed context transfer supplies neither a feature
   search, parity comparison nor GF(2) test. Those require separately
   declared measurements.

Leave #29 open. Exact rerun instructions and immutable tool provenance are
above. All new measurements use the named public CC0 inputs, not unspecified
private files. This aggregate study follows `RULES.md` and is released under
CC0 1.0.
