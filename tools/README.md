# tools

Analysis scripts, all original code (see RULES.md).

Each script should:
- take raw.pixls.us file paths as arguments and not download anything itself (`pixls_samples.py` is the one exception);
- print or write aggregate statistics only, with no images or pixel dumps;
- run on CPU, with GPU acceleration optional;
- state at the top which finding (an ID from `findings/`), lead issue (`#n`) or OPEN-QUESTIONS item it supports.

## Example tools

**`pixls_samples.py`** lists, checks and downloads raw.pixls.us Olympus/OM samples using the site's licence listing. It downloads CC0 files only and verifies SHA-256. See the top-level README.

**`manifest_rows.py`** turns local CC0 files into ready-made `samples/manifest.csv` rows, combining the licence listing with `orf_signature.py`.

**`orf_signature.py`** prints one CSV row per file with its measured container and payload facts: SHA-256, magic, make, model, payload size, bits per sample, compression tag, payload offset and bytes, and bits per pixel. It reads the TIFF structure only and decodes nothing.

    python tools/orf_signature.py path/to/* > rows.csv

**`bit_runs.py`** gives a histogram of zero-bit runs in the payload (MSB-first), as aggregate numbers. It's a starting point for bitstream work (the F1 lead, #11).

    python tools/bit_runs.py path/to/file.ORF --mb 1

Example output on raw.pixls.us `8549_OM System - OM-5 Mark II - 16bit (4_3).ORF` (CC0), first 1 MB:

    q= 0  share=0.48036
    q= 1  share=0.27349
    q= 2  share=0.13019
    q= 3  share=0.06272

**`orf_tokens.py`** parses the token stream described in lead #11 (q zero bits, stop bit, 5-bit suffix; escape at q >= 17) and prints aggregate statistics per file: tokens against width x height, bit alignment at multiples of the width, q histogram and escapes, suffix bit balance, H/L shares, and mutual information at token lags 1-3 (H->L, L->H, L->L, H->H), the b2 context gain and vertical lag 2, each with a baseline that shows the estimator bias. Numbers are printed as measured, whether or not they match that lead. It parses a prefix by default (`--max-tokens`, `--rows`); `--all` parses the whole payload.

    python tools/orf_tokens.py path/to/file.ORF --rows 400
    python tools/orf_tokens.py path/to/file.ORF --all

**`findings_index.py`** lists the verified findings under `findings/` by variant, with finder, verifier, title and status (verified or superseded). `--check` validates the files (file name, `Author:` matches the handle, `Verified by:` is another person, `Lead:` is `#n`, `Variant:` matches the folder, referenced IDs exist) and exits 1 on errors; CI runs it on pull requests.

    python tools/findings_index.py
    python tools/findings_index.py --check

All of them use the standard library only (Python 3.8+). Contributions of new tools are welcome. Follow the rules above and RULES.md.

**`v0_spec_check.py`** is an independent, aggregate-only implementation of
`specs/V0.md` at `bf56d39`, supporting lead #75. Original payload logic and
synthetic tests were written without target files, reference code, or output
hashes. Shared container code is limited to `orf_signature.Tiff` header/endian
and integer reads; an original wrapper validates relevant IFD descriptors.

    python -I tools/v0_spec_check.py --help
    python -I tools/v0_spec_check.py --self-test
    python -I tools/test_v0_spec_check.py
    python -I tools/v0_spec_check.py --measured-by @yourhandle --sample ID PUBLIC_NAME path/to/file.ORF

Repeat `--sample` for multiple files. IDs are distinct positive decimals; public
names may repeat. Match records by input SHA-256, never basename. Check CC0
licensing before supplying downloaded files. Each JSONL result includes public
identity, input/output hashes, measured signature, aggregates, selectors, source
hashes and pinned spec metadata. Failures emit sanitized categories, preserve
other results and return a nonzero exit code. No decoded data is written.

Selectors are **unverified spec generalizations**: packed-12 `IIRS` is plain,
`IIRO` reverses global four-byte words; no strip gaps means natural rows; one
packed-12 gap at the even-field boundary means two fields; packed-16 uses TIFF
byte order. Unsupported cases fail without trying alternatives. First/second
unit order is a convention, not physical pixel-order proof. The S4.3/S6 wording
ambiguity is resolved by preserving packed-16 stored words with **no numeric
shift**, including low nibbles. Above-4095 and nonzero-low-nibble counts are
separate measurements. Hashing uses explicit uint16 little-endian image rows.

Read-only mmap, individual strip reads, strict integer size classification and
row streaming are bounded by 8 GiB per file, 100,000 per dimension, 250,000,000
pixels, 4,096 IFDs and 1,000,000 strips. Malformed relevant fields, tied largest
IFDs, repeated pointers, overlaps, nonascending strips and unsupported gaps are
rejected. Report mismatches under these frozen assumptions; do not tune them to
expected hashes.

Input opening requires `os.O_NONBLOCK`: the acquired descriptor is checked with
`fstat` before any mmap/read, so a FIFO without a writer is rejected promptly and
later inputs still run. Descriptors close on success and failure. Platforms
without that flag fail explicitly per sample with `nonblocking_open_unavailable`;
regular-file decoding therefore requires nonblocking descriptor-open support.
This restriction is included in provenance and help. There is no path-check/open
fallback with a race. Symlinks to regular files remain usable. `--help` and
`--self-test` remain portable; FIFO and regular-file measurement tests skip when
the required platform facilities are absent, while the fail-closed mock still runs.
