# STM32-tools
Tools for development of STM32 microcontrollers.

## stm-size
The script parses the memory information from the linker script and the size program, and then displays them in a more readable form.

The script can automatically find a binary `.elf` and linker script `.ld` file, if the two folders do not exceed the level of the two.

### Demo
`stm-size`
```
╔════════════════════════════╗ ╔════════════════════════════╗
║      RAM MEMORY 42 %       ║ ║     FLASH MEMORY 51 %      ║
╟────────────────────────────╢ ╟────────────────────────────╢
║All:                   6 KiB║ ║All:                  32 KiB║
║Use:                 2.5 KiB║ ║Use:                  16 KiB║
║Free:                3.5 KiB║ ║Free:                 16 KiB║
╚════════════════════════════╝ ╚════════════════════════════╝
```

### Agruments
`stm-size -h`
```
usage: stm-size [-h] [-l PATH_LINKER] [-e PATH_ELF] [-c] [-v]

The script parses the memory information from the linkerscript and the size
program, and then displays them in a morereadable form.

optional arguments:
  -h, --help            show this help message and exit
  -l PATH_LINKER, --linker-script PATH_LINKER
                        destination linker script
  -e PATH_ELF, --elf PATH_ELF
                        destination elf file
  -c, --color           activated color output
  -v, --vertical        prints the tables underneath
```

## [Cortex Debug](https://github.com/Marus/cortex-debug)
To run debugging, you need to install the following tools:
* [ARM toolchain](https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm/downloads)
* [OpenOCD](https://github.com/ntfreak/openocd)
* [CMSIS-SVD](https://github.com/posborne/cmsis-svd)

### Visual Studio Code configuratin:

`launch.json`
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "cortex-debug",
            "request": "launch",
            "servertype": "openocd",
            "cwd": "${workspaceRoot}",
            "executable": "./build/discovery.elf",
            "name": "Debug (OpenOCD)",
            "device": "STM32F407",
            "svdFile" : "/home/wykys/projects/cmsis-svd/data/STMicro/STM32F407.svd",
            "configFiles": [
                "board/stm32f4discovery.cfg"
            ]
        }
    ]
}
```

`settings.json`
```json
{
    "cortex-debug.armToolchainPath": "/opt/gcc-arm-none-eabi/bin",
    "cortex-debug.openocdPath": "/usr/local/bin/openocd"
}
```