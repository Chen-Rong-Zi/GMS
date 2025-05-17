#!/usr/bin/python3
class HeapUnit:

    def __init__(self, onwer, value=None):
        self.owner = onwer
        self.value = value
        print(f'alloc {self.owner} {self.value = }')

    def mutate(self, value):
        assert isinstance(value, int)
        print(f'mutate {self.owner} {self.value = }')
        self.value = value

    def move(self, onwer):
        self.owner = onwer
        print(f'move {self.owner} {self.value = }')

    def get_value(self):
        assert self.owner
        return self.value

    def release(self):
        print(f'relase {self.owner}')
        self.owner = None
