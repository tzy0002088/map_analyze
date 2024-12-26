import re
import os
import argparse
from collections import defaultdict

class MapAnalyzer:
    def __init__(self, map_file: str, keyword: str, section_whitelist=None, mem_layout=None):
        self.__map_file = map_file
        self.__keyword = keyword
        self.__whitelist = section_whitelist or [".itcm_code", ".bss", ".sbss", ".data", ".sdata", ".dtcm_data", ".dtcm_data_no_load", ".text", ".flash_rodata", ".rodata"]
        self.__mem_layout = mem_layout or {
            "L2SRAM": [0x10000000, 0x10030000],
            "L1_ITCM": [0, 0x8000],
            "L1_DTCM": [0x00010000, 0x00018000],
            "L1CC": [0x30000000, 0x30010000],
            "FLASH": [0x10100000, 0x10300000],
        }

    def __preprocess_map_file(self) -> str:
        with open(self.__map_file, "r") as infile:
            lines = infile.readlines()
        start_index = next((i for i, line in enumerate(lines) if "Memory Configuration" in line), None)
        if start_index is None:
            raise ValueError("'Memory Configuration' not found in the map file.")

        temp_file = self.__map_file + ".processed"
        with open(temp_file, "w") as outfile:
            outfile.writelines(lines[start_index:])
        return temp_file

    def __get_whitelisted_name(self, section_name):
        exact_matches = {whitelisted: whitelisted for whitelisted in self.__whitelist}
        partial_matches = [whitelisted for whitelisted in self.__whitelist if whitelisted in section_name]
        return exact_matches.get(section_name) or (partial_matches[0] if partial_matches else None)

    def __analyze(self):
        section_usage = defaultdict(int)
        mem_usage = defaultdict(int)
        processed_map = self.__preprocess_map_file()

        pattern = re.compile(
            r"^\s*(\.\S+|COMMON)"
            r"(?:\s+0x[0-9a-fA-F]+\s+0x([0-9a-fA-F]+)\s+.*?\b" + re.escape(self.__keyword) + r"\S*\.o\b"
            r"|(?:\s*\n\s*0x[0-9a-fA-F]+\s+0x([0-9a-fA-F]+)\s+.*?\b" + re.escape(self.__keyword) + r"\S*\.o\b))",
            re.MULTILINE
        )
        address_pattern = r"\s(0x[0-9a-fA-F]+)\s+0x"

        with open(processed_map, "r") as f:
            content = f.read()
            matches = pattern.finditer(content)
            for match in matches:
                section_name = match.group(1)
                size = match.group(2) or match.group(3)
                size = int(size, 16)
                symble_addr = re.findall(address_pattern, match.group(0))
                if (whitelisted_name := self.__get_whitelisted_name(section_name)):
                    section_usage[whitelisted_name] += size
                    for region_name, address_range in self.__mem_layout.items():
                        start_addr, end_addr = address_range
                        if start_addr <= int(symble_addr[0], 16) < end_addr:
                            mem_usage[region_name] += size
        os.remove(processed_map)

        return section_usage, mem_usage

    def section_usage(self):
        section_usage, _ = self.__analyze()
        return section_usage

    def mem_usage(self):
        _, mem_usage = self.__analyze()
        return mem_usage

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Map analyze tool')
    parser.add_argument('-m', '--map', type=str, help='Map file path', required=True)
    parser.add_argument('-k', '--keyword', type=str, help='Module keyword, e.g., [rtos]', required=True)

    args = parser.parse_args()
    map = args.map
    keyword = args.keyword

    try:
        if os.path.isfile(map):
            analyzer = MapAnalyzer(map, keyword)
            section_usage = analyzer.section_usage()
            mem_usage = analyzer.mem_usage()
            for section, size in section_usage.items():
                print(f"{section}: {size} bytes")
            print('------------------------------')
            for region, size in mem_usage.items():
                print(f"{region}: {size} bytes")
        else:
            print(f"Error: File '{map}' does not exist.")
    except Exception as e:
        print(f"Error: {e}")
