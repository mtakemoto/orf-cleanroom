# Large-sensor bodies: k=5 parse is near the Bernoulli null (4 CC0 files)

Author: @radialmonster
Verified by: @radialmonster
Lead: #86
Variant: unassigned
Builds on: #11, #37

## Claim

On four CC0 large-sensor files (OM-1 Mark II ids 7267 and 7269, OM-3 ids 7801 and 7803; 10386x7792 and 8172x6132 payloads, 8.2 to 8.8 bits per pixel), the k=5 token parse from #11 gives about the token count per pixel that an independent-bits (Bernoulli) null predicts, within 0.3% to 2.1%. Token correlations of min(q,8) at lags 1 to 6 are small but nonzero (largest at lag 2 on the OM-1 Mark II files), and escapes (q >= 17) are far more frequent than the null gives. This holds for these four files only; see Verification for files where it does not.

## Original evidence

Lead #86, `tools/orf_tokens.py --max-tokens 1000000` on the four files (sha256 in `samples/manifest.csv`). Tokens per pixel real vs null: 7267 1.2194 vs 1.1939, 7269 1.2454 vs 1.2345, 7801 1.1680 vs 1.1626, 7803 1.1833 vs 1.1870.

## Verification

A new run on 2026-10-20 UTC at repo main `72b756c`, files downloaded with `tools/pixls_samples.py download` (CC0, each SHA-256 checked by the tool), `tools/orf_tokens.py` unchanged.

The four lead files, `--max-tokens 1000000`, reproduce the lead's figures: tokens per pixel real/null 1.2194/1.1939, 1.2454/1.2345, 1.1680/1.1626, 1.1833/1.1870; lag 1 +0.0860, +0.0763, +0.0275, +0.0353; lag 2 +0.1157, +0.1465, +0.0156, +0.0270 (lead: +0.116, +0.147, +0.016, +0.027). With `--max-tokens 1500000` the escape counts (q >= 17) are 3701, 6968, 860, 2832, equal to the lead's.

Wider run, files the lead did not use (`--max-tokens 1500000`, tokens per pixel real vs null, lag 1 / lag 2 correlation, escapes):
- 7262 OM-1 Mark II 5220x3912, 8.078 bpp: 1.1987 vs 1.1317 (+5.9%), +0.188 / +0.189, 5694
- 7263 OM-1 Mark II 8180x6132, 7.191 bpp: 1.1214 vs 1.0051 (+11.6%), +0.258 / +0.218, 610
- 7265 OM-1 Mark II 10400x7792, 6.980 bpp: 1.0939 vs 0.9785 (+11.8%), +0.252 / +0.220, 235
- 7796 OM-3 5220x3912, 7.764 bpp: 1.1014 vs 1.0961 (+0.5%), +0.037 / +0.007, 3150
- 7797 OM-3 8180x6132, 6.993 bpp: 1.0361 vs 0.9947 (+4.2%), +0.088 / +0.069, 269
- 7799 OM-3 10400x7792, 6.760 bpp: 1.0161 vs 0.9661 (+5.2%), +0.064 / +0.060, 89

So the near-null result is not a property of the bodies as a whole: it holds for the four high-bpp files (8.2 to 8.8) and for 7796, but the OM-1 Mark II files at about 7 bpp or below sit 6 to 12% above the null with lag correlations of +0.2 to +0.26. Escape frequency stays well above the null (about 0.0015%) in every file (0.006% to 0.46%). Not tested here: other prefix-code families, and the cause of the lag 2 peak.

## Reproduce

    python tools/pixls_samples.py download <dir outside repo> --model OM-3
    python tools/pixls_samples.py download <dir outside repo> --model "OM-1 Mark II"
    python -I tools/orf_tokens.py "<dir>/7267_OM System - OM-1 Mark II - 16bit (4_3).orf" --max-tokens 1000000

Repeat for each id above; read the lines "ones-density ... real X, Bernoulli null Y", "correlation of min(q,8)" and "escapes (q>=17)" (the latter with `--max-tokens 1500000`).
