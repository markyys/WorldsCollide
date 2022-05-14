# Function to get no of set bits in binary
# representation of positive integer n */
def  countSetBits(n):
    count = 0
    while (n):
        count += n & 1
        n >>= 1
    return count

def isSet(n, bit):
    return n & (1 << bit)

# Disclaimer: this is super hacky.
# Goal is to replace all enemy sprites with Rats and normalize their positions in battle
def main():
    import args

    args.post_gen = True
    args.output_file = "../rom/JexTest.sfc"

    from memory.memory import Memory
    from memory.space import Reserve
    memory = Memory()

    from data.enemy_graphics import EnemyGraphics
    from data.enemies import Enemies
    from data.bosses import dragon_enemy_name, normal_enemy_name, final_battle_enemy_name, name_enemy, final_battle_formation_name
    enemies = Enemies(memory.rom, args)

    # Rats:
    #   GFX: 0x0927
    #   Large: 0
    #   Mould: 16
    #   Palettes:
    #      Were (17): 0x2000
    #      Sewer (110): 0xCC00
    #      Vermin (199): 0x7201

    # GhostTrain has special logic to always use its sprite -- remove that
    #C2/B53E:	F0 01		BEQ $B541	(+1)	(If not, exit)
    #C2/B540:	6B		RTL
    # https://discord.com/channels/151057875106660352/168746496316014593/932706068537163807
    space = Reserve(0x2b53f, 0x2b53f, "ghosttrain branch")
    space.write(0x00) # always exit, even if ghost train

    # Formation location examples:
    # 1 enemy: Formation 0 (Lobo) - 6,9
    # 2 enemies: Formation 1 (2xLobo) - 5,7; 8,12
    # 3 enemies: Formation 14 (Were-Rat x3) 11,8; 4,10; 9, 14
    # 4 enemies: Formation 24 (Rhodox x4) 5, 8; 11, 9; 4, 13; 10, 14
    # 5 enemies: Formation 52 (Rhobite x5) 12, 14; 12, 8; 4, 8; 4, 14; 8, 11
    # 6 enemies: Formation 240 (Deep Eye x6) 6, 14; 12, 13; 8, 10; 3, 9; 8, 6; 13, 8

    positions = [
        [[6,9]],
        [[5,7],[8,12]],
        [[11,8],[4,10],[9,14]],
        [[5,8],[11,9],[4,13],[10,14]],
        [[12,14],[12,8],[4,8],[4,14],[8,11]],
        [[6,14],[12,13],[8,10],[3,9],[8,6],[13,8]]
    ]
    # go through each formation
    for formation in enemies.formations.formations:
        if formation.id not in final_battle_formation_name:
            # print(f"{formation.id}:")
            # print(formation.enemy_x_positions)
            # print(formation.enemy_y_positions)
            # determine which position set to use
            numBits = countSetBits(formation.enemy_slots) - 1
            # print(numBits)
            position = positions[numBits]
            # location in position
            posLoc = 0
            # go through each enemy slot
            for i in range(0, 6):
                if(isSet(formation.enemy_slots, i)):
                    formation.enemy_x_positions[i] = position[posLoc][0]
                    formation.enemy_y_positions[i] = position[posLoc][1]
                    posLoc += 1
            # print(formation.enemy_x_positions)
            # print(formation.enemy_y_positions)

    graphics = EnemyGraphics(memory.rom)

    for graphic in graphics.graphics:
        if graphic.id not in final_battle_enemy_name and enemies.get_name(graphic.id) != "":
            graphic.gfx_pointer = 0x0927
            graphic.large_template = 0
            graphic.mould_index = 16

            if graphic.id in dragon_enemy_name or graphic.id in normal_enemy_name:
                graphic.palette_pointer = 0xCC00
            else:
                graphic.palette_pointer = 0x2000

            enemies.enemies[graphic.id].name = "Rat"

    kefka_id = name_enemy["Kefka (Final)"]
    kefka = graphics.graphics[kefka_id]
    kefka.gfx_pointer = 0x0927
    kefka.large_template = 0
    kefka.mould_index = 16
    kefka.palette_pointer = 0x7201
    enemies.enemies[kefka_id].name = "King Rat"

    graphics.write()
    enemies.write()
    memory.write()

if __name__ == '__main__':
    main()
