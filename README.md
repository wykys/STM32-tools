# STM32-tools
Tools for development of STM32 microcontrollers.

## stm-size
The script parses the memory information from the linker script and the size program, and then displays them in a more readable form.

### Demo
```
╔════════════════════════════╗ ╔════════════════════════════╗
║      RAM MEMORY 3.1 %      ║ ║    FLASH MEMORY 12.0 %     ║
╟────────────────────────────╢ ╟────────────────────────────╢
║All:               128.0 KiB║ ║All:                 1.0 MiB║
║Use:                 4.0 KiB║ ║Use:               122.5 KiB║
║Free:              124.0 KiB║ ║Free:              901.5 KiB║
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
