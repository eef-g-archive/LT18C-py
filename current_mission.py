from Missions.mission_06 import run_mission
if __name__ == "__main__":
    curr_mission = -1
    mission_choice = int(input("Enter the current mission number: "))

    match mission_choice:
        case 1:
            from Missions.mission_01 import run_mission
            curr_mission = run_mission()
        case 3:
            from Missions.mission_03 import run_mission
            curr_mission = run_mission()
        case 4:
            from Missions.mission_04 import run_mission
            curr_mission = run_mission()
        case 5:
            from Missions.mission_05 import run_mission
            curr_mission = run_mission()
        case 6:
            from Missions.mission_06 import run_mission
            curr_mission = run_mission()
        case _:
            print(f"ERROR: Mission {mission_choice} does not exist!\nEnding program")
    
    if (curr_mission != -1):
        curr_mission