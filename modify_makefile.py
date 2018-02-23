#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path


CMD_FLASH = \
"""
#######################################
# flash
#######################################
prog:
\t{} -c port=SWD reset=HWrst -w build/$(TARGET).bin 0x08000000 -v -rst
"""

TAG_GENERIC = '# Generic Makefile (based on gcc)'
TAG_MODIFY_CPP = '# Modified for C++'
TAG_SOURCES_PATH = '# source path'
TAG_SOURCES_C = '# C sources'
TAG_SOURCES_ASM = '# ASM sources'
TAG_SOURCES_C_INC = '# C includes'
TAG_EOF = '# *** EOF ***'

class Makefile(object):
    def __init__(self, path: str='Makefile'):
        self.MAKEFILE_LOCATION = path
        with open(self.MAKEFILE_LOCATION + '_', 'r+') as fr:
            self.makefile = fr.read()
        self.modify()

    def __del__(self):
        with open(self.MAKEFILE_LOCATION, 'w') as fw:
            fw.write(self.makefile)

    def replace(self, old: str, new: str):
        self.makefile = self.makefile.replace(old, new)

    def unix_end_line(self):
        self.makefile.replace('\r\n', '\n')

    def get_position(self, expression: str) -> int:
        return self.makefile.find(expression) + len(expression) + 1

    def check_was_modified(self):
        if self.makefile.find(TAG_MODIFY_CPP) != -1:
            print('This Makefile was already mofified')
            exit()
        else:
            position = self.get_position(TAG_GENERIC)
            self.makefile = self.makefile[:position] + TAG_MODIFY_CPP + '\n' + self.makefile[position:]

    def repair_multiple_definition(self, tag: str):
        position_start = self.get_position(tag)
        i = position_start
        while self.makefile[i:i+2] != '\n\n' and self.makefile[i:i+2] != '\n#':
            i += 1
        position_end = i
        code = self.makefile[position_start:position_end].split('\n')
        var = code[0] + '\n'
        code = sorted(
            list(set(map(
                lambda x: x.replace('\\', '').strip(),
                code[1:],
            )))
        )
        code = ''.join(list(map(lambda x: x + ' \\\n', code[:-1])) + [code[-1] + '\n'])
        self.makefile = self.makefile[:position_start] + var + code + self.makefile[position_end:]

    def update_toolchain(self, cc: str='gcc'):
        self.replace('BINPATH = ', 'BINPATH = /opt/gcc-arm-none-eabi/bin/')
        self.replace('$(BINPATH)/', '$(BINPATH)')
        self.replace('OPT = -Og', 'OPT = -Os')
        if cc == 'gcc':
            self.replace('g++', 'gcc')
        else:
            self.replace('gcc', 'g++')

    def hide_command(self, cmd: str):
        self.replace('\t' + cmd, '\t@' + cmd)

    def show_command(self, cmd: str):
        self.replace('\t@' + cmd, '\t' + cmd)

    def add_stm32_programmer(self):
        home = str(Path.home())
        result = subprocess.run(
            ['find', home, '-name', 'STM32_Programmer_CLI'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        path = result.stdout.decode('utf8')[:-1]
        if path:
            prog_str = CMD_FLASH.format(path)
            position = self.makefile.find(TAG_EOF) - 1
            self.makefile = self.makefile[:position] + prog_str + self.makefile[position:]
        else:
            print('Install STM32 Programmer CLI for Flash firmware')

    def modify(self):
        self.unix_end_line()
        self.check_was_modified()
        self.repair_multiple_definition(TAG_SOURCES_PATH)
        self.repair_multiple_definition(TAG_SOURCES_C)
        self.repair_multiple_definition(TAG_SOURCES_C_INC)
        self.update_toolchain()
        self.hide_command('$(CC)')
        self.hide_command('$(AS)')
        self.add_stm32_programmer()


if __name__ == '__main__':
    Makefile()
