#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path


class Makefile(object):
    def __init__(self, path: str='Makefile'):
        self.MAKEFILE_LOCATION = path
        fr = open(self.MAKEFILE_LOCATION, 'r+')
        self.makefile = fr.read()
        fr.close()
        self.modify()

    def save(self):
        fw = open(self.MAKEFILE_LOCATION + '_test', 'w')
        fw.write(self.makefile)
        fw.close()

    def unix_end_line(self):
        self.makefile.replace('\r\n', '\n')

    def get_position(self, expression: str) -> int:
        return self.makefile.find(expression) + len(expression) + 1

    def check_was_modified(self):
        tag_modify = '# Modified for C++'

        if self.makefile.find(tag_modify) != -1:
            print('This Makefile was already mofified')
            exit()
        else:
            position = self.get_position('# Generic Makefile (based on gcc)')
            self.makefile = self.makefile[:position] + tag_modify + '\n' + self.makefile[position:]

    def repair_c(self):
        position_start = self.get_position('C_SOURCES =  \\')
        position_end = self.makefile.find('# ASM sources') - 1
        file_c = sorted(list(set(map(lambda x: x.replace('\\', '').strip(), self.makefile[position_start:position_end].split('\n')))))
        str_c = ''.join(list(map(lambda x: x + ' \\\n', file_c[:-1])) + [file_c[-1] + '\n'])

        self.makefile = self.makefile[:position_start] + str_c + self.makefile[position_end:]

    def add_stm32_programmer(self):
        home = str(Path.home())
        result = subprocess.run(['find', home, '-name', 'STM32_Programmer_CLI'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        path = result.stdout.decode('utf8')[:-1]

        if path:
            prog_str = \
"""
# Flash
prog:
\t{} -c port=SWD reset=HWrst -w build/$(TARGET).bin 0x08000000 -v -rst
""".format(path)
            position = self.makefile.find('# *** EOF ***') - 1
            self.makefile = self.makefile[:position] + prog_str + self.makefile[position:]
        else:
            print('Install STM32 Programmer CLI for Flash firmware')

    def modify(self):
        self.unix_end_line()
        self.check_was_modified()
        self.repair_c()
        self.add_stm32_programmer()
        self.save()


if __name__ == '__main__':
    Makefile()
