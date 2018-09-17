#!/usr/bin/env python3
# wykys 2018
# The script parses the memory information from the linker script and
# the size program, and then displays them in a more readable form.

import argparse
import sys
import subprocess
from pathlib import Path
from colors import Colors
from byte import Byte
from operator import methodcaller


class NotExistError(IOError):
    def __init__(self, name: str):
        self.error_text = '{} is not exists!'.format(name)

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
                sub_path = check_path(sub_path, is_ok, max_recursive, recursive_index + 1)
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
                length = Byte(line.strip().split(':')[1].strip().split(',')[1].split('=')[1])
                memory[name] = length
    return memory


def print_memory(memory):
    for name, length in memory.items():
        print('{}\t{}'.format(name, length))


def size_parser(path):
    result = subprocess.run(['arm-none-eabi-size', path], stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8')
    head, data = result.strip().split('\n')

    def parse_size_table(data):
        return list(map(methodcaller('strip'), data.split()))[:-2]

    head = parse_size_table(head)
    data = parse_size_table(data)

    size = dict()
    for i, name in enumerate(head):
        size[name] = Byte(data[i])

    return size


def calculate_percentages(use_memory, all_memory):
    return use_memory.value / (all_memory.value / 100)


def create_table(name, use_memory, all_memory, color=True):
    columns = 30
    width = columns - 2
    percent = calculate_percentages(use_memory, all_memory)
    bar = width if percent >= 100 else int(width*percent/100)

    head_str = '{} MEMORY {:.2g} %'.format(name, percent)
    all_str = 'All:'
    use_str = 'Use:'
    free_str = 'Free:'

    head_width_tag = '{:^' + str(width) + '}'
    all_width_tag = all_str + '{:>' + str(width - len(all_str)) + '}'
    use_width_tag = use_str + '{:>' + str(width - len(use_str)) + '}'
    free_width_tag = free_str + '{:>' + str(width - len(free_str)) + '}'

    if color:
        if percent < 60:
            color = Colors.bg.green + Colors.fg.darkgrey + Colors.bold
        elif percent < 80:
            color = Colors.bg.orange + Colors.fg.black + Colors.bold
        else:
            color = Colors.bg.red + Colors.fg.black + Colors.bold
    else:
        color = Colors.bold

    head = head_width_tag.format(head_str)
    head = ''.join((color, head[:bar], Colors.reset + Colors.bold, head[bar:], Colors.reset))

    table = []
    table.append('╔{}╗'.format('═'*width))
    table.append('║{}║'.format(head))
    table.append('╟{}╢'.format('─'*width))
    table.append('║{}║'.format(all_width_tag.format(str(all_memory))))
    table.append('║{}║'.format(use_width_tag.format(str(use_memory))))
    table.append('║{}║'.format(free_width_tag.format(str(all_memory - use_memory))))
    table.append('╚{}╝'.format('═'*width))
    return table


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
    parser.add_argument(
        '-c',
        '--color',
        dest='color',
        action='store_true',
        default=False,
        help='activated color output'
    )
    parser.add_argument(
        '-v',
        '--vertical',
        dest='table_rate',
        action='store_true',
        default=False,
        help='prints the tables underneath'
    )

    try:
        path_linker = check_linker_script_path(parser.parse_args().path_linker)
        path_elf = check_elf_path(parser.parse_args().path_elf)
    except NotExistError as e:
        print(str(e), file=sys.stderr)
        exit(-1)

    memory = linker_script_parser(path_linker)
    size = size_parser(path_elf)

    use_ram = size['data'] + size['bss']
    use_flash = size['text'] + size['data']

    color = parser.parse_args().color
    ram = create_table('RAM', use_ram, memory['RAM'], color)
    flash = create_table('FLASH', use_flash, memory['FLASH'], color)

    if parser.parse_args().table_rate:
        for line in ram + flash:
            print(line)
    else:
        for line_ram, line_flash in zip(ram, flash):
            print('{} {}'.format(line_ram, line_flash))
