#!/usr/bin/env python3
"""Pack a single sanders DTB into a QCDT v2 dt.img.

Replicates the ID table of the stock Motorola dt.img so the bootloader
matches every known board revision:
  platform 293 (MSM8953), variants 0x4b/0x4c, srev 8100..8400.
Format verified by round-trip with dtimgextract.
Usage: pack_qcdt.py <sanders.dtb> <dt.img>
"""
import struct
import sys

PAGE = 2048
ENTRIES = [
    (293, 0x4B, 0x8100),
    (293, 0x4B, 0x8200),
    (293, 0x4B, 0x8300),
    (293, 0x4B, 0x83B0),
    (293, 0x4B, 0x8400),
    (293, 0x4C, 0x8400),
]


def main() -> None:
    dtb = open(sys.argv[1], "rb").read()
    assert dtb[:4] == b"\xd0\x0d\xfe\xed", "not an FDT blob"

    def pad(b: bytes) -> bytes:
        return b + b"\x00" * ((PAGE - len(b) % PAGE) % PAGE)

    table = struct.pack("<4sII", b"QCDT", 2, len(ENTRIES))
    off = ((len(table) + len(ENTRIES) * 24 + PAGE - 1) // PAGE) * PAGE
    tbl = b""
    blob = b""
    for pid, vid, srev in ENTRIES:
        tbl += struct.pack("<6I", pid, vid, srev, 0, off, len(dtb))
        blob += pad(dtb)
        off += len(pad(dtb))
    out = table + tbl
    out += b"\x00" * (((len(out) + PAGE - 1) // PAGE) * PAGE - len(out))
    out += blob
    open(sys.argv[2], "wb").write(out)
    print("wrote %d bytes, %d entries" % (len(out), len(ENTRIES)))


if __name__ == "__main__":
    main()
