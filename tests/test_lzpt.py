import struct
from io import BytesIO
from fwtool.archive import isArchive
from fwtool.archive.lzpt import readLzpt, createLzpt


def test_readLzpt():
  with open("../nflasha15", "rb") as f:
   uncompressed = list(readLzpt(f))[0].contents.read()
   pass


def test_createLzptActualData():
  with open("../nflasha15_unpacked", "rb") as f:
      data = f.read()
  compressed = createLzpt(BytesIO(data))
  uncompressed = list(readLzpt(BytesIO(compressed)))[0].contents
  assert uncompressed.read() == data

def test_createLzpt():
  data = ",".join([str(x) for x in range(2000)]).encode("ascii")
  compressed = createLzpt(BytesIO(data))
  uncompressed = list(readLzpt(BytesIO(compressed)))[0].contents
  assert uncompressed.read() == data