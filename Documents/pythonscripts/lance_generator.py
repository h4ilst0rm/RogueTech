import json, math, copy, traceback, os

# writes standard dynamic lances for RT Core and Optionals
# run with python3 lance_generator.py
# adjust script, run script, inspect git diff for changes

path_to_lances = "Roguetech/Core/RogueTechCore/Lances/"

template = json.loads("""{
  "Description": {
    "Id": "",
    "Name": "",
    "Details": "",
    "Icon": "",
    "Cost": 0,
    "Rarity": 0,
    "Purchasable": false
  },
  "Difficulty": 1,
  "LanceTags": {
    "items": [],
    "tagSetSourceFile": "Tags/LanceTags"
  },
  "LanceUnits": []
}""")
    
slot_template = json.loads("""{
    "unitType": "Mech",
    "unitId": "Tagged",
    "pilotId": "Tagged",
    "unitTagSet": {
        "items": [],
        "tagSetSourceFile": "Tags/UnitTags"
    },
    "excludedUnitTagSet": {
        "items": [],
        "tagSetSourceFile": "Tags/UnitTags"
    },
    "pilotTagSet": {
        "items": [],
        "tagSetSourceFile": "Tags/PilotTags"
    },
    "excludedPilotTagSet": {
        "items": [],
        "tagSetSourceFile": "Tags/PilotTags"
    },
    "locked": false
}""")

bracket_map = [
    ["0-2","0-1","0-0","0-0"],
    ["0-2","0-1","0-1","0-1"],
    ["1-2","0-1","0-0","0-0"],
    ["1-2","0-2","0-0","0-0"],
    ["1-3","0-2","0-0","0-0"],#5
    ["2-3","0-3","0-0","0-0"],
    ["2-4","0-3","0-0","0-0"],
    ["3-4","0-4","0-0","0-0"],
    ["3-5","0-4","0-0","0-0"],
    ["4-5","0-5","0-0","0-0"],#10
    ["4-6","0-5","0-0","0-0"],
    ["5-6","0-6","0-0","0-0"],
    ["5-7","0-6","0-0","0-0"],
    ["6-7","0-7","0-0","0-0"],
    ["6-8","0-7","0-0","0-0"],#15
    ["7-8","0-8","0-0","0-0"],
    ["7-9","0-8","0-0","0-0"],
    ["7-9","0-9","0-0","0-0"],
    ["8-9","7-8","6-8","6-8"],
    ["8-9","8-9","7-9","6-9"],#20
]

def diff_bracket_excludes(diff, index):
    exclude_tags = []
    start, end = map(int, bracket_map[diff-1][index].split("-"))
    for i in range(0, 9):
        if i < start or i > end:
            exclude_tags.append(f"unit_bracket_{i}")
    return exclude_tags

weight_excludes = {}
weight_excludes["light"] = ["unit_assault","unit_heavy","unit_medium"]
weight_excludes["med/light"] = ["unit_assault","unit_heavy"]
weight_excludes["med"] = ["unit_assault","unit_heavy","unit_light"]
weight_excludes["hvy/med"] = ["unit_assault","unit_light"]
weight_excludes["hvy"] = ["unit_assault","unit_medium","unit_light"]
weight_excludes["ass/hvy"] = ["unit_medium","unit_light"]
weight_excludes["ass"] = ["unit_heavy","unit_medium","unit_light"]
weight_excludes["hvy/med/light"] = ["unit_assault"]
weight_excludes["ass/hvy/med"] = ["unit_light"]
weight_excludes["ass/hvy/med/light"] = []

weight_map = [
    ["light","light","light","light"],
    ["med/light","light","light","light"],
    ["med/light","med/light","light","light"],
    ["med","med/light","med/light","light"],
    ["med","med","med/light","light"], #5
    ["med","med","med/light","med/light"], 
    ["hvy/med","med","med","med/light"],
    ["hvy/med","hvy/med","med","med/light"],
    ["hvy","hvy/med","med","med/light"],
    ["hvy","hvy","hvy/med","med/light"], #10
    ["hvy","hvy","hvy/med","hvy/med/light"],
    ["ass/hvy","hvy","hvy/med","hvy/med/light"],
    ["ass/hvy","ass/hvy","hvy","hvy/med/light"],
    ["ass/hvy","ass/hvy","hvy","hvy/med"],
    ["ass/hvy","ass/hvy","hvy","hvy/med"], #15
    ["ass","ass/hvy","ass/hvy","ass/hvy/med"],
    ["ass","ass/hvy","ass/hvy","ass/hvy/med"],
    ["ass","ass","ass/hvy","ass/hvy/med"],
    ["ass","ass","ass/hvy","ass/hvy/med"],
    ["ass","ass","ass/hvy","ass/hvy"] #20
]

