## map_analyze

### 1. 介绍

​	map_analyze 用于分析 elf map 文件，能够方便分析出 `指定模块` 在可执行文件中各的静态内存占用。

### 2. 如何使用

#### 2.1 命令行中输入：

```
python3 map_analyze.py -m at820_alg_standard_demo.map -k rv_backtrace
```

命令行参数：

* -m: map 文件路径
* -k: 关键字，即模块名

> 模块的最小单位为一个 C 文件

#### 2.2 输出：

```
.text: 1614 bytes
.data: 66 bytes
.bss: 204 bytes
.rodata: 1219 bytes
------------------------------
L1_ITCM: 1614 bytes
L2SRAM: 270 bytes
FLASH: 1219 bytes
------------------------------
{
    "L1_ITCM": {
        "symbol": [
            ".text, size: 0x60",
            ".text.rv_backtrace_call_stack, size: 0xe4",
            ".text.rv_backtrace_init, size: 0x58",
            ".text.rv_backtrace_fault, size: 0x3f8",
            ".text.rv_backtrace_current, size: 0x84",
            ".text.rv_backtrace_current_thread_name, size: 0x12",
            ".text.rv_backtrace_current_thread_stack_addr, size: 0x12",
            ".text.rv_backtrace_current_thread_stack_size, size: 0x12"
        ],
        "all_size": 1614
    },
    "L2SRAM": {
        "symbol": [
            ".data.fw_info, size: 0x42",
            ".bss.callstack.1663, size: 0x40",
            ".bss.fault_call_stack.1652, size: 0x80",
            ".bss.thread_info.1653, size: 0xc"
        ],
        "all_size": 270
    },
    "FLASH": {
        "symbol": [
            ".rodata.code_section, size: 0x10",
            ".rodata.fault_cause.1623, size: 0x40",
            ".rodata.rv_backtrace_fault.str1.4, size: 0x2a0",
            ".rodata.stack_info_table, size: 0x30",
            ".rodata.str1.4, size: 0x1a3"
        ],
        "all_size": 1219
    }
}
```

输出说明：

* 上面一部分为 rv_backtrace 模块（rv_backtrace 目录下的所有 C 文件）各 section 占用
* 中间一部分为各 section 在最终 mem layout 中的占用
* 下面一部分为各内存区域中到低都包含了那些符号

### 3. 平台适配

​	在构造 MapAnalyzer 时，根据具体平台 lds 文件定义 `section_whitelist` 以及 `mem_layout`，如下：

```python
section_whitelist = [".bss", ".text", ".rodata", ".data"]
mem_layout = {
    "dtcm": [0x10000000, 0x10030000],
    "flash": [0, 0x8000],
    "flash_nc": [0x00010000, 0x00018000],
    "ram0": [0x30000000, 0x30010000],
}

# 默认内置 section_whitelist 与 mem_layout，需要根据具体平台修改 
analyzer = MapAnalyzer(map, keyword, section_whitelist, mem_layout)
```

>section_whitelist：section 白名单，希望统计的 section 名
>
>mem_layout：内存布局

