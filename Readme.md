## map_analyze

### 1. 介绍

​	map_analyze 用于分析 elf map 文件，能够方便分析出 `指定模块` 在可执行文件中各的静态内存占用。

### 2. 如何使用

#### 2.1 命令行中输入：

```
python3 map_analyze.py -m at820_alg_standard_demo.map -k rtos
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
