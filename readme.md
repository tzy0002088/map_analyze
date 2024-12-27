## map_analyze

### 1. 介绍

​	map_analyze 用于分析 elf map 文件，能够方便分析出 `指定模块` 在可执行文件中的静态内存占用。

### 2. 如何使用

#### 2.1 命令行中输入：

```
python3 map_analyze.py -m rtthread.map -k finsh
```

命令行参数：

* -m: map 文件路径
* -k: 关键字，即模块名

> 模块的最小单位为一个 C 文件

#### 2.2 输出：

```
.text: 11418 bytes
.rodata: 4509 bytes
.rti_fn: 4 bytes
.bss: 145 bytes
------------------------------
QFLASH: 15931 bytes
RAM: 145 bytes
------------------------------
{
    "QFLASH": {
        "symbol": [
            ".text.rt_list_isempty, size: 0x24",
            ".text.rt_list_len, size: 0x36",
            ".text.clear, size: 0x14",
            ".text.version, size: 0xe",
            ".text.object_split, size: 0x28",
            ".text.list_find_init, size: 0x46",
            ".text.list_get_next, size: 0xc6",
            ".text.list_thread, size: 0x208",
            ".text.show_wait_queue, size: 0x54",
            ".text.list_sem, size: 0x12c",
            ".text.list_event, size: 0x118",
            ".text.list_mutex, size: 0xe8",
            ".text.list_mailbox, size: 0x13c",
            ".text.list_msgqueue, size: 0x12c",
            ".text.list_memheap, size: 0xd8",
            ".text.list_mempool, size: 0x144",
            ".text.list_timer, size: 0x128",
            ".text.list_device, size: 0xf0",
            ".text.msh_help, size: 0x5c",
            ".text.cmd_ps, size: 0x18",
            ".text.cmd_free, size: 0x5c",
            ".text.msh_split, size: 0x170",
            ".text.msh_get_cmd, size: 0x64",
            ".text._msh_exec_cmd, size: 0xd4",
            ".text.msh_exec, size: 0xa0",
            ".text.str_common, size: 0x4a",
            ".text.msh_auto_complete_path, size: 0x228",
            ".text.msh_auto_complete, size: 0xe4",
            ".text.msh_readline, size: 0xa2",
            ".text.msh_exec_script, size: 0x17c",
            ".text.cmd_ls, size: 0x34",
            ".text.cmd_cp, size: 0x44",
            ".text.cmd_mv, size: 0x138",
            ".text.cmd_cat, size: 0x58",
            ".text.directory_delete_for_msh, size: 0x13c",
            ".text.cmd_rm, size: 0x1c4",
            ".text.cmd_cd, size: 0x58",
            ".text.cmd_pwd, size: 0x24",
            ".text.cmd_mkdir, size: 0x40",
            ".text.cmd_mkfs, size: 0x90",
            ".text.cmd_mount, size: 0xe0",
            ".text.cmd_umount, size: 0x64",
            ".text.cmd_df, size: 0x70",
            ".text.cmd_echo, size: 0x94",
            ".text.cmd_tail, size: 0x1bc",
            ".text.finsh_get_prompt, size: 0x9c",
            ".text.finsh_set_prompt_mode, size: 0x48",
            ".text.finsh_getchar, size: 0x90",
            ".text.finsh_rx_ind, size: 0x3c",
            ".text.finsh_set_device, size: 0xd8",
            ".text.shell_auto_complete, size: 0x34",
            ".text.shell_handle_history, size: 0x34",
            ".text.shell_push_history, size: 0x15e",
            ".text.finsh_thread_entry, size: 0x5cc",
            ".text.finsh_system_function_init, size: 0x2c",
            ".text.finsh_system_init, size: 0x9c",
            ".rodata, size: 0x6df",
            ".rodata, size: 0xac",
            ".rodata, size: 0x496",
            ".rodata, size: 0x91",
            ".rodata.name, size: 0x1ce",
            ".rodata.device_type_str, size: 0x64",
            ".rodata.name, size: 0x6d",
            ".rodata.__FUNCTION__.0, size: 0xe",
            ".rodata.name, size: 0x1fc",
            ".rodata.__FUNCTION__.6, size: 0x16",
            ".rodata.__FUNCTION__.5, size: 0xe",
            ".rodata.__FUNCTION__.4, size: 0xd",
            ".rodata.__FUNCTION__.3, size: 0x11",
            ".rti_fn.6, size: 0x4"
        ],
        "all_size": 15931
    },
    "RAM": {
        "symbol": [
            ".bss._syscall_table_begin, size: 0x4",
            ".bss._syscall_table_end, size: 0x4",
            ".bss.shell, size: 0x4",
            ".bss.finsh_prompt_custom, size: 0x4",
            ".bss.finsh_prompt.8, size: 0x81"
        ],
        "all_size": 145
    }
}
```

输出说明：

* 上面一部分为 finsh 模块（finsh 目录下的所有 C 文件）各 section 占用
* 中间一部分为各 section 在最终 mem layout 中的占用
* 下面一部分为各内存区域中包含了 finsh 模块的哪些符号

### 3. 平台适配

​	在构造 MapAnalyzer 时，根据具体平台 lds 文件定义 `section_whitelist`，如下：

```python
section_whitelist = ['.text', '.rodata', '.data', '.bss', '.rti_fn']

# 默认内置 section_whitelist，需要根据具体平台修改 
analyzer = MapAnalyzer(map, keyword, section_whitelist)
```

>section_whitelist：section 白名单，希望统计的 section 名

