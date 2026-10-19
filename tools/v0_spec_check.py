#!/usr/bin/env python3
"""Blind, aggregate-only V0 checker supporting lead #75 and specs/V0.md.

Original payload implementation from spec bf56d39; no reference decoder/oracle.
The shared Tiff class supplies only header/endian and integer-reading primitives.
S1.3/S1.4, S2.5 and S4.2 candidate selectors are unverified generalizations.
S3/S4 remain leads. S2.4 first/second order is a convention, not physical proof.
S4.3 preserves stored 16-bit words; S6 'unshifted' means no numeric shift here.
Regular-file measurement requires os.O_NONBLOCK; missing support yields
nonblocking_open_unavailable per sample. --help/--self-test remain usable.
"""
import argparse
import bisect
import hashlib
import importlib.util
import json
import mmap
import os
import re
import stat
import struct
import sys
from pathlib import Path

SPEC_REVISION = "bf56d39"
SPEC_SHA256 = "7a49a9bf1c26d9d613f29cd8d631da2e226c670ccdb7bedb635e3a02f25da46b"
MAX_FILE_BYTES = 8 * 1024 ** 3
MAX_DIMENSION = 100000
MAX_PIXELS = 250000000
MAX_IFDS = 4096
MAX_STRIPS = 1000000
WIDTH, HEIGHT, BITS, COMPRESSION = 256, 257, 258, 259
OFFSETS, COUNTS, SUBIFDS = 273, 279, 330
RELEVANT = {WIDTH, HEIGHT, BITS, COMPRESSION, OFFSETS, COUNTS, SUBIFDS}
SELECTORS = {
    "status": "unverified spec generalizations; fixed before target runs",
    "payload_ifd": "largest positive strip-byte total; ties rejected (S1.3)",
    "packed12_bytes": "IIRS plain; IIRO reverse global four-byte words (S2.5)",
    "rows": "no gaps natural; one packed-12 field-boundary gap two-fields (S1.4)",
    "packed16_endian": "TIFF byte-order mark, no smoothness override (S4.2/G2)",
    "unit_order": "first then second; physical pixel order unproven (S2.4/G4)",
    "packed16_output": "stored words preserved; S6 unshifted interpreted as no numeric shift (S4.3)",
    "shared_container": "orf_signature.Tiff header/endian/u16/u32 only; strict original descriptor wrapper",
    "payload_source": "original code from pinned spec; no decoder or oracle used",
}
INPUT_OPEN_CONTRACT = ("regular-file measurement requires os.O_NONBLOCK; validate the exact "
                       "descriptor with fstat before mmap/read; missing support returns "
                       "nonblocking_open_unavailable per sample without opening it")
LIMITS = {"file_bytes": MAX_FILE_BYTES, "dimension": MAX_DIMENSION,
          "pixels": MAX_PIXELS, "ifds": MAX_IFDS, "strips": MAX_STRIPS}


class CheckError(Exception):
    """Only fixed public categories reach output; never exception text/paths."""

    def __init__(self, category):
        super().__init__(category)
        self.category = category


def require(condition, category):
    if not condition:
        raise CheckError(category)


def load_tiff():
    # Deferred loading keeps imports/--help free of container and sample access.
    source = Path(__file__).resolve().with_name("orf_signature.py")
    spec = importlib.util.spec_from_file_location("_v0_shared_tiff", str(source))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Tiff


def hash_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                return digest.hexdigest()
            digest.update(block)


def provenance():
    source = Path(__file__).resolve()
    return {"spec_revision": SPEC_REVISION, "spec_sha256": SPEC_SHA256,
            "tool_sha256": hash_file(source),
            "tests_sha256": hash_file(source.with_name("test_v0_spec_check.py")),
            "shared_container_sha256": hash_file(source.with_name("orf_signature.py")),
            "selectors": dict(SELECTORS), "limits": dict(LIMITS),
            "input_open_contract": INPUT_OPEN_CONTRACT}