def diff_weight_excludes(diff, index):
    return weight_excludes[weight_map[diff-1][index]]

number = 0

def composition_tags(index = 0, diff = 0, category = "", composition = "", extras = []):
    include_tags = []
    exclude_tags = []

    match(composition):
        case "mech":
            include_tags.append("unit_mech")

        case "mixed":
            if index in [1,2]:
                include_tags.append("unit_vehicle")
            else:
                include_tags.append("unit_mech")

        case "vehicle":
            include_tags.append("unit_vehicle")

        # convoys
        case "allied":
            include_tags.append("unit_vehicle")
            include_tags.append("unit_vehicle_apc")

            exclude_tags.append("unit_noconvoy")
            exclude_tags.append("unit_vtol")
            exclude_tags.append("unit_airship")
            exclude_tags.append("unit_hover")
            exclude_tags.append("unit_vbied")
            exclude_tags.append("unit_thumper")
            exclude_tags.append("unit_sniper")
            exclude_tags.append("unit_longtom")
            exclude_tags.append("unit_arrow")
        case "opfor":
            include_tags.append("unit_vehicle")

            exclude_tags.append("unit_noconvoy")
            exclude_tags.append("unit_vtol")
            exclude_tags.append("unit_airship")
            exclude_tags.append("unit_hover")
            exclude_tags.append("unit_vbied")
            exclude_tags.append("unit_thumper")
            exclude_tags.append("unit_sniper")
            exclude_tags.append("unit_longtom")
            exclude_tags.append("unit_arrow")
        case "mechconvoy":
            include_tags.append("unit_mech")

            exclude_tags.append("unit_urbie")
            exclude_tags.append("unit_noconvoy")
            exclude_tags.append("unit_thumper")
            exclude_tags.append("unit_sniper")
            exclude_tags.append("unit_longtom")
            exclude_tags.append("unit_arrow")

        # turrets
        case "standard":
            include_tags.append("unit_turret")
        case "artillery":
            include_tags.append("unit_turret")
            if index in [1,2]:
                include_tags.append("unit_artilleryturret")

        case "bug":
            include_tags.append("unit_bug")
            exclude_tags += diff_weight_excludes(diff+1, index)
            
        case _:
            print("bad composition: " + str(composition))
            traceback.print_stack()
            print("bad composition: " + str(composition))
            exit()

    return (include_tags, exclude_tags)
    
def category_tags(index = 0, diff = 0, category = "", composition = "", extras = []):
    include_tags = []
    exclude_tags = []

    match(category):
        case "battle":
            if index == 0:
                include_tags.append("unit_lance_tank")

        case "cavalry":
            if index in [0,1]:
                include_tags.append("unit_lance_vanguard")

        case "fire":
            if index in [0,1]:
                include_tags.append("unit_lance_assassin")
            
        case "support":
            if index in [0,1]:
                include_tags.append("unit_lance_support")

        case "recon":
            if index == 0:
                include_tags.append("unit_predator")

        case "convoy":
            pass

        case "solo":
            if index == 0:
                exclude_tags.append("unit_squad")
                if "advanced" in extras:
                    include_tags.append("unit_advanced")
                else:
                    include_tags.append("unit_legendary")
            else:
                include_tags.append("unit_littlefriend")

        case "coupe":
            exclude_tags.append("unit_squad")

            if index == 0:
                include_tags.append("unit_elite")
            elif index == 1:
                include_tags.append("unit_legendary")
            else:
                include_tags.append("unit_advanced")

        case "duel":
            exclude_tags.append("unit_squad")

            if "advanced" in extras:
                include_tags.append("unit_advanced")
            else:
                include_tags.append("unit_legendary")

        case "turret":
            if diff < 5:
                exclude_tags.append("unit_artilleryturret")
                
        case "special":
            pass

        case _:
            print("bad category: " + str(category))
            traceback.print_stack()
            print("bad category: " + str(category))
            exit()

    return (include_tags, exclude_tags)

