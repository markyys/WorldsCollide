from event.event import *
from data.npc import NPC

class DebugRoom(Event):
    # Using the Vector Dining Room as our map
    DINING_ROOM_MAP = 0xfb

    def name(self):
        return "Debug Room"
    
    def init_event_bits(self, space):
        pass

    def remove_npcs_mod(self):
        # Remove all existing NPCs
        while(self.maps.get_npc_count(self.DINING_ROOM_MAP) > 0):
            self.maps.remove_npc(self.DINING_ROOM_MAP, 0)

    def _add_recruit_npc(self, character, x, y, direction):
        # Add an NPC to recruit each character
        src = [
            field.RecruitCharacter(character),
            field.PlaySoundEffect(150),
            field.Return(),
        ]
        space = Write(Bank.CC, src, "Recruit NPC")

        recruit_npc = NPC()
        recruit_npc.x = x
        recruit_npc.y = y
        recruit_npc.direction = direction
        recruit_npc.sprite = self.characters.get_sprite(character)
        recruit_npc.palette = self.characters.get_palette(character)
        recruit_npc.set_event_address(space.start_address)
        self.maps.append_npc(self.DINING_ROOM_MAP, recruit_npc)

    def add_recruit_npcs_mod(self):
        self._add_recruit_npc(self.characters.TERRA, 76, 16, direction.DOWN)
        self._add_recruit_npc(self.characters.LOCKE, 78, 16, direction.DOWN)
        self._add_recruit_npc(self.characters.CYAN, 82, 16, direction.DOWN)
        self._add_recruit_npc(self.characters.SHADOW, 84, 16, direction.DOWN)
        self._add_recruit_npc(self.characters.EDGAR, 80, 16, direction.DOWN)
        self._add_recruit_npc(self.characters.SABIN, 71, 16, direction.RIGHT)
        self._add_recruit_npc(self.characters.CELES, 71, 17, direction.RIGHT)
        self._add_recruit_npc(self.characters.STRAGO, 71, 18, direction.RIGHT)
        self._add_recruit_npc(self.characters.RELM, 71, 19, direction.RIGHT)
        self._add_recruit_npc(self.characters.SETZER, 71, 20, direction.RIGHT)
        self._add_recruit_npc(self.characters.MOG, 89, 16, direction.LEFT)
        self._add_recruit_npc(self.characters.GAU, 89, 17, direction.LEFT)
        self._add_recruit_npc(self.characters.GOGO, 89, 18, direction.LEFT)
        self._add_recruit_npc(self.characters.UMARO, 89, 19, direction.LEFT)

    def _add_teleport_npc(self, source_map, source_x, source_y, dest_map, dest_x, dest_y, direction):
        # Test code to add a Marshal battle NPC to Blackjack
        from data.bosses import name_pack
        src = [
            field.LoadMap(dest_map, direction, True, dest_x, dest_y, fade_in = True),
            field.Return(),
        ]
        space = Write(Bank.CC, src, "Teleport NPC")

        teleport_npc = NPC()
        teleport_npc.x = source_x
        teleport_npc.y = source_y
        teleport_npc.sprite = 22
        teleport_npc.palette = 3
        teleport_npc.direction = direction
        teleport_npc.set_event_address(space.start_address)
        self.maps.append_npc(source_map, teleport_npc)

    def add_teleport_npcs_mod(self):
        # get to and from the debug room via WoB Airship
        BLACKJACK_EXTERIOR_MAP = 0x06
        self._add_teleport_npc(BLACKJACK_EXTERIOR_MAP, 15, 4, self.DINING_ROOM_MAP, 80, 24, direction.DOWN)
        self._add_teleport_npc(self.DINING_ROOM_MAP, 80, 25, BLACKJACK_EXTERIOR_MAP, 15, 5, direction.UP)

    def mod(self):
        if self.args.debug:
            self.remove_npcs_mod()
            self.add_recruit_npcs_mod()
            self.add_teleport_npcs_mod()
