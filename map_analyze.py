import re
import os
import argparse
from collections import defaultdict
import json

class MapAnalyzer:
    def __init__(self, map_file: str, keyword: str, section_whitelist=None):
        self.__map_file = map_file
        self.__keyword = keyword
        self.__whitelist = section_whitelist or [".itcm_code", ".bss", ".sbss", ".data", ".sdata", ".dtcm_data", ".dtcm_data_no_load", ".text", ".flash_rodata", ".rodata"]

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

    def __get_whitelisted_name(self, section_name) -> str:
        exact_matches = {whitelisted: whitelisted for whitelisted in self.__whitelist}
        partial_matches = [whitelisted for whitelisted in self.__whitelist if whitelisted in section_name]
        return exact_matches.get(section_name) or (partial_matches[0] if partial_matches else None)

    def _parse_memory_layout(self, map_file):
        with open(map_file, "r") as f:
            lines = f.readlines()

        start_index = next((i for i, line in enumerate(lines) if "Memory Configuration" in line), None)
        if start_index is None:
            raise ValueError("'Memory Configuration' section not found in the map file.")

        end_index = next((i for i, line in enumerate(lines) if "Linker script and memory map" in line), None)
        if end_index is None:
            raise ValueError("'Linker script and memory map' section not found in the map file.")

        config_text = "".join(lines[start_index+3:end_index-2])
        pattern = re.compile(r"^\s*(\S+)\s+0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)", re.MULTILINE)

        mem_layout = {}
        matches = pattern.findall(config_text)

        for match in matches:
            name = match[0]
            origin = int(match[1], 16)
            length = int(match[2], 16)
            mem_layout[name] = [origin, origin + length]

        return mem_layout

    def __analyze(self):
        section_usage = defaultdict(int)
        mem_usage = defaultdict(lambda: {"symbol": [], "all_size": 0})
        processed_map = self.__preprocess_map_file()
        mem_layout = self._parse_memory_layout(processed_map)

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
                if (whitelisted_name := self.__get_whitelisted_name(section_name)) and size != 0:
                    section_usage[whitelisted_name] += size
                    for region_name, address_range in mem_layout.items():
                        start_addr, end_addr = address_range
                        if start_addr <= int(symble_addr[0], 16) < end_addr:
                            format_str = f"{section_name}, size: {hex(size)}"
                            mem_usage[region_name]["symbol"].append(format_str)
                            mem_usage[region_name]["all_size"] += size
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
    section_whitelist = ['.text', '.rodata', '.data', '.bss', '.rti_fn']
    try:
        if os.path.isfile(map):
            analyzer = MapAnalyzer(map, keyword, section_whitelist)
            section_usage = analyzer.section_usage()
            mem_usage = analyzer.mem_usage()
            for section, size in section_usage.items():
                print(f"{section}: {size} bytes")
            print('------------------------------')
            for region, data in mem_usage.items():
                print(f"{region}: {data['all_size']} bytes")
            print('------------------------------')
            print(json.dumps(mem_usage, indent=4))
        else:
            print(f"Error: File '{map}' does not exist.")
    except Exception as e:
        print(f"Error: {e}")
