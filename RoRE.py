# Reference:
# http://stackoverflow.com/questions/16115378/tkinter-example-code-for-multiple-windows-why-wont-buttons-load-correctly
# http://stackoverflow.com/questions/16798937/creating-a-browse-button-with-tkinter
# http://tkinter.unpythonic.net/wiki/tkFileDialog
# http://stackoverflow.com/questions/9239514/filedialog-tkinter-and-opening-files
#-------------------------------------------------------------------------------
# Plan:
# Open program
# Create Root Window
#   Create Save Navigator
#     save_path.in? open file at path: prompt for path (allow to browse?);
#     Test that Save.ini exists at path
#     Allow exit from program at this point
#   If path is established,
#     Back-up file
#     Read file into program
#       4 sets of data required:
#         1. Achievements, non-sensitive
#         2. Achievements, sensitive
#         3. Records, non-sensitive
#         4. Records, sensitive
#   Once file is read into program
#     Parse Sensitive Achievements&Records into nested lists
#       * Can use the text description in list to populate the set of check-boxes
#       * and use the index of same when writing to file
#       Records are split further into 
#         1. items
#         2. monsters
#         3. artifacts * N.B. artifacts are unlockable, rather than just a record
#       Achievements are split into
#         1. item unlocks (non-character sensitive)
#         2. character unlocks (non-character sensitive)
#         3. item unlocks (character sensitive)
#   Once info is parsed
#     Create Selection Menu
#       Options:
#         1. Unlock item logs (new window)
#         2. Unlock monster logs (new window)
#         3. Unlock achievements (new window)
#         4. Unlock artifacts (new window)
#         5. Unlock everything (button)
#         6. Reset everything (button)
#         7. Cancel (button)
#         8. Write and Save (button)
#   #---------------------------------------------------------------------------
#   Item logs
#     item_unlocked? allow log to be toggled : explain the achievement needed;
#     TODO, this^
#   Monster logs
#     Split into low-level and boss
#   Artifacts
#     Simply list them
#   Achievements
#     Most complex
#     3 groups:
#       1. item unlocks (non-character sensitive)
#       2. character unlocks (non-character sensitive)
#       3. item unlocks (character sensitive)
#     non-sensitive unlocks can be opened any time
#     character unlocks can be opened at any time
#     sensitives - char_unlocked? go : explain the achievement needed;
#   #---------------------------------------------------------------------------
#   Write to file
#     Write headers for achievement
#     Write non-sensitive info
#     Write sensitive, modified info
#     * entry_toggled_on? write entry: don't write it;
#     Ditto Records
# Close program
#-------------------------------------------------------------------------------

# Imports
import tkinter as tk
from tkinter.filedialog import askopenfilename
import os.path

# Figure bare minimum needed to selectively import for tkinter
# from tkinter.filedialog import askopenfilename, etc., eg.

# Window Class Definitions
# MainWindow, Item_Logs, Monster_Logs, Artifacts, Achievements
    
