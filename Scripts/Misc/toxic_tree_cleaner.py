#!/usr/bin/env python

from pathlib import Path
import string
import shutil

class Main:
  ILLEGAL_CHARS = {
      "<", ">", ":", "\"", "/", "\\", "|", "?", "*",
      "\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06",
      "\x07", "\x08", "\x09", "\x0A", "\x0B", "\x0C", "\x0D",
      "\x0E", "\x0F", "\x10", "\x11", "\x12", "\x13", "\x14",
      "\x15", "\x16", "\x17", "\x18", "\x19", "\x1A", "\x1B",
      "\x1C", "\x1D", "\x1E", "\x1F"
  }
  ILLEGAL_FILE_STEMS = {
    "CONIN$", "CONOUT$",
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6","COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
  }
  PUNCTUATION_CHARS = set(string.punctuation)

  def __init__(
    self,
    src_dpath_p,
    dest_dpath_p,
    dry_run=False,
  ):
    self.__src_dpath_p = src_dpath_p
    self.__dest_dpath_p = dest_dpath_p
    self.__dry_run = dry_run
    
    if self.__dry_run:
      def print_and_copy(elem_p, dest_leaf_p):
        print(f"[DRY COPY] {elem_p} => {dest_leaf_p}")

      def print_and_mkdir(current_src_node_dpath_p, current_dest_node_dpath_p):
        print(f"[DRY MKDIR] {current_src_node_dpath_p} => {current_dest_node_dpath_p}")

      class DestDPathIterator:
        _instance = None

        def __new__(cls, *args, **kwargs):
          if not cls._instance:
            cls._instance = super(DestDPathIterator, cls).__new__(cls)
          return cls._instance
      
        def __init__(self):
          self.__pseudo_tree = []

        def iter(self, dest_dpath_p):
          self.__pseudo_tree.append(dest_dpath_p)
          for elem_p in self.__pseudo_tree:
            if elem_p.parent == dest_dpath_p:
              yield elem_p
          return
    else:
      def print_and_copy(elem_p, dest_leaf_p):
        print(f"[COPY] {elem_p} => {dest_leaf_p}")
        shutil.copy(elem_p, dest_leaf_p, follow_symlinks=False)

      def print_and_mkdir(current_src_node_dpath_p, current_dest_node_dpath_p):
        print(f"[MKDIR] {current_src_node_dpath_p} => {current_dest_node_dpath_p}")
        current_dest_node_dpath_p.mkdir(exist_ok=True)

      class DestDPathIterator:
        @staticmethod
        def iter(dest_dpath_p):
          return dest_dpath_p.iterdir()

    self.__print_and_copy = print_and_copy
    self.__print_and_mkdir = print_and_mkdir
    self.__dest_dpath_iterator = DestDPathIterator()

  def run(self):
    self.__dest_dpath_p.mkdir(exist_ok=True)
  
    current_src_node_dpath_p = self.__src_dpath_p
    current_dest_node_dpath_p = self.__dest_dpath_p
    prev_node_name = ""

    while True:
      iterdir = current_src_node_dpath_p.iterdir()
      candidate_dpath_p = None

      for elem_p in iterdir:
        if elem_p.is_dir() and elem_p.name > prev_node_name:
          candidate_dpath_p = elem_p
          break
      else:
        for elem_p in current_src_node_dpath_p.iterdir():
          if elem_p.is_dir():
            continue
          new_leaf_name = self.create_new_name(current_dest_node_dpath_p, elem_p.name)
          dest_leaf_p = current_dest_node_dpath_p / new_leaf_name

          self.__print_and_copy(elem_p, dest_leaf_p)

        if current_src_node_dpath_p == self.__src_dpath_p:
          break
        prev_node_name = current_src_node_dpath_p.name
        current_src_node_dpath_p = current_src_node_dpath_p.parent
        current_dest_node_dpath_p = current_dest_node_dpath_p.parent
        continue

      for elem_p in iterdir:
        if (
          not elem_p.is_dir()
          or elem_p.name <= prev_node_name
        ):
          continue
        if elem_p.name < candidate_dpath_p.name:
          candidate_dpath_p = elem_p

      dest_node_name = self.create_new_name(current_dest_node_dpath_p, candidate_dpath_p.name)
      prev_node_name = ""

      current_dest_node_dpath_p /= dest_node_name
      self.__print_and_mkdir(current_src_node_dpath_p, current_dest_node_dpath_p)
      
      current_src_node_dpath_p = candidate_dpath_p

  def create_new_name(self, dest_dpath_p, original_name):
    tmp_name = original_name
    tmp1_p = dest_dpath_p / tmp_name
    
    tmp_name = "".join(
      c for c in tmp_name
      if c not in self.ILLEGAL_CHARS and 32 <= ord(c) < 128
    )

    tmp_name = tmp_name.lstrip(" ")
    tmp_name = tmp_name.rstrip(". ")

    tmp2_p = dest_dpath_p / tmp_name
    if not tmp_name:
      suffix_part = ".EmptySuffix"
      stem_part = "EmptyStem"
      new_name = f"{stem_part}{suffix_part}"
    elif tmp1_p.suffix and not tmp2_p.suffix:
      suffix_part = tmp2_p.stem
      stem_part = "EmptyStem"
      new_name = f"{stem_part}{suffix_part}"
    else:
      stem_part = tmp2_p.name.replace("".join(tmp2_p.suffixes), "")
      suffix_part = "".join(tmp2_p.suffixes)
      first_token = tmp_name.split(".", 1)[0].rstrip(" ").upper()

      if first_token in self.ILLEGAL_FILE_STEMS:
          new_name = f"{stem_part}Renamed{suffix_part}"
      else:
          new_name = f"{stem_part}{suffix_part}"

    i = 0
    while True:
      for elem_p in self.__dest_dpath_iterator.iter(dest_dpath_p):
        if elem_p.name.casefold() == new_name.casefold():
          new_name = f"{stem_part}{i}{suffix_part}"
          i += 1
          break
      else:
        break
          
    return new_name

def main(args):
  if args.src.resolve() == args.dest.resolve():
    raise shutil.SameFileError("Src and dest cannot be the same")
  if not args.src.is_dir():
    raise FileNotFoundError(f"Src {args.src} don't exist")

  args.dest.mkdir(exist_ok=True)
  Main(
    args.src,
    args.dest,
    args.dry_run,
  ).run()

if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(
    description=(
      "Copy a directory tree while sanitizing filenames so they are "
      "compatible with Windows filesystems."
    ),
    epilog=(
      "Examples:\n"
      " toxic-tree-cleaner src dest\n"
      " toxic-tree-cleaner /tmp/ToxicTree /tmp/DetoxedTree --dry-run\n"
    ),
    formatter_class=argparse.RawDescriptionHelpFormatter
  )
  parser.add_argument(
    "src",
    type=Path,
    help="Source directory to copy."
  )
  parser.add_argument(
    "dest",
    type=Path,
    help="Destination directory where the sanitized tree will be created."
  )
  parser.add_argument(
    "--dry-run",
    action="store_true",
    help=(
      "Simulate the operation without creating directories or copying files. "
      "Prints the actions that would be performed."
    )
  )
  args = parser.parse_args()
  main(args)
