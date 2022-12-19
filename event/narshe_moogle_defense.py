from event.event import *
import data.npc_bit as npc_bit
from constants.entities import character_id
import data.direction
from data.npc import NPC



# Seed to test:
# Problem(12/18): Getting rewarded with Esper from next check
# Seed      vy5vi4xa7pvm
# Flags     -sl -sc1 terra -sal -stl 30 -rnl -com 10299898982998989898989898 -xpm 99 -lsced 2 -hmced 2 -xgced 2 -ase 0.5 -bbs -drloc shuffle -stloc mix -be -fer 0 -gp 100000 -smc 3 -sws 10 -mca -frm -move bd
# Hash      Chancellor, Leo, Old Man, Yura

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

    def _add_moogle_to_party_src(self, party_idx):
        # Event logic to add a moogle to the given party

        # map of characters to replacement moogles. Our logic will be to replace any characters not in our party with their mapped moogle.
        # index is the character (0 - 14) -- note: no Terra, Locke, or Umaro replacement
        # value is the associated replacement Moogle (-1 = no replacement)
        MOOGLE_REPLACEMENT = [
            -1, #TERRA
            -1, #LOCKE
            0x12, # CYAN -> KUPEK
            0x13, # SHADOW -> KUPOP
            0x14, # EDGAR -> KUMAMA
            0x15, # SABIN -> KUKU
            0x16, # CELES -> KUTAN
            0x17, # STRAGO -> KUPAN
            0x18, # RELM -> KUSHU
            0x19, # SETZER -> KURIN
            0x0A, # MOG
            0x1A, # GAU -> KURU
            0x1B, # GOGO -> KAMOG
            -1, #UMARO
        ]

        # Goes through moogles, checking whether they're already created (either them or their associated character)
        MOOGLE_CHARACTERS = range(2,13) # range of characters replacable with moogles
        src = [
            field.LoadCreatedCharacters(),
        ]
        for character_idx in MOOGLE_CHARACTERS:
            moogle_id = MOOGLE_REPLACEMENT[character_idx]
            src += [
                # Has the character already been created?
                field.BranchIfEventBitSet(event_bit.multipurpose(character_idx), f"SKIP_{character_idx}"), 
                #if not, make it a moogle
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
                    field.RestoreMp(character_idx, 0x7f), # restore all MP
                ]
            src += [
                field.CreateEntity(character_idx),
                field.AddCharacterToParty(character_idx, party_idx),
                field.Branch("RETURN"), # added 1 - we're done
                f"SKIP_{character_idx}", 
            ]
        src += [
            f"RETURN",
            field.Return(),
        ]

        return src

    def add_moogles_to_parties(self):
        # Method for selecting parties or moogle replacements

        self.add_moogle_to_party = [] #note: 0-indexed whereas parties are 1 indexed in code
        # Create the needed methods for adding a moogle to a party
        for i in range(1,4):
            space = Write(Bank.CC, self._add_moogle_to_party_src(i), f"Add moogle to party {i}")
            self.add_moogle_to_party.append(space.start_address)

        src = [
            # field.FadeOutScreen(),
            # field.WaitForFade(),
            field.Call(field.DELETE_CHARACTERS_NOT_IN_ANY_PARTY),
        ]
        # special logic for party 1, which will already have party members.
        # Here, we add moogles to fill in gaps
        src += [
            field.SetParty(1),
            # if shadow not in party, remove dog block from him so that KUPOP doesn't have Interceptor
            field.BranchIfCharacterInParty(self.characters.SHADOW, "HAVE_SHADOW"),
            field.RemoveStatusEffects(self.characters.SHADOW, field.Status.DOG_BLOCK),
            "HAVE_SHADOW",
            field.BranchIfPartySize(1, "ADD_3"),
            field.BranchIfPartySize(2, "ADD_2"),
            field.BranchIfPartySize(3, "ADD_1"),
            field.BranchIfPartySize(4, "ADD_0"),
            "ADD_3",
            field.Call(self.add_moogle_to_party[0]),
            "ADD_2",
            field.Call(self.add_moogle_to_party[0]),
            "ADD_1",
            field.Call(self.add_moogle_to_party[0]),
            "ADD_0",
        ]

        # For parties 2 and 3, just iterate 4 times each
        for party in range(2,4):
             for party_spot in range(0, 4):
                 src += [
                     field.Call(self.add_moogle_to_party[party-1])
                 ]

        src += [
            field.RefreshEntities(),
            field.Call(field.DELETE_CHARACTERS_NOT_IN_ANY_PARTY),
        ]

        space = Reserve(0xca905, 0xcaa03, "moogle defense party creation", field.NOP())
        space.write(
            src,
            field.Branch(space.end_address + 1), # skip nops
        )

    def marshal_battle_mod(self):
        # Replace Marshal battle
        boss_pack_id = self.get_boss("Marshal")

        space = Reserve(0xcadac, 0xcadae, "marshal invoke battle", field.NOP())
        space.write(
            field.InvokeBattle(boss_pack_id, check_game_over = False)
        )

    def terra_npc_mod(self):
        # Add an NPC to replace Terra during the chase scene in Narshe South Caves (map 50). 
        # By doing so, it allows us to change her sprite without affecting a party Terra
        self.terra_npc = NPC()
        self.terra_npc.x = 55
        self.terra_npc.y = 11
        self.terra_npc.direction = direction.UP
        self.terra_npc.speed = 0
        self.terra_npc.event_byte = npc_bit.event_byte(npc_bit.MARSHAL_NARSHE_WOB) #dual purpose with showing Marshal NPC
        self.terra_npc.event_bit = npc_bit.event_bit(npc_bit.MARSHAL_NARSHE_WOB)
        self.terra_npc_id = self.maps.append_npc(50, self.terra_npc)
        
        # Replace collapsed Terra NPC
        self.terra_collapsed_npc = self.maps.get_npc(self.WOB_MAP_ID, self.COLLAPSED_TERRA_NPC_ID)

        # ensure that the terra falls in hole event never triggers, as we're reusing the associated event bit
        space = Reserve(0xca2e5, 0xca2e5, "terra falls in hole event start")
        space.write(
            field.Return()
        )

    def marshal_test_mod(self):
        # Test code to add a Marshal battle NPC to Blackjack
        from data.bosses import name_pack
        src = [
            field.LoadMap(30, direction.UP, True, 62, 37),
            #field.InvokeBattle(name_pack["Marshal"], 17),
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

    def marshal_npc_mod(self):
        # Change the NPC bit that activates Marshal
        marshal_npc = self.maps.get_npc(self.WOB_MAP_ID, 0x12)
        marshal_npc.event_byte = npc_bit.event_byte(npc_bit.MARSHAL_NARSHE_WOB)
        marshal_npc.event_bit = npc_bit.event_bit(npc_bit.MARSHAL_NARSHE_WOB)

    def arvis_start_mod(self):
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
            field.Branch(0xCCA2EB) # 'Got her!' scene
        ]
        space = Write(Bank.CC, src, "load narshe caves map for Terra event")
        got_her_map_change = space.start_address

        reward_text = ""
        if self.reward.type == RewardType.CHARACTER:
            reward_text = "pursuing someone important"
        elif self.reward.type == RewardType.ESPER:
            reward_text = "looking for a glowing stone"
        elif self.reward.type == RewardType.ITEM:
            reward_text = "looking for a rare treasure"

        # Change Arvis Script
        prepared_dialog = 0x21 # reuse "OLD MAN: Make your way out through the mines! I’ll keep these brutes occupied!"
        self.dialogs.set_text(prepared_dialog, f"Imperial troops are {reward_text} even as we speak! You must stop them!<line><line> Will you help?<line><choice> Yes<line><choice> No<end>")
        space = Reserve(0xca06f, 0xca07d, "arvis dialog", field.NOP())
        space.write(
             field.DialogBranch(prepared_dialog,
                                dest1 = got_her_map_change,
                                dest2 = field.RETURN)
        )

    def event_start_mod(self):
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
            field.EntityAct(self.COLLAPSED_TERRA_NPC_ID, True, 
                field_entity.SetSpriteLayer(0)),
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

        # Speed up Marshal coming down stairs
        space = Reserve(0xca7dd, 0xca7dd, "marshal speed")
        space.write(field_entity.Speed.FAST)

        # Clear guard dialog
        space = Reserve(0xca7ee, 0xca7f0, "dialog: Now we gotcha!", field.NOP())

        # No dialog starting at cc/a85f -- reasonable point to add in the Marshal NPC
        space = Reserve(0xca85f, 0xca86f, "dialog: There's a whole bunch of 'em + Kupo", field.NOP())
        space.write(
            field.ShowEntity(self.MARSHAL_NPC_ID), # show the Marshal NPC
        )

        # No dialog at cc/a8b3
        space = Reserve(0xca8b2, 0xca8b6, "dialog: Moogles! Are you saying you want to help me?", field.NOP())
        space.write(
            field.EntityAct(0x11, True, 
                field_entity.SetSpriteLayer(2),
            ),
        )

        # No Kupo!!! dialog
        space = Reserve(0xca8d2, 0xca8d4, "dialog: Kupo!!!", field.NOP())

        # Change logic for moogle party selection to account for any party variation
        self.add_moogles_to_parties()

        # Clear use of event_bit.12E (TERRA_COLLAPSED_NARHSE_WOB) and event_bit.003 (moogle defense) at cc/aaab so that we can reuse 12E 
        # and so that 003 doesn't cause issues at WoB Narshe entrance
        space = Reserve(0xcaaab, 0xcaaae, "set terra falls event bit & initiated moogle defense bit", field.NOP())

    def after_battle_mod(self, reward_instructions):
        # Victory condition (marshal defeated)
        # Remove moogles from party 
        src = [ 
            reward_instructions, 

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
            # give Shadow Interceptor again
            field.AddStatusEffects(self.characters.SHADOW, field.Status.DOG_BLOCK),
            
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

    def character_mod(self, character):
        sprite = character
        self.terra_npc.sprite = sprite
        self.terra_npc.palette = self.characters.get_palette(sprite)
        self.terra_collapsed_npc.sprite = sprite
        self.terra_collapsed_npc.palette = self.characters.get_palette(sprite)

        self.after_battle_mod([
            field.RecruitCharacter(character),
        ])

    def esper_item_mod(self, esper_item_instructions):
        #Using thematic Moogle sprite for Esper/Items
        esper_item_sprite = self.characters.get_sprite(self.characters.MOG)
        self.terra_npc.sprite = esper_item_sprite
        self.terra_npc.palette = self.characters.get_palette(self.terra_npc.sprite)
        self.terra_collapsed_npc.sprite = esper_item_sprite
        self.terra_collapsed_npc.palette = self.characters.get_palette(self.terra_collapsed_npc.sprite)

        self.after_battle_mod(esper_item_instructions)

    def esper_mod(self, esper):
        self.esper_item_mod([
            field.AddEsper(esper),
            field.Dialog(self.espers.get_receive_esper_dialog(esper)),
        ])

    def item_mod(self, item):
        self.esper_item_mod([
            field.AddItem(item),
            field.Dialog(self.items.get_receive_dialog(item)),
        ])

    def mod(self):
        if self.args.character_gating:
            self.add_gating_condition()

        self.terra_npc_mod() 
        #TEST: add an NPC to Blackjack that triggers Marshal battle #TODO REMOVE
        self.marshal_test_mod()

        self.marshal_npc_mod()

        self.arvis_start_mod()
        self.event_start_mod()
        self.marshal_battle_mod()

        if self.reward.type == RewardType.CHARACTER:
            self.character_mod(self.reward.id)
        elif self.reward.type == RewardType.ESPER:
            self.esper_mod(self.reward.id)
        elif self.reward.type == RewardType.ITEM:
            self.item_mod(self.reward.id)

        self.log_reward(self.reward)