class MainWindow:  
    def __init__(self, master, filepath):
        self.filepath = filepath
        self.entry_length = len(self.filepath)
        self.master = master        
        self.achievement_info = []
        self.record_info = []        
        self.monsters, self.monsters_length = self.setup_monsters()
        self.items = self.setup_items()
        self.artifacts = self.setup_artifacts()
        self.achievements = self.setup_achievements()
        self.make_main_window() 
        
    def make_main_window(self):
        self.frame1 = tk.Frame(self.master)
        self.frame2 = tk.Frame(self.master)
        self.frame3 = tk.Frame(self.master)
        self.buffer1 = tk.Frame(self.master, height = 40)
        self.buffer2 = tk.Frame(self.master, height = 40)
        
        self.entry = tk.Entry(self.frame1, 
                              width = self.entry_length)
        self.status = tk.Canvas(self.frame1, 
                                width = 15,
                                height = 15,
                                bg = "grey")
        self.update = tk.Button(self.frame1,
                                text = "Update path to file",
                                command = self.update_path)
        self.entry.insert(0, self.filepath)
        self.item_button = tk.Button(self.frame2,
                                     text = "Modify Item Logs",
                                     command = self.item_logs)
        self.monster_button = tk.Button(self.frame2,
                                        text = "Modify Monster Logs",
                                        command = self.monster_logs)
        self.artifact_button = tk.Button(self.frame2,
                                         text = "Modify Artifacts",
                                         command = self.artifacts_unlock)
        self.achievement_button = tk.Button(self.frame2,
                                            text = "Modify Achievements",
                                            command = self.achievements_unlock)
        self.unlockButton = tk.Button(self.frame2,
                                      text = "Unlock everything",
                                      command = self.unlock)
        self.resetButton = tk.Button(self.frame2,
                                     text = "Reset everything",
                                     command = self.reset)
        self.quitButton = tk.Button(self.frame3,
                                    text = "Save & Quit",
                                    command = self.quit)
        self.cancelButton = tk.Button(self.frame3,
                                      text = "Cancel",
                                      command = self.cancel)
        
        self.check_file()
        
        # Frame 1
        self.entry.grid(row=0, column=0)
        self.status.grid(row=0, column=1)
        self.update.grid(row=0, column=2)
        # Frame 2
        self.item_button.grid(row=0, column=0, sticky = 'w')
        self.monster_button.grid(row=1, column=0, sticky = 'w')
        self.unlockButton.grid(row=2, column=0, sticky = 'w')
        self.artifact_button.grid(row=0, column=3, sticky = 'w')
        self.achievement_button.grid(row=1, column=3, sticky = 'w')      
        self.resetButton.grid(row=2, column=3, sticky = 'w')
        # Frame 3
        self.cancelButton.grid(row=0, column=2)
        self.quitButton.grid(row=0, column=3)
        
        self.frame1.pack()
        self.buffer1.pack()
        self.frame2.pack()
        self.buffer2.pack()
        self.frame3.pack()

    def update_path(self):
        # Gets a filename, then tests whether it's valid.
        # If user cancels while browsing for file, temp_filepath will be ''.
        temp_filepath = askopenfilename()
        if len(temp_filepath) > 0:             
            self.filepath = temp_filepath
            file = open("Path_to_Save_File.in", 'w')
            file.write(self.filepath)
            file.close()              
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.filepath)
            valid = self.check_file()
            if valid:
                self.backup()
                self.read_in() 

    def check_file(self):
        # Checks for a file, then checks whether RoR will open it as a save file.
        # If file is not valid, all buttons except cancel & change path are
        # disabled.
        if os.path.isfile(self.filepath):
            if self.filepath[-8:] == "Save.ini":
                self.status.create_rectangle(0, 0, 16, 16, fill = "green")
                self.item_button["state"] = "normal"
                self.monster_button["state"] = "normal"
                self.artifact_button["state"] = "normal"
                self.achievement_button["state"] = "normal"
                self.unlockButton["state"] = "normal"
                self.resetButton["state"] = "normal"
                self.quitButton["state"] = "normal"               
                self.backup()              
                self.read_in()
                return True

        self.status.create_rectangle(0, 0, 16, 16, fill = "red")
        self.item_button["state"] = "disabled"
        self.monster_button["state"] = "disabled"
        self.artifact_button["state"] = "disabled"
        self.achievement_button["state"] = "disabled"
        self.unlockButton["state"] = "disabled"
        self.resetButton["state"] = "disabled"
        self.quitButton["state"] = "disabled" 
        return False

    def backup(self):
        # Open existing save file, copy it into a backup file.
        backup_name = "Backup.ini"
        file = open(self.filepath, 'r')
        backup_file = open(backup_name, 'w')
        for line in file:
            backup_file.write(line)
        file.close()
        backup_file.close()        

    def read_in(self):
        # Clears the data-structures in case the user goes from a valid save
        # file to another.
        # Streams non-sensitive info into achievement_info or record_info.
        # Co-ordinates sensitive info with the corresponding data-structure.
        self.reset()
        file = open(self.filepath, 'r')
        for line in file:
            line = line.strip()
            if (line == "[Achievement]"):
                in_structure = self.achievement_info
            elif (line == "[Record]"):
                in_structure = self.record_info
            else:
                if len(line) > 0:
                    item, value = line.split('=')
                    if '_' not in item:
                        if (item[:11] == "achievement"):
                            achievement_number = int(item[11:])
                            toggle = self.achievements[achievement_number][1]
                            toggle.set(int(value))
                        elif (item[:8] == "artifact"):
                            artifact_number = int(item[8:])
                            toggle = self.artifacts[artifact_number][1]
                            toggle.set(int(value))
                        elif (item[:4] == "item"):
                            item_number = int(item[4:])
                            toggle = self.items[item_number][1]
                            toggle.set(int(value))
                        elif (item[:4] == "mons"):
                            monster_number = int(item[4:])
                            toggle = self.monsters[monster_number][1]
                            toggle.set(int(value))
                    else:
                        in_structure.append([item, value])                  
        file.close()
        
    def reset(self):
        # Sets all toggle values to 0 and clears non-sensitive info away.
        for i in range(len(self.achievements)):
            self.achievements[i][1].set(0)
        for i in range(len(self.items)):
            self.items[i][1].set(0)
        for i in range(len(self.artifacts)):
            self.artifacts[i][1].set(0)
        for i in range(len(self.monsters)):
            self.monsters[i][1].set(0)
        self.achievement_info = []
        self.record_info = []
    
    def unlock(self):
        # Sets all toggle values to 2 or 1, whichever is correct for type.
        for i in range(len(self.achievements)):
            self.achievements[i][1].set(2)
        for i in range(len(self.items)):
            self.items[i][1].set(1)
        for i in range(len(self.artifacts)):
            self.artifacts[i][1].set(1)
        for i in range(len(self.monsters)):
            self.monsters[i][1].set(1)
    
    def cancel(self):
        # Quit without writing.
        self.master.destroy()
        
    def quit(self):
        # Write to file, then quit.
        self.write()
        self.master.destroy()

    def write(self):
        # Open save file
        # Set header for achievements
        # Write non-sensitive info from achievements
        # Write sensitive info from same
        # Ditto records
        # If entry is toggled off, don't write it
        achievement_header = "[Achievement]\n"
        record_header = "[Record]\n"
        
        file = open(self.filepath, 'w')
        file.write(achievement_header)        
        self.write_achievements(file)
        file.write(record_header)
        self.write_records(file)
        file.close()
    
    def write_achievements(self, file):
        for item in self.achievement_info:
            term = item[0]
            value = item[1]
            string = term + '=' + value + '\n'
            file.write(string)
        for i in range(len(self.achievements)):
            if self.achievements[i][1].get() != 0:
                term = "achievement" + str(i)
                value = str(self.achievements[i][1].get())
                string = term + '=' + value + '\n'
                file.write(string)
        file.write('\n')
    
    def write_records(self, file):
        for item in self.record_info:
            term = item[0]
            value = item[1]
            string = term + '=' + value + '\n'
            file.write(string)
        for i in range(len(self.items)):
            if self.items[i][1].get() != 0:
                term = "item" + str(i)
                value = str(self.items[i][1].get())
                string = (term + '=' + value + '\n')
                file.write(string)
        for i in range(len(self.artifacts)):
            if self.artifacts[i][1].get() != 0:
                term = "artifact" + str(i)
                value = str(self.artifacts[i][1].get())
                string = (term + '=' + value + '\n')
                file.write(string)
        for i in range(len(self.monsters)):
            if self.monsters[i][1].get() != 0:
                term = "mons" + str(i)
                value = str(self.monsters[i][1].get())
                string = (term + '=' + value + '\n')
                file.write(string)
    # These are responsible for the new windows that open when the user selects
    # what they want to modify.
    def item_logs(self):
        self.newWindow = tk.Toplevel(self.master)
        self.selection = ItemLogs(self.newWindow, self.items)
    def monster_logs(self):
        self.newWindow = tk.Toplevel(self.master)
        self.selection = MonsterLogs(self.newWindow, self.monsters, self.monsters_length)
    def artifacts_unlock(self):
        self.newWindow = tk.Toplevel(self.master)
        self.selection = Artifacts(self.newWindow, self.artifacts)
    def achievements_unlock(self):
        self.newWindow = tk.Toplevel(self.master)
        self.selection = Achievements(self.newWindow, self.achievements)

    def setup_monsters(self):
        monsters = ["Lemurian", "Rock Golem", "Wisp", "Greater Wisp",
                    "Sand Crab", "Jellyfish", "Child", "Spitter",
                    "Tiny Imp", "Black Imp", "Mushrum", "Whorl", "Clay Man",
                    "Bighorn Bison", "Mechanical Spider", "Gup", "Parent",
                    "Evolved Lemurian", "Temple Guard", "Elder Lemurian",
                         "Archer Bug"]
        bosses = ["Colossus", "Wandering Vagrant", "Magma Worm",
                  "Ancient Wisp", "Imp Overlord", "Ifrit", "Toxic Beast",
                  "Cremator", "Scavenger", "Providence"]
        monsters_length = len(monsters)
        monsters += bosses
        for i in range(len(monsters)):
            monsters[i] = [monsters[i], tk.IntVar()]
            monsters[i][1].set(0)
        return monsters, monsters_length
    
    def setup_items(self):
        items = ["Meat Nuggets", "Fire Shield", "Bustling Fungus",
                 "Lens Maker's Glasses", "Sprouting Egg", "Headstompers",
                 "Life Savings", "Barbed Wire", "Rusty Knife", "Mysterious Vial",
                 "Mortar Tube", "Warbanner", "Monster Tooth", "Crowbar",
                 "Medkit", "Paul's Goat Hoof", "Bitter Root", "Sticky Bomb",
                 "Soldier's Syringe", "Snake Eyes", "Hermit's Scarf",
                 "Gasoline", "Spikestrip", "Time Keeper's Secret",
                 "Smart Shopper", "Infusion", "Will-o'-the-Wisp",
                 "AtG Missile Mk. 1", "Tough Times", "Energy Cell",
                 "Rusty Jetpack", "Leeching Seed", "Ukulele",
                 "Boxing Gloves", "Prison Shackels", "Guardian's Heart",
                 "Chargefield", "Arms Race", "Golden Gun", "56 Leaf Clover",
                 "Concussion Grenades", "Filial Imprinting",
                 "Deadman's Foot", "Toxic Worm", "Harvester's Scythe",
                 "Panic Mines", "Predatory Instincts", "Thallium",
                 "Tesla Coil", "Old Box", "Beating Embryo", "Permafrost",
                 "AtG Missile Mk. 2", "Happiest Mask", "Plasma Chain",
                 "Heaven Cracker", "Rapid Mitosis", "Ceremonial Dagger",
                 "Repulsion Armor", "Brilliant Behemoth", "Wicked Ring",
                 "Alien Head", "The Ol' Lopper", "The Hit List",
                 "Photon Jetpack", "Shattering Justice", "Telescopic Sight",
                 "Fireman's Boots", "Hyper-Threader", "Dio's Best Friend",
                 "Ancient Scepter", "Rotten Brain", "Safeguard Lantern",
                 "Snowglobe", "Skeleton Key", "Foreign Fruit",
                 "Instant Minefield", "Jar of Souls", "Carrara Marble",
                 "Sawmerang", "Shattered Mirror", 
                 "Disposable Missile Launcher", "Gold-plated Bomb", 
                 "Drone Repair Kit",  "Crudely Drawn Buddy", "Prescriptions",
                 "Shield Generator", "Unstable Watch", "Lost Doll",
                 "Pillaged Gold", "Captain's Brooch", "The Back-up", 
                 "Massive Leech", "Glowing Meteorite", "Legendary Spark", 
                 "Imp Overlord's Tentacle", "Burning Witness", "Colossal Knurl",
                 "Ifrit's Horn", "Nematocyst Nozzle"]
        for i in range(len(items)):
            items[i] = [items[i], tk.IntVar()]
            items[i][1].set(0)
        return items
            
    def setup_artifacts(self):
        artifacts = ["Honor", "Kin", "Distortion", "Spite", "Glass", "Enigma",
                     "Sacrifice", "Command", "Spirit", "Origin"]  
        for i in range(len(artifacts)):
            artifacts[i] = [artifacts[i], tk.IntVar()]
            artifacts[i][1].set(0)
        return artifacts
    
    def setup_achievements(self):
        achievements = ["Defeat 20 lemurians in 1 playthrough",
                        "Clear the 1st stage under 5 minutes",
                        "Dodge 7 lethal attacks",
                        "Survive a boss with less than 20% health",
                        "4 drone helpers at once", "Fail a shrine three times",
                        "Beat the 3rd Stage", "Kill the Scavenger",
                        "Survive 40 minutes", "Kill a boss with Lights Out",
                        "Reset your cooldown 15 times consecutively", "None",
                        "End a Teleporter timer with 0 enemies on the map",
                        "Activate the 3rd teleporter without being hurt once",
                        "Kill the Magma Worm, Wandering Vagrant, and Colossus",
                        "Block 2000 damage total with your shield",
                        "Stay in Shield Mode for 5 minutes straight (in combat)",
                        "Find the robot janitor", 
                        "Kill 10 enemies simultaneously with Forced Reassembly",
                        "Stay above 70% health for 25 minutes",
                        "Collect 15 Monster Logs", "Achieve 200% attack speed",
                        "Defeat the Legendary Wisp without taking damage",
                        "Purchase 40 drones total", 
                        "Detonate 15 Bounding Mines within 5 seconds",
                        "Kill a boss in 15 seconds or less",
                        "Clear a path for the survivor", 
                        "Survive the teleporter event without falling below 50% health",
                        "Reach level 10 without getting hurt more than once",
                        "Beat the game", "Achieve 20 consecutive perfect reloads",
                        "1-shot kill 10 enemies consecutively",
                        "Free the chained creature",
                        "Spread 10.000 feet of caustic sludge",
                        "Spread epidemic to 25 enemies",
                        "Die 50 times", "Find the bloated survivor",
                        "Obtain 7 Monster Teeth and 1 Guardian Heart",
                        "Reach 650 health", 
                        "Unlock a golden chest with the Explorer's Key",
                        "Deal 5000 damage in one shot", "Drown 20 Whorls",
                        "Bank 20.000 gold", "Collect 4 Keycards",
                        "Use a health shrine that drops you below 5% health",
                        "Pass a shrine 4 times in a row", 
                        "Beat the game on Monsoon difficulty",
                        "Beat the game 5 times", "Eviscerate 50 enemies"]
        for i in range(len(achievements)):
            achievements[i] = [achievements[i], tk.IntVar()]
            achievements[i][1].set(0)      
        return achievements

