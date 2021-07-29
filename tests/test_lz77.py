from io import BytesIO
from fwtool.lz77 import find_longest_match, deflateLz77, inflateLz77

def test_find_longest_match():
 assert find_longest_match(b"aaabab", 2) == (-1, -1)
 assert find_longest_match(b"aaabab", 4) == (-1, -1)
 assert find_longest_match(b"abaabab", 3) == (3, 3)
 assert find_longest_match(b"a" * 8*1024, 4099) == (4095, 64)

def test_deflate77():
 data = ",".join([str(x) for x in range(2000)]).encode("ascii")
 compressed = deflateLz77(BytesIO(data))
 uncompressed = inflateLz77(BytesIO(compressed))
 assert uncompressed == data