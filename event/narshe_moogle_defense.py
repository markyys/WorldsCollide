from event.event import *
import data.npc_bit as npc_bit
from constants.entities import character_id
import data.direction

class NarsheMoogleDefense(Event):
    WOB_MAP_ID = 0x33

    def name(self):
        return "Narshe Moogle Defense"

    def character_gate(self):
        return self.characters.MOG

    def init_rewards(self):
        self.reward = self.add_reward(RewardType.CHARACTER | RewardType.ESPER | RewardType.ITEM)

    def init_event_bits(self, space):
        if self.args.character_gating:
            space.write(
                # Hide Arvis until you have Mog
                field.ClearEventBit(npc_bit.ARVIS_INTRO),
            )
        else:
            space.write(
                # Always show Arvis
                field.SetEventBit(npc_bit.ARVIS_INTRO),
            )
        space.write(
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
            field.FadeOutScreen(),
            field.WaitForFade(),
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
                    # Give it the name and properties of the moogle
                    field.SetName(character_idx, moogle_id),
                    field.SetProperties(character_idx, moogle_id),
                    field.CreateEntity(character_idx),
                    field.RefreshEntities(),
                ]
                if self.args.start_average_level:
                    src += [
                        # Average character level via field command - example ref: CC/3A2C
                        field.AverageLevel(character_idx),
                        field.RestoreHp(character_idx, 0x7f), # restore all HP
                        field.RestoreMp(character_idx, 0x7f), # restore all HP
                    ]
                src += [
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
        if self.args.character_gating:
            self.add_gating_condition() #TODO

        # Change the NPC bit that activates Marshal
        marshal_npc = self.maps.get_npc(self.WOB_MAP_ID, 0x12)
        marshal_npc.event_byte = npc_bit.event_byte(npc_bit.MARSHAL_NARSHE_WOB)
        marshal_npc.event_bit = npc_bit.event_bit(npc_bit.MARSHAL_NARSHE_WOB)

        # ensure that the terra falls in hole event never triggers, as we're reusing the associated event bit
        space = Reserve(0xca2e5, 0xca2e5, "terra falls in hole event start")
        space.write(
            field.Return()
        )

        # Actions after accepting
        src = [
            field.FadeOutScreen(),
            field.WaitForFade(),
            field.HideEntity(field_entity.PARTY0),
            field.LoadMap(0x32, direction.UP, True, 55, 11),
            field.CreateEntity(character_id["TERRA"]),
            field.EntityAct(character_id["TERRA"], True,
                field_entity.SetPosition(55, 11),
                field_entity.Turn(data.direction.UP)
            ),
            field.ShowEntity(character_id["TERRA"]),
            field.FadeInScreen(),
            field.WaitForFade(),
            field.Call(0xCCA2EB) # 'Got her!' scene
        ]
        space = Write(Bank.CC, src, "load narshe caves map for Terra event")
        got_her_map_change = space.start_address

        # Change Arvis Script
        prepared_dialog = 0x21 # reuse "OLD MAN: Make your way out through the mines! I’ll keep these brutes occupied!"
        self.dialogs.set_text(prepared_dialog, "ARVIS: Took you long enough! Will you help?<line><choice> Yes<line><choice> No<end>")
        space = Reserve(0xca06f, 0xca07d, "arvis dialog", field.NOP())
        space.write(
             field.DialogBranch(prepared_dialog,
                                dest1 = got_her_map_change,
                                dest2 = field.RETURN)
        )

        # Clear got her dialog
        space = Reserve(0xca2f0, 0xca2f2, "dialog: Got her", field.NOP()) # 'Got her' dialog

        # clear out the flashback, but show "Locke" in to allow for drop-down
        space = Reserve(0xca436, 0xca75a, "Terra flashback", field.NOP()) # with fade out
        space.write(
            field.ShowEntity(field_entity.PARTY0),
            field.StartSong(13), # play song: Locke
            field.SetEventBit(event_bit.TEMP_SONG_OVERRIDE), # keep song playing
            field.Branch(space.end_address + 1), # skip nops
        )

        # Change Locke to party leader
        locke_action_queues = [0xca76b, 0xca77b, 0xca786, 
                               0xca78e, 0xca793 , 0xca799, 0xca79f, 
                               0xca7a4, 0xca7a8, 0xca7af, 0xca7b3, 
                               0xca7b8]
                               # 0xca868 NO-OP'd below
        for address in locke_action_queues:
            space = Reserve(address, address, "locke drop down to protect terra")
            space.write(field_entity.PARTY0)

        # Clear guard dialog
        space = Reserve(0xca7ee, 0xca7f0, "dialog: Now we gotcha!", field.NOP())

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

        # Clear use of event_bit.12E (TERRA_COLLAPSED_NARHSE_WOB) and event_bit.003 (moogle defense) at cc/aaab so that we can reuse 12E 
        # and so that 003 doesn't cause issues at WoB Narshe entrance
        space = Reserve(0xcaaab, 0xcaaae, "set terra falls event bit & initiated moogle defense bit", field.NOP())

        # Victory condition (marshal defeated)
        # Remove moogles from party 
        src = [
            field.FadeOutScreen(),
            field.WaitForFade(),

            field.ClearEventBit(event_bit.TEMP_SONG_OVERRIDE), # allow song to change on map change
            field.ClearEventBit(npc_bit.MARSHAL_NARSHE_WOB), # Remove Marshal
            field.ClearEventBit(npc_bit.TERRA_COLLAPSED_NARSHE_WOB), # Remove collapsed Terra

            Read(0xcaded, 0xcadf2), # load map

            field.HideEntity(0x1B), # the exit block at top of map

            field.SetParty(1),
            field.Call(field.REMOVE_ALL_CHARACTERS_FROM_ALL_PARTIES),
        ]
        for character_idx in range(self.characters.CHARACTER_COUNT):
            src += [
                # Restore character appearance, name, and properties
                field.SetSprite(character_idx, self.characters.get_sprite(character_idx)),
                field.SetPalette(character_idx, self.characters.get_palette(character_idx)),
                field.SetName(character_idx, character_idx),
                field.SetProperties(character_idx, character_idx),
            ]
        src += [ 
            field.Call(field.REFRESH_CHARACTERS_AND_SELECT_PARTY),
            field.UpdatePartyLeader(),
            field.ShowEntity(field_entity.PARTY0),
            field.RefreshEntities(),

            field.FreeScreen(),

            field.FadeInScreen(),
            field.WaitForFade(),

            field.SetEventBit(event_bit.FINISHED_MOOGLE_DEFENSE),
            field.FreeMovement(),

            # hide Arvis 
            field.ClearEventBit(npc_bit.ARVIS_INTRO),
            field.FinishCheck(),
            field.Return(),
        ]
        space = Reserve(0xcade5, 0xcb04f, "moogle defense victory", field.NOP())
        space.write(src)



