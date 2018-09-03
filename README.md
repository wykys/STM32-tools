# STM32-tools
Tools for development of STM32 microcontrollers.

## stm-size
The script parses the memory information from the linker script and the size program, and then displays them in a more readable form.

The script can automatically find a binary `.elf` and linker script `.ld` file, if the two folders do not exceed the level of the two.

### Demo
`stm-size`<br/>
╔════════════════════════════╗ ╔════════════════════════════╗<br/>
║      RAM MEMORY 3.1 %      ║ ║    FLASH MEMORY 12.0 %     ║<br/>
╟────────────────────────────╢ ╟────────────────────────────╢<br/>
║All:               128.0 KiB║ ║All:                 1.0 MiB║<br/>
║Use:                 4.0 KiB║ ║Use:               122.5 KiB║<br/>
║Free:              124.0 KiB║ ║Free:              901.5 KiB║<br/>
╚════════════════════════════╝ ╚════════════════════════════╝<br/>


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
