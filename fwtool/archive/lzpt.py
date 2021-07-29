"""A decoder for LZPT compressed image files"""
# Kernel source: arch/arm/include/asm/mach/warmboot.h
# Kernel source: arch/arm/mach-cxd90014/include/mach/cmpr.h

import io
import math
from stat import *

from . import *
from .. import lz77
from ..io import *
from ..lz77 import deflateLz77
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
  for i, entry in enumerate(tocEntries):
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
 from multiprocessing import Pool
 from math import ceil

 file.seek(0, os.SEEK_END)
 file_size = file.tell()
 file.seek(0)
 num_chunks = ceil(file_size / block_size)
 header_size = LzptHeader.size
 toc_size = (num_chunks * LzptTocEntry.size)

 input_blocks = [io.BytesIO(file.read(block_size)) for i in range(num_chunks)]

 table_of_contents = b""
 output_data = b""
 with Pool() as pool:
  for index, result in enumerate(pool.imap(deflateLz77, input_blocks)):
   compressed_block = result
   offset = len(output_data)
   output_data += compressed_block
   table_of_contents += LzptTocEntry.pack(offset=(header_size + toc_size + offset), size=len(compressed_block))
   print("> %.2f%%" % (float(index) / num_chunks * 100))

 header = LzptHeader.pack(magic=lzptHeaderMagic, blockSize=int(math.log2(block_size)), tocOffset=header_size, tocSize=toc_size)
 return header + table_of_contents + output_data
