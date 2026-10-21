# Corrected trailing-one counts reproduced on the full 87-file cohort

Author: @radialmonster
Verified by: @mtakemoto
Lead: #87
Variant: unassigned
Builds on: #11, 2026-10-20--radialmonster--trailing-one-bit-in-compressed-payloads
Partial: corrected 87-file tail-count histograms only; padding, token endpoints and the cause of zero-ending files remain open

## Claim

In a new whole-payload run on the 87 distinct CC0 variable-size files identified by the pre-lead manifest, 82 payloads end in at least one 1 bit and five end in a 0 bit. The maximum trailing-one run is 10 bits. The corrected last-byte, last-eight-byte and full-payload histograms from lead #87 all reproduce exactly.

A final-byte count is capped at eight: seven files have exactly eight trailing ones and two have ten, so nine files enter the last-byte bin eight. The ten-bit runs cross a byte boundary. These literal counts do not identify padding or the last decoded token.

## Original evidence

@radialmonster opened lead #87 on 2026-10-19, measuring the then-available CC0 files with `size_class=variable` using the original `tools/orf_tokens.py` payload locator. The original eight-byte histogram summed to 106 rather than 87 because files were counted more than once. The finder explicitly corrected it on 2026-10-20 in the lead body and [this comment](https://github.com/radialmonster/orf-cleanroom/issues/87#issuecomment-6295727037). This finding reproduces the corrected histogram, not the superseded 106-count version.

The immutable pre-lead manifest at `ad566d4c5820716efb47a02d20fe9e4444b272e8` contains exactly 87 distinct hashes with `source=pixls`, `licence=CC0`, and `size_class=variable`. The earlier Partial finding verified 16 preselected model-weighted files, 15 positive; it did not verify the full 87-file, file-weighted distribution. That finding is unchanged.

## Verification

On 2026-10-21 UTC, @mtakemoto fixed all 87 cohort members and the corrected comparison histograms before the new run. The cohort is `tools/cohorts/lead87-trailing-ones-v1-full.json`, with exact-file SHA-256 `13d58cd6149671e53cbd853956ac40f0b4673f00bebe3b79e0d10fd1f2ce49e2`. Current catalogue checks found 104 CC0 files, none beyond the original 104-file collection, so there was no unused publicly listed CC0 input outside the finder's collection. This is a new run on the same original 87 hashes, extending the earlier verifier's 16-file coverage to all 87 and independently scanning each full payload; it is not unseen-body validation.

All 87 input identities matched the public catalogue/manifest SHA-256 and passed `tools/pixls_samples.py check` as CC0 before measurement. Every cohort payload has one image strip. The original contiguous locator is appropriate here; the new counter is not a generic separated-strip parser. It indexes inputs by streamed SHA-256 regardless of cache filename/extension and counts duplicate cached copies once. Each measured signature must be variable-size with compression tag 1; signature hash, dimensions and payload byte count are checked against the declaration/locator. Compression tag 1 alone does not distinguish compressed ORF from fixed-size V0.

