"""A decoder for LZPT compressed image files"""
# Kernel source: arch/arm/include/asm/mach/warmboot.h
# Kernel source: arch/arm/mach-cxd90014/include/mach/cmpr.h

import io
from stat import *

from . import *
from .. import lz77
from ..io import *
from ..util import *

# struct wbi_lzp_hdr
LzptHeader = Struct('LzptHeader', [
 ('magic', Struct.STR % 4),
 ('blockSize', Struct.INT32),
 ('tocOffset', Struct.INT32),
 ('tocSize', Struct.INT32),
])
# CMPR_LZPART_MAGIC
lzptHeaderMagic = b'TPZL'

# struct wbi_lzp_entry
LzptTocEntry = Struct('LzptTocEntry', [
 ('offset', Struct.INT32),
 ('size', Struct.INT32),
])

def isLzpt(file):
 """Checks if the LZPT header is present"""
 header = LzptHeader.unpack(file)
 return header and header.magic == lzptHeaderMagic

def readLzpt(file):
 """Decodes an LZPT image and returns its contents"""
 header = LzptHeader.unpack(file)

 if header.magic != lzptHeaderMagic:
  raise Exception('Wrong magic')

 tocEntries = [LzptTocEntry.unpack(file, header.tocOffset + offset) for offset in range(0, header.tocSize, LzptTocEntry.size)]

 def generateChunks():
  for entry in tocEntries:
   file.seek(entry.offset)
   block = io.BytesIO(file.read(entry.size))

   read = 0
   while read < 2 ** header.blockSize:
    contents = lz77.inflateLz77(block)
    yield contents
    read += len(contents)

 yield UnixFile(
  path = '',
  size = -1,
  mtime = 0,
  mode = S_IFREG,
  uid = 0,
  gid = 0,
  contents = ChunkedFile(generateChunks),
 )


def createLzpt(file, block_size=(64*1024)):
 block = file.read(block_size)
 table_of_contents = []
 data = b''
 while len(block) > 0:
  compressed = lz77_compress(block, window_size=4096)
  offset = len(data)
  data += compressed
  table_of_contents.append(LzptTocEntry.pack(offset=offset, size=len(compressed)))
  block = file.read(block_size)

 header = LzptHeader.pack(magic=lzptHeaderMagic, blockSize=block_size, tocOffset=24, tocSize=(len(table_of_contents) * LzptTocEntry.size))
 pass
