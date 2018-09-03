#!/usr/bin/env python3
import argparse
import sys
import subprocess
from pathlib import Path


class Byte:
    def __init__(self, number):
        self._unit_dict = {
            'B': 1,
            'K': 2**10,
            'M': 2**20,
            'KB': 2**10,
            'KiB': 2**10,
            'MiB': 2**20,
            'GiB': 2**30,
            'TiB': 2**40,
            'PiB': 2**50,
            'EiB': 2**60,
            'ZiB': 2**70,
            'YiB': 2**80,
            'kB': 10**3,
            'MB': 10**6,
            'GB': 10**9,
            'TB': 10**12,
            'PB': 10**15,
            'EB': 10**18,
            'ZB': 10**21,
            'YB': 10**24,
        }
        if type(number) is str:
            if number.isdigit():
                self.bytes = int(number)
            else:
                for i in range(len(number)):
                    if number[i].isalpha():
                        unit = number[i:].strip()
                        number = float(number[:i])
                        break

                self.bytes = int(number * self._unit_dict[unit])

        else:
            self.bytes = int(number)

    def get_bytes(self):
        return self.bytes

    def set_bytes(self, number):
        self.__init__(number)

    def __add__(self, other):
        return Byte(self.bytes + other.bytes)

    def __str__(self):
        if self.bytes >= 2**20:
            return '{:.1f} MiB'.format(self.bytes / 2**20)
        elif self.bytes >= 2**10:
            return '{:.1f} KiB'.format(self.bytes / 2**10)
        else:
            return '{:.1f} B'.format(self.bytes)

    def __repr__(self):
        return self.__str__()


class NotExist(Exception):
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


def check_path(path, is_ok, max_recursive=float('inf'), recursive_index=0):
    path = Path(path)
    if path.is_dir():
        for sub_path in path.iterdir():
            if sub_path.is_dir() and recursive_index < max_recursive:
                sub_path = check_path(sub_path, is_ok, max_recursive, recursive_index + 1)
            if is_ok(sub_path):
                path = sub_path
                break

    if (path.exists() and is_ok(path)) or recursive_index:
        return path
    else:
        raise NotExist(path)


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
        return list(map(lambda s: s.strip(), data.split()))[:-2]

    head = parse_size_table(head)
    data = parse_size_table(data)

    size = dict()
    for i in range(len(head)):
        size[head[i]] = Byte(data[i])

    return size


def calculate_percentages(use_memory, all_memory):
    return use_memory.get_bytes() / (all_memory.get_bytes() / 100)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
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

    try:
        path_linker = check_linker_script_path(parser.parse_args().path_linker)
        path_elf = check_elf_path(parser.parse_args().path_elf)
    except NotExist as e:
        print(str(e), file=sys.stderr)
        exit(-1)

    print(path_linker)
    print(path_elf)

    memory = linker_script_parser(path_linker)
    size = size_parser(path_elf)

    use_ram = size['data'] + size['bss']
    use_flash = size['text'] + size['data']

    print('USE RAM: {} of {} ({:.0f} %)'.format(use_ram, memory['RAM'], calculate_percentages(use_ram, memory['RAM'])))
    print('USE FLASH: {} of {} ({:.0f} %)'.format(use_flash, memory['FLASH'], calculate_percentages(use_flash, memory['FLASH'])))