def unit_include_exclude(index = 0, diff = 0, category = "", composition = "", extras = []):
    include_tags = ["{CUR_TEAM.faction}"]
    exclude_tags = ["unit_killteam", "unit_noncombatant"]

    exclude_tags += diff_bracket_excludes(diff, index)

    tags = composition_tags(index, diff, category, composition, extras)
    include_tags += tags[0]
    exclude_tags += tags[1]
    
    tags = category_tags(index, diff, category, composition, extras)
    include_tags += tags[0]
    exclude_tags += tags[1]

    def remove_brackets(tags = []):
        remove = []
        for tag in tags:
            if "unit_bracket_" in tag:
                remove.append(tag)
        for tag in remove:
            tags.remove(tag)

    if category == "convoy":
        exclude_tags.remove("unit_noncombatant")

    if "vtol" in extras and "unit_vehicle" in include_tags:
        include_tags.append("unit_vtol")

    if "hover" in extras and "unit_vehicle" in include_tags:
        include_tags.append("unit_hover")
        
    if "MBT" in extras and "unit_vehicle" in include_tags:
        include_tags.append("unit_MBT")

    if "demolisher" in extras and "unit_vehicle" in include_tags:
        remove_brackets(exclude_tags)
        include_tags.append("unit_demolisher")

    if "unit_artilleryturret" in include_tags:
        include_tags.remove("{CUR_TEAM.faction}")

    if "primitive" in extras and index in [0, 1, 2]:
        include_tags.remove("{CUR_TEAM.faction}")
        include_tags.append("unit_primitive")

        remove_brackets(exclude_tags)
        if diff < 3:
            exclude_tags.append("unit_assault")
            exclude_tags.append("unit_heavy")
            exclude_tags.append("unit_medium")
        elif diff < 6:
            exclude_tags.append("unit_assault")
            exclude_tags.append("unit_heavy")
        elif diff < 9:
            exclude_tags.append("unit_assault")
            exclude_tags.append("unit_light")
        else:
            exclude_tags.append("unit_light")

    if index in [2, 3]:
        if "medium" in extras:
            include_tags.append("unit_medium")
        if "heavy" in extras:
            include_tags.append("unit_heavy")
        if "assault" in extras:
            include_tags.append("unit_assault")

    # limit worst case BA and ultralight spam at very low diff
    if "unit_mech" in include_tags and diff < 3 and index in [0, 1] and "unit_squad" not in exclude_tags:
        exclude_tags.append("unit_squad")

    return (include_tags, exclude_tags)

def pilot_tags(index = 0, diff = 0, category = "", composition = "", extras = []):
    include_tags = []

    pilot_diff = math.ceil(diff/2.0)

    include_tags.append("pilot_npc_d"+str(pilot_diff))

    if (index == 0 ):
        include_tags.append("pilot_npc_high")   

    return include_tags

def tanker_tags(index = 0, diff = 0, category = "", composition = "", extras = []):
    include_tags = []

    pilot_diff = math.ceil(diff/2.0)
    
    include_tags.append("pilot_npc_tanker_d"+str(pilot_diff))
    include_tags.append("{CUR_TEAM.faction}")

    return include_tags

def turret_tags(index = 0, diff = 0, category = "", composition = "", extras = []):
    include_tags = []

    pilot_diff = math.ceil(diff/2.0)
    
    include_tags.append("pilot_turret_d"+str(pilot_diff))

    return include_tags

