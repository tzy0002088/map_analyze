import re
import os
import argparse
from collections import defaultdict

def map_analyze(map: str, keyworld: str):

    section_usage = defaultdict(int)
    previous_line = ""
    current_line = ""
    same_line_pattern = re.compile(
        r'^\s*(\.\S+|COMMON)\s+0x[0-9a-fA-F]+\s+0x([0-9a-fA-F]+)\s+.*?(\b' + re.escape(keyworld) + r'\S*\.o\b)'
    )
    size_pattern = re.compile(r'\s+0x[0-9a-fA-F]+\s+0x([0-9a-fA-F]+)')
    section_name_pattern = re.compile(r'^\s*(\.\S+)')

    with open(map, "r") as f:
        for next_line in f:
            previous_line = current_line
            current_line = next_line.strip()

            match = same_line_pattern.search(current_line)
            if match:
                section_name = match.group(1)  # 段名，例如 .text.HAL_I2S_Init
                size = int(match.group(2), 16)  # 段大小
                if section_name.startswith('.sbss') or section_name.startswith('.bss') or section_name == "COMMON":
                    section_usage['.bss'] += size
                elif section_name.startswith('.sdata'):
                    section_usage['.data'] += size
                elif section_name.startswith('.text'):
                    section_usage['.text'] += size
                elif section_name.startswith('.rodata'):
                    section_usage['.rodata'] += size
                else:
                    section_usage[section_name] += size
                continue
            elif re.search(r'\b' + re.escape(keyworld) + r'\S*\.o\b', current_line):
                section_match = section_name_pattern.search(previous_line)  # 上一行找段名
                size_match = size_pattern.search(previous_line + " " + current_line)  # 找段大小
                if section_match and size_match:
                    section_name = section_match.group(1)  # 段名，例如 .rodata.HAL_I2S_Config
                    size = int(size_match.group(1), 16)  # 段大小
                    if section_name.startswith('.sbss') or section_name.startswith('.bss') or section_name == "COMMON":
                        section_usage['.bss'] += size
                    elif section_name.startswith('.sdata'):
                        section_usage['.data'] += size
                    elif section_name.startswith('.text'):
                        section_usage['.text'] += size
                    elif section_name.startswith('.rodata'):
                        section_usage['.rodata'] += size
                    else:
                        section_usage[section_name] += size

    return section_usage

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='map analyze tool')
    parser.add_argument('-m', '--map', type=str, help='map file path')
    parser.add_argument('-k', '--keyword', type=str, help='module keyworld, [middleware]')

    args = parser.parse_args()
    map = args.map
    key = args.keyword

    if not args.map or not args.keyword:
        parser.print_help()
    elif os.path.isfile(map):
        section_usage = map_analyze(map, key)
        for section, size in section_usage.items():
            print(f"{section}: {size} bytes")