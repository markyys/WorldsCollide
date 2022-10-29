Beta Branch for 1.1.x

Adds the following flags for new features:
1. `-stloc/-drloc <original | shuffle | mix>` for Kielbasigo's Status Boss Location/Dragon Boss Location shuffle or mix. Shuffle = shuffled amongst themselves, Mix = mixed boss pool <https://github.com/AtmaTek/WorldsCollide/pull/35>
2. `-fc` to Fix Capture Bugs (multi-steal not giving more than 1 item and weapon specials not proccing) <https://github.com/AtmaTek/WorldsCollide/pull/18>
3. `-np` flag for Sprites in peekable checks are left a mystery until reward <https://github.com/AtmaTek/WorldsCollide/pull/15>
4. `-cc` flag for Controllable Coliseum <https://github.com/AtmaTek/WorldsCollide/pull/21>
5. Kielbasiago's movement options: <https://github.com/AtmaTek/WorldsCollide/pull/37>
    - `-noshoes` flag for "Removes Sprint Shoes from appearing in shops, chests, etc."
    - `-move og | as | bd | ssbd` for Movement Speed (MS) changes:
        - **Original (`og`)** -- MS 2 by default, MS 3 with sprint shoes |
        - **Auto Sprint (`as`)** -- MS 3 by default, MS 2 when holding B (new default, equivalent to deprecated `-as` flag)|
        - **B Dash (`bd`)** -- MS 3 by default, MS 4 when holding B |
        - **Sprint Shoes B Dash (`ssbd`)** -- MS 3 by default, MS 2 when holding B, MS 4 when holding B with sprint shoes
6. `-rls` flag for "Remove spells from learnable sources: Items, Espers, Natural Magic, and Objectives" <https://github.com/AtmaTek/WorldsCollide/pull/43>
7. `-scis` flag for "Sketch & Control 100% accurate and use Sketcher/Controller's stats" <https://github.com/AtmaTek/WorldsCollide/pull/28>
8. `-scia` flag for "Improves Sketch & Control abilities. Removes Battle from Sketch. Adds Rage as a Sketch/Control possibility for most monsters. Gives Sketch abilities to most bosses." <https://github.com/AtmaTek/WorldsCollide/pull/28>
9. `-stesp <MIN> <MAX>` for "Give Player between MIN - MAX espers at the start of the seed <https://github.com/AtmaTek/WorldsCollide/pull/34>
10. `-wmhc` for "World Minimap High Contrast -- makes minimap opaque and increases contrast of location indicator" <https://github.com/AtmaTek/WorldsCollide/pull/23>
11. `-stl <level>` for "Set Starting Level <https://github.com/AtmaTek/WorldsCollide/pull/39>
12. Franklin's MP Randomization flags <https://github.com/AtmaTek/WorldsCollide/pull/38>
    - `-mmps` for Magic spells' MP costs shuffled
    - `-mmprv <MIN> <MAX>` for Magic spells' MP costs randomized between given values (0-254)
    - `-mmprp <MIN> <MAX>` for each Magic spell's MP cost set to random percent of original within given range (0 - 200)
13. `-u254` to make Ultima cost 254 MP <https://github.com/AtmaTek/WorldsCollide/pull/38>
14. `-warp` to make Warp cost 0 MP and give to all characters <https://github.com/AtmaTek/WorldsCollide/pull/46>
15. `-sj <quantity>` to add the given quantity of junk (tier 0) weapon/shields/helmets/armor/relics to starting inventory <https://github.com/AtmaTek/WorldsCollide/pull/48>
16. `-rechu` to replace all Random (non-fixed/non-boss/non-Veldt/non-Zone Eater) checks with Coliseum Chupon. <https://github.com/AtmaTek/WorldsCollide/pull/47>
17. `-npctips` for Franklin's NPC general game tips <https://github.com/AtmaTek/WorldsCollide/pull/56>
18. `-llr` to randomize L.x Lore Levels (L.5 Doom, L.4 Flare, L.3 Muddle, L? Pearl) <https://github.com/AtmaTek/WorldsCollide/pull/57>
19. `-hf` to hide flags from .txt file and Flags menus. Have Fun! <https://github.com/AtmaTek/WorldsCollide/pull/58>
20. `-sesb` and `-sebr` for Expensive Super Balls and Expensive Breakable Rods <https://github.com/ff6wc/WorldsCollide/pull/27>

