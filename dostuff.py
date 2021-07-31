from io import BytesIO

from fwtool.archive.lzpt import createLzpt, readLzpt
from fwtool.lz77 import inflateLz77

if __name__ == "__main__":
    with open("nflasha15_unpacked", "rb") as f:
        data = f.read()

    # compressed = createLzpt(BytesIO(data))
    # with open("nflasha15_compressed", "wb") as f:
    #     print("Writing")
    #     f.write(compressed)

    with open("nflasha15_compressed", "rb") as f:
        with open("nflasha15_reunpacked", "wb") as output:
            print("Reading")
            compressed = f.read()
            uncompressed = next(readLzpt(BytesIO(compressed))).contents.read()
            assert uncompressed == data
            print("equal")
            output.write(uncompressed)
