#!/usr/bin/env python3
# wykys 2018
# The script parses the memory information from the linker script and
# the size program, and then displays them in a more readable form.

import sys
import bitmath
import argparse
import subprocess
from pathlib import Path
from operator import methodcaller

from rich import print
from rich.table import Table


def parse_size(num: str) -> bitmath.ALL_UNIT_TYPES:
    num = num.strip()
    last = num[-1]
    if last != 'B':
        if last.isalpha():
            num += 'i'
        num += 'B'
    return bitmath.parse_string(num).best_prefix()


class NotExistError(IOError):
    def __init__(self, name: str):
        self.error_text = f'{name} is not exists!'

    def __str__(self):
        return self.error_text


def is_exact_file(path, suffix):
    path = Path(path)
    return path.suffix == suffix and path.is_file()


def is_linker_script(path):
    return is_exact_file(path, '.ld')


def is_elf(path):
    return is_exact_file(path, '.elf')


def check_path(path, is_ok, max_recursive=None, recursive_index=0):
    path = Path(path)
    if path.is_dir():
        for sub_path in path.iterdir():
            if sub_path.is_dir() and (recursive_index < max_recursive or recursive_index is None):
                sub_path = check_path(
                    sub_path, is_ok, max_recursive, recursive_index + 1)
            if is_ok(sub_path):
                path = sub_path
                break

    if (path.exists() and is_ok(path)) or recursive_index:
        return path
    else:
        raise NotExistError(path)


def check_elf_path(path):
    return check_path(path, is_elf, max_recursive=2)


def check_linker_script_path(path):
    return check_path(path, is_linker_script, max_recursive=1)


def linker_script_parser(path):
    with open(path, 'r') as fr:
        script = fr.readlines()

    memory_flag = False
    memory = dict()

    for line in script:
        if 'MEMORY' in line:
            memory_flag = True
        elif memory_flag:
            if '}' in line:
                break
            elif 'LENGTH' in line:
                name = line.strip().split(':')[0].strip().split()[0].strip()
                data = line.strip().split(':')[1].strip().split(',')[
                    1].split('=')[1]
                memory[name] = parse_size(data)
    return memory


class SizeParser:
    def __init__(self) -> None:
        pass

    def parse_size_table(self, data):
        return list(
            map(
                methodcaller('strip'), data.split()
            )
        )[:-2]


def size_parser(path):
    result = subprocess.run(
        [
            '/opt/gcc-arm-none-eabi/bin/arm-none-eabi-size',
            path
        ],
        stdout=subprocess.PIPE
    )

    result = result.stdout.decode('utf-8')
    head, data = result.strip().split('\n')

    def parse_size_table(data):
        return list(map(methodcaller('strip'), data.split()))[:-2]

    head = parse_size_table(head)
    data = parse_size_table(data)

    size = dict()
    for i, name in enumerate(head):
        size[name] = parse_size(data[i])

    return size


class Memory:
    def __init__(self, name, size, use) -> None:
        self.name = name
        self.size = size
        self.use = use
        self.free = (size - use).best_prefix()
        self.percent = 100 * use / size


class MemoryUsage:
    def __init__(self, memory: list) -> None:
        self.memory = memory
        self.show()

    def show(self):
        NUMBER_OF_BARS = 40

        grid = Table.grid(expand=False)
        grid.add_column(justify='left', style='bold magenta')
        grid.add_column()
        grid.add_column(justify='left')
        grid.add_column()
        grid.add_column(justify='right', style='magenta')
        grid.add_column()
        grid.add_column(justify='right', style='cyan')
        grid.add_column(justify='center', style='')
        grid.add_column(justify='right', style='cyan')

        for memory in self.memory:

            bars = int(NUMBER_OF_BARS * memory.percent / 100)
            spaces = NUMBER_OF_BARS - bars

            grid.add_row(
                f'  {memory.name}',
                ' ',
                f'[red]{bars * "━"}[/][#444444]{spaces * "━"}[/]',
                ' ',
                f'{memory.percent:.0f} %',
                '  ',
                f'{memory.use.format("{value:.1f} {unit}")}',
                ' / ',
                f'{memory.size.format("{value:.1f} {unit}")}'
            )

        print(grid)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='stm-size',
        description='The script parses the memory information from the linker'
        'script and the size program, and then displays them in a more'
        'readable form.'
    )
    parser.add_argument(
        '-l',
        '--linker-script',
        dest='path_linker',
        action='store',
        default='.',
        help='destination linker script',
    )
    parser.add_argument(
        '-e',
        '--elf',
        dest='path_elf',
        action='store',
        default='.',
        help='destination elf file',
    )

    args = parser.parse_args()

    try:
        path_linker = check_linker_script_path(args.path_linker)
        path_elf = check_elf_path(args.path_elf)

    except NotExistError as e:
        print(str(e), file=sys.stderr)
        exit(-1)

    memory = linker_script_parser(path_linker)
    size = size_parser(path_elf)

    use_ram = size['data'] + size['bss']
    use_flash = size['text'] + size['data']

    MemoryUsage(
        [
            Memory(
                name='RAM',
                size=memory['RAM'],
                use=use_ram
            ),
            Memory(
                name='FLASH',
                size=memory['FLASH'],
                use=use_flash
            )
        ]
    )
