# Header IIRO packed-12: word-reversed order smoother whole-frame on XZ-10 and SH-2; packed-16 byte order follows the TIFF mark on 3 of 3 whole-frame

Author: @radialmonster
Verified by: @radialmonster
Lead: #78
Variant: V0
Builds on: #77, #75, 2026-10-20--radialmonster--iirs-iiro-header-whole-frame-byte-order
Partial: IIRO side of the pairing whole-frame on the two CC0 IIRO packed-12 files not re-run before (XZ-10, SH-2), and the packed-16 byte order versus the TIFF byte-order mark measured by whole-frame smoothness on E-1, E-400 and E-10. Still open: a packed-12 or packed-16 file from a body not in the CC0 set, header versus strip table, and the confound with camera generation.

## Claim

On packed-12 files with header `IIRO` (one strip, no gap) the word-reversed byte order (bytes of each 4-byte word reversed) is far smoother than the plain order over the whole frame. On packed-16 files the 16-bit byte order that is smoother matches the TIFF byte-order mark (`II` little-endian, `MM` big-endian).

## Original evidence

Lead #78 (@radialmonster, 2026-10-18): 9 CC0 packed-12 files (6 `IIRS`, 3 `IIRO`) and 3 CC0 packed-16 files, via `tools/layout_probe.py` and the decoder. The earlier partial finding re-ran 7 of the 9 packed-12 files whole-frame (XZ-10 and SH-2 not available then) and did not test packed-16.

## Verification

New run on 2026-10-21 UTC by @radialmonster, at repo commit 6ad67a6, with a new script (listing below; stdlib plus `tools/orf_signature.py` for TIFF parsing; `decoder/` not used). Files downloaded with `tools/pixls_samples.py download` (CC0, SHA-256 verified). Roughness is sum |v[x]-v[x+2]| over all `height` rows divided by the mean level, for each candidate byte order. This is a wider run (whole frame) than the lead; it is not a new body, since the lead already used every one of these files.

IIRO packed-12 (single strip, no gap):
- XZ-10, 3984x2990 (raw.pixls.us id 2431, sha256 a25383acad9b...): plain 0.590, reversed 0.025
- SH-2, 4624x3470 (id 792, sha256 6e6b9b7dd9de...): plain 0.806, reversed 0.058

packed-16 (roughness of little-endian versus big-endian 16-bit words):
- E-1, 2624x1966 (id 1800, 16 strips, TIFF mark `II`): LE 0.062, BE 0.707, smoother LE
- E-400, 3768x2840 (id 2151, 89 strips, mark `II`): LE 0.039, BE 0.704, smoother LE
- E-10, 2256x1684 (id 5424, 15 strips, mark `MM`): LE 0.831, BE 0.044, smoother BE

So the two remaining CC0 IIRO packed-12 files fit the rule (together with the earlier XZ-2 re-run, 3 of 3 CC0 IIRO packed-12 whole-frame), and the packed-16 smoother order agrees with the TIFF mark 3 of 3 (all `IIRO` or `MMOR` headers, 1 big-endian file only). XZ-1 (id 1759, `16bit` in its name) is size class "variable", not packed-16, and is not counted. No new body was available, so the confounds with camera generation and body stand, and nothing here separates the header from the strip table or the TIFF mark from the file header (`MMOR` carries both).

## Reproduce

    python -I hdr_whole2.py PATH_TO_REPO/tools FILE [FILE ...]

where `hdr_whole2.py`:

    import sys
    sys.path.insert(0, sys.argv[1])
    import orf_signature as S
    def unpack12(b, w):
        o = []
        for i in range(0, len(b) - 2, 3):
            o.append(b[i] << 4 | b[i+1] >> 4); o.append((b[i+1] & 15) << 8 | b[i+2])
        return o[:w]
    def unpack16(b, w, big):
        return [(b[i] << 8 | b[i+1]) if big else (b[i+1] << 8 | b[i]) for i in range(0, w * 2, 2)]
    def rev4(b):
        b = bytearray(b)
        for i in range(0, len(b) // 4 * 4, 4): b[i:i+4] = b[i:i+4][::-1]
        return bytes(b)
    def rough(rows):
        s = t = 0
        for r in rows:
            for x in range(len(r) - 2):
                s += abs(r[x] - r[x+2]); t += r[x] + r[x+2]
        return s / (t / 2) if t else 0
    for p in sys.argv[2:]:
        data = open(p, 'rb').read(); t = S.Tiff(data)
        best = max(t.all_ifds(), key=lambda d: sum(d.get(0x117) or [0]))
        sig = S.signature(p)
        offs, cnts = best.get(0x111) or [], best.get(0x117) or []
        gaps = [g for g in (offs[i+1]-offs[i]-cnts[i] for i in range(len(offs)-1)) if g]
        L = [sig['sha256'][:12], data[:4].decode('latin1'), sig['size_class'], 'strips=%d' % len(offs), 'gaps=%s' % gaps[:3]]
        w, h = sig['payload_w'], sig['payload_h']
        pay = b''.join(data[o:o+c] for o, c in zip(offs, cnts))
        if sig['size_class'] == 'packed-12':
            rb = w * 3 // 2
            rows = [pay[y*rb:(y+1)*rb] for y in range(h)]
            L += ['plain=%.3f' % rough([unpack12(r, w) for r in rows]), 'rev=%.3f' % rough([unpack12(rev4(r), w) for r in rows])]
        elif sig['size_class'] == 'packed-16':
            rb = w * 2
            rows = [pay[y*rb:(y+1)*rb] for y in range(h)]
            L += ['LE=%.3f' % rough([unpack16(r, w, False) for r in rows]), 'BE=%.3f' % rough([unpack16(r, w, True) for r in rows])]
        print(*L)

Files: CC0 raw.pixls.us ids 2431, 792, 1800, 2151, 5424 (run `pixls_samples.py check` on each first). The TIFF mark is the first two bytes of the file.