def build_lances(category, composition, start_diff, stop_diff, extras = [], location = ""):

    for diff in range(start_diff, stop_diff+1):

        lancedef = copy.deepcopy(template)
        lance_tags = []

        slots = 4
        if "small" in extras:
            slots = 3

        if category == "MCDuel":
            slots = 2

        if slots < 4:
            lance_tags.append("lance_type_notfull")

        match(category):
            case "battle":
                lance_tags.append("lance_type_battle")

            case "cavalry":
                lance_tags.append("lance_type_cavalry")

            case "fire":
                lance_tags.append("lance_type_fire")

            case "recon":
                lance_tags.append("lance_type_recon")

            case "support":
                lance_tags.append("lance_type_support")

            case "convoy":
                pass # tagged based on composition

            case "solo":
                lance_tags.append("lance_type_solo")

            case "duel":
                lance_tags.append("lance_type_duel")

            case "turret":
                lance_tags.append("lance_type_turret")

            case "coupe":
                lance_tags.append("lance_type_coupe")

            case "special":
                lance_tags.append("lance_type_special")

            case _:
                print("bad category: " + str(category))
                traceback.print_stack()
                print("bad category: " + str(category))
                exit()

        match(composition):
            case "mech":
                if category != "duel":
                    lance_tags.append("lance_type_mech")
                    lance_tags.append("lance_type_notallvehicles")

            case "mixed":
                if category != "turret":
                    lance_tags.append("lance_type_mixed")
                    lance_tags.append("lance_type_notallvehicles")

            case "vehicle":
                lance_tags.append("lance_type_vehicle")
                if "vtol" in extras:
                    lance_tags.append("lance_type_vtol")

            # convoys
            case "allied":
                lance_tags.append("lance_type_convoy")
            case "opfor":
                lance_tags.append("lance_type_OpForConvoy")
            case "mechconvoy":
                lance_tags.append("lance_type_mechconvoy")
            
            # turrets
            case "standard":
                pass
            case "artillery":
                lance_tags.append("lance_type_arty_turret")
                pass

            # special bug lance
            case "bug":
                lance_tags.append("lance_type_bug")

            case _:
                print("bad composition: " + str(composition))
                traceback.print_stack()
                print("bad composition: " + str(composition))
                exit()

        lancedef["LanceTags"]["items"] = lancedef["LanceTags"]["items"] + lance_tags
            
        lancedef["LanceUnits"] = []

        for index in range(0, 4):

            slot = copy.deepcopy(slot_template)

            if index >= slots:
                slot["unitId"] = "mechDef_None"
                lancedef["LanceUnits"].append(slot)
                continue

            unit_tags = unit_include_exclude(index, diff, category, composition, extras)

            slot["unitTagSet"]["items"] = unit_tags[0]
            slot["excludedUnitTagSet"]["items"] = unit_tags[1]

            if "unit_mech" in unit_tags[0]:
                slot["pilotTagSet"]["items"] = pilot_tags(index, diff, category, composition, extras)
            elif "unit_vehicle" in unit_tags[0]:
                slot["pilotTagSet"]["items"] = tanker_tags(index, diff, category, composition, extras)
            elif "unit_turret" in unit_tags[0]:
                slot["pilotTagSet"]["items"] = turret_tags(index, diff, category, composition, extras)
            elif category == "special":
                match(composition):
                    case "bug":
                        slot["pilotTagSet"]["items"] = pilot_tags(index, diff, category, composition, extras)
                    case _:
                        print("bad composition: " + str(composition))
                        traceback.print_stack()
                        print("bad composition: " + str(composition))
                        exit()
            else:
                print("bad tags to pilot: " + str(unit_tags[0]))
                traceback.print_stack()
                print("bad tags to pilot: " + str(unit_tags[0]))
                exit()


            slot["excludedPilotTagSet"]["items"] = []

            if "unit_mech" in unit_tags[0] or "unit_bug" in unit_tags[0]:
                slot["unitType"] = "Mech"
            elif "unit_vehicle" in unit_tags[0]:
                slot["unitType"] = "Vehicle"
            elif any(tag in ["unit_turret", "unit_artilleryturret"] for tag in unit_tags[0]):
                slot["unitType"] = "Turret"
            else:
                print("unhandled slot unit type")
                print(" ".join([composition, category]))
                print(unit_tags[0])
                traceback.print_stack()
                exit()

            lancedef["LanceUnits"].append(slot)

        lance_id = f"lancedef_{category}_{composition}_d{str(diff)}"
        lance_id + "_".join(extras)

        lancedef["Difficulty"] = diff
        lancedef["Description"]["Id"] = lance_id

        for extra in extras:
            lancedef["Description"]["Id"] = lancedef["Description"]["Id"] + "_" + extra

        lancedef["Description"]["Name"] = " ".join(["D"+str(diff), category.capitalize(), composition.capitalize()])

        save_path = path_to_lances + location
        save_path += "/".join([category.capitalize(), composition.capitalize()])

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        save_path +=  "/" + lancedef["Description"]["Id"] + ".json"

        with open(save_path, 'w', newline='\n') as new_file:
            json.dump(lancedef, new_file, indent=2)
            new_file.write("\n")

        global number
        number += 1

