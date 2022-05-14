class EnemyGraphic():

    def __init__(self, id, data):
        self.id = id
        self.gfx_pointer = int.from_bytes(data[0:2], "little") # also including 3bpp; since it should always be set the same
        self.palette_pointer = int.from_bytes(data[2:4], "little") & 0xff7f
        self.large_template = (data[2] & 0x80) >> 7
        self.mould_index = data[4]

    def data(self):
        data = [0x00] * 5
        
        data[0:2] = self.gfx_pointer.to_bytes(2, "little")
        data[2:4] = self.palette_pointer.to_bytes(2, "little")
        data[2]   = (data[2] | (self.large_template << 7))
        data[4]   = self.mould_index

        return data

    def print(self):
        print(f"{self.id}: ")
        print(f"   gfx_pointer:     0x{self.gfx_pointer:x}")
        print(f"   palette_pointer: 0x{self.palette_pointer:x}")
        print(f"   large_template:  {self.large_template}")
        print(f"   mould_index:     {self.mould_index}")
        print()


if __name__ == '__main__':
    data = [0x27, 0x09, 0x00, 0x20, 0x10]
    eg = EnemyGraphic(0, data)
    eg.print()
    new_data = eg.data()
    print(' '.join(format(x, '02x') for x in new_data))