class ItemLogs:
    def __init__(self, master, items):
        self.items = items
        self.master = master
        self.make_window()

    def make_window(self):    
        self.frame1 = tk.Frame(self.master)
        self.frame2 = tk.Frame(self.master)
       
        # TODO: Check whether the log requires an item to be unlocked to display
        tk.Label(self.frame1,
                 text = "Item Logs",
                 font = "Verdana 9 bold"
                 ).grid(row=0, column=0, sticky = 'w')
        
        row_count = 1
        col_count = 0        
        for i in range(len(self.items)):
            name = self.items[i][0]
            toggle = self.items[i][1]
            tk.Checkbutton(self.frame1,
                            text = name,
                            variable = toggle
                            ).grid(row = row_count, column = col_count, sticky = 'w')
            row_count += 1
            if row_count > 25:
                row_count -= 25
                col_count += 1
                
        self.quitButton = tk.Button(self.frame2,
                                    text = "Return to Main Menu",
                                    command = self.quit).pack()
        self.frame1.pack()
        self.frame2.pack()
 
    def quit(self):
        self.master.destroy()    
        
class MonsterLogs:
    def __init__(self, master, monsters, monster_length):
        self.monsters = monsters
        self.monster_length = monster_length
        self.master = master
        self.make_window()
        
    def make_window(self):
        self.frame1 = tk.Frame(self.master)
        self.frame2 = tk.Frame(self.master)

        row_count = 0
        col_count = 0         
        tk.Label(self.frame1, 
                 text = "Monster Logs", 
                 font = "Verdana 9 bold"
                 ).grid(row = row_count, column = col_count, sticky = 'w')
        row_count += 1
       
        for i in range(self.monster_length):
            name = self.monsters[i][0]
            toggle = self.monsters[i][1]
            tk.Checkbutton(self.frame1,
                           text = name,
                           variable = toggle
                           ).grid(row = row_count, column = col_count, sticky = 'w')
            row_count += 1
            
        row_count = 0
        col_count += 1
        tk.Label(self.frame1, 
                 text = "Boss Logs",
                 font = "Verdana 9 bold"
                 ).grid(row = row_count, column = col_count, sticky = 'w')
        row_count += 1
        
        for i in range(self.monster_length, len(self.monsters)):
            name = self.monsters[i][0]
            toggle = self.monsters[i][1]
            tk.Checkbutton(self.frame1,
                           text = name,
                           variable = toggle
                           ).grid(row = row_count, column = col_count, sticky = 'w')   
            row_count += 1
            
        self.quitButton = tk.Button(self.frame2,
                                    text = "Return to Main Menu",
                                    command = self.quit).pack()
        self.frame1.pack()
        self.frame2.pack()

    def quit(self):
        self.master.destroy()

