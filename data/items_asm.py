from memory.space import Bank, Reserve, Write, Read
import instruction.asm as asm

from data.item_names import name_id
import random

def stronger_atma_weapon():
    space = Reserve(0x20e59, 0x20e59, "atma weapon divisor exponent")
    space.write(4) # change modifier from 2^(5+1) to 2^(4+1)

def cursed_shield_mod(battles):
    src = [
        asm.LDA(battles, asm.IMM8),                 # a = battles required
        asm.INC(0x3ec0, asm.ABS),                   # increment cursed shield battle count
        asm.CMP(0x3ec0, asm.ABS),                   # compare battle count with battles required
        asm.BNE("NOT_UNCURSED"),                    # branch if count != required

        asm.STZ(0x3ec0, asm.ABS),                   # reset count back to zero
        Read(0x26003, 0x2600b),                     # set uncursed flag and change item to paladin shield
        asm.RTS(),

        "NOT_UNCURSED",
        asm.LDA(name_id["Cursed Shld"], asm.IMM8),  # a = cursed shield id
        asm.RTS(),
    ]
    space = Write(Bank.C2, src, "cursed shield uncursed check")
    uncurse_shield_check = space.start_address

    space = Reserve(0x25ffe, 0x2600b, "cursed shield battles increment", asm.NOP())
    space.write(
        asm.JSR(uncurse_shield_check, asm.ABS),
    )

def atma_weapon_palette(outer_bgr, middle_bgr, inner_bgr, white_bgr):
    # Set the atma weapon palette colors to the given BGR15s
    # Default hex: e801 0014 e77d fe7f c07c 0024 f71d a900
    # outer most blue is 0024 (byte offset 10)
    # middle blue is c07c (byte offset 8)
    # inner most blue is e77d (byte offset 4)
    # center white is f37f (byte offset 6)
    # The base address of the palette (Battle Animation Palette 31)
    ATMA_PALETTE_ADDR = 0x1261f0

    space = Reserve(ATMA_PALETTE_ADDR + 10, ATMA_PALETTE_ADDR + 11, "atma outer blue")
    space.write(outer_bgr.data)

    space = Reserve(ATMA_PALETTE_ADDR + 8, ATMA_PALETTE_ADDR + 9, "atma middle blue")
    space.write(middle_bgr.data)

    space = Reserve(ATMA_PALETTE_ADDR + 4, ATMA_PALETTE_ADDR + 5, "atma inner blue")
    space.write(inner_bgr.data)

    if white_bgr is not None:
        space = Reserve(ATMA_PALETTE_ADDR + 6, ATMA_PALETTE_ADDR + 7, "atma center white")
        space.write(white_bgr.data)

    # TODO: set the slash palette that appears over the enemy to match
    # this is palette 120, labelled as "Generic Blue Palette". modifying it likely breaks other things