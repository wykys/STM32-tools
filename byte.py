# wykys 2018
# The object for computing and printing binary units


class Byte:
    _unit_dict = {
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

    def __init__(self, number=0):
        self.value = number

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, number):
        if isinstance(number, str):
            if number.isdigit():
                self._value = int(number)
            else:
                for i, num in enumerate(number):
                    if num.isalpha():
                        unit = number[i:].strip()
                        number = float(number[:i])
                        break

                self._value = int(number * self._unit_dict[unit])

        else:
            self._value = int(number)

    def __add__(self, other):
        return Byte(self.value + other.value)

    def __sub__(self, other):
        return Byte(self.value - other.value)

    def __str__(self):
        if self.value >= 2**20:
            return '{:.1f} MiB'.format(self.value / 2**20)
        elif self.value >= 2**10:
            return '{:.1f} KiB'.format(self.value / 2**10)
        else:
            return '{:.1f} B'.format(self.value)

    def __repr__(self):
        return self.__str__()
