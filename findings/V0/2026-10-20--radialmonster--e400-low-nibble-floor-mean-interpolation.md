# E-400 low-nibble words are floor-mean interpolated pixels

Author: @radialmonster
Verified by: @radialmonster
Lead: #79
Variant: V0
Builds on: #75, #71
Partial: the floor-mean rule and its family counts on the one E-400 file (791 of 792 interior); the lead's parity table is corrected below, and its Next steps are not tested

## Claim
On the E-400 packed-16 file, 793 words have a non-zero low nibble. For 791 of the 792 interior ones, the stored word equals floor(mean of the stored words of the 4 nearest same-colour neighbours): the axial neighbours two pixels away (up, down, left, right) at 386 words, the diagonal neighbours one pixel away at 405 words. The low nibble of such a word is 4, 8 or 12 (quarters of a 12-bit step) in 791 words. Decoded words are therefore left unshifted. Correction to the lead's parity table: the diagonal-1 family sits at both parities (0,0) and (1,1) (218 and 187), not only at (0,0). Axial-2 sits at (0,1) 183 and (1,0) 203.

## Original evidence
Lead #79: `tools/e400_probe.py` at 683842a; file raw.pixls.us 2151 E-400, SHA-256 1354e0ac98ea90820227650031d8215637a2aaabd15de995c5a1e00b1986261b (CC0). Counts as in the claim.

## Verification
New run on 2026-10-20, with a second script written for this check (inline below), not `e400_probe.py`; it reads the payload rows through `decoder/orf_decode.py` and does its own neighbour test over the whole frame.
- Same file (the only CC0 file with such words: of the three CC0 packed-16 bodies, E-1 has 0 non-zero-nibble words, the lead reports 0 for E-10 and I did not re-measure that). The lead already used every CC0 file of this model, so this is a wider run on the same file: both families tested on every non-zero-nibble word, separately by position parity.
- 793 words with non-zero low nibble. Of 792 interior: axial-2 floor-mean match 386 (parity (0,1) 183, (1,0) 203), diagonal-1 floor-mean match 405 (parity (0,0) 218, (1,1) 187), neither 1. Total 791 of 792. `tools/e400_probe.py` reproduces its own counts (386, 5, 5, 5, 3; controls 2 to 13 of 793) at 683842a.
- The lead's parity table prints (1,1) as 0 diag-1 plus 1 unmatched, but its rows sum to 605 of 792; the 187 missing words are the diagonal-1 matches at (1,1). So green sites are (0,0) and (1,1), as a Bayer pattern predicts, and the lead's open question "why no mapped words at parity (1,1)" is moot: there are 188 (187 matched, 1 not).
- Low nibble equals 4 * ((sum of the four neighbour words >> 4) mod 4) in 790 of the 791 matched words; the exception is the nibble-15 word below. Nibble values outside {4, 8, 12}: (y 1, x 778) nibble 10, on the top edge, and (y 2586, x 3680) nibble 15, interior.
- The single interior exception (y 2585, x 3681, word 17964) has neighbour words axial-2 [15536, 15456, 16192, 16512] and diagonal-1 [15888, 15200, 16335, 16336]; neither mean is near it. Its diagonal neighbour (2586, 3680) is the nibble-15 word. This looks like a different mechanism and stays open.

## Reproduce
`python -I tools/e400_probe.py "<2151 E-400 file>"` for the lead's counts, and for the whole-frame, per-parity test:

    import sys; sys.path.insert(0,'decoder'); import orf_decode as od, collections
    path=sys.argv[1]; p=od.Payload(path); w,h=p.sig['payload_w'],p.sig['payload_h']; rb=od.row_bytes('packed-16',w)
    with open(path,'rb') as f: img=[od.unpack_row('packed-16','le',p.read(f,y*rb,rb),w)[0] for y in range(h)]
    bad=[(y,x) for y in range(h) for x,v in enumerate(img[y]) if v&15]
    A=[(-2,0),(2,0),(0,-2),(0,2)]; D=[(-1,-1),(-1,1),(1,-1),(1,1)]
    c=collections.Counter()
    for y,x in bad:
        if y<2 or x<2 or y>=h-2 or x>=w-2: continue
        f=lambda N: sum(img[y+a][x+b] for a,b in N)//4==img[y][x]
        c[(y&1,x&1,'A' if f(A) else '','D' if f(D) else '')]+=1
    print(len(bad), sorted(c.items()))

Run from the repo root with `python -I` on the file; expected `793` and counts (0,0,D) 218, (0,1,A) 183, (1,0,A) 203, (1,1,D) 187, (1,1,none) 1.
