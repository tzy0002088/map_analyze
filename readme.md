## map_analyze

### 1. 介绍

​	map_analyze 用于分析 elf map 文件，能够方便分析出 `指定模块` 在可执行文件中各的静态内存占用。

### 2. 如何使用

#### 2.1 命令行中输入：

```
python3 map_analyze.py -m xxxx_demo.map -k rtos
```

命令行参数：

* -m: map 文件路径
* -k: 关键字，即模块名

> 模块的最小单位为一个 C 文件

#### 2.2 输出：

```
.sdata: 8 bytes
.sbss: 124 bytes
.bss: 141724 bytes
.text: 12472 bytes
.rodata: 157 bytes
------------------------------
L2SRAM: 141856 bytes
FLASH: 12629 bytes
```

输出说明：

* 上面一部分为 rtos 模块（rtos 目录下的所有 C 文件）各 section 占用
* 下面一部分为各 section 在最终 内存/flash 中的占用，如 FLASH 的 12629 bytes 包含 .text 段与.rodata 段，其余 section 全部在 L2SRAM 中

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