The counter and independent synthetic suite were frozen at tool commit `cec72b12579809c616b9b09bfe13b1ce89ec3486` before target measurement (tool PR #132). Seven tests passed, including all 65,536 two-byte values against a literal-bit-string oracle, empty/all-one/>64-bit boundaries, renamed/duplicate cache inputs, mixed success/missing inputs, invalid cohort declarations and fixed-size rejection. The CLI self-test passed the same suite. Original helpers are imported rather than copied. Source SHA-256:

- `tools/trailing_ones_probe.py`: `61031132013010e3813141b5199ebe2096e9231363090e4b2e77f3f894f7a940`
- `tools/orf_tokens.py`: `df1ad48d331207e887adcfd4b86d3ef96ae9a909fa0f2ef5048d149936e572a2`
- `tools/orf_signature.py`: `b1b6f091bfb986ab7aca3ad1f513202acfaaccc424272523589142444d025afb`

The measurement exited with status 0, with 87 successful rows and no failures. Each of the three windows was counted separately; every file satisfied `byte = min(full,8)` and `eight = min(full,64)`. The last-eight and full-payload counts agreed on every file, not merely in aggregate.

| Run length | Last-byte files | Last-eight-byte files | Full-payload files |
| ---: | ---: | ---: | ---: |
| 0 | 5 | 5 | 5 |
| 1 | 12 | 12 | 12 |
| 2 | 8 | 8 | 8 |
| 3 | 8 | 8 | 8 |
| 4 | 12 | 12 | 12 |
| 5 | 8 | 8 | 8 |
| 6 | 17 | 17 | 17 |
| 7 | 8 | 8 | 8 |
| 8 | 9 | 7 | 7 |
| 10 | 0 | 2 | 2 |

The zero-ending files are IDs 1431, 2152, 5286, 6345 and 7802. The ten-bit runs are IDs 3210 and 6343. Those identities and counts are reported below; their token-end behavior and the reason for the zero endings were not tested.

Conditional on independent fair final bits, the exact one-sided probability of 82 or more positives in 87 is 39,285,576 / 2^87, approximately 2.538770845326447e-19. Shared encoders/camera families mean file independence is an assumption, not an established property. This conditional arithmetic does not prove padding, a decoding rule, or generalization beyond this fixed cohort. No run-length goodness-of-fit test or token parse was performed.

All inputs are publicly listed CC0 files. Only public identities and aggregate counts are committed, not raw bytes, images or pixel values. The manifest already contains these hashes and @mtakemoto signature measurements; no redundant rows were appended.

## Reproduce

Use a clean checkout of this original repository. The separate tool PR can be fetched before maintainer merge, then pinned to the exact measured commit:

```sh
git fetch origin refs/pull/132/head
git switch --detach cec72b12579809c616b9b09bfe13b1ce89ec3486
python -I tools/trailing_ones_probe.py --self-test
python -I tools/pixls_samples.py download /path/to/lead87-samples
python -I tools/pixls_samples.py check /path/to/lead87-samples/*
python -I tools/trailing_ones_probe.py --cohort tools/cohorts/lead87-trailing-ones-v1-full.json --sample-dir /path/to/lead87-samples --measured-by @yourhandle
```

The downloader selects CC0 files only; keep them outside the repository and recheck licences before use. The counter selects only the frozen 87 hashes, even if the download directory contains additional CC0 files. Missing required inputs produce explicit failure JSON and a nonzero exit rather than a smaller silently substituted cohort. Compare the output's cohort/source hashes above, then all three histograms and per-file rows below. An input/output hash or count mismatch is a failed reproduction, not a reason to change membership.

## Public input identities and measured counts

| raw.pixls.us ID | Public filename | Measured model | Input SHA-256 | Last byte | Last eight bytes | Full payload |
| --- | --- | --- | --- | ---: | ---: | ---: |
| 241 | Olympus - E-P3 - 16bit (4:3).ORF | E-P3 | `540edabdd9d4e6ef8602f56443730cc3133d714dc4d3d2c607e2f0aa6be5cbcd` | 2 | 2 | 2 |
| 1051 | Olympus - E-M1 - 16bit (4:3).orf | E-M1 | `19ba17e778ae802d4039f0e88bb1cd68825780788b8058c479067e32b9a63eda` | 1 | 1 | 1 |
| 1079 | Olympus - E-PM1 - 16bit (4:3).ORF | E-PM1 | `db8a564def35efaadf72cf74de92fa3959b2ab44bee4e0ec7876305830c59765` | 2 | 2 | 2 |
| 1084 | Olympus - E-M5 - 16bit (4:3).ORF | E-M5 | `b2221977cbc6eba0d3b363351072092e5647eaa0d02a5d8432b5d985b29f669f` | 6 | 6 | 6 |
| 1090 | Olympus - E-P5 - 16bit (4:3).ORF | E-P5 | `a1345ebe8d8722e791cbd52778e73257c5ff457ee13988fd78eac61eec841c21` | 5 | 5 | 5 |
| 1135 | Olympus - TG-4 - 16bit (4:3).ORF | TG-4 | `a056d3fad56762d8a125806a0a4857341f115bc6303085b7297758be8d93b20a` | 5 | 5 | 5 |
| 1173 | Olympus - E-410 - 16bit (4:3).ORF | E-410 | `b545f3d831275d7febb1d02bfa22b03078eeff27fcb4c5be6806e89857bb1ed7` | 3 | 3 | 3 |
| 1233 | Olympus - E-PM2 - 16bit (4:3).ORF | E-PM2 | `84f9442e59eba80a6272a07759517dd0e32dfa114d2cc541ec3a67eea34cca55` | 4 | 4 | 4 |
| 1330 | Olympus - E-PL3 - 16bit (4:3).ORF | E-PL3 | `ce90f016fc6ddb14e407071c5a035b68039c5aec5a801e4152a88d2c2388f0d4` | 8 | 8 | 8 |
| 1331 | Olympus - E-M10 - 16bit (4:3).ORF | E-M10 | `d7f6ac99ee1f824e81ec0e71599f0f87f9b2e2675f7ddfdb21202281b8bdc5e0` | 6 | 6 | 6 |
| 1430 | Olympus - E-PL6 - 16bit (4:3).orf | E-PL6 | `38d3750abbcf847bba58e254b2ab8c57d8c9f3fc48490c29ae2b55c4e84d5f64` | 6 | 6 | 6 |
| 1431 | Olympus - E-PL7 - 16bit (4:3).orf | E-PL7 | `e0e138e9d33b0d2a16c0a9378582ddaac71d0b2cf07bc9ed459df275aa025c60` | 0 | 0 | 0 |
| 1723 | Olympus - TG-5 - 16bit (4:3).ORF | TG-5 | `1fd6d09b8c93a9bb629e1871859c18a6763397301396844c34217330de094453` | 6 | 6 | 6 |
| 1752 | Olympus - E-PL8 - 16bit (4:3).ORF | E-PL8 | `68400f859dea4be9a398fdc1f97613962b92d14b53d96531e2310b7dde2e674e` | 4 | 4 | 4 |
| 1754 | Olympus - E-PL1 - 16bit (4:3).ORF | E-PL1 | `d8895526c8215925468d503d1879b18c2e3e38140bffeba77351b9e55683aac9` | 6 | 6 | 6 |
| 1759 | Olympus - XZ-1 - 16bit (4:3).orf | XZ-1 | `3f5fb6f36ad4132323cab790e30b0bc10217aa7fb703518005a5800c908ba8a3` | 8 | 8 | 8 |
| 1776 | Olympus - E-PL5 - 16bit (4:3).ORF | E-PL5 | `08e90f890283f4af3c05b14c67851dd2d52c5fcaf24522634d0d9ef734213427` | 4 | 4 | 4 |
| 1787 | Olympus - E-M10 Mark III - 16bit (4:3).ORF | E-M10 Mark III | `11d90cbb564ad2c660c7a8d5d81d99c2c018aa27fdec45ed6c461fa5d24f942b` | 6 | 6 | 6 |
| 1788 | Olympus - E-PL2 - 16bit (4:3).ORF | E-PL2 | `85055c7c661f96ba1c930fdd522d0598c9bc44ea6363725e9cd48646d8782f4e` | 5 | 5 | 5 |
| 1803 | Olympus - E-3 - 16bit (4:3).ORF | E-3 | `ba4605bbd9fe9b77971da444bcdb1698904c0ad4ebdf9dd42dd45ab255f3f6d4` | 4 | 4 | 4 |
| 1805 | Olympus - E-620 - 16bit (4:3).orf | E-620 | `b3aff4240fc5b3f772c58f2b651c9d47904a575d5a22fcac49ed43374a5d779a` | 7 | 7 | 7 |
| 1993 | Olympus - E-M1MarkII - 16bit (4:3).ORF | E-M1MarkII | `0b433019e5fa61548d7eb0eb7bb90894251542c056da72355202382696d0ceb8` | 8 | 8 | 8 |
| 1994 | Olympus - E-M1MarkII - 16bit (4:3).ORF | E-M1MarkII | `f8d04ca777b3cd4d1eed4c2971d713d6ac7397bf1254929b4097c4b619f49c23` | 8 | 8 | 8 |
| 1995 | Olympus - E-M1MarkII - 16bit (4:3).ORI | E-M1MarkII | `8af918366ed969c6dddf5a48b8810fec1024858d22c75c5f1ac1a5c750a57a1f` | 5 | 5 | 5 |
| 1996 | Olympus - E-M1MarkII - 16bit (4:3).ORF | E-M1MarkII | `eeb589558062114c1f4db00c2341eac6741fb345be871a40f3428600f84a95a2` | 1 | 1 | 1 |
| 1997 | Olympus - E-M1MarkII - 16bit (4:3).ORI | E-M1MarkII | `89138ccc958509ca1beb7028452400ab7f42061c0fc56e35c8a7d7a4a808dd0a` | 5 | 5 | 5 |
| 1998 | Olympus - E-M1MarkII - 16bit (4:3).ORF | E-M1MarkII | `4bc52d99e4fbf2f09335a3301a4634bc261a98441edb824434ec069f7026cd71` | 1 | 1 | 1 |
| 2150 | Olympus - E-420 - 16bit (4:3).ORF | E-420 | `4b981b6e82357514b00183f3c676202625a61684373cc32decb361639ed2eec4` | 5 | 5 | 5 |
| 2152 | Olympus - E-5 - 16bit (4:3).ORF | E-5 | `ab0d54e3819c9372df0fa98c8686dba0ae87c9d43526a5dd6fd26bd2a664483d` | 0 | 0 | 0 |
| 2430 | Olympus - E-P2 - 16bit (4:3).ORF | E-P2 | `2666a6ed03e8678bc6ce0e5354f39a07284e6f8b200dc696d9b543dc9f82bdd5` | 6 | 6 | 6 |
| 2533 | Olympus - E-PL9 - 16bit (4:3).ORF | E-PL9 | `22525e54442f52281d007b5e8a75a2c61f768856699cf5ed697d85e055f2cc4f` | 7 | 7 | 7 |
| 2602 | OLYMPUS - STYLUS1,1s - 16bit (4:3).ORF | STYLUS1,1s | `09ffeb7d6741e877cb4102c7a379a896d6c1c178cff8844013f7960f03f1234f` | 7 | 7 | 7 |
| 2857 | Olympus - E-M5 Mark II - 16bit 16bit "normal" (4:3).ORI | E-M5MarkII | `f2c7a1dfbfcc6093b28373a1616569b8bd9c2d91cb708480b8312d510c57fbd6` | 3 | 3 | 3 |
| 2978 | Olympus - PEN-F - 16bit (4:3).orf | PEN-F | `156bf12075c4f69a3e475518f67db9d4010972d8123bdd27ae8c9177b443c374` | 8 | 8 | 8 |
| 3041 | Olympus - E-M1X - 16bit (4:3).ORF | E-M1X | `ab171cedfe3a65438dd47c2df704a7d3001f45f5ab43e67b7f96cfe30b6ebbcf` | 1 | 1 | 1 |
| 3210 | Olympus - TG-6 - 16bit (4:3).ORF | TG-6 | `edd6f928bc790c79852a17fce56718d26563c7a593894d22970ef0fdb86ba45f` | 8 | 10 | 10 |
| 3331 | Olympus - Stylus1 - 16bit (4:3).ORF | STYLUS1 | `cc2ad0341b2dcebdda8e5365e3ff96086180f24cd1ffe3401e7903b54ad54091` | 2 | 2 | 2 |
| 3573 | Olympus - E-M5 Mark III - 16bit (4:3).ORF | E-M5MarkIII | `391f2f6ba712a517212cae53bfc9a313fc4d106d0b04d3b9af68a4ed2d5d944e` | 4 | 4 | 4 |
| 3588 | OLYMPUS - E-M5 Mark III - 16bit (4:3).ORF | E-M5MarkIII | `24de6ac3bd5e668ee22fd0dbf2e344608949eb85f7342f28470ce709c9d51226` | 4 | 4 | 4 |
| 3800 | Olympus - E-M1MarkIII - 16bit (4:3).ORF | E-M1MarkIII | `1e7a256eff14df75055dd7fe7a68aabefb4d8ed475317e80ebf7ff77d5bcfd3f` | 6 | 6 | 6 |
| 3801 | Olympus - E-M1MarkIII - 16bit (4:3).ORF | E-M1MarkIII | `e9a21175493e9d9e5653aa91f1bd6fbf421aba42b59b4ffe7cd1f7cac2de385c` | 5 | 5 | 5 |
| 3802 | Olympus - E-M1MarkIII - 16bit (4:3).ORI | E-M1MarkIII | `83932e61123a90a423a81f87d08c9ed66bca5feb0d900d7d1d0924845dfa9f46` | 3 | 3 | 3 |
| 3803 | Olympus - E-M1MarkIII - 16bit (4:3).ORF | E-M1MarkIII | `4ad47518e3766fae6b98f8b18f3aae3c277e5966028e3f2e0d2702bb0f17a3cd` | 6 | 6 | 6 |
| 3804 | Olympus - E-M1MarkIII - 16bit (4:3).ORI | E-M1MarkIII | `d831692b608471ad64667eb2485bab553de0ddb9366d384c4ecb731092b5dc42` | 7 | 7 | 7 |
| 3970 | Olympus - E-PL10 - 16bit (4:3).ORF | E-PL10 | `6911f11810545cc2c55882ef6fa6aa2f25d34674865f8ade15e47990865e37ed` | 4 | 4 | 4 |
| 4126 | Olympus - E-M10 Mark IV - 16bit (4:3).ORF | E-M10MarkIV | `ce03e936cb2e8131343e7045a3249f78477bd2ae944e121ace72058b89fef509` | 5 | 5 | 5 |
| 4132 | Olympus - E-M10 Mark IV - 16bit (4:3).ORF | E-M10MarkIV | `77b67d898f85d3d738cb16daf9740c0fcf078ce9662c381994604ac540ce36b4` | 1 | 1 | 1 |
| 4927 | Olympus - E-M10 Mark IIIs - 16bit (4:3).ORF | E-M10MarkIIIS | `8bc0009eaacdbeacc72606581665702a1242bc6d4b405d1f0b3f149fe6c85e55` | 6 | 6 | 6 |
| 5099 | Olympus - E-P1 - 16bit (4:3).ORF | E-P1 | `862b9d409279af0528810aa02eb5b4140d7854f9d637d4188b82ebaf4bf0d4cf` | 6 | 6 | 6 |
| 5283 | OM System - OM-1 - 16bit (4:3).ORF | OM-1 | `bf2eef6becc0851e48231617c3e2eac27a2cdb44c75b93035c561d837952c18b` | 8 | 8 | 8 |
| 5284 | OM System - OM-1 - 16bit (4:3).ORF | OM-1 | `f0301e1b49a4ffbb366ec9800ebe9210f421fb25e75dcdf7d63e4b05bc063caf` | 2 | 2 | 2 |
| 5285 | OM System - OM-1 - 16bit (4:3).ORF | OM-1 | `862dda54644400335633578ea3a37912fbe56429f755499fdbcab9e993543874` | 1 | 1 | 1 |
| 5286 | OM System - OM-1 - 16bit (4:3).ORI | OM-1 | `2fd8bd46e2644fe28092fd921d9647007afd6d1e879c5ff19b1e3df50c578df1` | 0 | 0 | 0 |
| 5287 | OM System - OM-1 - 16bit (4:3).ORI | OM-1 | `dcbc06ba28c641197b65d931c203c5dd697fd34ae79b649a9a6d9cfc84e4bca2` | 2 | 2 | 2 |
| 5449 | Olympus - E-510 - 16bit (4:3).ORF | E-510 | `efab3d91a4f52ce65a428c15af5a54a170ef5961fb7765265c432faf19d6744c` | 2 | 2 | 2 |
| 5782 | Olympus - E-450 - 16bit (4:3).ORF | E-450 | `ce44576886d214d194896c32bdd05881f25a23053455decc3da18c46fee96fad` | 6 | 6 | 6 |
| 5915 | Olympus - E-M10 Mark II - 16bit (4:3).ORF | E-M10MarkII | `1a95224502963c892aa69ceb58767e58730f223c4b60b62119261d45eeba8bd9` | 7 | 7 | 7 |
| 5980 | Olympus - E-P7 - 16bit (4:3).ORF | E-P7 | `391b7a28d088f093a93d05c43b82bc8e9403579dea8cdc066d28af53a773d9c5` | 4 | 4 | 4 |
| 6343 | OM System - OM-5 - 16bit (4:3).ORF | OM-5 | `ee0213ee4899d677d9bd538d8cfa4d0f69bdbacd462c1cf3ca3901036cf2fce7` | 8 | 10 | 10 |
| 6344 | OM System - OM-5 - 16bit (4:3).ORF | OM-5 | `42b13fbc10627907881975fb1f617bd7afa90ef448c239ce3ad41a4b9ceca512` | 4 | 4 | 4 |
| 6345 | OM System - OM-5 - 16bit (4:3).ORI | OM-5 | `c8277d133c7ac86c7e4af5787fa06515fef8fe044c1b22209c62704537c48e02` | 0 | 0 | 0 |
| 6346 | OM System - OM-5 - 16bit (4:3).ORF | OM-5 | `ffd47d5924b65abdd8af761665d67705fe028cfd08e5efbc264b64a20830d9f4` | 7 | 7 | 7 |
| 6347 | OM System - OM-5 - 16bit (4:3).ORI | OM-5 | `062c4934ae9ab7595a45b56e2ad36a5ca05d75a8bed64f6d18cc88f9006ac9a9` | 2 | 2 | 2 |
| 6946 | OM System - TG-7 - 16bit (4:3).ORF | TG-7 | `4f7344c67bfcfcfec45f754195ba612fc2ad6312f5fab87812bf04b9e9e7d46a` | 3 | 3 | 3 |
| 7262 | OM System - OM-1 Mark II - 16bit (4:3).orf | OM-1MarkII | `d0fe58daf2f0bd749ecb18311e55408f0e7804de8e5e6580e815eae50d834cbd` | 3 | 3 | 3 |
| 7263 | OM System - OM-1 Mark II - 16bit (4:3).orf | OM-1MarkII | `780fa6a22ecd272cf3e86c04114439953b95fbc1bba8a05b4c99595a22e36bba` | 3 | 3 | 3 |
| 7264 | OM System - OM-1 Mark II - 16bit (4:3).ori | OM-1MarkII | `d7fea34029b9926e7d9cf6ecdfef9de90cbda41ff6eea009cc1a4f5b1813b8df` | 3 | 3 | 3 |
| 7265 | OM System - OM-1 Mark II - 16bit (4:3).orf | OM-1MarkII | `c7bd43b29ed89542058534b867fa894b8550d1960503cf4b4cb9f5912fd242b3` | 1 | 1 | 1 |
| 7266 | OM System - OM-1 Mark II - 16bit (4:3).ori | OM-1MarkII | `1c994e4bf5aa4e48d6ec97a1f83558184a866f71bca2b5b1bf914a159927e199` | 4 | 4 | 4 |
| 7267 | OM System - OM-1 Mark II - 16bit (4:3).orf | OM-1MarkII | `5c4845bcf87d868c1b770d7e92e574e148d82acb2806cddd9df5a7a47d7cd756` | 4 | 4 | 4 |
| 7268 | OM System - OM-1 Mark II - 16bit (4:3).ori | OM-1MarkII | `a5ee1e874d7aa357192173e12695627f90a8800a272b6c6e4959f029afb59837` | 6 | 6 | 6 |
| 7269 | OM System - OM-1 Mark II - 16bit (4:3).orf | OM-1MarkII | `dd2a6c1c4ca4d86201207925477e2ea8e50ebd53d7df9117847093f5023540ec` | 4 | 4 | 4 |
| 7270 | OM System - OM-1 Mark II - 16bit (4:3).ori | OM-1MarkII | `e4f3583f0bfb1efb0f40b201c5bb0cb1c30ace875a7f96d93fa7dddcc6966f5f` | 6 | 6 | 6 |
| 7796 | OM System - OM-3 - 16bit (4:3).ORF | OM-3 | `1cee7deb661e45101ab3ca6c4240d24ed949b167ed423703fca15c09dd8ec176` | 1 | 1 | 1 |
| 7797 | OM System - OM-3 - 16bit (4:3).ORF | OM-3 | `318e35647d93b2c598c0fec1d0d075336d2e2f5e6930faee05f32182c9a8ac5f` | 1 | 1 | 1 |
| 7798 | OM System - OM-3 - 16bit (4:3).ORI | OM-3 | `6fab41a21d5c8c0469619049888b0a36c7b260d893e3c35c174044b7293e9d43` | 2 | 2 | 2 |
| 7799 | OM System - OM-3 - 16bit (4:3).ORF | OM-3 | `9da7407d27007320c5bcf4e4d0b8c5c7bb533669cf4fabdf4e6a4b567cf318cc` | 6 | 6 | 6 |
| 7800 | OM System - OM-3 - 16bit (4:3).ORI | OM-3 | `5640fb1a2ceff83d3678f46a7acdabd9ec393d318718c9c48a9c650afe7a7c58` | 3 | 3 | 3 |
| 7801 | OM System - OM-3 - 16bit (4:3).ORF | OM-3 | `8832599870d20a96f28897e3e28d9705a4bd05871c9833c7c60a8b59d7d64b82` | 1 | 1 | 1 |
| 7802 | OM System - OM-3 - 16bit (4:3).ORI | OM-3 | `2f8c0363376fe1c4f669f1c6c881611e8a71e39320bbac3c691405583b671cf2` | 0 | 0 | 0 |
| 7803 | OM System - OM-3 - 16bit (4:3).ORF | OM-3 | `63a5b4da41fdbe8b31213ca7a11408dfd0453d893f17ac09a73471580ffbd8f0` | 6 | 6 | 6 |
| 7804 | OM System - OM-3 - 16bit (4:3).ORI | OM-3 | `bcc05bd57e78cbbb308a596f97987975f7167b17768d8c2d536c87e0c34298e0` | 6 | 6 | 6 |
| 8549 | OM System - OM-5 Mark II - 16bit (4:3).ORF | OM-5MarkII | `c6fe861982ddc18464cf6858d2700f6813cc3a17956bcb12d1179212c999c76a` | 1 | 1 | 1 |
| 8550 | OM System - OM-5 Mark II - 16bit (4:3).ORI | OM-5MarkII | `8ebb09fb177f29f88faab15a1b1498182448a4b6d65dc5a2f533d5d5b5de1be0` | 8 | 8 | 8 |
| 8552 | OM System - OM-5 Mark II - 16bit (4:3).ORF | OM-5MarkII | `4d79adadf1f736cdbd666bc5f750ee75235b365ecb5fa8dcbc6cd7ca461343ed` | 7 | 7 | 7 |
| 8553 | OM System - OM-5 Mark II - 16bit (4:3).ORF | OM-5MarkII | `6c34d583e2c98840828fa500e54e47f270f138dfc697a9a7cd084575305d3c9f` | 1 | 1 | 1 |
| 8554 | OM System - OM-5 Mark II - 16bit (4:3).ORI | OM-5MarkII | `de530604f60a7e4f867ff8bf7889fc8b49fbe3e93f660ba72d13dccabe5bc583` | 7 | 7 | 7 |
