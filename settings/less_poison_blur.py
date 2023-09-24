## Original mod from Beyond Chaos
## https://github.com/FF6BeyondChaos/BeyondChaosRandomizer/blob/main/BeyondChaos/patches.py
## look for section beginning with "nicer_poison(fout):"
from memory.space import Reserve
import instruction.asm as asm

### reduce poison pixellation effect while walking
### does not affect poison sound effect while on overworld map
class LessPoisonBlur:
    def __init__(self):
        self.mod()

    def mod(self):
        # make poison pixelation effect 1/10 of it's vanilla amount in dungeons/towns
        space = Reserve(0x00e82, 0x00e9f, "town/dungeon poison gfx fix")
        space.write(
            [0x0F, 0x0F, 0x0F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F,
             0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F,
             0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x0F, 0x0F, 0x0F]
        )
        
        # remove poison pixelation on the overworld
        space = Reserve(0x2e1864, 0x2e1865, "overworld poison gfx fix")
        space.write(
            asm.LDA(0x00, asm.IMM8),
        )