## CORE

# lance_type_battle - tank

build_lances("battle", "mech", 1, 2, extras=["small"])
build_lances("battle", "mech", 1, 20)
build_lances("battle", "mech", 5, 10, extras=["medium"])
build_lances("battle", "mech", 10, 15, extras=["heavy"])
build_lances("battle", "mech", 15, 20, extras=["assault"])
build_lances("battle", "mech", 1, 10, extras=["primitive"])

build_lances("battle", "mixed", 1, 2, extras=["small"])
build_lances("battle", "mixed", 1, 20)
build_lances("battle", "mixed", 5, 10, extras=["medium"])
build_lances("battle", "mixed", 10, 15, extras=["heavy"])
build_lances("battle", "mixed", 15, 20, extras=["assault"])
build_lances("battle", "mixed", 1, 10, extras=["primitive"])

build_lances("battle", "vehicle", 1, 2, extras=["small"])
build_lances("battle", "vehicle", 1, 20)
build_lances("battle", "vehicle", 5, 10, extras=["medium"])
build_lances("battle", "vehicle", 10, 15, extras=["heavy"])
build_lances("battle", "vehicle", 15, 20, extras=["assault"])
build_lances("battle", "vehicle", 15, 20, extras=["demolisher"])

# lance_type_cavalry - vanguard

build_lances("cavalry", "mech", 1, 2, extras=["small"])
build_lances("cavalry", "mech", 1, 20)
build_lances("cavalry", "mech", 5, 10, extras=["medium"])
build_lances("cavalry", "mech", 10, 15, extras=["heavy"])
build_lances("cavalry", "mech", 15, 20, extras=["assault"])

build_lances("cavalry", "mixed", 1, 2, extras=["small"])
build_lances("cavalry", "mixed", 1, 20)
build_lances("cavalry", "mixed", 5, 10, extras=["medium"])
build_lances("cavalry", "mixed", 10, 15, extras=["heavy"])
build_lances("cavalry", "mixed", 15, 20, extras=["assault"])

build_lances("cavalry", "vehicle", 1, 2, extras=["small"])
build_lances("cavalry", "vehicle", 1, 20)

# lance_type_fire - assassin

build_lances("fire", "mech", 1, 2, extras=["small"])
build_lances("fire", "mech", 1, 20)
build_lances("fire", "mech", 5, 10, extras=["medium"])
build_lances("fire", "mech", 10, 15, extras=["heavy"])
build_lances("fire", "mech", 15, 20, extras=["assault"])

build_lances("fire", "mixed", 1, 2, extras=["small"])
build_lances("fire", "mixed", 1, 20)
build_lances("fire", "mixed", 5, 10, extras=["medium"])
build_lances("fire", "mixed", 10, 15, extras=["heavy"])
build_lances("fire", "mixed", 15, 20, extras=["assault"])

build_lances("fire", "vehicle", 1, 2, extras=["small"])
build_lances("fire", "vehicle", 1, 20)

# lance_type_recon - predator

build_lances("recon", "mech", 1, 2, extras=["small"])
build_lances("recon", "mech", 1, 20)
build_lances("recon", "mech", 5, 10, extras=["medium"])
build_lances("recon", "mech", 10, 15, extras=["heavy"])
build_lances("recon", "mech", 15, 20, extras=["assault"])

build_lances("recon", "mixed", 1, 2, extras=["small"])
build_lances("recon", "mixed", 1, 20)
build_lances("recon", "mixed", 5, 10, extras=["medium"])
build_lances("recon", "mixed", 10, 15, extras=["heavy"])
build_lances("recon", "mixed", 15, 20, extras=["assault"])
build_lances("recon", "mixed", 5, 20, extras=["vtol"])
build_lances("recon", "mixed", 5, 20, extras=["hover"])

