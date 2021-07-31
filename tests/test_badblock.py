from io import BytesIO

from fwtool.lz77 import inflateLz77, deflateLz77


def test_badblock():
    with open("badblock", "rb") as file:
        block = file.read()
        subblock_size = 4096
        subblocks = [block[i:i + subblock_size] for i in range(0, len(block), subblock_size)]
        for i, subblock in enumerate(subblocks):
            compressed = deflateLz77(BytesIO(subblock))
            uncompressed = inflateLz77(BytesIO(compressed))
            assert subblock == uncompressed

def test_badsubblock():
    with open("badsubblock", "rb") as file:
        block = file.read()
        compressed = deflateLz77(BytesIO(block))
        uncompressed = inflateLz77(BytesIO(compressed))
        assert block == uncompressed

if __name__ == "__main__":
    test_badblock()
    test_badsubblock()