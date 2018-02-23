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

CMD_OBJECTS_APPEND_CPP = \
"""
OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(CPP_SOURCES:.cpp=.o)))
vpath %.cpp $(sort $(dir $(CPP_SOURCES)))
"""

CMD_BUILD_CPP = \
"""
$(BUILD_DIR)/%.o: %.cpp Makefile | $(BUILD_DIR)
\t$(CC) -c $(CFLAGS) -Wa,-a,-ad,-alms=$(BUILD_DIR)/$(notdir $(<:.cpp=.lst)) $< -o $@
"""

CFLAGS = (
    '$(MCU)',
    '-std=c++11',
    '-Wno-write-strings',
    '-specs=nano.specs',
    '-specs=nosys.specs',
    '$(C_DEFS)',
    '$(C_INCLUDES)',
    '$(OPT)',
    '-Wall',
    '-fdata-sections',
    '-ffunction-sections',
)

LDFLAGS = (
    '$(MCU)',
    '-Wl,--no-wchar-size-warning',
    '-specs=nosys.specs',
    '-specs=nano.specs',
    '-T$(LDSCRIPT)',
    '$(LIBDIR)',
    '$(LIBS)',
)

TAG_GENERIC = '# Generic Makefile (based on gcc)'
TAG_MODIFY_CPP = '# Modified for C++'
TAG_SOURCES_PATH = '# source path'
TAG_SOURCES_C = '# C sources'
TAG_SOURCES_ASM = '# ASM sources'
TAG_SOURCES_C_INC = '# C includes'
TAG_LIST_OF_OBJECTS = '# list of objects'
TAG_LIST_OF_CPP_OBJECTS = '# list of C++ objects'
TAG_LIFT_OF_ASM_OBJECTS = '# list of ASM program objects'
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

    def get_position_front(self, expression: str) -> int:
        return self.makefile.find(expression) - 1

    def get_position(self, expression: str) -> int:
        return self.makefile.find(expression)

    def get_position_behind(self, expression: str) -> int:
        return self.makefile.find(expression) + len(expression) + 1

    def flags(self, list_of_flags: tuple) -> str:
        return ''.join(map(lambda x: x + ' ', list_of_flags))[:-1]

    def set_variable(self, name: str, value: str):
        position_start = self.get_position_behind(name + ' ')
        i = position_start
        while self.makefile[i] != '\n':
            i += 1
        position_end = i
        self.makefile = self.makefile[:position_start] + ' ' + value + self.makefile[position_end:]

    def check_was_modified(self):
        if self.get_position(TAG_MODIFY_CPP) != -1:
            print('This Makefile was already mofified')
            exit()
        else:
            position = self.get_position_behind(TAG_GENERIC)
            self.makefile = self.makefile[:position] + TAG_MODIFY_CPP + '\n' + self.makefile[position:]

    def repair_multiple_definition(self, tag: str):
        position_start = self.get_position_behind(tag)
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

    def update_toolchain(self):
        self.replace('$(BINPATH)/', '$(BINPATH)')
        self.set_variable('BINPATH', '/opt/gcc-arm-none-eabi/bin/')

    def support_cpp(self):
        self.set_variable('CC', '$(BINPATH)$(PREFIX)g++')
        self.set_variable('CFLAGS', self.flags(CFLAGS))
        self.set_variable('LDFLAGS', self.flags(LDFLAGS))
        position = self.get_position(TAG_LIFT_OF_ASM_OBJECTS)
        self.makefile = self.makefile[:position] + TAG_LIST_OF_CPP_OBJECTS + CMD_OBJECTS_APPEND_CPP + self.makefile[position:]
        position = self.get_position_front('$(BUILD_DIR)/%.o: %.s Makefile | $(BUILD_DIR)')
        self.makefile = self.makefile[:position] + CMD_BUILD_CPP + self.makefile[position:]

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
            position = self.get_position_front(TAG_EOF)
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
        self.support_cpp()
        self.set_variable('OPT', '-Os')
        self.hide_command('$(CC)')
        self.hide_command('$(AS)')
        self.hide_command('$(CP)')
        self.hide_command('$(AR)')
        self.hide_command('$(SZ)')
        self.hide_command('$(HEX)')
        self.hide_command('$(BIN)')
        self.add_stm32_programmer()


if __name__ == '__main__':
    Makefile()
