from event.event import *
import data.npc_bit as npc_bit
from constants.entities import character_id
import data.direction
from data.npc import NPC

class NarsheMoogleDefense(Event):
    WOB_MAP_ID = 0x33
    MARSHAL_NPC_ID = 0x12
    COLLAPSED_TERRA_NPC_ID = 0x19

    def name(self):
        return "Narshe Moogle Defense"

    def character_gate(self):
        return self.characters.MOG

    def init_rewards(self):
        self.reward = self.add_reward(RewardType.CHARACTER | RewardType.ESPER | RewardType.ITEM)

    def init_event_bits(self, space):
        space.write(
            field.SetEventBit(npc_bit.ARVIS_INTRO), # show Arvis
            field.ClearEventBit(npc_bit.MARSHAL_NARSHE_WOB), # do not show marshal
        )

    def refresh_characters_and_select_parties_with_moogles_mod(self):
        # Method for selecting parties or moogle replacements

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
                    # Ref: CC/A93D to make characters into moogles
                    # Make character look like a moogle
                    field.SetSprite(character_idx, self.characters.get_sprite(self.characters.MOG)),
                    field.SetPalette(character_idx, self.characters.get_palette(self.characters.MOG)),
                    # Give it the name and properties of the moogle
                    field.SetName(character_idx, moogle_id),
                    field.SetProperties(character_idx, moogle_id),
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
            field.UpdatePartyLeader(),
            field.ShowEntity(field_entity.PARTY0),
            field.RefreshEntities(),
            field.Return(),
        ]

        space = Write(Bank.CC, src, "field function refresh characters and select three parties with moogles")
        self.refresh_characters_and_select_parties_with_moogles = space.start_address

    def marshal_battle_mod(self):
        boss_pack_id = self.get_boss("Rizopas")

        space = Reserve(0xcadac, 0xcadae, "marshal invoke battle", field.NOP())
        space.write(
            field.InvokeBattle(boss_pack_id, check_game_over = False)
        )

    def add_terra_npc(self):
        # Add an NPC to replace Terra during the chase scene in Narshe South Caves (map 50). 
        # By doing so, it allows us to change her sprite without affecting a party Terra
        terra_npc = NPC()
        terra_npc.x = 55
        terra_npc.y = 11
        terra_npc.sprite = self.characters.get_sprite(self.characters.MOG)
        terra_npc.palette = self.characters.get_palette(self.characters.MOG)
        terra_npc.direction = direction.UP
        terra_npc.speed = 0
        terra_npc.event_byte = npc_bit.event_byte(npc_bit.MARSHAL_NARSHE_WOB) #dual purpose with showing Marshal NPC
        terra_npc.event_bit = npc_bit.event_bit(npc_bit.MARSHAL_NARSHE_WOB)
        self.terra_npc_id = self.maps.append_npc(50, terra_npc)
        
        # Replace collapsed Terra NPC
        terra_collapsed_npc = self.maps.get_npc(self.WOB_MAP_ID, self.COLLAPSED_TERRA_NPC_ID)
        terra_collapsed_npc.sprite = self.characters.get_sprite(self.characters.MOG)
        terra_collapsed_npc.palette = self.characters.get_palette(self.characters.MOG)
        
    def after_battle_mod(self):
        # Victory condition (marshal defeated)
        # Remove moogles from party 
        src = [ 
            field.FadeOutScreen(),
            field.WaitForFade(),

            field.ClearEventBit(event_bit.TEMP_SONG_OVERRIDE), # allow song to change on map change
            field.ClearEventBit(npc_bit.MARSHAL_NARSHE_WOB), # Remove Marshal and "Terra" in south caves
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

    def add_gating_condition(self):
        #TODO: if Mog not recruited, hide Arvis via map 30 NPC 1 entrance event (CC/395A)
        pass

    def mod(self):
        if self.args.character_gating:
            self.add_gating_condition()

        self.add_terra_npc() # TODO: hide her by default, maybe by updating the map event or setting the event_byte/event_bit

        #TEST: add an NPC to Blackjack that triggers Marshal battle #TODO REMOVE
        from data.bosses import name_pack
        src = [
            field.InvokeBattle(name_pack["Marshal"], 17),
            field.FadeInScreen(),
            field.WaitForFade(),
            field.Return(),
        ]
        space = Write(Bank.CC, src, "TEST Marshal battle")
        test_marshal_battle = space.start_address

        test_npc = NPC()
        test_npc.x = 16
        test_npc.y = 4
        test_npc.sprite = 52
        test_npc.palette = 0
        test_npc.direction = direction.DOWN
        test_npc.speed = 0
        test_npc.set_event_address(test_marshal_battle)
        self.maps.append_npc(0x6, test_npc)
        # TODO: remove above here (Test code)

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
            field.SetEventBit(npc_bit.MARSHAL_NARSHE_WOB), # Show "Terra" in south caves and Marshal in battle
            field.SetEventBit(npc_bit.TERRA_COLLAPSED_NARSHE_WOB), # Show collapsed "Terra"
            field.LoadMap(0x32, direction.UP, True, 55, 11),
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

        #Replace Terra commands in script with new NPC for which we can manipulate the sprite/palette to match the reward
        terra_action_queues = [0xCA2EB, 0xCA2F3, 0xCA31F, 0xCA32D, 0xCA34F, 0xCA362, 0xCA371, 0xCA38B, 0xCA390, 0xCA397, 0xCA3BC]
        for address in terra_action_queues:
            space = Reserve(address, address, "terra chased action queues")
            space.write(self.terra_npc_id)

        # Clear got her dialog
        space = Reserve(0xca2f0, 0xca2f2, "dialog: Got her", field.NOP()) # 'Got her' dialog

        # clear out Terra's fall & flashback, but show "Locke" (party leader) to allow for drop-down
        space = Reserve(0xca3f9, 0xca769, "Terra fall and flashback", field.NOP())
        space.write(
            
            field.ShowEntity(self.COLLAPSED_TERRA_NPC_ID),
            field.HideEntity(self.MARSHAL_NPC_ID),
            field.ShowEntity(field_entity.PARTY0),
            field.RefreshEntities(),
            field.StartSong(13), # play song: Locke
            field.SetEventBit(event_bit.TEMP_SONG_OVERRIDE), # keep song playing
            field.Branch(space.end_address + 1), # skip nops
        )

        # Change Locke actions to Party Leader
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
            field.ShowEntity(self.MARSHAL_NPC_ID), # show the Marshal NPC
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

        # Replace Marshal battle
        self.marshal_battle_mod()

        self.after_battle_mod()

        self.log_reward(self.reward)




