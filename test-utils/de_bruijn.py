#!/usr/bin/env python3
from typing import Iterable, Union, Any, Dict
"""
The following function comes from wikipedia, which is origianlly part of the
sagemath library
"""
def de_bruijn(k: Union[Iterable[Any], int], n: int) -> str:
    """de Bruijn sequence for alphabet k
    and subsequences of length n.

    Example usage:
    print(de_bruijn(2, 5))
    print(de_bruijn(2, 6))
    print(de_bruijn("abcd", 2))
    """
    # Two kinds of alphabet input: an integer expands
    # to a list of integers as the alphabet..
    if isinstance(k, int):
        alphabet = list(map(str, range(k)))
    else:
        # While any sort of list becomes used as it is
        alphabet = k
        k = len(k)

    a = [0] * k * n
    sequence = []

    def db(t, p):
        if t > n:
            if n % p == 0:
                sequence.extend(a[1 : p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)

    db(1, 1)
    return "".join(alphabet[i] for i in sequence)

def isPowerOf2(x: int) -> bool:
    return x == (x & -x)

class PowerOf2ValToIndex(object):
    """
    Represents parameters of an algorithm that can quickly convert a power-of-2
    integer (e.g., x == 32) to the index of the set bit (e.g., log2(x) == 5).
    How it works:
    Multiple x with a magic number that is a de bruijn sequence, resulting a
    left-shifted de bruijn sequence. The higher bits of the results is unique
    and depends on each power-of-2 x (this is the properties of the de bruijn
    sequence).
    Last step is to query a lookup table to recover the log2(x) based on those
    higher bits.
    """
    # The multiplication operand used as a hash function based on
    # a de Bruijn sequence
    hashmulti_op: int
    # The lookup table used to map hash results (higher bits of the
    # multiplication results of the above de Bruijn sequence and the power-of-2
    # number under question) # back to the index of the bit
    lookup_tbl: Dict[int, int]
    target_bitwidth: int
    offset_bitwidth: int

    def ExportToCppHeader(self):
        lookup_tbl_content = ', '.join([
            str(self.lookup_tbl[i]) for i in range(self.target_bitwidth)
        ])
        print(f"constexpr uint8_t deBruijnLookupTable[{self.target_bitwidth}] = {{")
        print(lookup_tbl_content)
        print(f"}};")
        # A hint of how to compute the de bruijn based hash function
        print(f"hint:\n\t(({hex(self.hashmulti_op)} * x) >> {self.target_bitwidth - self.offset_bitwidth})")

def genPowerOf2ValToIndex(bitwidth: int):
    """
    bitwidth must be a power-of-2, representing the integer type that we want
    to generate a configuration of a de Bruijn based log2 algorithm specific
    for power-of-2 values.
    Typical integer types are 32-bit and 64-bit.
    """
    algo_config = PowerOf2ValToIndex()
    assert(isPowerOf2(bitwidth))
    offset_bitwidth = (bitwidth - 1).bit_length()
    de_bruijn_seq_str = de_bruijn(2, offset_bitwidth)
    hashmulti_op = int(f"0b{de_bruijn_seq_str}", base=2)
    hash_shift_width = bitwidth - offset_bitwidth;
    mask = ~(-1 << offset_bitwidth)
    lookup_tbl = {
            (((hashmulti_op << i) >> hash_shift_width) & mask): i
            for i in range(bitwidth)
    }
    algo_config.hashmulti_op = hashmulti_op
    algo_config.lookup_tbl = lookup_tbl
    algo_config.target_bitwidth = bitwidth
    algo_config.offset_bitwidth = offset_bitwidth
    return algo_config
print("for uint32_t")
PowerOf2Int32ToIndex = genPowerOf2ValToIndex(32)
PowerOf2Int32ToIndex.ExportToCppHeader()
print("for uint64_t")
PowerOf2Int64ToIndex = genPowerOf2ValToIndex(64)
PowerOf2Int64ToIndex.ExportToCppHeader()