Other changes:
- QoL: Mt Kolts is peekable -- the shadowy figure will now represent the reward <https://github.com/AtmaTek/WorldsCollide/pull/15>
- QoL: Once you have 22 coral, every teleporter will take you to chest <https://github.com/AtmaTek/WorldsCollide/pull/16>
- Feature: The Top 4 Magitek default to disabled for all characters, and are now unlockable for an objective (result = 59, "Magitek Upgrade") <https://github.com/AtmaTek/WorldsCollide/pull/25>
- Bugfix: Learn Spells reward can no longer give Life spells during permadeath seeds. <https://github.com/AtmaTek/WorldsCollide/pull/43>
- Feature: Added Gau-Father Reunion as a Quest objective (objective string ends with `.12.10`). Hint: take Gau + Sabin to Gau's Father House in WoR. <https://github.com/AtmaTek/WorldsCollide/pull/32>
- Bugfix: Fixing bug that prevented learning Bum Rush if the Blitzer was recruited at level >= 42 <https://github.com/AtmaTek/WorldsCollide/pull/36>
- Feature: Esper and Lore MP random value MP costs can now go to 254. <https://github.com/AtmaTek/WorldsCollide/pull/38>
- Feature: New Title Graphics from CDude <https://github.com/AtmaTek/WorldsCollide/pull/40>
- QoL: Move Descriptions in Rage Menu <https://github.com/AtmaTek/WorldsCollide/pull/41>
- Bugfix: Removing Excluded Non-S Tier Items (ex: Fenix Down in permadeath) from scaled or tiered chests <https://github.com/AtmaTek/WorldsCollide/pull/44>
- QoL: Ensuring Gau can use Magic in FT <https://github.com/AtmaTek/WorldsCollide/pull/45>
- QoL: Config options default to commonly used values <https://github.com/AtmaTek/WorldsCollide/pull/49>
- Feature: Added Unlock Perma KT Skip as an Objective Result (result `61`) <https://github.com/AtmaTek/WorldsCollide/pull/50>
- Bugfix: Fixed Burning House Objective dialog causing warp to wrong Thamasa map <https://github.com/AtmaTek/WorldsCollide/pull/52>
- QoL: Following Kefka at Narshe, the party warps to Arvis' house <https://github.com/AtmaTek/WorldsCollide/pull/53>
- QoL: Objective menu has "Any" and "All" indications that get grayed out upon completion <https://github.com/AtmaTek/WorldsCollide/pull/59>
- Feature: Added "KT Gauntlet", a new way to enter Kefka's Tower <https://github.com/AtmaTek/WorldsCollide/pull/59> - See [Gauntlet](#gauntlet) section below for more information
    - "Unlock KT Gauntlet" Result - Result id `62`
    - "Completed KT Gauntlet" Quest - Append objective string `.12.11` (12 is "Quest" type, 11 is "Completed KT Gauntlet" condition)
- Feature: Added five checks, one for each main boss in Kefka's Tower
    - Unlike other checks, these do not yield inherent rewards
    - However, this will increase the number of checks, so it will affect things like "Checks" scaling and the "Checks" objective condition
    - These can also be used as objective check conditions
    - Kefka's Tower Ambush (adding the following to the end of the objective string `11.59`)
    - Kefka's Tower Guardian (objective string `11.60`)
    - KT Left Triad Statue (objective string `11.61`)
    - KT Mid Triad Statue (objective string `11.62`)
    - KT Right Triad Statue (objective string `11.63`)

### Gauntlet
- This functions similarly to the KT Skip. When unlocked, it will show a new option in the dialog when entering KT.
- When entering the gauntlet the player will fight all five "required" KT fights back to back. There will be no chance to menu or save until you've completed the gauntlet.
- Preview video: https://www.youtube.com/watch?v=dtlHM_naEoo&t=1s
- The battle order is a follows:
    - The **RIGHT** party will fight the boss in the Ambush location
    - The **MIDDLE** party will fight the boss in the Guardian location
    - The **LEFT** party will fight the boss in the Left Triad Statue
    - The **RIGHT** party will fight the boss in the Right Triad Statue
    - The **MIDDLE** party will fight the boss in the Middle Triad Statue
    - Once the gauntlet is complete all 3 parties will drop down into the final switch room. You can then warp out, or backtrack to access save points.

**Gauntlet Known Issues**
- Sometimes when running the gauntlet with anything but vanilla bosses the "seamless music" isn't working correctly. It may also plays victory music
- Sometimes the guardian cutscene does not intialize the middle party's spot correctly, but it's only a visual issue
- Entering KT normally, looting the "validation chest", warping out before killing Poltergeist, then entering the gauntlet will double-loot the validation chest again during the poltergeist cutscene
- Entering KT normally, killing Inferno, warping out, then entering the gauntlet will play the WOR overworld music throughout the entirety of the gauntlet (assuming seamless music is working)