build_lances("recon", "vehicle", 1, 2, extras=["small"])
build_lances("recon", "vehicle", 1, 20)
build_lances("recon", "vehicle", 5, 10, extras=["medium"])
build_lances("recon", "vehicle", 10, 15, extras=["heavy"])
build_lances("recon", "vehicle", 15, 20, extras=["assault"])
build_lances("recon", "vehicle", 5, 20, extras=["vtol"])

# lance_type_support - support

build_lances("support", "mech", 1, 2, extras=["small"])
build_lances("support", "mech", 1, 20)
build_lances("support", "mech", 5, 10, extras=["medium"])
build_lances("support", "mech", 10, 15, extras=["heavy"])
build_lances("support", "mech", 15, 20, extras=["assault"])
build_lances("support", "mech", 1, 20, extras=["indirect"])

build_lances("support", "mixed", 1, 2, extras=["small"])
build_lances("support", "mixed", 1, 20)
build_lances("support", "mixed", 5, 10, extras=["medium"])
build_lances("support", "mixed", 10, 15, extras=["heavy"])
build_lances("support", "mixed", 15, 20, extras=["assault"])
build_lances("support", "mixed", 10, 20, extras=["carrier"])
build_lances("support", "mixed", 10, 20, extras=["indirect"])
build_lances("support", "mixed", 10, 20, extras=["command"])

build_lances("support", "vehicle", 1, 2, extras=["small"])
build_lances("support", "vehicle", 1, 20)
build_lances("support", "vehicle", 5, 10, extras=["medium"])
build_lances("support", "vehicle", 10, 15, extras=["heavy"])
build_lances("support", "vehicle", 15, 20, extras=["assault"])
build_lances("support", "vehicle", 10, 20, extras=["carrier"])
build_lances("support", "vehicle", 10, 20, extras=["indirect"])
build_lances("support", "vehicle", 10, 20, extras=["command"])

# lance_type_convoy, allied side escort convoy
# lance_type_OpForConvoy, ambush convoy target
# lance_type_mechconvoy, both sides, bad pilots
build_lances("convoy", "allied", 1, 20)
build_lances("convoy", "opfor", 1, 20)
build_lances("convoy", "mechconvoy", 1, 20)

# lance_type_solo, assassination, high prio target + lights (for when few other contracts call them)
build_lances("solo", "mech", 1, 20)
build_lances("solo", "mech", 1, 20, extras=["advanced"])

# lance_type_turret
build_lances("turret", "standard", 1, 20)
build_lances("turret", "artillery", 18, 20)

# Mission control

build_lances("duel", "mech", 1, 20, location="../../MissionControl/overrides/lances/")
build_lances("duel", "mech", 1, 20, location="../../MissionControl/overrides/lances/", extras=["advanced"])

## Elites submod

# lance_type_coupe, challenge coupe & friends, mechs kitted to gills
build_lances("coupe", "mech", 1, 20, location="../../../Optionals/RogueElites/Base/Lances/")
# assassination target elites
build_lances("solo", "mech", 5, 20, location="../../../Optionals/RogueElites/Base/Lances/", extras=["elite"])
# elite + stealth lance to bring elites into normal figts
build_lances("fire", "mech", 5, 20, location="../../../Optionals/RogueElites/Base/Lances/", extras=["elite", "stealth"])

## RISC submod

build_lances("battle", "mech", 5, 20, location="../../../Optionals/RISCtech/Base/Lances/", extras=["risc"])
build_lances("battle", "mixed", 5, 20, location="../../../Optionals/RISCtech/Base/Lances/", extras=["risc"])

## Urbie  submod

build_lances("battle", "mech", 1, 8, location="../../../Optionals/Urbocalypse/Base/Lances/", extras=["urbie"])
build_lances("battle", "mixed", 4, 8, location="../../../Optionals/Urbocalypse/Base/Lances/", extras=["urbie"])

## Lances for specific things

build_lances("special", "bug", 1, 15)

print(f"Finished writing {number} LanceDefs.")

exit()

