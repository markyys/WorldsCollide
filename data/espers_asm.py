from memory.space import Bank, Reserve, Allocate, Write, Read
import instruction.asm as asm

def equipable_mod(espers):
    from data.characters import Characters

    character_id_address = 0x1cf8
    gray_out_if_equipped = 0xc35576
    set_text_color = 0xc35595
    equipped_esper_address = 0x161e
    esper_spells_address = 0xd86e01

    # Make completed espers yellow. Thanks to Lenophis for the asm

    # Verify routine -- make sure an esper isn't already equipped
    src = [
        asm.BCC("esper_NOPE"), # coming in, if the carry is clear, it can't be equipped
        asm.LDX(0x00, asm.DIR),
        asm.TXY(),
        "verify_loop",
        asm.LDA(0xe0, asm.DIR), # load esper
        asm.CMP(equipped_esper_address, asm.ABS_X), # does this character have this esper equipped already?
        asm.BEQ("esper_NOPE"),
        asm.A16(),
        asm.TXA(),
        asm.CLC(),
        asm.ADC(0x0025, asm.IMM16),
        asm.TAX(),
        asm.TDC(),
        asm.A8(),
        asm.INY(),
        asm.CPY(0x000c, asm.IMM16), # have we checked all available characters?
        asm.BNE("verify_loop"),
        # if after the entire loop nobody has it equipped, we can flag it as equippable! let's put it on!
        asm.SEC(),
        asm.RTS(),
        "esper_NOPE",
        # if somebody else already has this esper equipped, simply exit out and flag it as can't be equipped
        asm.CLC(), # TODO: add flag to allow multi-equipped espers by removing this line
        asm.RTS(),
    ]
    space = Write(Bank.C3, src, "verify esper isn't equipped")
    verify_esper_equipped = space.start_address
    print(f"verify_esper_equipped: {verify_esper_equipped:x}")

    # We need to determine how many spells an esper teaches
    # In: X = offset into esper_spell_address to first spell
    src = [
        asm.PHX(), # keep our current esper index
        asm.STZ(0xb4, asm.DIR), # zero out our scratch for this indicator
        asm.LDY(0x0005, asm.IMM16),
        "esper_count_loop",
        asm.LDA(esper_spells_address, asm.LNG_X), # load this esper's spell
        asm.CMP(0xff, asm.IMM8), # no spell?
        asm.BEQ("esper_spell_skip"),
        asm.INC(0xb4, asm.DIR), # add one to this esper's spell count
        "esper_spell_skip",
        asm.INX(),
        asm.INX(), # x+2 to get to next spell
        asm.DEY(),
        asm.BNE("esper_count_loop"),
        asm.PLX(), # restore our esper index
        asm.RTL(),
    ]
    space = Write(Bank.F0, src, "count esper spells")
    esper_spell_count = space.start_address_snes

    print(f"esper_spell_count: {esper_spell_count:x}")

    # We need to re-make the "determine who is equipping which espers" routine, because of more checks we need to add
    # We are adding in one additional check to see if a particular character has learned all of the spells that the esper teaches
    src = [
        asm.LDA(0xe0, asm.DIR), # load esper
        asm.STA(0x4202, asm.ABS), # multiplier
        asm.LDA(0x0b, asm.IMM8),  # 11 bytes per esper data at esper_spells_address
        asm.STA(0x4203, asm.ABS), # multiplier
        asm.NOP(), # wait
        asm.STZ(0xb3, asm.DIR), # scratch RAM
        asm.LDX(0x4216, asm.ABS), # load our product -- the offset into esper_spells_address
        asm.JSL(esper_spell_count),
        asm.LDY(0x0005, asm.IMM16), #each esper can teach up to 5 spells
        "check_esper_spells_loop",
        asm.LDA(esper_spells_address, asm.LNG_X), # load our spell that esper teaches
        asm.CMP(0xff, asm.IMM8), # no spell?
        asm.BEQ("check_count"), # branch and do our normal check if so. Note that we will not check any further in the loop since even in rando there isn't a spell after a no-entry
        # if we are here, we have a spell to teach. Now we check to see if this character has learned it
        asm.PHY(),
        asm.LDY(0x67, asm.DIR), # load our character index
        asm.LDA(0x0000, asm.ABS_Y), # load character ID
        asm.STA(0x4202, asm.ABS), # multiplier
        asm.LDA(0x36, asm.IMM8),
        asm.STA(0x4203, asm.ABS), # multiplier
        asm.TDC(),
        asm.LDA(esper_spells_address, asm.LNG_X), # load our spell again
        asm.A16(),
        asm.CLC(),
        asm.ADC(0x4216, asm.ABS), # add it to the product
        asm.TAY(),
        asm.A8(),
        asm.TDC(),
        asm.LDA(0x1a6e, asm.ABS_Y), # load spells known
        asm.PLY(),
        asm.CMP(0xff, asm.IMM8), # is this spell learned?
        asm.BNE("check_count"), # branch and go do our normal check if not. We know this esper hasn't taught this character every spell it can
        # at this point, this spell has been taught
        asm.INC(0xb3, asm.DIR), # increment spell taught count
        asm.INX(),
        asm.INX(), # X + 2 to get to next spell (of 5)
        asm.DEY(),
        asm.BNE("check_esper_spells_loop"), # more spells to check
        "check_count",
        asm.LDA(0xb3, asm.DIR), # load our spell taught count
        asm.CMP(0xb4, asm.DIR), # does it match the number of spells this esper teaches?
        asm.BNE("set_white_or_gray"),
        asm.LDA(0x30, asm.IMM8), # yellow text to indicate we're learned all spells
        asm.STA(0x29, asm.DIR), # update text color
        asm.STZ(0xb3, asm.DIR), # zero out scratch again, just in case
        asm.STZ(0xb4, asm.DIR), # zero out scratch again, just in case
        asm.LDA(0xe0, asm.DIR),
        asm.SEC(), # set carry to indicate to verify_esper_equipped that it may be equippable
        asm.RTS(),

        "set_white_or_gray",
        asm.LDX(0x00, asm.DIR),
        asm.LDY(0x0010, asm.IMM16),
        "loop",
        asm.LDA(equipped_esper_address, asm.ABS_X), # esper equipped by this character
        asm.CMP(0xe0, asm.DIR), # does it match?
        asm.BEQ("set_gray"), # branch if so, exit out
        asm.A16(),
        asm.TXA(),
        asm.CLC(),
        asm.ADC(0x0025, asm.IMM16), 
        asm.TAX(),
        asm.A8(),
        asm.DEY(),
        asm.BNE("loop"),
        asm.LDA(0x20, asm.IMM8), # if we got here, it's not equipped. Set white text
        asm.BRA("skip_one"),
        "set_gray",
        asm.LDA(0x2c, asm.IMM8), # gray text, blue background
        "skip_one",
        asm.STA(0x29, asm.DIR), # update text color
        asm.STZ(0xb3, asm.DIR), # zero out our scratch again, just in case
        asm.STZ(0xb4, asm.DIR), # zero out our scratch again, just in case
        asm.LDA(0xe0, asm.DIR),
        asm.SEC(), # set carry to indicate to verify_esper_equipped that it may be equippable
        asm.RTS(),
    ]
    space = Write(Bank.C3, src, "check if character has learned all spells")
    learned_all_check = space.start_address

    print(f"learned_all_check: {learned_all_check:x}")

    space = Reserve(0x358e6, 0x358eb, "equip esper if name not grayed out", asm.NOP())
    space.add_label("EQUIP_ESPER", 0x35902)
    space.write(
        asm.JSR(verify_esper_equipped, asm.ABS),
        asm.BCS("EQUIP_ESPER"),
    )
    # end lenophis edit

    space = Allocate(Bank.C3, 146, "equipable espers", asm.NOP())

    equip_table = space.next_address
    for esper in espers.espers:
        space.write(
            esper.equipable_characters.to_bytes(2, "little"),
        )

    store_character_id = space.next_address
    space.copy_from(0x31b61, 0x31b63)   # x = character slot, a = character id
    space.write(
        asm.STA(character_id_address, asm.ABS),
        asm.RTS(),
    )

    check_equipable = space.next_address
    space.write(
        asm.PHX(),
        asm.PHP(),
        asm.STA(0xe0, asm.DIR),         # save esper (for use by callers)
        asm.XY8(),
        asm.A16(),
        asm.ASL(),                      # a = esper id * 2 (2 bytes for character bits)
        asm.TAX(),                      # x = esper id * 2
        asm.PHX(),
        asm.LDA(character_id_address, asm.ABS), # a = character id
        asm.ASL(),                      # a = character id * 2 (2 bytes for character bits)
        asm.TAX(),                      # x = character id * 2
        asm.LDA(0xc39c67, asm.LNG_X),   # a = character bit mask
        asm.PLX(),
        asm.AND(equip_table, asm.LNG_X),# and character bit mask with esper equipable bit mask
        asm.BEQ("NOT_EQUIPABLE"),       # branch if result is zero
        asm.PLP(),
        asm.PLX(),
        asm.JMP(learned_all_check, asm.ABS),

        "NOT_EQUIPABLE",
        asm.PLP(),
        asm.PLX(),
        asm.CLC(), # clear carry to indicate to verify_esper_equipped that it can't be equipped
        asm.LDA(0x28, asm.IMM8),        # load text color (gray)
        asm.JMP(set_text_color, asm.ABS),
    )

    # TODO add new text type for this
    cant_equip_len = len("Can't equip!")
    cant_equip_error_text = space.next_address
    space.write(
        0x82, # C
        0x9a, # a
        0xa7, # n
        0xc3, # '
        0xad, # t
        0xff, #
        0x9e, # e
        0xaa, # q
        0xae, # u
        0xa2, # i
        0xa9, # p
        0xbe, # !
    )

    # change error message from "<character> has it!" to "Can't equip!"
    unequipable_error = space.next_address
    space.write(
        asm.LDA(0x1602, asm.ABS_X),     # a = first letter of name of character with esper equipped
        asm.CMP(0x80, asm.IMM8),        # compare against empty character (no character has esper equipped)
        asm.BCC("UNEQUIPABLE"),         # branch if not already equipped by another character

        "ALREADY_EQIPPED",
        asm.LDY(Characters.NAME_SIZE, asm.IMM8),    # y = name length
        asm.RTS(),

        "UNEQUIPABLE",
        asm.PLX(),                      # pull return address (do not return to vanilla already equipped)
        asm.LDX(0x0000, asm.IMM16),     # start at character zero in error message

        "PRINT_ERROR_LOOP",
        asm.LDA(cant_equip_error_text, asm.LNG_X),  # a = error_message[x]
        asm.STA(0x2180, asm.ABS),                   # print error_message[x]
        asm.INX(),
        asm.CPX(cant_equip_len, asm.IMM16),
        asm.BCC("PRINT_ERROR_LOOP"),
        asm.STZ(0x2180, asm.ABS),                   # print NULL
        asm.JMP(0x7fd9, asm.ABS),                   # print error_message
    )

    space = Reserve(0x31b61, 0x31b63, "skill menu store character id")
    space.write(
        asm.JSR(store_character_id, asm.ABS),
    )

    space = Reserve(0x35594, 0x35594, "already equipped esper name color")
    space.write(
        0x2c, # gray, blue shadow
    )

    space = Reserve(0x355af, 0x355b1, "load name length for esper already equipped error message", asm.NOP())
    space.write(
        asm.JSR(unequipable_error, asm.ABS),
    )

    space = Reserve(0x35524, 0x35526, "load esper palette", asm.NOP())
    space.write(
        asm.JSR(check_equipable, asm.ABS),
    )

    space = Reserve(0x358e1, 0x358e3, "load esper palette", asm.NOP())
    space.write(
        asm.JSR(check_equipable, asm.ABS),
    )

    space = Reserve(0x359b1, 0x359b3, "load esper palette", asm.NOP())
    space.write(
        asm.JSR(check_equipable, asm.ABS),
    )

