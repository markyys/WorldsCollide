from event.event import *
import data.npc_bit as npc_bit

class NarsheMoogleDefense(Event):
    WOB_MAP_ID = 0x33

    def name(self):
        return "Narshe Moogle Defense"

    def init_event_bits(self, space):
        space.write(
            field.SetEventBit(npc_bit.TERRA_COLLAPSED_NARSHE_WOB), # show terra
            field.ClearEventBit(npc_bit.MARSHAL_NARSHE_WOB),       # do not show marshal
        )

    def refresh_characters_and_select_parties_with_moogles_mod(self):
        # Write a function for selecting parties or moogle replacements

        # map of characters to replacement moogles. Our logic will be to replace any characters not in our party with their mapped moogle.
        # index is the character (0 - 14) -- note: no Terra, Locke, or Umaro replacement
        # value is the associated replacement Moogle (-1 = no replacement)
        MOOGLE_REPLACEMENT = [
            -1, #TERRA
            -1, #LOCKE
            0x12,
            0x13,
            0x14,
            0x15,
            0x16,
            0x17,
            0x18,
            0x19,
            0x0A, # MOG
            0x1A,
            0x1B,
            -1, #UMARO
        ]

        # create all available characters, select count parties, delete characters not placed into any party
        src = [
            field.Call(field.DELETE_ALL_CHARACTERS),
        ]

        for character_idx, moogle_id in enumerate(MOOGLE_REPLACEMENT):
            next_character_branch = f"NEXT_CHARACTER_{character_idx}"
            if moogle_id == -1:
                # no moogle; check if the character exists -- If so, create entity. Vanilla logic from CA/C90B
                src += [
                    field.BranchIfEventBitClear(0x2F0 + character_idx, next_character_branch),
                    field.CreateEntity(character_idx),
                    next_character_branch,
                ] 
            else:
                # moogle exists -- check if the character exists -- if not, replace with moogle.
                src += [
                    field.BranchIfEventBitSet(0x2F0 + character_idx, next_character_branch),
                    # Make character look like a moogle
                    field.SetSprite(character_idx, self.characters.get_sprite(self.characters.MOG)),
                    field.SetPalette(character_idx, self.characters.get_palette(self.characters.MOG)),
                    # Give it the name and properties of the moogle #TODO: average moogle level to parties
                    field.SetName(character_idx, moogle_id),
                    field.SetProperties(character_idx, moogle_id),
                    next_character_branch,
                    field.CreateEntity(character_idx),
                ]
        src += [
            field.RefreshEntities(),
            field.SelectParties(3),
            field.Call(field.DELETE_CHARACTERS_NOT_IN_ANY_PARTY),
            field.RefreshEntities(),
            field.Return(),
        ]
        space = Write(Bank.CC, src, "field function refresh characters and select three parties with moogles")
        self.refresh_characters_and_select_parties_with_moogles = space.start_address

    def mod(self):
        # Change the NPC bit that activates Marshal
        marshal_npc = self.maps.get_npc(self.WOB_MAP_ID, 0x12)
        marshal_npc.event_byte = npc_bit.event_byte(npc_bit.MARSHAL_NARSHE_WOB)
        marshal_npc.event_bit = npc_bit.event_bit(npc_bit.MARSHAL_NARSHE_WOB)

        # Change the TERRA NPC such that it triggers the battle
        terra_npc = self.maps.get_npc(self.WOB_MAP_ID, 0x19)
        terra_npc.unknown1 = 0 # part of animation
        terra_npc.sprite = 106
        terra_npc.palette = 6
        terra_npc.split_sprite = 1
        terra_npc.direction = direction.DOWN

        # clear the scenes after terra falls in hole for event initialization
        prepared_dialog = 0x32 # reuse "LOCKE: Wonderful There's a whole bunch of 'em"
        self.dialogs.set_text(prepared_dialog, "Prepared?<line><choice> Yes<line><choice> No<end>")
        space = Reserve(0xca2e6, 0xca754, "terra falls in hole scenes", field.NOP())
        space.write(
            field.DialogBranch(prepared_dialog,
                               dest1 = space.end_address + 1,
                               dest2 = field.RETURN)
        )
        terra_npc.set_event_address(space.start_address)

        # clear the locke drop-down animation at the start of event
        space = Reserve(0xca75b, 0xca7be, "locke drops down before battle", field.NOP())
        space.write(
            field.StartSong(13), # play song: Locke
            field.SetEventBit(event_bit.TEMP_SONG_OVERRIDE), # keep song playing
            field.FadeInScreen(speed = 2),
            field.WaitForFade(),
        )

        # Clear guard dialog
        space = Reserve(0xca7ee, 0xca7f0, "dialog: Now we gotcha!", field.NOP())

        # ensure that the terra falls in hole event never triggers, as we're reusing the associated event bit
        space = Reserve(0xca2e5, 0xca2e5, "terra falls in hole event start")
        space.write(
            field.Return()
        )
        # Clear use of event_bit.12E (TERRA_COLLAPSED_NARHSE_WOB) at cc/aaab so that we can reuse that bit
        space = Reserve(0xcaaab, 0xcaaac, "set terra falls event bit", field.NOP())

        # No dialog starting at cc/a85f -- reasonable point to add in the Marshal NPC
        space = Reserve(0xca85f, 0xca86f, "dialog: There's a whole bunch of 'em + Kupo", field.NOP())
        space.write(
            field.SetEventBit(npc_bit.MARSHAL_NARSHE_WOB), # show the Marshal NPC
        )

        # No dialog at cc/a8b3
        space = Reserve(0xca8b3, 0xca8b6, "dialog: Moogles! Are you saying you want to help me?", field.NOP())

        # No Kupo!!! dialog
        space = Reserve(0xca8d2, 0xca8d4, "dialog: Kupo!!!", field.NOP())

        # Disable cc/a905 - cc/a93a
        space = Reserve(0xca905, 0xca93a, "moogle defense explain", field.NOP())
        space.write(
            field.Branch(space.end_address + 1), # skip nops
        )

        # Change logic at a93a - aa03 for moogles 
        # - make sure it doesn't replace characters we have
        # - use party selection screen to select the party (with Moogles filled in)
        self.refresh_characters_and_select_parties_with_moogles_mod()

        space = Reserve(0xca93b, 0xcaa04, "moogle defense party creation", field.NOP())
        space.write(
            field.Call(self.refresh_characters_and_select_parties_with_moogles),
            field.Branch(space.end_address + 1), # skip nops
        )

        # Victory condition (marshal defeated)
        # Remove moogles and party 
        src = [
            field.FadeOutScreen(),
            field.WaitForFade(),

            field.ClearEventBit(event_bit.TEMP_SONG_OVERRIDE), # allow song to change on map change
            field.ClearEventBit(npc_bit.MARSHAL_NARSHE_WOB), # Remove Marshal
            field.ClearEventBit(npc_bit.TERRA_COLLAPSED_NARSHE_WOB), # Remove collapsed Terra
            field.HideEntity(0x1B), # the exit block at top of map

            Read(0xcaded, 0xcadf2), # load map
        ]
        for character_idx in range(self.characters.CHARACTER_COUNT):
            src += [
                # Remove all characters from parties
                field.RemoveCharacterFromParties(character_idx),
                # Restore character appearance, name, and properties
                field.SetSprite(character_idx, self.characters.get_sprite(character_idx)),
                field.SetPalette(character_idx, self.characters.get_palette(character_idx)),
                field.SetName(character_idx, character_idx),
                field.SetProperties(character_idx, character_idx),
            ]
        src += [ 
            field.Call(field.REFRESH_CHARACTERS_AND_SELECT_PARTY),

            field.FreeScreen(),

            field.FadeInScreen(),
            field.WaitForFade(),

            field.SetEventBit(event_bit.FINISHED_MOOGLE_DEFENSE),
            field.FreeMovement(),
            field.Return(),
        ]
        space = Reserve(0xcade5, 0xcb04f, "moogle defense victory", field.NOP())
        space.write(src)



