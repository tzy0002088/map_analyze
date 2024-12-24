import re
import os
import argparse
from collections import defaultdict

whitelist = ['.itcm_code', '.bss', '.sbss', '.data', '.sdata', '.dtcm_data', '.dtcm_data_no_load', '.text', '.flash_rodata', '.rodata']

def preprocess_map_file(map_path: str) -> str:
    """Preprocess the map file to retain only content after 'Memory Configuration'."""
    with open(map_path, "r") as infile:
        lines = infile.readlines()
    start_index = next((i for i, line in enumerate(lines) if "Memory Configuration" in line), None)

    if start_index is None:
        raise ValueError("'Memory Configuration' not found in the map file.")

    temp_file = map_path + ".processed"
    with open(temp_file, "w") as outfile:
        outfile.writelines(lines[start_index:])

    return temp_file

def map_analyze(map: str, keyword: str):
    section_usage = defaultdict(int)
    same_line_pattern = re.compile(
        r'^\s*(\.\S+|COMMON)\s+0x[0-9a-fA-F]+\s+0x([0-9a-fA-F]+)\s+.*?\b' + re.escape(keyword) + r'\S*\.o\b'
    )
    size_pattern = re.compile(r'\s+0x[0-9a-fA-F]+\s+0x([0-9a-fA-F]+)')
    section_name_pattern = re.compile(r'^\s*(\.\S+)')

    def get_whitelisted_name(section_name):
        return next((whitelisted for whitelisted in whitelist if section_name.startswith(whitelisted)), None)

    with open(map, "r") as f:
        previous_line = ""
        for current_line in f:
            current_line = current_line.strip()

            match = same_line_pattern.search(current_line)
            if match:
                section_name = match.group(1)  # .text.HAL_I2S_Init
                size = int(match.group(2), 16)
                if (whitelisted_name := get_whitelisted_name(section_name)):
                    section_usage[whitelisted_name] += size
                continue

            if re.search(r'\b' + re.escape(keyword) + r'\S*\.o\b', current_line):
                section_match = section_name_pattern.search(previous_line)
                size_match = size_pattern.search(previous_line + " " + current_line)
                if section_match and size_match:
                    section_name = section_match.group(1)  # .rodata.HAL_I2S_Config
                    size = int(size_match.group(1), 16)
                    if (whitelisted_name := get_whitelisted_name(section_name)):
                        section_usage[whitelisted_name] += size

            previous_line = current_line

    return section_usage

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Map analyze tool')
    parser.add_argument('-m', '--map', type=str, help='Map file path', required=True)
    parser.add_argument('-k', '--keyword', type=str, help='Module keyword, e.g., [middleware]', required=True)

    args = parser.parse_args()
    map = args.map
    keyword = args.keyword

    try:
        if os.path.isfile(map):
            processed_map = preprocess_map_file(map)
            section_usage = map_analyze(processed_map, keyword)
            os.remove(processed_map)
            for section, size in section_usage.items():
                print(f"{section}: {size} bytes")
        else:
            print(f"Error: File '{map}' does not exist.")
    except Exception as e:
        print(f"Error: {e}")
