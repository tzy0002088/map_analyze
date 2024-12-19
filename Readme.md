# map analyze

## 介绍

这是一个用于统计固件中各模块资源占用的工具，使用命令如下：

```
python3 map_analyze.py -m xxxx.map -k usb_descriptors
```

这样子会将 usb_descriptors.o 所占用的资源统计出来，输出如下：

```
.text: 170 bytes
.rodata: 365 bytes
.data.string_desc_arr: 20 bytes
.data: 2 bytes
.bss: 64 bytes
```

