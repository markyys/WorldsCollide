from data.enemy_graphic import EnemyGraphic
from data.structures import DataArray

class EnemyGraphics():
    DATA_START = 0x127000
    DATA_END = 0x12777f
    DATA_SIZE = 5

    def __init__(self, rom):
        self.rom = rom

        self.data = DataArray(self.rom, self.DATA_START, self.DATA_END, self.DATA_SIZE)

        self.graphics = []
        for index in range(len(self.data)):
            graphic = EnemyGraphic(index, self.data[index])
            self.graphics.append(graphic)
    
    def write(self):
        for index in range(len(self.graphics)):
            self.data[index] = self.graphics[index].data()

        self.data.write()

    def print(self):
        for graphic in self.graphics:
            graphic.print()

