
import random


class Storage:

    def __init__(self):
        self.data = [random.randint(0,100) for _ in range(10)]

    def __repr__(self) -> str:
        return " ".join(map(str, self.data))

    def __getitem__(self, index: tuple[int, int]) -> int:
        return self.data[index[0] + index[1]]

s = Storage()

print(s)
print(s[1,2])