def read_ifd(data, tiff, offset):
    """Validate descriptors before integer access; never parse irrelevant strings.

    Unlike the permissive shared Tiff.ifd, this wrapper rejects malformed relevant
    fields and never allocates from an unchecked count. Header and integer reads
    still use the shared TIFF primitives (public TIFF structure, S1.3).
    """
    size = len(data)
    require(8 <= offset <= size - 2, "malformed_ifd_bounds")
    entries = tiff.u16(offset)
    end = offset + 2 + entries * 12
    require(end + 4 <= size, "malformed_ifd_table")
    tags = {}
    for index in range(entries):
        pos = offset + 2 + index * 12
        tag, typ = tiff.u16(pos), tiff.u16(pos + 2)
        if tag not in RELEVANT:
            continue
        require(tag not in tags, "duplicate_relevant_tag")
        count = tiff.u32(pos + 4)
        if tag == SUBIFDS:
            require(typ in (4, 13), "invalid_field_type")
            bound = MAX_IFDS
        else:
            require(typ in (3, 4), "invalid_field_type")
            bound = MAX_STRIPS if tag in (OFFSETS, COUNTS, BITS) else 1
        require(count > 0, "empty_relevant_field")
        require(count <= bound, "field_count_limit")
        if tag in (WIDTH, HEIGHT, COMPRESSION):
            require(count == 1, "non_scalar_field")
        unit = 2 if typ == 3 else 4
        nbytes = count * unit
        value_pos = pos + 8 if nbytes <= 4 else tiff.u32(pos + 8)
        require(value_pos <= size and nbytes <= size - value_pos,
                "malformed_field_bounds")
        read = tiff.u16 if typ == 3 else tiff.u32
        tags[tag] = [read(value_pos + unit * i) for i in range(count)]
    return tags, tiff.u32(end)


