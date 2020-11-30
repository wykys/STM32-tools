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

For LinuxMint 20, it is necessary to install the library for debugging via openocd to work correctly.
```sh
sudo apt install libncurses5
```

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
            "cwd": "${workspaceRoot}/build",
            "executable": "charger-display-fw.elf",
            "name": "Debug (OpenOCD)",
            "device": "STM32F410",
            "svdFile": "/home/wykys/projects/cmsis-svd/data/STMicro/STM32F410.svd",
            "showDevDebugOutput": false,
            "configFiles": [
                "interface/stlink.cfg",
                "target/stm32f4x.cfg"
            ],
            "swoConfig": {
                "enabled": true,
                "cpuFrequency": 100000000,
                "swoFrequency": 1800000,
                "source": "probe",
                "decoders": [
                    {
                        "type": "console",
                        "label": "ITM",
                        "port": 0
                    }
                ]
            }
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

## STM32CubeProgrammer Linux support
``` bash
# add new repo
wget -q -O - "https://download.bell-sw.com/pki/GPG-KEY-bellsoft" | sudo apt-key add -
echo "deb [arch=amd64] https://apt.bell-sw.com/ stable main" | sudo tee /etc/apt/sources.list.d/bellsoft.list
# install
sudo apt update
sudo apt install bellsoft-java8-full
# select JDK8
sudo update-alternatives --config java
# run STM32CubeProgrammer
```
