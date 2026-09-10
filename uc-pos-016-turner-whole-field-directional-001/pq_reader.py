"""
Minimal pure-Python Parquet reader (no pyarrow/fastparquet available in this
sandbox — PyPI/npm/apt egress are all blocked here, and the device bridge to
Kellen's machine, which has pyarrow in its `snakes` conda env, is currently
down: `device_bash` fails with a virtiofs mount error on every call).

Implements just enough of the Parquet spec to read the columns this build
needs out of `phils_YYYY.parquet` (written by pandas/pyarrow, PLAIN or
RLE_DICTIONARY encoding, SNAPPY or UNCOMPRESSED codec, flat schema so
repetition levels are always 0-width). Not a general-purpose reader.
"""
from __future__ import annotations
import struct
import zlib

# ---------------------------------------------------------------------------
# Thrift Compact Protocol — generic reader
# ---------------------------------------------------------------------------
CT_STOP, CT_BOOLT, CT_BOOLF, CT_BYTE, CT_I16, CT_I32, CT_I64, CT_DOUBLE, \
    CT_BINARY, CT_LIST, CT_SET, CT_MAP, CT_STRUCT = range(13)


def read_varint(buf, pos):
    result = 0
    shift = 0
    while True:
        b = buf[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return result, pos


def zigzag_decode(n):
    return (n >> 1) ^ -(n & 1)


def read_zzvarint(buf, pos):
    v, pos = read_varint(buf, pos)
    return zigzag_decode(v), pos


def read_value(buf, pos, ttype):
    if ttype == CT_BOOLT:
        return True, pos
    if ttype == CT_BOOLF:
        return False, pos
    if ttype == CT_BYTE:
        return buf[pos], pos + 1
    if ttype in (CT_I16, CT_I32, CT_I64):
        return read_zzvarint(buf, pos)
    if ttype == CT_DOUBLE:
        return struct.unpack_from('<d', buf, pos)[0], pos + 8
    if ttype == CT_BINARY:
        ln, pos = read_varint(buf, pos)
        return bytes(buf[pos:pos + ln]), pos + ln
    if ttype in (CT_LIST, CT_SET):
        header = buf[pos]; pos += 1
        size = header >> 4
        etype = header & 0x0F
        if size == 15:
            size, pos = read_varint(buf, pos)
        out = []
        for _ in range(size):
            v, pos = read_value(buf, pos, etype)
            out.append(v)
        return out, pos
    if ttype == CT_STRUCT:
        return read_struct(buf, pos)
    if ttype == CT_MAP:
        size, pos = read_varint(buf, pos)
        if size == 0:
            return {}, pos
        kv_types = buf[pos]; pos += 1
        ktype = kv_types >> 4
        vtype = kv_types & 0x0F
        out = {}
        for _ in range(size):
            k, pos = read_value(buf, pos, ktype)
            v, pos = read_value(buf, pos, vtype)
            out[k] = v
        return out, pos
    raise ValueError(f"unsupported thrift compact type {ttype} at {pos}")


def read_struct(buf, pos):
    """Returns (dict field_id -> value, new_pos). BOOL values collapse to
    python bool directly (no separate value byte needed for struct fields)."""
    fields = {}
    last_fid = 0
    while True:
        header = buf[pos]; pos += 1
        if header == 0:  # STOP
            break
        delta = header >> 4
        ttype = header & 0x0F
        if delta == 0:
            fid, pos = read_zzvarint(buf, pos)
        else:
            fid = last_fid + delta
        last_fid = fid
        val, pos = read_value(buf, pos, ttype)
        fields[fid] = val
    return fields, pos


# ---------------------------------------------------------------------------
# Parquet enums (parquet-format parquet.thrift)
# ---------------------------------------------------------------------------
PTYPE = {0: 'BOOLEAN', 1: 'INT32', 2: 'INT64', 3: 'INT96', 4: 'FLOAT',
         5: 'DOUBLE', 6: 'BYTE_ARRAY', 7: 'FIXED_LEN_BYTE_ARRAY'}
CODEC = {0: 'UNCOMPRESSED', 1: 'SNAPPY', 2: 'GZIP', 3: 'LZO', 4: 'BROTLI',
         5: 'LZ4', 6: 'ZSTD', 7: 'LZ4_RAW'}
ENCODING = {0: 'PLAIN', 2: 'PLAIN_DICTIONARY', 3: 'RLE', 4: 'BIT_PACKED',
            5: 'DELTA_BINARY_PACKED', 6: 'DELTA_LENGTH_BYTE_ARRAY',
            7: 'DELTA_BYTE_ARRAY', 8: 'RLE_DICTIONARY', 9: 'BYTE_STREAM_SPLIT'}
PAGE_TYPE = {0: 'DATA_PAGE', 1: 'INDEX_PAGE', 2: 'DICTIONARY_PAGE',
             3: 'DATA_PAGE_V2'}


# ---------------------------------------------------------------------------
# Pure-python raw Snappy decompression (block format, not framed)
# ---------------------------------------------------------------------------
def snappy_decompress(data: bytes) -> bytes:
    length, pos = read_varint(data, 0)
    out = bytearray(length)
    outpos = 0
    n = len(data)
    while pos < n:
        tag = data[pos]; pos += 1
        kind = tag & 0x03
        if kind == 0:  # literal
            ln = tag >> 2
            if ln < 60:
                ln += 1
            else:
                extra = ln - 59
                ln = int.from_bytes(data[pos:pos + extra], 'little') + 1
                pos += extra
            out[outpos:outpos + ln] = data[pos:pos + ln]
            pos += ln
            outpos += ln
        else:
            if kind == 1:  # copy, 1-byte offset
                ln = ((tag >> 2) & 0x07) + 4
                offset = ((tag & 0xE0) << 3) | data[pos]
                pos += 1
            elif kind == 2:  # copy, 2-byte offset
                ln = (tag >> 2) + 1
                offset = int.from_bytes(data[pos:pos + 2], 'little')
                pos += 2
            else:  # kind == 3, copy, 4-byte offset
                ln = (tag >> 2) + 1
                offset = int.from_bytes(data[pos:pos + 4], 'little')
                pos += 4
            copy_from = outpos - offset
            if offset >= ln:
                out[outpos:outpos + ln] = out[copy_from:copy_from + ln]
            else:
                for i in range(ln):
                    out[outpos + i] = out[copy_from + i]
            outpos += ln
    return bytes(out)


def decompress_page(codec_id, data, uncompressed_size):
    codec = CODEC[codec_id]
    if codec == 'UNCOMPRESSED':
        return data
    if codec == 'SNAPPY':
        return snappy_decompress(data)
    if codec == 'GZIP':
        return zlib.decompress(data, 47)
    raise ValueError(f"unsupported codec {codec}")


# ---------------------------------------------------------------------------
# RLE / bit-packed hybrid decoder (used for def levels and dict indices)
# ---------------------------------------------------------------------------
def read_bitpacked_group(buf, pos, bitwidth, nvalues_hint=None):
    """Read one bit-packed run: header already consumed by caller giving
    num_groups (groups of 8). Returns (values_list, new_pos)."""
    raise NotImplementedError  # inlined below instead


def decode_rle_bitpacked_hybrid(buf, pos, bitwidth, num_values):
    """Decode exactly `num_values` values from an RLE/bit-packed hybrid
    stream starting at `pos` (no outer length prefix — caller strips that)."""
    out = []
    nbytes_per_group = bitwidth  # bytes needed to hold 8 bitwidth-packed values... see below
    while len(out) < num_values:
        header, pos = read_varint(buf, pos)
        if header & 1 == 0:
            run_len = header >> 1
            width_bytes = (bitwidth + 7) // 8
            val = int.from_bytes(buf[pos:pos + width_bytes], 'little')
            pos += width_bytes
            out.extend([val] * run_len)
        else:
            num_groups = header >> 1
            count = num_groups * 8
            total_bits = count * bitwidth
            total_bytes = (total_bits + 7) // 8
            chunk = buf[pos:pos + total_bytes]
            pos += total_bytes
            # unpack bitwidth-bit little-endian-packed values
            bitbuf = 0
            bitcnt = 0
            vals = []
            for b in chunk:
                bitbuf |= (b << bitcnt)
                bitcnt += 8
                while bitcnt >= bitwidth:
                    vals.append(bitbuf & ((1 << bitwidth) - 1))
                    bitbuf >>= bitwidth
                    bitcnt -= bitwidth
            out.extend(vals[:count])
    return out[:num_values], pos


def bitwidth_for(max_val):
    if max_val <= 0:
        return 0
    return max_val.bit_length()


# ---------------------------------------------------------------------------
# Parquet file reader
# ---------------------------------------------------------------------------
class ParquetFile:
    def __init__(self, path):
        with open(path, 'rb') as f:
            self.data = f.read()
        assert self.data[:4] == b'PAR1' and self.data[-4:] == b'PAR1', "not a parquet file"
        footer_len = struct.unpack('<I', self.data[-8:-4])[0]
        footer_start = len(self.data) - 8 - footer_len
        meta, _ = read_struct(self.data, footer_start)
        self.num_rows = meta.get(3, 0)
        self.row_groups_raw = meta.get(4, [])
        schema_raw = meta.get(2, [])
        # schema[0] is the root group; children follow flattened (flat schema
        # assumed — true for these files: no nested/repeated fields)
        self.columns = [s.get(4) for s in schema_raw[1:]]  # names, in order
        self.col_index = {name.decode(): i for i, name in enumerate(self.columns)}

    def column_names(self):
        return [c.decode() for c in self.columns]

    def read_columns(self, names):
        """Returns dict[name] -> list of python values (None for nulls),
        length == self.num_rows, in on-disk row order."""
        wanted = {n: self.col_index[n] for n in names}
        out = {n: [] for n in names}
        for rg in self.row_groups_raw:
            chunks = rg.get(1, [])
            for n, idx in wanted.items():
                chunk = chunks[idx]
                meta = chunk.get(3)  # ColumnMetaData struct
                ptype = PTYPE[meta[1]]
                codec_id = meta[4]
                num_values = meta[5]
                dict_page_offset = meta.get(11)
                data_page_offset = meta[9]
                start = dict_page_offset if dict_page_offset is not None else data_page_offset
                vals = self._read_column_chunk(start, ptype, codec_id, num_values)
                out[n].extend(vals)
        return out

    def _read_page_header(self, pos):
        hdr, newpos = read_struct(self.data, pos)
        return hdr, newpos

    def _read_column_chunk(self, pos, ptype, codec_id, total_num_values):
        buf = self.data
        dictionary = None
        values = []
        while len(values) < total_num_values:
            hdr, pos = self._read_page_header(pos)
            page_type = PAGE_TYPE[hdr[1]]
            uncompressed_size = hdr[2]
            compressed_size = hdr[3]
            raw = buf[pos:pos + compressed_size]
            pos += compressed_size
            page_data = decompress_page(codec_id, raw, uncompressed_size)

            if page_type == 'DICTIONARY_PAGE':
                dph = hdr[7]
                n = dph[1]
                dictionary = self._decode_plain(page_data, ptype, n)
                continue

            if page_type == 'DATA_PAGE':
                dh = hdr[5]
                n = dh[1]
                encoding = ENCODING[dh[2]]
                p = 0
                # definition levels (only present if column is OPTIONAL —
                # detect via presence of extra bytes: try/except-free approach
                # is unreliable, so we rely on caller knowledge: all target
                # columns here are OPTIONAL in this schema).
                def_len = struct.unpack_from('<I', page_data, p)[0]
                p += 4
                def_bitwidth = 1
                def_levels, _ = decode_rle_bitpacked_hybrid(
                    page_data, p, def_bitwidth, n)
                p += def_len
                num_defined = sum(1 for d in def_levels if d == 1)

                if encoding in ('PLAIN_DICTIONARY', 'RLE_DICTIONARY'):
                    bitwidth = page_data[p]; p += 1
                    idxs, p = decode_rle_bitpacked_hybrid(
                        page_data, p, bitwidth, num_defined)
                    defined_vals = [dictionary[i] for i in idxs]
                elif encoding == 'PLAIN':
                    defined_vals = self._decode_plain(
                        page_data[p:], ptype, num_defined)
                else:
                    raise ValueError(f"unsupported data page encoding {encoding}")

                it = iter(defined_vals)
                for d in def_levels:
                    values.append(next(it) if d == 1 else None)
                continue

            raise ValueError(f"unexpected page type {page_type}")
        return values

    @staticmethod
    def _decode_plain(buf, ptype, n):
        out = []
        pos = 0
        if ptype == 'BOOLEAN':
            for i in range(n):
                byte = buf[pos + (i // 8)]
                out.append(bool((byte >> (i % 8)) & 1))
            return out
        if ptype == 'INT32':
            out = list(struct.unpack_from(f'<{n}i', buf, pos))
            return out
        if ptype == 'INT64':
            out = list(struct.unpack_from(f'<{n}q', buf, pos))
            return out
        if ptype == 'FLOAT':
            out = list(struct.unpack_from(f'<{n}f', buf, pos))
            return out
        if ptype == 'DOUBLE':
            out = list(struct.unpack_from(f'<{n}d', buf, pos))
            return out
        if ptype == 'BYTE_ARRAY':
            for _ in range(n):
                ln = struct.unpack_from('<I', buf, pos)[0]
                pos += 4
                out.append(buf[pos:pos + ln].decode('utf-8', errors='replace'))
                pos += ln
            return out
        raise ValueError(f"unsupported plain type {ptype}")


def read_parquet_columns(path, columns):
    """Public helper: returns a dict[col] -> list(values), plus 'num_rows'."""
    pf = ParquetFile(path)
    data = pf.read_columns(columns)
    return data, pf.num_rows