def container(data, tiff_class=None):
    require(len(data) >= 8, "truncated_header")
    require(len(data) <= MAX_FILE_BYTES, "file_size_limit")
    require(data[:2] in (b"II", b"MM"), "invalid_byte_order")
    if tiff_class is None:
        tiff_class = load_tiff()
    try:
        tiff = tiff_class(data)
    except (ValueError, struct.error):
        raise CheckError("invalid_orf_magic") from None
    require(tiff.magic in (0x4F52, 0x5352), "unsupported_tiff_magic")
    pending = [tiff.u32(4)]
    seen = set()
    best = None
    best_total = 0
    tied = False
    while pending:
        offset = pending.pop()
        if offset == 0:
            continue
        require(offset not in seen, "repeated_ifd_offset")
        require(len(seen) < MAX_IFDS, "ifd_limit")
        seen.add(offset)
        tags, following = read_ifd(data, tiff, offset)
        # Bound the traversal queue too, even before its pointers are visited.
        additions = ([following] if following else []) + [v for v in tags.get(SUBIFDS, []) if v]
        require(len(pending) + len(additions) + len(seen) <= MAX_IFDS,
                "ifd_limit")
        pending.extend(additions)
        total = sum(tags.get(COUNTS, []))
        if total > best_total:
            best, best_total, tied = tags, total, False
        elif total and total == best_total:
            tied = True
    require(best is not None, "missing_positive_payload")
    require(not tied, "ambiguous_payload_ifd")
    require(all(tag in best for tag in (WIDTH, HEIGHT, OFFSETS, COUNTS)),
            "missing_payload_fields")
    width, height = best[WIDTH][0], best[HEIGHT][0]
    require(width > 0 and height > 0, "zero_dimensions")
    require(width <= MAX_DIMENSION and height <= MAX_DIMENSION, "dimension_limit")
    pixels = width * height
    require(pixels <= MAX_PIXELS, "pixel_limit")
    offsets, counts = best[OFFSETS], best[COUNTS]
    require(len(offsets) == len(counts), "mismatched_strip_arrays")
    require(0 < len(offsets) <= MAX_STRIPS, "strip_count_limit")
    gaps = []
    total = 0
    previous_end = None
    for start, count in zip(offsets, counts):
        require(count > 0, "zero_strip_size")
        require(start <= len(data) and count <= len(data) - start,
                "strip_out_of_bounds")
        if previous_end is not None:
            require(start >= previous_end, "unsupported_strip_order_or_overlap")
            if start > previous_end:
                gaps.append(total)
        total += count
        previous_end = start + count
    packing = classify(total, pixels)
    if packing == "packed-12":
        require(width % 2 == 0, "unsupported_packed12_width")
        row_bytes = width * 3 // 2
        header = bytes(data[:4])
        require(header in (b"IIRS", b"IIRO"), "unsupported_packed12_header")
        reverse = header == b"IIRO"
        require(not reverse or total % 4 == 0, "partial_reversed_word")
        byte_order = "reverse-four-byte-words" if reverse else "plain"
    elif packing == "packed-12.8":
        require(width % 10 == 0, "unsupported_packed128_width")
        row_bytes = width // 10 * 16
        reverse, byte_order = False, "LSB-first-units"
    else:
        row_bytes = width * 2
        reverse = False
        byte_order = "little" if tiff.e == "<" else "big"
    require(total == row_bytes * height, "row_payload_mismatch")
    if not gaps:
        layout = "natural"
    else:
        require(packing == "packed-12" and len(gaps) == 1 and
                gaps[0] == ((height + 1) // 2) * row_bytes,
                "unsupported_strip_gaps")
        layout = "two-fields"
    return {"width": width, "height": height, "payload_bytes": total,
            "packing": packing, "row_bytes": row_bytes, "layout": layout,
            "byte_order": byte_order, "reverse": reverse,
            "offsets": offsets, "counts": counts, "strip_count": len(counts),
            "gap_count": len(gaps), "ifd_count": len(seen),
            "bits_per_sample": best.get(BITS), "compression_tag": best.get(COMPRESSION),
            "header_hex": bytes(data[:4]).hex(),
            "tiff_byte_order": "little" if tiff.e == "<" else "big"}


def classify(nbytes, pixels):
    # S1.2 / F-fixed: exact integer equations, never rounded bpp or Compression.
    if 2 * nbytes == 3 * pixels:
        return "packed-12"
    if 5 * nbytes == 8 * pixels:
        return "packed-12.8"
    if nbytes == 2 * pixels:
        return "packed-16"
    raise CheckError("unsupported_variable_payload")


class StripReader:
    """Logical concatenation; never reads physical gaps or sorts strips."""

    def __init__(self, data, offsets, counts):
        require(len(offsets) == len(counts) and bool(counts), "mismatched_strip_arrays")
        self.data, self.offsets = data, offsets
        self.ends = []
        total = 0
        previous_end = None
        for start, count in zip(offsets, counts):
            require(start >= 0 and count > 0 and start + count <= len(data),
                    "strip_out_of_bounds")
            require(previous_end is None or start >= previous_end,
                    "unsupported_strip_order_or_overlap")
            total += count
            self.ends.append(total)
            previous_end = start + count
        self.total = total

    def plain(self, start, size):
        require(start >= 0 and size >= 0 and start + size <= self.total,
                "logical_read_bounds")
        if size == 0:
            return b""
        index = bisect.bisect_right(self.ends, start)
        result = bytearray()
        while size:
            logical_base = self.ends[index - 1] if index else 0
            take = min(size, self.ends[index] - start)
            physical = self.offsets[index] + start - logical_base
            chunk = self.data[physical:physical + take]
            require(len(chunk) == take, "short_strip_read")
            result.extend(chunk)
            size -= take
            start += take
            index += 1
        return bytes(result)

    def read(self, start, size, reverse=False):
        require(start >= 0 and size >= 0 and start + size <= self.total,
                "logical_read_bounds")
        if not reverse:
            return self.plain(start, size)
        require(self.total % 4 == 0, "partial_reversed_word")
        if size == 0:
            return b""
        first, end = start // 4 * 4, (start + size + 3) // 4 * 4
        source = self.plain(first, end - first)
        words = bytearray(len(source))
        for pos in range(0, len(source), 4):
            words[pos:pos + 4] = source[pos:pos + 4][::-1]
        return bytes(words[start - first:start - first + size])


def stored_row(image_y, height, layout):
    require(0 <= image_y < height, "row_index_bounds")
    if layout == "natural":
        return image_y
    require(layout == "two-fields", "unsupported_row_layout")
    return image_y // 2 + (((height + 1) // 2) if image_y % 2 else 0)


def decode_row(raw, width, packing, byte_order):
    """S2.1 (finding), S3.1 and S4.3 (leads); one row, explicit ordering."""
    values = []
    pad_total = pad_nonzero = 0
    if packing == "packed-12":
        require(width % 2 == 0 and len(raw) == width * 3 // 2,
                "row_length_mismatch")
        for pos in range(0, len(raw), 3):
            a, b, c = raw[pos:pos + 3]
            values.extend(((a << 4) | (b >> 4), ((b & 15) << 8) | c))
    elif packing == "packed-12.8":
        require(width % 10 == 0 and len(raw) == width // 10 * 16,
                "row_length_mismatch")
        for group in range(0, len(raw), 16):
            for pos in range(group, group + 15, 3):
                a, b, c = raw[pos:pos + 3]
                values.extend((a | ((b & 15) << 8), (b >> 4) | (c << 4)))
            pad_total += 1
            pad_nonzero += int(raw[group + 15] != 0)
    elif packing == "packed-16":
        require(byte_order in ("little", "big"), "unsupported_word_endian")
        require(len(raw) == width * 2, "row_length_mismatch")
        for pos in range(0, len(raw), 2):
            values.append(int.from_bytes(raw[pos:pos + 2], byte_order))
    else:
        raise CheckError("unsupported_packing")
    require(len(values) == width, "row_value_count_mismatch")
    return values, pad_total, pad_nonzero


def measure(data, tiff_class=None):
    info = container(data, tiff_class)
    reader = StripReader(data, info["offsets"], info["counts"])
    digest = hashlib.sha256()
    count = total = above = low = padding = nonzero = consumed = 0
    minimum, maximum = 65535, 0
    for y in range(info["height"]):
        index = stored_row(y, info["height"], info["layout"])
        raw = reader.read(index * info["row_bytes"], info["row_bytes"], info["reverse"])
        values, pads, nonzero_pads = decode_row(raw, info["width"], info["packing"], info["byte_order"])
        canonical = bytearray(len(values) * 2)
        for x, value in enumerate(values):
            # Explicit LE serialization, independent of native host byte order.
            canonical[2 * x] = value & 255
            canonical[2 * x + 1] = value >> 8
            minimum, maximum = min(minimum, value), max(maximum, value)
            total += value
            above += int(value > 4095)
            low += int((value & 15) != 0)
        digest.update(canonical)
        count += len(values)
        consumed += len(raw)
        padding += pads
        nonzero += nonzero_pads
    require(count == info["width"] * info["height"] and consumed == reader.total,
            "inexact_payload_end")
    result = {key: value for key, value in info.items()
              if key not in ("offsets", "counts", "reverse", "row_bytes")}
    result.update({"exact_end": True, "payload_bytes_consumed": consumed,
                   "output_count": count, "output_min": minimum, "output_max": maximum,
                   "output_sum": total, "above4095_count": above,
                   "nonzero_low_nibble_count": low, "padding_count": padding,
                   "nonzero_padding_count": nonzero, "output_sha256": digest.hexdigest()})
    return result


def measure_path(path):
    # Opening a FIFO in buffered read mode can block before fstat. Acquire a
    # nonblocking descriptor, validate that exact object, and close on all paths.
    # Fail closed without O_NONBLOCK rather than race a path stat against open.
    require(hasattr(os, "O_NONBLOCK"), "nonblocking_open_unavailable")
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_BINARY", 0) | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        require(stat.S_ISREG(before.st_mode), "unsupported_file_type")
        require(before.st_size <= MAX_FILE_BYTES, "file_size_limit")
        require(before.st_size >= 8, "truncated_header")
        with mmap.mmap(descriptor, 0, access=mmap.ACCESS_READ) as data:
            result = measure(data)
            # Independent input pass; no payload-derived hash reuse.
            digest = hashlib.sha256()
            while True:
                block = os.read(descriptor, 1024 * 1024)
                if not block:
                    break
                digest.update(block)
            after = os.fstat(descriptor)
            require((before.st_size, before.st_mtime_ns, before.st_ctime_ns) ==
                    (after.st_size, after.st_mtime_ns, after.st_ctime_ns),
                    "input_changed_during_measurement")
            result["input_sha256"] = digest.hexdigest()
            return result
    finally:
        os.close(descriptor)


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse normally echoes unknown arguments; those may contain paths.
        self.exit(2, "invalid command line; use --help\n")


def valid_identity(sample_id, name):
    return (re.fullmatch(r"[1-9][0-9]{0,11}", sample_id) is not None and
            1 <= len(name) <= 512 and name not in (".", "..") and
            all(ord(c) >= 32 and ord(c) != 127 for c in name) and
            "/" not in name and "\\" not in name)


def main(argv=None):
    parser = SafeParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run independent synthetic tests only")
    parser.add_argument("--measured-by", metavar="HANDLE")
    parser.add_argument("--sample", action="append", nargs=3, metavar=("ID", "PUBLIC_NAME", "FILE"))
    args = parser.parse_args(argv)
    if args.self_test:
        if args.sample or args.measured_by:
            parser.error("self-test cannot take samples")
        spec = importlib.util.spec_from_file_location("_v0_spec_tests", str(Path(__file__).resolve().with_name("test_v0_spec_check.py")))
        tests = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tests)
        return 0 if tests.run_tests().wasSuccessful() else 1
    if not args.sample or not args.measured_by or re.fullmatch(r"@?[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", args.measured_by) is None:
        parser.error("sample and valid handle required")
    # Invalid identities cannot safely be reflected in error output.
    if any(not valid_identity(sid, name) for sid, name, path in args.sample):
        parser.error("invalid public identity")
    if len({sid for sid, name, path in args.sample}) != len(args.sample):
        parser.error("duplicate public ID")
    try:
        source = provenance()
    except OSError:
        for sample_id, name, path in args.sample:
            print(json.dumps({"sample_id": sample_id, "public_name": name,
                              "measured_by": args.measured_by, "status": "error",
                              "category": "provenance_unavailable",
                              "selectors": SELECTORS,
                              "input_open_contract": INPUT_OPEN_CONTRACT}, sort_keys=True))
        return 1
    failed = False
    for sample_id, name, path in args.sample:
        row = {"sample_id": sample_id, "public_name": name,
               "measured_by": args.measured_by, "provenance": source}
        try:
            row.update(measure_path(path))
            row["status"] = "ok"
        except CheckError as exc:
            row.update(status="error", category=exc.category)
            failed = True
        except OSError:
            row.update(status="error", category="file_access_error")
            failed = True
        except (ValueError, struct.error, OverflowError):
            row.update(status="error", category="malformed_container")
            failed = True
        print(json.dumps(row, sort_keys=True, ensure_ascii=True))
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