class Artifacts:
    def __init__(self, master, artifacts):
        self.artifacts = artifacts
        self.master = master
        self.make_window()
    
    def make_window(self):
        self.frame1 = tk.Frame(self.master)
        self.frame2 = tk.Frame(self.master)
        
        row_count = 0
        tk.Label(self.frame1, 
                 text = "Artifacts", 
                 font = "Verdana 9 bold"
                 ).grid(row = row_count, column = 0, sticky = 'w')
        for i in range(len(self.artifacts)):
            name = self.artifacts[i][0]
            toggle = self.artifacts[i][1]
            tk.Checkbutton(self.frame1,
                           text = name,
                           variable = toggle
                           ).grid(row = row_count, column = 0, sticky = 'w')
            row_count += 1
                         
        self.quitButton = tk.Button(self.frame2,
                                    text = "Return to Main Menu",
                                    command = self.quit).pack()
        self.frame1.pack()
        self.frame2.pack()

    def quit(self):
        self.master.destroy()
        
class Achievements:
    # TODO: Co-ordinate item logs & achievements more thoroughly
    # TODO: get the geometry manager working better    
    def __init__(self, master, achievements):         
        self.characters, self.specifics = self.get_specifics()
        self.master = master
        self.achievements = achievements
        self.columns = self.set_columns()
        self.rows = self.set_rows()
        self.make_window()
        
    def make_window(self):
        self.frame1 = tk.Frame(self.master)
        self.frame2 = tk.Frame(self.master)
        self.frame3 = tk.Frame(self.master)
        
        self.generics = tk.Label(self.frame1,
                                 text = "Generic Achievements",
                                 font = "Verdana 9 bold"
                                 ).grid(row = self.rows['generic'],
                                        column = 0, 
                                        sticky = 'w')
        self.rows['generic'] += 1
        self.character_specifics = tk.Label(self.frame2,
                                            text = "Character & Character-specific Achievements",
                                            font = "Verdana 9 bold"
                                            ).grid(row = 0, column = 3, sticky = 'e')
        for i in range(len(self.characters)):
            name = self.characters[i]
            tk.Label(self.frame2,
                     text = name,
                     font = "Verdana 9 bold"
                     ).grid(row = self.rows[name],
                            column = self.columns[self.characters[i]],
                            sticky = 'w')            

        for i in range(len(self.achievements)):
            cheevo_name = self.achievements[i][0]
            toggle = self.achievements[i][1]
            # Test whether it unlocks a character
            # Test whether it needs a character to be unlocked
            for key in self.specifics:
                if cheevo_name == self.specifics[key][0]:
                    tk.Checkbutton(self.frame2,
                                   text = ("Unlock: " + cheevo_name),
                                   variable = toggle,
                                   onvalue = 2
                                   ).grid(row = self.rows[cheevo_name],
                                          column = (self.columns[key]) + 1,
                                          sticky = 'w')
                    break
                elif cheevo_name == self.specifics[key][1]:
                    tk.Checkbutton(self.frame2,
                                   text = cheevo_name,
                                   variable = toggle,
                                   onvalue = 2
                                   ).grid(row = self.rows[cheevo_name],
                                          column = (self.columns[key]) + 1,
                                          sticky = 'w')
                    break
                elif cheevo_name == self.specifics[key][2]:
                    tk.Checkbutton(self.frame2,
                                   text = cheevo_name,
                                   variable = toggle,
                                   onvalue = 2
                                   ).grid(row = self.rows[cheevo_name],
                                          column = (self.columns[key]) + 1,
                                          sticky = 'w')
                    break
            else:
                tk.Checkbutton(self.frame1,
                               text = self.achievements[i][0],
                               variable = self.achievements[i][1],
                               onvalue = 2
                               ).grid(row = self.rows["generic"],
                                      column = self.columns['generic'],
                                      sticky = 'w')
                self.rows["generic"] += 1

                
        self.quitButton = tk.Button(self.frame3,
                                    text = "Return to Main Menu",
                                    command = self.quit).pack()
        
        self.frame1.grid(row = 0, column = 0)
        self.frame2.grid(row = 0, column = 1)
        self.frame3.grid(row = 1, column = 1)
    
    def set_columns(self):
        columns = {}
        for character in self.characters:
            if self.characters.index(character) < len(self.characters) // 2:
                columns[character] = 1
            else:
                columns[character] = 3
        columns['generic'] = 0
        return columns
    
    def set_rows(self):
        rows = {}
        rows['generic'] = 0
        cheevos_per_char = 3
        midpoint = len(self.characters) // 2
        for character in self.characters:
            char_index = self.characters.index(character)
            char_row = 1 + (char_index * cheevos_per_char)
            
            for cheevo in self.specifics[character]:
                cheevo_index = self.specifics[character].index(cheevo)
                cheevo_row = 1 + (char_index * cheevos_per_char) + cheevo_index
                if cheevo_row <= (midpoint * cheevos_per_char):
                    rows[cheevo] = cheevo_row
                else:
                    rows[cheevo] = cheevo_row - (midpoint * cheevos_per_char)
                    
            if char_row < (midpoint * cheevos_per_char):
                rows[character] = (char_row)
            else:
                rows[character] = (char_row - (midpoint * cheevos_per_char))
        return rows
    
    def get_specifics(self):
        characters = ["Commando", "Enforcer", "Bandit", "Huntress", "HAN-D",
                                   "Engineer", "Miner", "Sniper", "Acrid", "Mercenary"]
                
        character_unlocks = {"Commando":["None",
                                         "Dodge 7 lethal attacks",
                                         "Activate the 3rd teleporter without being hurt once"],
                             "Bandit":["Beat the 3rd Stage",
                                       "Kill a boss with Lights Out",
                                       "Reset your cooldown 15 times consecutively"],
                             "Enforcer":["Kill the Magma Worm, Wandering Vagrant, and Colossus",
                                         "Block 2000 damage total with your shield",
                                         "Stay in Shield Mode for 5 minutes straight (in combat)"],
                             "Huntress":["Collect 15 Monster Logs",
                                         "Achieve 200% attack speed",
                                         "Defeat the Legendary Wisp without taking damage"],
                             "HAN-D":["Find the robot janitor",
                                      "Kill 10 enemies simultaneously with Forced Reassembly",
                                      "Stay above 70% health for 25 minutes"],                       
                             "Engineer":["Purchase 40 drones total",
                                         "Detonate 15 Bounding Mines within 5 seconds",
                                         "Kill a boss in 15 seconds or less"],
                             "Miner":["Clear a path for the survivor",
                                      "Survive the teleporter event without falling below 50% health",
                                      "Reach level 10 without getting hurt more than once"],
                             "Sniper":["Beat the game",
                                       "Achieve 20 consecutive perfect reloads",
                                       "1-shot kill 10 enemies consecutively"],
                             "Acrid":["Free the chained creature",
                                      "Spread 10.000 feet of caustic sludge",
                                      "Spread epidemic to 25 enemies"],                                           
                             "Mercenary":["Beat the game 5 times",
                                          "Eviscerate 50 enemies",
                                          "Beat the game on Monsoon difficulty"]}
        return characters, character_unlocks    
        
    def quit(self):
        self.master.destroy()    

class SaveEditor:
    def __init__(self):
        self.root = tk.Tk()
        
        self.default_file_path = "C:/Program Files (x86)/Steam/SteamApps/common/Risk of Rain/"
        self.default_file_name = "Save.ini"
        self.default_file_backup = "Save_Editor_Backup.ini"
        self.saved_file_path = "Path_to_Save_File.in"
        self.file_path = ''
        
        # Check whether path to Save.ini has been altered; default if not
        if os.path.isfile(self.saved_file_path):
            file = open(self.saved_file_path, 'r')
            self.file_path = file.readline().strip()
            file.close()
        else:
            self.file_path = self.default_file_path + self.default_file_name
        
        self.main = MainWindow(self.root, self.file_path)
        self.root.mainloop()

def main():
    editor = SaveEditor()
    
if __name__ == "__main__":
    main()
