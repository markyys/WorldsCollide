Beta Branch for 1.1.x

Adds the following flags for new features:
1. `-stloc/-drloc <original | shuffle | mix>` for Kielbasigo's Status Boss Location/Dragon Boss Location shuffle or mix. Shuffle = shuffled amongst themselves, Mix = mixed boss pool
2. `-fc` to Fix Capture Bugs (multi-steal not giving more than 1 item and weapon specials not proccing)
3. `-np` flag for Sprites in peekable checks are left a mystery until reward
4. `-cc` flag for Controllable Coliseum
5. Kielbasiago's movement options: 
    - `-noshoes` flag for "Removes Sprint Shoes from appearing in shops, chests, etc."
    - `-move og | as | bd | ssbd` for Movement Speed (MS) changes:
        - **Original (`og`)** -- MS 2 by default, MS 3 with sprint shoes | 
        - **Auto Sprint (`as`)** -- MS 3 by default, MS 2 when holding B (new default, equivalent to deprecated `-as` flag)| 
        - **B Dash (`bd`)** -- MS 3 by default, MS 4 when holding B | 
        - **Sprint Shoes B Dash (`ssbd`)** -- MS 3 by default, MS 2 when holding B, MS 4 when holding B with sprint shoes
6. `-rls` flag for "Remove spells from learnable sources: Items, Espers, Natural Magic, and Objectives"
7. `-scis` flag for "Sketch & Control 100% accurate and use Sketcher/Controller's stats"
8. `-scia` flag for "Improves Sketch & Control abilities. Removes Battle from Sketch. Adds Rage as a Sketch/Control possibility for most monsters. Gives Sketch abilities to most bosses."
9. `-stesp <MIN> <MAX>` for "Give Player between MIN - MAX espers at the start of the seed
10. `-wmhc` for "World Minimap High Contrast -- makes minimap opaque and increases contrast of location indicator"
11. `-stl <level>` for "Set Starting Level
12. Franklin's MP Randomization flags
    - `-mmps` for Magic spells' MP costs shuffled
    - `-mmprv <MIN> <MAX>` for Magic spells' MP costs randomized between given values (0-254)
    - `-mmprp <MIN> <MAX>` for each Magic spell's MP cost set to random percent of original within given range (0 - 200)
13. `-u254` to make Ultima cost 254 MP
14. `-warp` to make Warp cost 0 MP and give to all characters
15. `-sj <quantity>` to add the given quantity of junk (tier 0) weapon/shields/helmets/armor/relics to starting inventory
16. `-rechu` to replace all Random (non-fixed/non-boss/non-Veldt/non-Zone Eater) checks with Coliseum Chupon.

Other changes:
- QoL: Mt Kolts is peekable -- the shadowy figure will now represent the reward
- QoL: Once you have 22 coral, every teleporter will take you to chest
- Feature: The Top 4 Magitek default to disabled for all characters, and are now unlockable for an objective (result = 59, "Magitek Upgrade")
- Bugfix: Learn Spells reward can no longer give Life spells during permadeath seeds.
- Feature: Added Gau-Father Reunion as a Quest objective (objective string ends with `.12.10`). Hint: take Gau + Sabin to Gau's Father House in WoR.
- Bugfix: Fixing bug that prevented learning Bum Rush if the Blitzer was recruited at level >= 42
- Feature: Esper and Lore MP random value MP costs can now go to 254.
- Feature: New Title Graphics from CDude
- QoL: Move Descriptions in Rage Menu
- Bugfix: Removing Excluded Non-S Tier Items (ex: Fenix Down in permadeath) from scaled or tiered chests
- QoL: Ensuring Gau can use Magic in FT

Associated PRs:
- Feature: Add ability to shuffle/mix both dragons and statues: <https://github.com/AtmaTek/WorldsCollide/pull/35>
- QoL: Ebot's Rock: Add guaranteed warp to chest: <https://github.com/AtmaTek/WorldsCollide/pull/16>
- QoL & Feature: Making Mt. Kolts peekable & add no-peeking flag: <https://github.com/AtmaTek/WorldsCollide/pull/15>
- Bugfix: Fix weapon special abilities with Capture and Multi-steals only giving 1 item: <https://github.com/AtmaTek/WorldsCollide/pull/18>
- Feature: Adding Controllable Coliseum flag: <https://github.com/AtmaTek/WorldsCollide/pull/21>
- Feature: Making Top 4 Magitek commands an objective result: <https://github.com/AtmaTek/WorldsCollide/pull/25>
- Feature: Adding flags to improve Sketch/Control: <https://github.com/AtmaTek/WorldsCollide/pull/28>
- Feature: Add Remove learnable spells flag + Submenu: <https://github.com/AtmaTek/WorldsCollide/pull/43>
- Feature: Adding Gau and Father Reunion as a Quest: <https://github.com/AtmaTek/WorldsCollide/pull/32>
- Feature: Adding flag for giving starting Espers: <https://github.com/AtmaTek/WorldsCollide/pull/34>
- Bugfix: Can't learn Bum Rush if recruited >= 42: <https://github.com/AtmaTek/WorldsCollide/pull/36>
- Feature: Add Dash/Sprint Shoe Dash movement options, reorganize the auto-sprint/dash flags: <https://github.com/AtmaTek/WorldsCollide/pull/37>
- Feature: Set Starting level: <https://github.com/AtmaTek/WorldsCollide/pull/39>
- Feature: Magic MP Randomization: <https://github.com/AtmaTek/WorldsCollide/pull/38>
- QoL: Adding Rage Move descriptions to rage men: <https://github.com/AtmaTek/WorldsCollide/pull/41>
- Bugfix: Removing excluded non-S tier items from tiered or scaled chests: <https://github.com/AtmaTek/WorldsCollide/pull/44>
- QoL: Ensuring that Gau can use Magic in FT <https://github.com/AtmaTek/WorldsCollide/pull/45>
- Feature: Adding warp-all flag for 0 cost starting Warp <https://github.com/AtmaTek/WorldsCollide/pull/46>
- Feature: Adding random-encounters-chupon flag <https://github.com/AtmaTek/WorldsCollide/pull/47>
- Kielbasiago's add --start-junk flag <https://github.com/AtmaTek/WorldsCollide/pull/48>


