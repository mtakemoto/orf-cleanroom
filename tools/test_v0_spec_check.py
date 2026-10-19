#!/usr/bin/env python3
"""Independent synthetic checks for tools/v0_spec_check.py (lead #75).

Original encoders use bit strings; expected hashes use independently serialized
values or literal bytes. No raw files, target identities, or reference imports.
Module import performs no file access; run_tests loads only the new checker.
"""
import contextlib
import errno
import hashlib
import importlib.util
import io
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


def load_checker():
    source = Path(__file__).resolve().with_name("v0_spec_check.py")
    spec = importlib.util.spec_from_file_location("_independent_v0_check", str(source))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def msb_encode(values):
    bits = "".join(format(value, "012b") for value in values)
    assert len(bits) % 8 == 0
    return bytes(int(bits[pos:pos + 8], 2) for pos in range(0, len(bits), 8))


def lsb_encode(values, pads=None):
    assert len(values) % 10 == 0
    result = bytearray()
    for group in range(len(values) // 10):
        # Ordered bit stream: bit zero of first value is first on the wire.
        bits = "".join(format(v, "012b")[::-1] for v in values[group * 10:group * 10 + 10])
        result.extend(int(bits[pos:pos + 8][::-1], 2) for pos in range(0, 120, 8))
        result.append(0 if pads is None else pads[group])
    return bytes(result)


def canonical(values):
    return b"".join(value.to_bytes(2, "little") for value in values)


def reversed_words(payload):
    assert len(payload) % 4 == 0
    return b"".join(payload[pos:pos + 4][::-1] for pos in range(0, len(payload), 4))


class Synthetic:
    """Tiny original TIFF writer; data/IFD placement is independent of checker."""

    def __init__(self, endian="little", magic=0x5352):
        self.endian = endian
        self.prefix = "<" if endian == "little" else ">"
        self.data = bytearray(b"II" if endian == "little" else b"MM")
        self.data.extend(struct.pack(self.prefix + "HI", magic, 0))

    def patch16(self, pos, value):
        self.data[pos:pos + 2] = value.to_bytes(2, self.endian)

    def patch32(self, pos, value):
        self.data[pos:pos + 4] = value.to_bytes(4, self.endian)

    def add_ifd(self, fields):
        offset = len(self.data)
        self.data.extend(b"\x00" * (2 + 12 * len(fields) + 4))
        self.patch16(offset, len(fields))
        positions = {}
        for index, (tag, typ, values) in enumerate(fields):
            pos = offset + 2 + 12 * index
            positions.setdefault(tag, pos)
            self.patch16(pos, tag)
            self.patch16(pos + 2, typ)
            self.patch32(pos + 4, len(values))
            unit = 2 if typ == 3 else 4
            raw = b"".join(value.to_bytes(unit, self.endian) for value in values)
            if len(raw) <= 4:
                self.data[pos + 8:pos + 8 + len(raw)] = raw
            else:
                self.patch32(pos + 8, len(self.data))
                self.data.extend(raw)
        return offset, positions, offset + 2 + 12 * len(fields)


def make_orf(payload, width, height, endian="little", magic=0x5352,
             splits=None, gaps=None, extra=None):
    result = Synthetic(endian, magic)
    splits = [len(payload)] if splits is None else splits
    assert sum(splits) == len(payload)
    offsets = []
    cursor = 0
    for index, size in enumerate(splits):
        if gaps and index in gaps:
            result.data.extend(b"\xfa" * gaps[index])
        offsets.append(len(result.data))
        result.data.extend(payload[cursor:cursor + size])
        cursor += size
    fields = [(256, 4, [width]), (257, 4, [height]),
              (258, 3, [12]), (259, 3, [1]),
              (273, 4, offsets), (279, 4, splits)]
    fields.extend(extra or [])
    offset, positions, following = result.add_ifd(fields)
    result.patch32(4, offset)
    result.positions, result.following = positions, following
    return result


class V0SpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = load_checker()
        cls.tiff = cls.c.load_tiff()

    def measure(self, obj):
        return self.c.measure(obj.data, self.tiff)

    def error(self, obj, category):
        with self.assertRaises(self.c.CheckError) as caught:
            self.measure(obj)
        self.assertEqual(caught.exception.category, category)

    def test_msb_hand_bytes_and_unit_order(self):
        self.assertEqual(msb_encode([0x123, 0xabc]), bytes.fromhex("12 3a bc"))
        self.assertEqual(msb_encode([0, 4095]), bytes.fromhex("00 0f ff"))
        self.assertEqual(self.c.decode_row(bytes.fromhex("12 3a bc"), 2, "packed-12", "plain"),
                         ([0x123, 0xabc], 0, 0))
        self.assertEqual(self.c.decode_row(bytes.fromhex("ff f0 00"), 2, "packed-12", "plain")[0], [4095, 0])

    def test_all4096_msb_values(self):
        values = list(range(4096)) + list(reversed(range(4096)))
        actual, pads, nonzero = self.c.decode_row(msb_encode(values), len(values), "packed-12", "plain")
        self.assertEqual(actual, values)
        self.assertEqual((pads, nonzero), (0, 0))

    def test_lsb_hand_bytes_and_all4096(self):
        values = [0x123, 0xabc] + [0] * 8
        self.assertEqual(lsb_encode(values, [255]), bytes.fromhex("23 c1 ab") + b"\x00" * 12 + b"\xff")
        values = list(range(4096)) + [4095, 0, 1, 2048]
        encoded = lsb_encode(values, [i % 256 for i in range(410)])
        actual, pads, nonzero = self.c.decode_row(encoded, len(values), "packed-12.8", "LSB-first-units")
        self.assertEqual(actual, values)
        self.assertEqual(pads, 410)
        self.assertEqual(nonzero, 408)

    def test_word_preservation_literal_orders(self):
        little = bytes.fromhex("00 00 01 00 ff 0f 00 10 ff ff")
        big = bytes.fromhex("00 00 00 01 0f ff 10 00 ff ff")
        expected = [0, 1, 4095, 4096, 65535]
        self.assertEqual(self.c.decode_row(little, 5, "packed-16", "little")[0], expected)
        self.assertEqual(self.c.decode_row(big, 5, "packed-16", "big")[0], expected)
        for order, raw in (("little", little), ("big", big)):
            with self.subTest(order=order):
                result = self.measure(make_orf(raw, 5, 1, endian=order))
                self.assertEqual(result["output_sha256"], hashlib.sha256(little).hexdigest())
                self.assertEqual((result["output_count"], result["output_min"], result["output_max"], result["output_sum"]), (5, 0, 65535, 73727))
                self.assertEqual(result["above4095_count"], 2)
                self.assertEqual(result["nonzero_low_nibble_count"], 3)
                self.assertEqual(result["byte_order"], order)

    def test_row_mapping_both_directions(self):
        for height, stored_labels, lookup in (
            (1, [0], [0]), (4, [0, 2, 1, 3], [0, 2, 1, 3]),
            (5, [0, 2, 4, 1, 3], [0, 3, 1, 4, 2])):
            actual = [self.c.stored_row(y, height, "two-fields") for y in range(height)]
            self.assertEqual(actual, lookup)
            self.assertEqual([stored_labels[s] for s in actual], list(range(height)))
        for height in range(1, 102):
            stored_labels = list(range(0, height, 2)) + list(range(1, height, 2))
            actual = [self.c.stored_row(y, height, "two-fields") for y in range(height)]
            self.assertEqual(sorted(actual), list(range(height)))
            for y, index in enumerate(actual):
                self.assertEqual(stored_labels[index], y)
            self.assertEqual([self.c.stored_row(y, height, "natural") for y in range(height)], list(range(height)))
        for y, h, layout in ((-1, 4, "natural"), (4, 4, "natural"), (0, 1, "unknown")):
            with self.assertRaises(self.c.CheckError):
                self.c.stored_row(y, h, layout)

    def test_global_reversal_reader_every_slice(self):
        # Physical boundaries and logical words are deliberately misaligned.
        original = bytes(range(24))
        encoded = reversed_words(original)
        data = encoded[:5] + b"ignored" + encoded[5:14] + b"gap" + encoded[14:]
        reader = self.c.StripReader(data, [0, 12, 24], [5, 9, 10])
        for start in range(25):
            for size in range(25 - start):
                self.assertEqual(reader.read(start, size, True), original[start:start + size])
                self.assertEqual(reader.read(start, size), encoded[start:start + size])
        for start, size in ((-1, 1), (0, -1), (24, 1), (25, 0)):
            with self.assertRaises(self.c.CheckError):
                reader.read(start, size, True)
        with self.assertRaises(self.c.CheckError):
            self.c.StripReader(b"123", [0], [3]).read(0, 3, True)
        with self.assertRaises(self.c.CheckError):
            self.c.StripReader(b"123", [0], [4])
        with self.assertRaises(self.c.CheckError):
            self.c.StripReader(b"1234", [0, 1], [2, 2])

    def test_plain_canonical_literal_hash(self):
        result = self.measure(make_orf(bytes.fromhex("12 3a bc 00 0f ff"), 4, 1, splits=[1, 2, 3]))
        expected = bytes.fromhex("23 01 bc 0a 00 00 ff 0f")
        self.assertEqual(result["output_sha256"], hashlib.sha256(expected).hexdigest())
        self.assertEqual(result["output_sum"], 7134)
        self.assertEqual((result["output_count"], result["output_min"], result["output_max"]), (4, 0, 4095))
        self.assertEqual(result["packing"], "packed-12")
        self.assertEqual(result["layout"], "natural")
        self.assertEqual(result["gap_count"], 0)
        self.assertEqual(result["strip_count"], 3)
        self.assertEqual(result["payload_bytes_consumed"], 6)
        self.assertTrue(result["exact_end"])
        self.assertNotIn("offsets", result)

    def test_reversed_triples_rows_and_strips(self):
        values = [1, 123, 4095, 3, 2048, 15, 19, 4000]
        encoded = reversed_words(msb_encode(values))
        result = self.measure(make_orf(encoded, 2, 4, magic=0x4f52, splits=[1, 4, 2, 5]))
        self.assertEqual(result["output_sha256"], hashlib.sha256(canonical(values)).hexdigest())
        self.assertEqual(result["byte_order"], "reverse-four-byte-words")
        self.assertEqual(result["layout"], "natural")

    def test_two_fields_even_odd_literal_canonical(self):
        # Width two yields 3-byte rows; odd height exposes the inverse-mapping trap.
        for height, stored_labels in ((4, [0, 2, 1, 3]), (5, [0, 2, 4, 1, 3])):
            payload = b"".join(msb_encode([y, 256 + y]) for y in stored_labels)
            field_bytes = ((height + 1) // 2) * 3
            result = self.measure(make_orf(payload, 2, height,
                                  splits=[field_bytes, len(payload) - field_bytes], gaps={1: 7}))
            expected = (bytes.fromhex("00 00 00 01 01 00 01 01 02 00 02 01 03 00 03 01") +
                        (bytes.fromhex("04 00 04 01") if height == 5 else b""))
            self.assertEqual(result["output_sha256"], hashlib.sha256(expected).hexdigest())
            self.assertEqual(result["layout"], "two-fields")
            self.assertEqual(result["gap_count"], 1)

    def test_reversal_across_field_gap(self):
        values = [0, 256, 2, 258, 1, 257, 3, 259]
        encoded = reversed_words(msb_encode(values))
        result = self.measure(make_orf(encoded, 2, 4, magic=0x4f52,
                              splits=[6, 6], gaps={1: 11}))
        expected = bytes.fromhex("00 00 00 01 01 00 01 01 02 00 02 01 03 00 03 01")
        self.assertEqual(result["output_sha256"], hashlib.sha256(expected).hexdigest())

    def test_packed128_multiple_groups_rows_and_padding(self):
        values = list(range(40))
        payload = lsb_encode(values, [0, 255, 0, 1])
        result = self.measure(make_orf(payload, 20, 2, splits=[3, 22, 39]))
        self.assertEqual(result["output_sha256"], hashlib.sha256(canonical(values)).hexdigest())
        self.assertEqual((result["padding_count"], result["nonzero_padding_count"]), (4, 2))
        self.assertEqual(result["byte_order"], "LSB-first-units")
        # LSB layout is independent of TIFF byte order.
        result2 = self.measure(make_orf(payload, 20, 2, endian="big"))
        self.assertEqual(result2["output_sha256"], result["output_sha256"])

    def test_integer_classification(self):
        for pixels, nbytes, expected in ((10, 15, "packed-12"), (10, 16, "packed-12.8"), (10, 20, "packed-16"),
                                        (10 ** 18, 16 * 10 ** 17, "packed-12.8")):
            self.assertEqual(self.c.classify(nbytes, pixels), expected)
        for nbytes in (14, 17, 19, 21):
            with self.assertRaises(self.c.CheckError):
                self.c.classify(nbytes, 10)
        obj = make_orf(b"\0" * 7, 4, 1)
        with mock.patch.object(self.c, "decode_row", side_effect=AssertionError("must not decode variable")):
            self.error(obj, "unsupported_variable_payload")

    def test_width_header_and_gap_guards(self):
        cases = [
            (make_orf(b"\0" * 6, 1, 4), "unsupported_packed12_width"),
            (make_orf(b"\0" * 16, 5, 2), "unsupported_packed128_width"),
            (make_orf(b"\0" * 6, 2, 2, endian="big"), "unsupported_packed12_header"),
            (make_orf(b"\0" * 3, 2, 1, magic=0x4f52), "partial_reversed_word"),
            (make_orf(b"\0" * 12, 2, 4, splits=[3, 9], gaps={1: 1}), "unsupported_strip_gaps"),
            (make_orf(b"\0" * 12, 2, 4, splits=[3, 3, 6], gaps={1: 1, 2: 1}), "unsupported_strip_gaps"),
            (make_orf(b"\0" * 16, 4, 2, splits=[8, 8], gaps={1: 1}), "unsupported_strip_gaps"),
            (make_orf(b"\0" * 32, 10, 2, splits=[16, 16], gaps={1: 1}), "unsupported_strip_gaps"),
        ]
        for obj, category in cases:
            with self.subTest(category=category):
                self.error(obj, category)
        for packing, width, raw, endian in (("packed-12", 2, b"\0\0", "plain"),
                                            ("packed-12.8", 10, b"\0" * 15, "LSB-first-units"),
                                            ("packed-16", 2, b"\0", "little"),
                                            ("packed-16", 1, b"\0\0", "unknown"),
                                            ("other", 1, b"\0\0", "little")):
            with self.assertRaises(self.c.CheckError):
                self.c.decode_row(raw, width, packing, endian)

    def test_header_and_ifd_guards(self):
        obj = make_orf(b"\0" * 3, 2, 1)
        for payload, category in ((b"", "truncated_header"),
                                  (b"ZZRS" + b"\0" * 4, "invalid_byte_order"),
                                  (b"II\0\0" + b"\0" * 4, "invalid_orf_magic")):
            bad = Synthetic()
            bad.data = bytearray(payload)
            self.error(bad, category)
        self.error(make_orf(b"\0" * 4, 2, 1, magic=42), "unsupported_tiff_magic")
        obj.patch32(4, len(obj.data))
        self.error(obj, "malformed_ifd_bounds")
        obj = make_orf(b"\0" * 3, 2, 1)
        obj.data.pop()
        self.error(obj, "malformed_ifd_table")
        obj = make_orf(b"\0" * 3, 2, 1)
        obj.patch32(obj.following, int.from_bytes(obj.data[4:8], "little"))
        self.error(obj, "repeated_ifd_offset")
        obj = make_orf(b"\0" * 3, 2, 1)
        obj.patch32(4, 0)
        self.error(obj, "missing_positive_payload")

    def test_relevant_descriptor_guards(self):
        cases = [(256, "type", 2, "invalid_field_type"),
                 (273, "type", 13, "invalid_field_type"),
                 (256, "count", 0, "empty_relevant_field"),
                 (256, "count", 2, "field_count_limit"),
                 (259, "count", 2, "field_count_limit"),
                 (273, "count", 1000001, "field_count_limit"),
                 (258, "type", 1, "invalid_field_type")]
        for tag, field, value, category in cases:
            obj = make_orf(b"\0" * 3, 2, 1)
            if field == "type":
                obj.patch16(obj.positions[tag] + 2, value)
            else:
                obj.patch32(obj.positions[tag] + 4, value)
            self.error(obj, category)
        self.error(make_orf(b"\0" * 3, 2, 1, extra=[(256, 4, [2])]), "duplicate_relevant_tag")
        obj = make_orf(b"\0" * 6, 4, 1, splits=[3, 3])
        obj.patch32(obj.positions[273] + 8, len(obj.data) - 2)
        self.error(obj, "malformed_field_bounds")
        obj = make_orf(b"\0" * 3, 2, 1, extra=[(330, 3, [0])])
        self.error(obj, "invalid_field_type")
        # Irrelevant fields cannot induce parsing of huge strings or counts.
        obj = make_orf(b"\0" * 3, 2, 1, extra=[(270, 4, [0])])
        obj.patch16(obj.positions[270] + 2, 2)
        obj.patch32(obj.positions[270] + 4, 0xffffffff)
        obj.patch32(obj.positions[270] + 8, 0xffffffff)
        self.assertEqual(self.measure(obj)["output_count"], 2)
        # SHORT dimensions/strips are allowed; inline offsets/counts stay numeric.
        obj = make_orf(b"\0" * 3, 2, 1)
        for tag in (256, 257, 273, 279):
            obj.patch16(obj.positions[tag] + 2, 3)
        self.assertEqual(self.measure(obj)["output_count"], 2)

    def test_payload_selection_and_subifds(self):
        obj = make_orf(b"\0" * 6, 4, 1)
        second, positions, following = obj.add_ifd([(256, 4, [2]), (257, 4, [1]),
                                                   (273, 4, [8]), (279, 4, [3])])
        obj.patch32(obj.following, second)
        self.assertEqual(self.measure(obj)["output_count"], 4)
        obj.patch32(positions[279] + 8, 6)
        self.error(obj, "ambiguous_payload_ifd")
        # Metadata root references the image through a LONG/IFD SubIFD.
        for typ in (4, 13):
            obj = make_orf(b"\0" * 3, 2, 1)
            raw_ifd = int.from_bytes(obj.data[4:8], "little")
            root, positions, following = obj.add_ifd([(330, typ, [raw_ifd])])
            obj.patch32(4, root)
            self.assertEqual(self.measure(obj)["ifd_count"], 2)
        obj = make_orf(b"\0" * 3, 2, 1)
        # A descriptor can be well-formed but selected required fields absent.
        obj.patch16(obj.positions[256], 999)
        self.error(obj, "missing_payload_fields")

    def test_dimensions_strips_and_limits(self):
        obj = make_orf(b"\0" * 3, 0, 1)
        self.error(obj, "zero_dimensions")
        obj = make_orf(b"\0" * 3, 100001, 1)
        self.error(obj, "dimension_limit")
        obj = make_orf(b"\0" * 3, 100000, 100000)
        self.error(obj, "pixel_limit")
        obj = make_orf(b"\0" * 6, 4, 1, splits=[3, 3])
        obj.patch32(obj.positions[273] + 4, 1)
        self.error(obj, "mismatched_strip_arrays")
        obj = make_orf(b"\0" * 6, 4, 1, splits=[3, 3])
        count_base = int.from_bytes(obj.data[obj.positions[279] + 8:obj.positions[279] + 12], "little")
        obj.patch32(count_base, 0)
        self.error(obj, "zero_strip_size")
        obj = make_orf(b"\0" * 3, 2, 1)
        obj.patch32(obj.positions[273] + 8, 0xffffffff)
        self.error(obj, "strip_out_of_bounds")
        for second_start in (8, 7):
            obj = make_orf(b"\0" * 6, 4, 1, splits=[3, 3])
            array = int.from_bytes(obj.data[obj.positions[273] + 8:obj.positions[273] + 12], "little")
            obj.patch32(array + 4, second_start)
            self.error(obj, "unsupported_strip_order_or_overlap")
        obj = make_orf(b"\0" * 3, 2, 1)
        with mock.patch.object(self.c, "MAX_FILE_BYTES", len(obj.data) - 1):
            self.error(obj, "file_size_limit")
        with mock.patch.object(self.c, "MAX_IFDS", 0):
            self.error(obj, "ifd_limit")
        # Optional compression is reported, not used to decide packing.
        obj.patch32(obj.positions[259] + 8, 999)
        self.assertEqual(self.measure(obj)["compression_tag"], [999])

    @unittest.skipUnless(hasattr(os, "O_NONBLOCK"), "regular-file measurement requires nonblocking open")
    def test_cli_hashes_identities_failure_isolation(self):
        with tempfile.TemporaryDirectory(prefix="v0-synthetic-") as directory:
            private = Path(directory) / "private-input.ORF"
            private.write_bytes(make_orf(bytes.fromhex("12 3a bc"), 2, 1).data)
            missing = Path(directory) / "secret-missing.ORF"
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                code = self.c.main(["--measured-by", "@tester", "--sample", "1", "same.ORF", str(private),
                                    "--sample", "2", "same.ORF", str(missing),
                                    "--sample", "3", "same.ORF", str(private)])
            self.assertEqual(code, 1)
            rows = [json.loads(line) for line in buffer.getvalue().splitlines()]
            self.assertEqual([row["status"] for row in rows], ["ok", "error", "ok"])
            self.assertEqual([row["sample_id"] for row in rows], ["1", "2", "3"])
            self.assertEqual(rows[0]["input_sha256"], hashlib.sha256(private.read_bytes()).hexdigest())
            self.assertEqual(rows[0]["input_sha256"], rows[2]["input_sha256"])
            self.assertEqual(rows[1]["category"], "file_access_error")
            self.assertNotIn(directory, buffer.getvalue())
            self.assertNotIn("private-input", buffer.getvalue())
            self.assertNotIn("secret-missing", buffer.getvalue())
            for row in rows:
                for key in ("tool_sha256", "tests_sha256", "shared_container_sha256", "spec_sha256"):
                    self.assertRegex(row["provenance"][key], r"^[0-9a-f]{64}$")
                self.assertEqual(row["provenance"]["spec_revision"], "bf56d39")
                self.assertIn("unverified", row["provenance"]["selectors"]["status"])
                self.assertIn("no numeric shift", row["provenance"]["selectors"]["packed16_output"])

    @unittest.skipUnless(hasattr(os, "mkfifo") and hasattr(os, "O_NONBLOCK"),
                         "FIFO/nonblocking open unavailable")
    def test_fifo_rejection_does_not_block_following_sample(self):
        with tempfile.TemporaryDirectory(prefix="v0-synthetic-fifo-") as directory:
            fifo = Path(directory) / "private-fifo"
            try:
                os.mkfifo(fifo)
            except OSError as exc:
                if exc.errno in (errno.ENOSYS, errno.EOPNOTSUPP, errno.EPERM, errno.EACCES):
                    self.skipTest("FIFO creation unsupported in this environment")
                raise
            regular = Path(directory) / "private-regular.ORF"
            regular.write_bytes(make_orf(bytes.fromhex("12 3a bc"), 2, 1).data)
            command = [sys.executable, "-I", self.c.__file__, "--measured-by", "tester",
                       "--sample", "1", "fifo.ORF", str(fifo),
                       "--sample", "2", "regular.ORF", str(regular)]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True, timeout=5)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stderr, "")
            rows = [json.loads(line) for line in result.stdout.splitlines()]
            self.assertEqual([row["sample_id"] for row in rows], ["1", "2"])
            self.assertEqual(rows[0]["status"], "error")
            self.assertEqual(rows[0]["category"], "unsupported_file_type")
            self.assertEqual(rows[1]["status"], "ok")
            self.assertEqual(rows[1]["output_sha256"],
                             hashlib.sha256(bytes.fromhex("23 01 bc 0a")).hexdigest())
            self.assertNotIn(directory, result.stdout)
            self.assertNotIn("private-", result.stdout)

    def test_safe_open_closes_rejected_descriptor_and_fails_closed(self):
        if hasattr(os, "O_NONBLOCK"):
            with tempfile.TemporaryDirectory(prefix="v0-synthetic-descriptor-") as directory:
                path = Path(directory) / "empty.ORF"
                path.write_bytes(b"")
                real_open, real_close = self.c.os.open, self.c.os.close
                with mock.patch.object(self.c.os, "open", wraps=real_open) as opened, \
                        mock.patch.object(self.c.os, "close", wraps=real_close) as closed:
                    with self.assertRaises(self.c.CheckError) as caught:
                        self.c.measure_path(path)
                    self.assertEqual(caught.exception.category, "truncated_header")
                    self.assertEqual(closed.call_count, 1)
                    self.assertTrue(opened.call_args[0][1] & os.O_NONBLOCK)
        # No path stat/open fallback can reintroduce a check/open race. Both
        # samples promptly report the public category without touching paths.
        with mock.patch.dict(self.c.os.__dict__):
            self.c.os.__dict__.pop("O_NONBLOCK", None)
            buffer = io.StringIO()
            with mock.patch.object(self.c.os, "open") as opened, \
                    contextlib.redirect_stdout(buffer):
                code = self.c.main(["--measured-by", "tester",
                                    "--sample", "1", "first.ORF", "/private/first",
                                    "--sample", "2", "second.ORF", "/private/second"])
                opened.assert_not_called()
            self.assertEqual(code, 1)
            rows = [json.loads(line) for line in buffer.getvalue().splitlines()]
            self.assertEqual([row["sample_id"] for row in rows], ["1", "2"])
            self.assertTrue(all(row["status"] == "error" and
                                row["category"] == "nonblocking_open_unavailable" for row in rows))
            self.assertTrue(all("requires os.O_NONBLOCK" in row["provenance"]["input_open_contract"]
                                for row in rows))
            self.assertNotIn("/private/", buffer.getvalue())

    def test_provenance_failure_keeps_each_identity(self):
        buffer = io.StringIO()
        with mock.patch.object(self.c, "provenance", side_effect=OSError("/private/source")), \
                contextlib.redirect_stdout(buffer):
            code = self.c.main(["--measured-by", "tester", "--sample", "1", "public", "/private/a",
                                "--sample", "2", "public", "/private/b"])
        self.assertEqual(code, 1)
        rows = [json.loads(line) for line in buffer.getvalue().splitlines()]
        self.assertEqual([row["sample_id"] for row in rows], ["1", "2"])
        self.assertTrue(all(row["category"] == "provenance_unavailable" for row in rows))
        self.assertNotIn("private", buffer.getvalue())

    def test_additional_container_bounds_and_selection(self):
        obj = make_orf(b"\0" * 3, 2, 1, extra=[(330, 4, [0])])
        obj.patch32(obj.positions[330] + 4, self.c.MAX_IFDS + 1)
        self.error(obj, "field_count_limit")
        obj = make_orf(b"\0" * 3, 2, 1, extra=[(330, 4, [0xffffffff])])
        self.error(obj, "malformed_ifd_bounds")
        # The queue is bounded before following pointers, not only after visits.
        obj = make_orf(b"\0" * 3, 2, 1, extra=[(330, 4, [8, 9])])
        with mock.patch.object(self.c, "MAX_IFDS", 2):
            self.error(obj, "ifd_limit")
        obj = make_orf(b"\0" * 6, 4, 1, splits=[3, 3])
        array = int.from_bytes(obj.data[obj.positions[279] + 8:obj.positions[279] + 12], "little")
        obj.patch32(obj.positions[279] + 8, 0xffffffff)
        self.error(obj, "malformed_field_bounds")
        obj.patch32(obj.positions[279] + 8, array)
        with mock.patch.object(self.c, "MAX_STRIPS", 1):
            self.error(obj, "field_count_limit")
        # Two smaller equal candidates do not make a later larger one ambiguous.
        obj = make_orf(b"\0" * 6, 4, 1)
        first_ifd = int.from_bytes(obj.data[4:8], "little")
        smaller_fields = [(256, 4, [2]), (257, 4, [1]), (273, 4, [8]), (279, 4, [3])]
        small1, positions, next1 = obj.add_ifd(smaller_fields)
        small2, positions, next2 = obj.add_ifd(smaller_fields)
        obj.patch32(next1, small2)
        obj.patch32(next2, first_ifd)
        obj.patch32(4, small1)
        result = self.measure(obj)
        self.assertEqual(result["output_count"], 4)
        self.assertEqual(result["ifd_count"], 3)
        # Big-endian inline SHORT arrays exercise descriptor endianness too.
        obj = Synthetic("big", 0x4f52)
        obj.data.extend(bytes.fromhex("00 01 10 00"))
        root, positions, following = obj.add_ifd([(256, 3, [2]), (257, 3, [1]),
                                                  (273, 3, [8, 10]), (279, 3, [2, 2])])
        obj.patch32(4, root)
        result = self.measure(obj)
        self.assertEqual(result["output_sha256"], hashlib.sha256(bytes.fromhex("01 00 00 10")).hexdigest())

    def test_cli_invalid_values_are_not_echoed(self):
        for argv in (["--unknown", "/private/secret"],
                     ["--measured-by", "/private/secret"],
                     ["--measured-by", "tester", "--sample", "1", "/private/name", "secret"],
                     ["--measured-by", "tester", "--sample", "1", "ok", "secret", "--sample", "1", "ok2", "secret2"]):
            error = io.StringIO()
            with contextlib.redirect_stderr(error), self.assertRaises(SystemExit) as caught:
                self.c.main(argv)
            self.assertEqual(caught.exception.code, 2)
            self.assertNotIn("private", error.getvalue())
            self.assertNotIn("secret", error.getvalue())
        self.assertTrue(self.c.valid_identity("123", "public (4:3).ORF"))
        for sid, name in (("0", "name"), ("1", ".."), ("1", "a\nb"), ("1", "a\\b"), ("1", "a/b")):
            self.assertFalse(self.c.valid_identity(sid, name))

    def test_no_file_access_on_import_and_isolated_help(self):
        # Import uses no open/hash/load of sibling code; only stdlib imports.
        # execute source after the allowed test read so audit covers module body.
        source = Path(self.c.__file__).read_text()
        with mock.patch("builtins.open", side_effect=AssertionError("import IO")), \
                mock.patch.object(Path, "open", side_effect=AssertionError("import IO")):
            namespace = {"__name__": "_import_only", "__file__": self.c.__file__}
            exec(compile(source, self.c.__file__, "exec"), namespace)
        command = [sys.executable, "-I", self.c.__file__, "--help"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--sample", result.stdout)
        self.assertEqual(result.stderr, "")

    @unittest.skipUnless(hasattr(os, "O_NONBLOCK"), "regular-file measurement requires nonblocking open")
    def test_mmap_empty_changed_and_resource_guards(self):
        with tempfile.TemporaryDirectory(prefix="v0-synthetic-") as directory:
            path = Path(directory) / "synthetic.ORF"
            path.write_bytes(b"")
            with self.assertRaises(self.c.CheckError) as caught:
                self.c.measure_path(path)
            self.assertEqual(caught.exception.category, "truncated_header")
            obj = make_orf(b"\0" * 3, 2, 1)
            path.write_bytes(obj.data)
            with mock.patch.object(self.c, "MAX_FILE_BYTES", 1):
                with self.assertRaises(self.c.CheckError) as caught:
                    self.c.measure_path(path)
                self.assertEqual(caught.exception.category, "file_size_limit")
            # fstat snapshots change while source bytes remain a valid fixture.
            real_stat = path.stat()
            changed = mock.Mock(st_size=real_stat.st_size, st_mtime_ns=real_stat.st_mtime_ns + 1,
                                st_ctime_ns=real_stat.st_ctime_ns, st_mode=real_stat.st_mode)
            with mock.patch.object(self.c.os, "fstat", side_effect=[real_stat, changed]):
                with self.assertRaises(self.c.CheckError) as caught:
                    self.c.measure_path(path)
                self.assertEqual(caught.exception.category, "input_changed_during_measurement")


def run_tests():
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(V0SpecTests)
    return unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    sys.exit(0 if run_tests().wasSuccessful() else 1)
