# packed-12.8: 16-byte groups of ten 12-bit values (five 3-byte units, LSB first) plus one pad byte

Author: @radialmonster
Verified by: @radialmonster
Lead: #70
Variant: V0
Builds on: #28

## Claim

The 5 CC0 `packed-12.8` files (E-300, E-330, E-500, and the high-resolution E-M5 Mark II and PEN-F files) store every row as a run of 16-byte groups holding 10 pixels. Bytes 0 to 14 of a group are five 3-byte units, each carrying two 12-bit values least-significant bit first (first value = byte0 | (byte1 & 15) << 8, second = byte1 >> 4 | byte2 << 4); byte 15 is padding and is zero in every group of the whole payload on all 5 files. Rows are contiguous, stride = width x 1.6 bytes. The order of the two pixels inside a unit is not decided by these statistics.

## Original evidence

Lead #70 (opened by @radialmonster, 2026-10-19), from `tools/orf_v0_unpack.py` (last changed in `0785fcb`) on 5 files with the default window (3 bands of 16 rows, first 1200 columns): raw.pixls.us 2856 E-M5MarkII high-res (5c42fa75...), 2878 E-300 (6d818dbf...), 2977 PEN-F (f87a5f32...), 3540 E-500 (fa5a4759...), 3624 E-330 (ba11eb97...).

## Verification

New run on 2026-10-20 UTC by @radialmonster, after the lead was posted, on repository commit `a4bf2af` (`tools/orf_v0_unpack.py` last changed in `1b6c2fc`), Python 3.13. The lead already used every CC0 file with `size_class` `packed-12.8` (the other CC0 PEN-F file, 2978, is `variable`, and the E-M5 Mark II "normal" file is not a payload of this class), so no unused CC0 file exists. This is a wider run on the same files, in two parts. All 5 SHA-256 prefixes matched the lead and `pixls_samples.py check` reported every file CC0.

1. Wider window: 8 bands of 32 rows and 3200 columns (about 7 times the lead's 3 x 16 x 1200 window). The chosen layout is `group16-lsb-pad15` on 5 of 5 files, margin (best score of the next layout family divided by the winner's) and row-stride correlation at the true stride, with 1 byte off in brackets and 16 bytes (one group) off after the slash:
- E-M5 Mark II high-res: margin 4.03, 0.947 (-0.012 / -0.006), 16 off 0.750 / 0.736
- E-300: margin 4.87, 0.960 (-0.038 / -0.018), 16 off 0.815 / 0.810
- PEN-F: margin 5.06, 0.991 (-0.023 / -0.002), 16 off 0.848 / 0.836
- E-500: margin 4.76, 0.977 (-0.066 / -0.026), 16 off 0.861 / 0.865
- E-330: margin 3.20, 0.970 (0.055 / 0.062), 16 off 0.668 / 0.672
Margins are 3.2 to 5.1 (lead: 3.4 to 5.6). The pair order inside a unit is again undecided: the tool reports a tie within 2% with the swapped order on E-M5 Mark II, PEN-F and E-500 (h1 gap 0.0 to 0.9%) and lists the swap as an alternative on E-300 and E-330 (h1 gap 1.5%, 1.5%).

2. Whole payload, the lead's first next step: payload bytes equal width x height x 1.6 exactly on all 5 files (102926336, 13461504, 129725440, 13461504, 12857600 bytes), so the payload is a whole number of 16-byte groups with no tail (6432896, 841344, 8107840, 841344, 803600 groups). Byte 15 of every group is 0 in all of them (0 non-zero pad bytes out of 6432896, 841344, 8107840, 841344 and 803600).

This reproduces the claim; the first part is the same tool on the same files with a larger sample of each frame, so it checks repeatability, not an independent implementation. No pixel values or images were written or compared with another decoder.

## Reproduce

Keep the files outside the repository (here `../orf-samples-pk`). From the repository root:

    python tools/pixls_samples.py download --model E-300 ../orf-samples-pk
    (same for E-330, E-500, PEN-F, E-M5MarkII)
    python tools/pixls_samples.py check FILE [FILE ...]
    python tools/orf_v0_unpack.py --bands 8 --rows 32 --cols 3200 FILE [FILE ...]

Read the `chosen:` line and the `row-stride test` line of each file. Pad-byte check over the whole payload (inline):

    python -I -c "import sys; sys.path.insert(0,'tools'); import orf_signature as s
    for p in sys.argv[1:]:
        g=s.signature(p); o=int(g['payload_offset']); n=int(g['payload_bytes'])
        d=open(p,'rb').read()[o:o+n]; pads=d[15:n//16*16:16]
        print(g['sha256'][:12], n, n%16, len(pads), sum(1 for b in pads if b))" FILE [FILE ...]

where FILE are raw.pixls.us ids 2856, 2878, 2977, 3540, 3624; the last three columns are bytes left after whole groups, number of groups, and non-zero pad bytes.
