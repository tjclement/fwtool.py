from fwtool.archive.lzpt import readLzpt, createLzpt
from fwtool.archive import isArchive

if __name__ == "__main__":
 with open("nflasha15", "rb") as file_in:
  res = list(readLzpt(file_in))
  is_arch = isArchive(res[0].contents)
  pass
 with open("nflasha15_unpacked", "rb") as file_in:
  res = createLzpt(file_in)
  pass