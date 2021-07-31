"""LZ77 decompressor"""
# Kernel source: lib/lz77/lz77_inflate.c
import struct
from io import BytesIO
from math import ceil

LZ77_COMPRESSED = (0xF0)
LZ77_RAW = (0x0F)

def inflateLz77(file):
 """Decodes LZ77 compressed data"""
 type = ord(file.read(1))

 if type == 0x0f:
  file.read(1)
  data = file.read(2)
  l = ord(data[0:1]) | ord(data[1:2]) << 8
  return file.read(l)
 elif type == 0xf0:
  out = b''
  lengths = list(range(3, 17)) + [32, 64]

  while True:
   flags = ord(file.read(1))

   if flags == 0:
    # special case to improve performance
    out += file.read(8)
   else:
    for i in range(8):
     if (flags >> i) & 0x1:
      data = file.read(2)
      l = lengths[ord(data[0:1]) >> 4]
      bd = (ord(data[0:1]) & 0xf) << 8 | ord(data[1:2])

      if bd == 0:
       return out

      d = out[-bd:]
      d *= l // len(d) + 1
      out += d[:l]
     else:
      out += file.read(1)
 else:
  raise Exception('Unknown type')


def find_longest_match(body, current_index, window_size=4095):
 """
 @param body The text in which to search
 @param current_index The index in the text from which N characters onwards will be matched to previous segments
 @returns (offset, length) How many characters back the match was found, and for how many characters in length
 """
 find = bytes.find
 lengths = (list(range(3,17)) + [32, 64])
 lengths.reverse()
 start = max(0, current_index-window_size)
 body_len = len(body)
 max_len = min(64, body_len-current_index-1)

 for length in lengths:
  if length <= max_len and current_index >= length:
   match_pos = find(body[start:current_index], body[current_index:current_index+length])
   if match_pos != -1:
    return current_index-start-match_pos, length
 return -1, -1


def deflateLz77(file, window_size=4095):
 # Could do this in chunks, but Sony camera partitions are small enough to easily fit in RAM
 data = file.read()
 data_len = len(data)
 compressed = bytes([LZ77_COMPRESSED])
 flags = 0
 section = b""
 flag_index = 0
 data_index = 0

 while data_index < data_len:
  offset, length = find_longest_match(data, data_index, window_size)
  if offset == -1:
   section += data[data_index:data_index+1]
   data_index += 1
  else:
   length_index = length - 3 if 3 <= length <= 16 else (14 if length == 32 else (15 if length == 64 else None))
   info = (length_index << 12) | offset
   section += struct.pack(">H", info)
   flags |= (1 << flag_index)
   data_index += length

  flag_index += 1
  if flag_index == 8:
   compressed += bytes([flags]) + section
   flag_index = 0
   flags = 0
   section = b""

 # Add bytes that mark end of stream
 for finish_index in range(flag_index, 8):
  flags |= 1 << finish_index
 compressed += bytes([flags]) + section + b"\x00\x00"  # empty l and bd mark end of stream

 return compressed
