from memory.space import Reserve, Write, Bank, Read
import instruction.asm as asm

class WorldMap:
    def __init__(self, rom, args):
        self.rom = rom
        self.args = args

    def y_chocobo(self):
        # TEMP_BYTE = 0xe8
        # SWITCH_TO_CHOCO_BIT = 0x08 # an otherwise unused bit in E8
        # # First, we need to catch that Y was pressed. To do so, we'll follow similar logic as EE/2067, which looks for the A button to be pressed to switch to the airship.
        # # We'll use an otherwise unused bit in $E8 to indicate that we want to switch to chocobo
        # # E8 bits documented on https://www.ff6hacking.com/wiki/doku.php?id=ff3:ff3us:doc:asm:ram:world_ram:
        #     # 40 = airship taking off
        #     # 04 = arrows are not locked
        #     # 02 = arrows are shown
        #     # Tested glitchy bits
        #         # 80 = when set, map flashes glitchiness
        #         # 20 = when set, causes sprite locks to get locked such that arrows move them and map flashes glitchiness
        #         # 10 = screen goes black, party is back at airship location, sprites & palettes modified upon getting on airship
        #     # 08 = seems to be safe for this purpose
        # src = [
        #     asm.LDA(0x09, asm.DIR),                 # Load buttons pressed (byte 2 -- B, Y, Select, Start, Up, Down, Left, Right)
        #     asm.BIT(0x40, asm.IMM8),                # Y pressed?
        #     asm.BEQ("Y_NOT_PRESSED"),
        #     asm.LDA(TEMP_BYTE, asm.DIR),            # Load the temporary byte
        #     asm.ORA(SWITCH_TO_CHOCO_BIT, asm.IMM8), # set the bit
        #     asm.STA(TEMP_BYTE, asm.DIR),            # store it back in for use below
        #     "Y_NOT_PRESSED",
        #     asm.LDA(0x08, asm.DIR),                 # Displaced code -- Load buttons pressed (byte 1 -- A, X, L, R)
        #     asm.BIT(0x80, asm.IMM8),                # Displaced code -- A pressed?
        #     asm.RTS(),
        # ]
        # space = Write(Bank.EE, src, "check Y button press")
        # self.y_button_check = space.start_address
        
        # space = Reserve(0x2e2067, 0x2e206a, "A button pressed?", asm.NOP())
        # space.write(
        #     asm.JSR(self.y_button_check, asm.ABS)
        # )

        # Second, we'll act upon the $E8 value above. Here, we'll mimic the swap to the airship at EE/03F8 by calling the similar method InitChoco
        # ref: https://github.com/everything8215/ff6/blob/main/src/world/main.asm#L13117
        # @03fe:
        # lda     $11f6
        # ora     #$10       --- this is checked in ee/0377 routine. Unclear why
        # sta     $11f6
        # jsr     _ee94d4
        # lda     #$8f
        # sta     hINIDISP
        # sei
        # stz     hHDMAEN
        # stz     $11fd
        # stz     $11fe
        # stz     $11ff
        # lda     $e0
        # sta     $1f60
        # lda     $e2
        # sta     $1f61
        # jsr     PopMode7Vars -- don't include
        # jmp     InitAirship  -- don't include
        src = [
            asm.LDA(0x09, asm.DIR),            # Load buttons pressed (byte 2 -- B, Y, Select, Start, Up, Down, Left, Right)
            asm.BIT(0x40, asm.IMM8),           # Y pressed?
            asm.BEQ("Y_NOT_PRESSED"),
            #Read(0x2e03fe, 0x2e0424),          # copy from the similar code that loads airship (up to but not including PopMode7Vars, since that's called by InitChoco)
            # Just copying it as-is causes it to play the Airship takeoff animation and us to switch to chocobo with no sprite
            # start copy-paste

            # Removing these 3 lines readds the chocobo sprite
            # asm.LDA(0x11f6, asm.ABS),
            # asm.ORA(0x10, asm.IMM8),    # Remove -- this is 0 for the normal InitChoco call
            # asm.STA(0x11f6, asm.ABS), 

            # Removing this line removes the "Airship taking off" animation
            #asm.JSR(0x94d4, asm.ABS),

            # These lines don't seem to have any effect, so commenting them out
            # Having them in place causes graphical flickering upon reentering town
            #Read(0x2e0409, 0x2e0411), # Just copying LDA #$8f, STA SNES.INIDISP, SEI, and STZ SNES.HDMAEN

            # Having these 3 copy-pasted lines moves me a relative position on the world map
            # asm.STZ(0x11fd, asm.ABS), # 0x89 for normal chocobo -- World Map Event Pointer
            # asm.STZ(0x11fe, asm.ABS), # 0x33 for normal chocobo
            # asm.STZ(0x11ff, asm.ABS), # 0xcc for normal chocobo
            # These 6 commands don't seem to be needed
            # asm.LDA(0x89, asm.IMM8),
            # asm.STA(0x11fd, asm.ABS),
            # asm.LDA(0x33, asm.IMM8),
            # asm.STA(0x11fe, asm.ABS),
            # asm.LDA(0xcc, asm.IMM8),
            # asm.STA(0x11ff, asm.ABS),

            # These 4 commands don't seem to matter
            # asm.LDA(0xe0, asm.DIR),   # Load position X
            # asm.STA(0x1f60, asm.ABS), # Store position X (in tiles)
            # asm.LDA(0xe2, asm.DIR),   # Load position Y
            # asm.STA(0x1f61, asm.ABS), # Store position Y (in tiles)
            # end copy-paste
            asm.JMP(0x86cc, asm.ABS),          # Jump to the "InitChoco" routine
            # Remaining issue: After this code executes, entering a town doesn't work -- screen goes black


            # commented out for quick test
            "Y_NOT_PRESSED",
            # asm.LDA(0xe8, asm.DIR),            # Displaced Code -- check for "Airship taking off"
            # asm.BIT(0x40, asm.IMM8),                # Displaced Code
            # asm.RTS(),
        ]
        # space = Write(Bank.EE, src, "check switch to Chocobo")
        # self.choco_switch = space.start_address
        # print(f"{self.choco_switch:x} {len(space)}")
        

        # space = Reserve(0x2e03f8, 0x2e03fb, "airship bit set?", asm.NOP())
        # space.write(
        #     asm.JSR(self.choco_switch, asm.ABS)
        # )

        # quick test: does it work if I replace the airship logic?
        # answer: sort of -- I can load a town, but my sprite is invisible or corrupted (depending on character)
        space = Reserve(0x2e03f2, 0x2e042a, "airship takeoff", asm.NOP())
        space.write(
            src
        )

        # E8 seems to be getting set every time -- why don't I just check the Y button directly in this latter spot?

    def world_minimap_high_contrast_mod(self):
        # Thanks to Osteoclave for identifying these changes

        # Increases the sprite priority for the minimap sprites
        # So it gets drawn on top of the overworld instead of being translucent
        #ee4146=1b
        space = Reserve(0x2e4146, 0x2e4146, "minimap sprite priority")
        space.write(0x1b) # default: 0x0b

        # Colors bytes: gggrrrrr, xbbbbbgg
        # High contrast location indicator on minimaps
        # d2eeb8=ff + d2eeb9=7f
        # d2efb8=ff + d2efb9=7f
        location_indicator_addr = [0x12eeb8,  # WoB default: 1100
                                   0x12efb8]  # WoR default: 1100
        for loc_addr in location_indicator_addr:
            space = Reserve(loc_addr, loc_addr+1, "high contrast minimap indicator")
            space.write(0xff, 0x7f)

        # d2eeba=ff + d2eebb=7f
        # d2efba=ff + d2efbb=7f
        location_indicator_addr = [0x12eeba,  # WoB default: 1f00
                                   0x12efba]  # WoR default: 1f00
        for loc_addr in location_indicator_addr:
            space = Reserve(loc_addr, loc_addr+1, "high contrast minimap indicator")
            space.write(0xff, 0x7f) 

        # Additional minimap palette mods
        # default: 84 10 e7 1c 4a 29 10 42 ff 7f
        # WoB: d2eea2=00 + d2eea3=14 + d2eea4=82 + d2eea5=28 + d2eea6=e4 + d2eea7=38 + d2eea8=67 + d2eea9=51 + d2eeaa=9c + d2eeab=02
        # WoR: d2efa2=00 + d2efa3=14 + d2efa4=82 + d2efa5=28 + d2efa6=e4 + d2efa7=38 + d2efa8=67 + d2efa9=51 + d2efaa=9c + d2efab=02
        minimap_palette_bytes = [0x00, 0x14, 0x82, 0x28, 0xe4, 0x38, 0x67, 0x51, 0x9c, 0x02]
        minimap_palette_addr = [0x12eea2, # WoB
                                0x12efa2] # WoR
        for addr in minimap_palette_addr:
            space = Reserve(addr, addr+len(minimap_palette_bytes)-1, "minimap palette")
            space.write(minimap_palette_bytes)

        # This changes the color of the Floating Continent (pre-floating) on WoB
        # default: e7 1c 4a 29 10 42
        # d2eeac=82 + d2eead=28 + d2eeae=e4 + d2eeaf=38 + d2eeb0=67 + d2eeb1=51
        addr = 0x12eeac
        minimap_palette_bytes = [0x82, 0x28, 0xe4, 0x38, 0x67, 0x51]
        space = Reserve(addr, addr+len(minimap_palette_bytes)-1, "floating continent palette")
        space.write(minimap_palette_bytes)

    def mod(self):
        if self.args.world_minimap_high_contrast:
            self.world_minimap_high_contrast_mod()
        self.y_chocobo()