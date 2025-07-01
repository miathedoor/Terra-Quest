"""
Mia Isidore
2025.01.21
ICS3U - FSE

Terra Quest is an endless sidescroller with randomly generated level layouts.
The level layout is tile based, so values for different tile types are stored in a 2D list.
The objective of the game is to collect 100 gems in each terrain/level.
The player can choose and unlock different characters and terrains. The player can also buy powerups/upgrades for the player.

User progress such as:
- number of coins collected,
- number of gems collected,
- which players have been unlocked,
- which terrains have been unlocked,
- player stats including speed, agility (jump power),
  how many gems you lose when you touch a spike (gem resist)
  and how many coins you lose when you touch a spike (coin resist)...
are all saved to text files to be used again.
The user has the option to reset all game data to deafult starting values. 

"""

from random import *
from pygame import *

init()

TILE_SIZE = 18 # side length of tiles
BACKGROUND_SIZE = 24 # length of background tiles

FIT = (TILE_SIZE * BACKGROUND_SIZE) # 18 x 24 so that all my tiles will fit perfectly on the screen with no remainders.
WIDTH, HEIGHT = FIT*2, FIT
screen = display.set_mode((WIDTH, HEIGHT))
display.set_caption("Terra Quest")

LEVEL_WIDTH = 400  # number of tile colums in a "level chunk" when scrolling.
# Since this is an endless scroller, once the player reaches the end of the level chunk,
# 400 more tile columns worth of game is generated.

LEVEL_HEIGHT = HEIGHT // TILE_SIZE # the number of tiles tall the screen is.

coin_sound = mixer.Sound("DATA/music/coin.mp3") # collecting coins sound
gem_sound = mixer.Sound("DATA/music/gem.mp3") # collecting gems

#----------------------------------

# This game saves the player's progress in the game, such as number of coins and gems collected,
# what characters and terrains they've unlocked, and upgrades to their other stats like speed/agility.

def extract_data(data_file):
    """
    Takes the name of a text file and reads+returns the data inside it.
    """
    data_string = open(f"DATA/stats/{data_file}.txt").read().strip().split(" ")
    data = []
    for d in data_string:
        data.append(int(d))
    return data

def save_data(data_file, data):
    """
    Takes the name of a text file and saves the actual data by writing it to the text file.
    """
    out =  open(f"DATA/stats/{data_file}.txt", "w")

    for d in data:
        out.write(f"{d} ")

    out.close()

#----------------------------------

# I downloaded a tileset for the graphics of my game.

# top, right, bottom, left = trbl
# The terrain tiles in the tileset have a dark border on different locations on different tiles.
# Some tiles have a dark border on the top and left, some just on the top, etc.
# The list below classifies the different tiles by the borders they have.
terrain_terms = ["tl", "t", "tr", "trl", # terrain tiles have obvious markings such as green grass/snow/sand that set them apart from other terrain types.
             "tbl", "tb", "trb", "trbl"]
dirt_terms = ["bl", "b", "rb", "rbl", # dirt tiles are different from terrain tiles because the dirt matches with all the terrains.
              "l", "pure", "r", "rl"]

dirt_blocks = {} # will store dirt block images.

coin_image = image.load(f"DATA/images/Tiles/coin_0000.png") # coin image 
spike_image = image.load("DATA/images/Tiles/hazards/spike.png") # spike image


def generate_level(terrain):
    """
    The game's level is randomly generated and a 2D list is used
    to store the type of tile that will be in that tile position in the 2D list.
    
    """
    
    terrain_blocks = {} # will store terrain block images.
    count = 0
    for types in range(1,3): # loading terrain images
        for parts in range(4): 
            terrain_blocks[terrain_terms[count]] = image.load(f"DATA/images/Tiles/platforms/terrains/{terrain}/tile_0{types}0{parts}.png")
            dirt_blocks[dirt_terms[count]] = image.load(f"DATA/images/Tiles/platforms/dirt/tile_0{types}0{parts}.png")
            count += 1
            
    terrain_blocks[terrain_terms[-1]] = image.load(f"DATA/images/Tiles/platforms/terrains/{terrain}/tile_0203.png") # appending the final tile types
    dirt_blocks[dirt_terms[-1]] = image.load(f"DATA/images/Tiles/platforms/dirt/tile_0203.png") # since they wouldn't get appended in the loop above.
    # I have to load the images in such a convuluted loop because I spent time renaming them in a way thinking I would  use the numbers of their image file name in my code.
    # I didn't end up using them, so I realize I could've named them more simply, but it would take too much time to change everything.

    gem_image = image.load(f"DATA/images/Tiles/platforms/terrains/{terrain}/gem.png") # gem image, changes based on terrain type.
    
    decor_images = [] # will store terrain-themed decor tiles.
    for d in range(3):
        decor_images.append(image.load(f"DATA/images/Tiles/platforms/terrains/{terrain}/decor_0{d}.png"))

        

    # Since my game is an endless scroller, I generate a fresh level tile layouts everytime the player reaches the end of the current one.
    # To have a smooth transition between the end of one level "chunk" and the next chunk, I want the start and end to be uniformly "blank"
    # The "blank" layout is added to the tile layout at the end, over everything else that has been added.
    blank_space_tiles = ((WIDTH // 2) // TILE_SIZE) + ((WIDTH // 2) // TILE_SIZE)
    
    level = [] # The 2D list the tile layout will be stored in.
    for i in range(LEVEL_HEIGHT): # appending empty values 
        level.append([0] * LEVEL_WIDTH) 


    for x in range(LEVEL_WIDTH):# create a base layer that runs the entire width of the level
        level[LEVEL_HEIGHT - 1][x] = "pure" # layer closest to the bottom of the screen will be a "pure" dirt block with no dark border
        level[LEVEL_HEIGHT - 2][x] = "t" # the layer on top of the pure layer will be the terrain tile that only has a dark border on the top of the tile design.

    for i in range(blank_space_tiles, LEVEL_WIDTH-blank_space_tiles): # I don't want to generate anything in the reserved blank space at the start and end of level chunks.
        platform_height = randint(1, 9) # random height of a platform, in terms of tiles
        platform_width = randint(1, 9) # random width

        if (random() < 0.05): # generate coins
            coin_number = randint(3, 10) # coins are generated in "strings"

            x = randint(0, LEVEL_WIDTH - 1 - coin_number) # I had to make sure the random amount of coins generated 
            y = randint(0, LEVEL_HEIGHT-4)# wouldn't have x,y values that surpasses the level's limit.
            for j in range(coin_number):
                if level[y][x+j] == False: # To prevent coins from generating on top of tiles that are already occupying that position in the 2D layout
                    level[y][x+j] = "coin" # we can't assign coordinates in the normal "x, y" format since the format of a 2D list is that
                    # x is located INSIDE the yth list in the overall 2D list.

        if (random() < 0.04): # generate gems
            x = randint(0, LEVEL_WIDTH-1)
            y = randint(0, LEVEL_HEIGHT-4)
            if level[y][x] == False:
                level[y][x] = "gem"
        
                
        if (random() < 0.2) and (i + platform_width < LEVEL_WIDTH): # generate platforms

            platform_type = choice(["floating", "land", "land"]) # there are 2 types of platforms,
            # ones that float in the air, and ones that are "realistic" land masses
            
            if platform_type == "floating": # Generate a floating platform

                x = randint(0, LEVEL_WIDTH-blank_space_tiles-2- platform_width) # Once again, make sure the platform doesn't go out of the level's limits.
                y = randint(2, LEVEL_HEIGHT-4)

                level[y][x] = "tbl" # the first block will be a terrain block that is covered on all sides except the right, since it will connect to the following tiles:
                for j in range(1, platform_width+1):
                    level[y][x+j] = "tb"
                    if j == platform_width: # the last block will be like the first, but open on the left side only to connect nicely.
                        level[y][x+j+1]  = "trb"


            elif platform_type == "land": # Generate land mass platform
                
                x, y = i, LEVEL_HEIGHT-1

                for col in range(platform_width):
                    """
                     There are three different parts to a land mass:
                     -The starting column
                     -The middle column(s)
                     -The ending column
                     ---Some columns are only one tile wide as well.
                     Each of these scenarios has two types of tile designs associated with it:
                     - the terrain-themed tile that goes on the very top
                     - the dirt tile that builds the rest of the column.
                     
                     The blocks dictionary below contains the tile designs associated to each scenario of column type.
                    """
                    blocks = { "first":("l", "tl"),  # the first column needs a left border
                           "middle":("pure", "t"), # the middle columns(s) should be pure, without border. Only the top terrain tile should have a border. 
                           "last":("r", "tr"), # opposite of the first column
                           "single":("rl", "trl")} # singular columns need to be bordered on both sides.
                    
                    if platform_width == 1: # singular column
                        type_col = "single"
                    else: # else, it's a land mass that is not a single tower 
                        if col == 0: # the first column
                            type_col = "first" # type col is will be the key to the different scenarios in the blocks dictionary.
                        elif col == platform_width-1: # last column
                            type_col = "last"
                        else: # everything else is a middle column
                            type_col = "middle"

                    ex = x+col # x = x coord in the 2D list. col = the column in the platform we're currently assigning to the 2D list.
                    for row in range(platform_height):
                        level[y-row][ex] = blocks[type_col][0] # starting from the bottom and building up to the top, dirt blocks
                    level[y-platform_height][ex] = blocks[type_col][1] # the tile above those dirt blocks will be a terrain tile
                    
                    if (random() < 0.05) and y - platform_height - 1 > 0: # generate spikes
                        spike_number = randint(1, platform_width) # spikes also can appear in strings like coins.

                        sx = ex
                        sy = y-platform_height-1
                        for j in range(spike_number):
                            if level[sy][sx+j] == False and level[sy+1][sx+j] in terrain_terms: # spikes should'nt float, there should be a platform beneath them for realism.
                                level[sy][sx+j] = "spike" # that's why we check with "level[sy+1][sx+j]" being True to make sure there's a platform beneath.


                    if (random() < 0.5) and y - platform_height - 1 > 0: # generate terrain-themed decor
                        sx = ex
                        sy = y-platform_height-1
                        decor = randint(0, 2)
                        
                        if level[sy][sx] == False and level[sy+1][sx] in terrain_terms: # same idea as spikes, they can't float like coins and gems can.
                                level[sy][sx] = f"decor_0{decor}"

    # Now that everything else has bee generated, we add that black space at the start and end
    # for smooth transition between level generations
    
    for col in range(0, blank_space_tiles):
        for row in range(LEVEL_HEIGHT):
            level[row][col] = None  # Clearing any stray tiles at the start of the level

        level[LEVEL_HEIGHT - 1][col] = "pure" # pure dirt layer
        level[LEVEL_HEIGHT - 2][col] = "t" # top terrain layer
    
    for col in range(LEVEL_WIDTH - blank_space_tiles, LEVEL_WIDTH):# same as above but on the end of the level
        for row in range(LEVEL_HEIGHT):
            level[row][col] = None  
        level[LEVEL_HEIGHT - 1][col] = "pure" # setting the floor
        level[LEVEL_HEIGHT - 2][col] = "t" # setting the floor top layer
        

    return level, terrain_blocks, gem_image, decor_images



# Since the background was also given as tiles in the tileset I downloaded,
# I used code to piece together the background image.

background_terms = ["top","middle0","bottom", "middle1"] # Same idea as terrain generation, different types of tiles need to be classified
# So that an aesthetically pleasing layout can be created.

def generate_background(terrain):
    
    background_image = {}

    for i in range(4):
        background_image[background_terms[i]] = image.load(f"DATA/images/Tiles/backgrounds/{terrain}/tile_000{i}.png")
       
    for col in range(WIDTH//BACKGROUND_SIZE): # The top tiles are a lighter colour and only take up the top half of the screen.
        for row in range((HEIGHT//BACKGROUND_SIZE)//2):
            screen.blit(background_image["top"] , (col*BACKGROUND_SIZE, row*BACKGROUND_SIZE))

        for row in range((HEIGHT//BACKGROUND_SIZE)//2, HEIGHT//BACKGROUND_SIZE): # the bottom half will be a darker colour
            screen.blit(background_image["bottom"] , (col*BACKGROUND_SIZE, row*BACKGROUND_SIZE))

    flag = True
    for col in range(WIDTH//BACKGROUND_SIZE): # in the middle, there's an 2 term pattern of trees in the distance
        if flag:# I use a flag to decide which term of tree tile image should be blitted
            screen.blit(background_image["middle0"] , (col*BACKGROUND_SIZE, HEIGHT//2))
            flag = False
        else:
            screen.blit(background_image["middle1"] , (col*BACKGROUND_SIZE, HEIGHT//2))
            flag = True

    return screen.copy() # return the full image of the background



######################################################################

running = {"menu":False,
           "character_select":False,
           "terrain_select":False,
           "game":False,
           "shop":False,
           "tutorial":False,
           "reset":False,
           "win_screen": False,
           "reset": False
           
           } # each different mode of the game is in its own function with its own while loop that is running separately.

completed_terrains = 0 # checks if the game was been won by the player
# After the player has beat the game, each time they open up the game to play again,
# they will be reminded of the fact that they beat the game.

def main_menu():
    global game_started, completed_terrains

    # check each time the player returns to the menu after running a terrain or opening the game again
    # if they've beat the game or not.
    for p in range(len(terrains)): # For each terrain that has the required amount of gems,
        if extract_data(f"player_gems_{terrains[p]}")[0] >= 100: # increment the completed_terrains variable to keep track of the fact
            completed_terrains += 1

    if completed_terrains == 3: # If they've got 100 gems in each terrain, they've won.
        win_screen()
    elif completed_terrains < 3: # If they haven't fully finished the game, reset that variable to prevent unwanted incrementation
        completed_terrains = 0
        

    MENU_TILE = TILE_SIZE*2 # Spacings between menu objects are bigger than between game/level layout tiles
    screen.blit(generate_background("green"), (0,0))
    
    play_image = image.load(f"DATA/images/menu/button_play.png") # the tree leaf block that is the play button
    play_image_size = play_image.get_height() 
    play_rect = Rect((WIDTH//2)-(MENU_TILE*2),
                     LEVEL_HEIGHT-(LEVEL_HEIGHT-1),
                     play_image_size,
                     play_image_size)

    log_image = image.load(f"DATA/images/menu/log.png") # the trunk under the player button is just a log image blitted over and over
    log_image_size = log_image.get_height()

    # The buttons you can press in the menu
    menu_options = ["shop",
                    "tutorial",
                    "reset"]
    menu_images = [] # will store the buttons
    menu_rects = [] # stores the button coordinates

    menu_start = [ (WIDTH//2)-(MENU_TILE*3.3), play_rect.bottom+MENU_TILE] # the starting coord of the first button
    menu_size = [241, 49] # width and height of the menu buttons

    for m in range(len(menu_options)):
        menu_images.append(image.load(f"DATA/images/menu/button_{menu_options[m]}.png"))
        menu_rects.append(Rect(menu_start[X], menu_start[Y], menu_size[X], menu_size[Y]))
        menu_start[Y] += MENU_TILE*2 # the starting y coord is incremented for the next button

    screen.blit(play_image, play_rect) # blit the play button 
        
    for y in range(play_rect.bottom, HEIGHT,log_image_size):
        screen.blit(log_image, ((WIDTH//2)-(TILE_SIZE*1.3), y)) # blit the logs that make up the trunk


    for m in range(len(menu_options)):
        screen.blit(menu_images[m], menu_rects[m]) # blit the menu buttons


    game_started = False # this is a global variable that is essential for generating fresh levels as the player reaches the end of the current one.
    # See its usage in run_game()
    # it is set to false in this menu since the game is obviously not started yet while the user is still in the menu.

    running["menu"] = True
    while running["menu"]:
        for e in event.get():
            if e.type == QUIT:
                running["menu"] = False
            if e.type == MOUSEBUTTONDOWN:
                if play_rect.collidepoint(e.pos):
                    character_select()  # When the play button is pressed, the user is taken to the character select screen first
                    running["menu"] = False

                for m in range(len(menu_options)):
                    if menu_rects[m].collidepoint(e.pos):
                        if menu_options[m] == "shop": # shop button pressed
                            run_shop()
                            running["menu"] = False
                        elif menu_options[m] == "tutorial": # tutorial button
                            run_tutorial()
                            running["menu"] = False
                        elif menu_options[m] == "reset": # reset button
                            reset_confirm()
                            running["menu"] = False
                            
        
        display.flip()
  
#----------------------------------

back_button = image.load("DATA/images/menu/button_back.png") # "takes you back to the menu or whatever you were viewing before" button
button_rect = Rect(10, HEIGHT-back_button.get_height()-10, back_button.get_width(), back_button.get_height()) # coords for the back button


def reset_confirm():
    """
    Since the program saves the player's progress, it also gives the option to restart the game by resetting all progress.
    This function asks the user for confirming the  reset in case they accidentally pressed the reset button in the menu.
    """
    screen.blit(generate_background("green"), (0,0))
    confirm_image = image.load("DATA/images/menu/reset_confirmation.png")
    screen.blit(confirm_image, (WIDTH//2-confirm_image.get_width()//2, HEIGHT//2-confirm_image.get_height()//2 ))
    


    yes_button = image.load("DATA/images/menu/button_yes.png") # "yes I want to reset" button
    yes_rect = Rect(WIDTH//2+40, 270, yes_button.get_width(), yes_button.get_height())
    
    new_back_button = Rect(WIDTH//2-back_button.get_width()-30, 270, back_button.get_width(), back_button.get_height())
    # in every other instance the back button is in the bottom left corner, but in this reset confirmation, it's in the middle of the screen.


    screen.blit(yes_button, yes_rect)
    screen.blit(back_button, new_back_button)

    running["reset"] = True
    while running["reset"]:
        for e in event.get():
            if e.type == QUIT:
                running["reset"] = False
            if e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    if yes_rect.collidepoint(e.pos): # yes I want to reset all my hard earned progress
                        reset_values = ["player_coins", # these are all the data files that need to be reset to default values
                                        "player_gems_forest",
                                        "player_gems_tundra",
                                        "player_gems_desert",
                                        "unlocked_players",
                                        "unlocked_terrains",
                                        "player_stats"
                                        ]
                        for r in reset_values:
                            default = extract_data(f"default/{r}") # there's a folder filled with all the default values, copies of each data file
                            save_data(r, default)
                            
                        main_menu() # back the main menu once the act is done
                        running["reset"] = False

                            
                    elif new_back_button.collidepoint(e.pos): # I spent 143 hours on this game.
                        main_menu()
                        running["reset"] = False

        display.flip()
                        

def win_screen():
    # The user has beat the main goal of the game...

    screen.fill(0)
    screen.blit(image.load("DATA/images/relic.png"), (0,0)) 
    screen.blit(back_button, button_rect) # ...but they can continue to play since this game is so awesome and addicting.
    

    running["win_screen"] = True
    while running["win_screen"]:
        for e in event.get():
            if e.type == QUIT: # :(
                running["win_screen"] = False
            if e.type == MOUSEBUTTONDOWN: 
                if e.button == 1:
                    if button_rect.collidepoint(e.pos): # :)
                        main_menu()
                        running["win_screen"] = False

        display.flip()




######################################################################

players = ["green", "blue", "pink", "yellow", "beige"] # Different characters you can play as.

def character_select():
    """
    Before the actual game can be played, the player chooses a character to play as.
    """
    
    unlocked_players = extract_data("unlocked_players") # however they need to unlock characters before being able to play as them
    
    screen.blit(generate_background("green"), (0,0))

    # Since the images of the character avatars got blurry when I tried resizing them and putting them on blue squares in canva,
    # I decided to transform the character images to be bigger and placed them on top of blue squares using code:
    
    PROFILE_TILE = 72 # going to be the size of the player avatars once they've been transform.scaled
    SELECT_TILE = 96 # Size of the blue square behind player avaters
    SELECT_GAP = (WIDTH-len(players)*SELECT_TILE)//(len(players)+1) # gap between each select square

    unlocked_image = image.load("DATA/images/characters/unlocked.png") # the blue square 
    locked_image = image.load("DATA/images/characters/locked.png") # actual locked image

    select_profiles = [] # will store the transformed player avatars.
    select_rects = [] # Rects of the selectable options will be
    
    select_start = [SELECT_GAP, (HEIGHT//2)-(SELECT_TILE//2)] # coord of the first option which will be incremented for each next option
    for p in range(len(players)):
        select_profiles.append(transform.scale(image.load(f"DATA/images/Tiles/Characters/players/tile_{p}000.png"), (PROFILE_TILE, PROFILE_TILE)))
        select_rects.append(Rect(select_start[X], select_start[Y], SELECT_TILE, SELECT_TILE))
        select_start[X] += SELECT_TILE+SELECT_GAP 

        screen.blit(unlocked_image, select_rects[p])
        screen.blit(select_profiles[p], (select_rects[p][X]+PROFILE_TILE*0.2, select_rects[p][Y]+PROFILE_TILE*0.25, PROFILE_TILE, PROFILE_TILE))
        
        if unlocked_players[p] == False: # if the player is locked, blit the locked image on top of the option.
            screen.blit(locked_image, select_rects[p])

    screen.blit(back_button, button_rect)
    
    running["character_select"] = True
    while running["character_select"]:
        for e in event.get():
            if e.type == QUIT:
                running["character_select"] = False
            if e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    if button_rect.collidepoint(e.pos): # back to menu
                        main_menu()
                        running["character_select"] = False
                for p in range(len(players)):
                    if select_rects[p].collidepoint(e.pos) and unlocked_players[p]: # if the player clicks an unlocked option
                        player_frames = generate_player(p) # load the selected character's animation frames
            
                        terrain_select(player_frames) # next the player needs to choose what terrain 
                        running["character_select"] = False
                        
        
        display.flip()


LEFT, RIGHT = 0, 1  # constant indexes where the left facing and right facing images will be stored
# these constants are also used for movement and animation of the player.

def generate_player(selected_player):
    """
    Load the selected character's animation frames.
    """
    player_frames = [[],[]] # LEFT, RIGHT

    for f in range(2):
        i = image.load(f"DATA/images/Tiles/Characters/players/tile_{selected_player}00{f}.png")
        player_frames[LEFT].append(i)
        player_frames[RIGHT].append(transform.flip(i, True, False))
        
    return player_frames


#----------------------------------

pixel_font24 = font.Font("DATA/PressStart2P-Regular.ttf", 24) # font size 24
pixel_font18 = font.Font("DATA/PressStart2P-Regular.ttf", 18) # font size 18

terrains = ["forest", # the 3 different terrains you can play in.
            "tundra",
            "desert"]

def terrain_select(player_frames): # player frames are passed into terrain select so it can be passed into the actual run game function
    """
    After selecting a character to play as, select the terrain you want to play in before the real game begins.
    """
    unlocked_terrains = extract_data("unlocked_terrains") # essentially the same code as with the character select
    # But I made the entire image for each selecting profile on canva so there is less complex coord assigning/blitting of images.
    
    screen.blit(generate_background("green"), (0,0))
                
    SELECT_TILE = 182
    SELECT_GAP = (WIDTH-len(terrains)*SELECT_TILE)//(len(terrains)+1)

    locked_image = image.load("DATA/images/terrains/locked.png")

    select_profiles = []
    select_rects = []

    # For blitting the count of gems the user has collected so far above each terrain
    gem_counts = [] 
    for p in range(len(terrains)):
        gem_value = extract_data(f"player_gems_{terrains[p]}")
        gem_count_text = pixel_font18.render(f"{str(gem_value[0])}/100", True, (255, 255, 255))
        gem_counts.append(gem_count_text)

    
    select_start = [SELECT_GAP, (HEIGHT//2)-(SELECT_TILE//2)]
    for p in range(len(terrains)):
        select_profiles.append(image.load(f"DATA/images/terrains/profile_{terrains[p]}.png"))
        select_rects.append(Rect(select_start[X], select_start[Y], SELECT_TILE, SELECT_TILE))
        select_start[X] += SELECT_TILE+SELECT_GAP
    for p in range(len(terrains)):
        screen.blit(select_profiles[p], select_rects[p])
        if unlocked_terrains[p] == False: 
            screen.blit(locked_image, select_rects[p])
        else: # if the terrain is unlocked, blit the gem count 
            W, H = 2, 3
            gem_image = image.load(f"DATA/images/Tiles/platforms/terrains/{terrains[p]}/gem.png") # image of actual gem

            gem_start = select_rects[p][X], select_rects[p][Y]-gem_image.get_height()-10
            
            screen.blit(gem_image, gem_start) # blit the gem 
            screen.blit(gem_counts[p], (gem_start[X]+gem_image.get_width()+10, gem_start[Y])) # blit the text
            
            
            
    screen.blit(back_button, button_rect)
    
    running["terrain_select"] = True
    while running["terrain_select"]:
        for e in event.get():
            if e.type == QUIT:
                running["terrain_select"] = False
            if e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    if button_rect.collidepoint(e.pos): # when the back button is pressed
                        character_select() # it goes back to character select
                        running["terrain_select"] = False
                for p in range(len(terrains)):
                    if select_rects[p].collidepoint(e.pos) and unlocked_terrains[p]:
                        run_game(player_frames, terrains[p]) # run the game, passing in the selected terrain
                        running["terrain_select"] = False
                        
        
        display.flip()


######################################################################

# the player's data is more easy to manage as a list.
guy = [0,0,  2, True,False, 0,WIDTH//2,0, 1,5, 24]

# The below constants are the indexes at which each of the player's data is found in the list
X,Y,VY, ONGROUND,MOVING, FRAME,START_X,SCROLL_Y, DIRECTION,SPEED, SIZE = 0,1, 2,3,4, 5,6,7, 8,9, 10



SPEED, AGILITY, GEM_RESIST, COIN_RESIST = 0, 1, 2, 3 # these are also constants for another list called "player_stats"
# player_stats can be upgraded by the player and is player progress that is saved and extracted every time, in a separate list.
# agility = jump power
#Gem and coin resist is the number of item you lose when you touch a spike. you can upgrade in the shop to reduce the number of item you lose.

def run_game(player_frames, current_terrain):
    """
    Runs all the functions necessary to play the actual game.
    """
    global guy, game_started
    
    background_image = generate_background(current_terrain)
    
    player_coins = extract_data("player_coins")
    player_gems = extract_data(f"player_gems_{current_terrain}")
    player_stats = extract_data("player_stats")


    myClock = time.Clock()
    running["game"] = True
    while running["game"]:
        for e in event.get():
            if e.type == QUIT: # save player progress when they quit the program
                save_data("player_coins", player_coins)
                save_data(f"player_gems_{current_terrain}", player_gems)
                running["game"] = False
            if e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    if button_rect.collidepoint(e.pos): # back to the menu
                        save_data("player_coins", player_coins) # save player progress
                        save_data(f"player_gems_{current_terrain}", player_gems)
                        
                        main_menu()
                        running["game"] = False


        screen.blit(background_image, (0,0))

        if not game_started:
            """
            Whenver game is considered not started, all values are reset/re-generated.
            This variable is set to false when the player collides with the end of the current level chunk, see check_collide() function.
            """
            level, terrain_blocks, gem_image, decor_images = generate_level(current_terrain)
            guy[X]= guy[START_X]
            
            game_started = True
        
        draw_level(guy, level, terrain_blocks, gem_image, player_frames, decor_images, player_coins, player_gems)
        
        moving_right, moving_left = check_collision(guy, level, player_stats, player_coins, player_gems)
        move_player(guy, moving_right, moving_left, player_frames, player_stats)
        draw_player(guy, player_frames)
        

        screen.blit(back_button, button_rect) 
        myClock.tick(60)
        display.flip()


             
#--------------------------------------------

def draw_level(guy, level, terrain_blocks, gem_image, player_frames, decor_images, player_coins, player_gems):
    """
    Takes the 2D list and draws tiles corresponding to the data the list holds.
    """

    offset = WIDTH//2 - guy[X] 
    
    for row_index, row in enumerate(level): # The level is filled with string values at each position.
        for col_index, tile_id in enumerate(row): # The string values will finally be blitted as images:
            
            if tile_id:
                if tile_id in terrain_terms:
                    tile = terrain_blocks[tile_id] # the tile will be the image (block) at the key of that tile id
                elif tile_id in dirt_terms:
                    tile = dirt_blocks[tile_id]
                else:
                    tile_images = {"coin":coin_image, # tile_id:corresponding image
                                   "gem":gem_image,
                                   "spike":spike_image,
                                   "safe_spike":spike_image,
                                   "decor_00":decor_images[0],
                                   "decor_01":decor_images[1],
                                   "decor_02":decor_images[2],
                                   }
                    
                    tile = tile_images[tile_id]
                    
                if tile:
                    screen.blit(tile, ((col_index * TILE_SIZE) + offset, row_index * TILE_SIZE))

    # display the count of coins the player has collected
    player_coins_text = pixel_font24.render(str(player_coins[0]), True, (255, 255, 255)) 
    coin_start = WIDTH-coin_image.get_width()-player_coins_text.get_width()-BACKGROUND_SIZE
    
    screen.blit(transform.scale(coin_image, (BACKGROUND_SIZE, BACKGROUND_SIZE)), (coin_start, HEIGHT-24))
    screen.blit(player_coins_text, (coin_start+BACKGROUND_SIZE, HEIGHT-24))
    
    # Display gem count
    player_gems_image = pixel_font24.render(str(player_gems[0]), True, (255, 255, 255))

    screen.blit(transform.scale(gem_image, (BACKGROUND_SIZE, BACKGROUND_SIZE)), (coin_start, HEIGHT-24*2))
    screen.blit(player_gems_image, (coin_start+BACKGROUND_SIZE, HEIGHT-24*2))

#--------------------------------------------

def move_player(guy, moving_right, moving_left, player_frames, player_stats):
    """
    Moves the player based on user key presses.
    """
    
    keys = key.get_pressed()
    guy[MOVING] = False  # Flag if player is moving to decide wheter to animate or not

    # Horizontal movement
    if keys[K_LEFT] and guy[X] > guy[START_X] and moving_left: # see moving_left/right in check_collide() function
        guy[X] -= player_stats[SPEED]
        guy[DIRECTION] = LEFT # set direction for animation
        guy[MOVING] = True # animation only occurs when there is movement
    
        
    elif keys[K_RIGHT] and guy[X] < LEVEL_WIDTH*TILE_SIZE and moving_right:
        guy[X] += player_stats[SPEED]
        guy[DIRECTION] = RIGHT  
        guy[MOVING] = True
        

    # Jumping
    if keys[K_UP] and guy[ONGROUND]:
        guy[VY] = -player_stats[AGILITY]
        guy[ONGROUND] = False # you're in the air! see check_collide() for getting back down to earth.


    # Gravity 
    guy[Y] += guy[VY]
    guy[VY] += 1  

    # keep player from jumping/moving out of screen limits.
    if guy[X] < 0:
        guy[X] = 0
    elif guy[X] > LEVEL_WIDTH * TILE_SIZE - guy[SIZE]:
        guy[X] = LEVEL_WIDTH * TILE_SIZE - guy[SIZE]

    if guy[Y] < 0:
        guy[Y] = 0
    elif guy[Y] > LEVEL_HEIGHT * TILE_SIZE - guy[SIZE]:
        guy[Y] = LEVEL_HEIGHT * TILE_SIZE - guy[SIZE]


   
def draw_player(guy, image_frames): # drawing/blitting and animation
    
    if guy[MOVING]:
        guy[FRAME] += 0.25 # 0.15 = frame_speed
        if guy[FRAME] >= len(image_frames):
            guy[FRAME] = 0
    else:
        guy[FRAME] = 0  # standing frame when idle
    
    # Blits the player facing the direction they are moving in and the animation frame
    player_image = image_frames[guy[DIRECTION]][int(guy[FRAME])]
    screen.blit(player_image, (WIDTH//2, guy[Y]))

    
def check_collision(guy, level, player_stats, player_coins, player_gems):
    global game_started

    player_rect = Rect(guy[X], guy[Y], guy[SIZE], guy[SIZE])  # Player rectangle
    
    guy[ONGROUND] = False # These variables are set to these assumptions because in the following code,
    moving_left = True # we will see if they will be proven to be opposite of what they are right here,
    moving_right = True # which means a collision happened. Otherwise, they'll stay the same, meaning no collision occured.

    
    if player_rect.right > (LEVEL_WIDTH * TILE_SIZE - WIDTH // 2):
        # if the player reachers the halfway of the screen before the end of level chunk,
        # set game started to false so that run_game() will reset/re-generate data for the game.
        # (the player only has to reach halfway of the screen before the level end so that the transition
        # between the start and end of level chunks is smooth)
        
        game_started = False
        

    for row in range(0, LEVEL_HEIGHT): # Similar to draw_level()
        for col in range(0, LEVEL_WIDTH):
            
            tile_id = level[row][col] # string value in 2D list at the current position
            tile_rect = Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
            if tile_id and player_rect.colliderect(tile_rect):

                # landing on platform collisions
                if tile_id in terrain_terms:
                    if guy[VY] > 0 and player_rect.move(0,-guy[VY]).colliderect(tile_rect)==False:
                        guy[ONGROUND] = True
                        guy[VY] = 0
                        guy[Y] = tile_rect.top - guy[SIZE]
                        
                    
                # Left/right wall collisoins
                if tile_id in terrain_terms or tile_id in dirt_terms: # you can also collide with 
                    if  tile_rect.left <= player_rect.right and player_rect.right < tile_rect.right and  player_rect.move(-player_stats[SPEED], 0).colliderect(tile_rect) == False:
                        # set moving_left/right false when a collision occurs,
                        # so then in move_player, the player won't move at all since moving_left/right is false
                        moving_right = False
                        
                    if  player_rect.left <= tile_rect.right and tile_rect.left < player_rect.left and  player_rect.move(player_stats[SPEED], 0).colliderect(tile_rect) == False:
                        moving_left = False


                # Other collisions
                if tile_id == "coin": # collect coins
                    player_coins[0] += 1
                    coin_sound.play()
                    level[row][col] = None
                if tile_id == "gem":# collect gems
                    player_gems[0] += 1
                    gem_sound.play()
                    level[row][col] = None
                if tile_id == "spike": # get harmed by spikes
                    player_gems[0] -= player_stats[GEM_RESIST] # gem resist is the number of gems you lose if you touch a spike.
                    if player_gems[0] < 0: # you can upgrade in the shop to reduce this number.
                        player_gems[0] = 0

                    player_coins[0] -= player_stats[COIN_RESIST]
                    if player_coins[0] < 0:
                        player_coins[0] = 0

                    level[row][col] = "safe_spike" # once the spike has done damage once, it'll become "safe" and won't continue to hurt the player

                    
    return moving_right, moving_left

                        

######################################################################

def run_shop():
    """
    To purchase terrains, characters, and upgrades.
    I got the code for the vertical scrolling code in the shop and the tutorial function
    from "100 Days of Code: The Complete Python Pro Bootcamp" on Udemy.
    
    """
    background_image = generate_background("green")
    unlocked_players = extract_data("unlocked_players")
    unlocked_terrains = extract_data("unlocked_terrains")

    player_coins = extract_data("player_coins")
    player_stats = extract_data("player_stats")

    BROWN = 120, 67, 27

    items = []# a list that will store dictionaries for each item that can be bought.

    SELECT = [0, 0,655, 259,18] # Dimensions for select boxes, like with the guy list that had the player dimensions.
    W, H, GAP = 2,3,4

    SELECT[X] = (WIDTH - SELECT[W]) // 2
    SELECT[Y] = SELECT[GAP] #  starting y position will be a GAP length away from the top of the screen.

    powerups = ["agility_plus", "speed_plus", "gems", "coins", "agility_minus", "speed_minus"] # the differnt upgrades available to purchase
    
    shop_names = terrains + players + powerups # overall every item available for purchase.
    shop_prices = [1000, 1000, 1000, # prices of each item.
                   500, 500, 500, 500, 500,
                   50, 100, 500, 250, 50, 100]

    
    for name in shop_names:
        add_to_shop = False
        
        if name in terrains:
            if unlocked_terrains[terrains.index(name)] == False: #checks if the terrain is unlocked
              add_to_shop = True # and if it is locked, that means this item needs to be added to the shop.
              
        elif name in players:
            if unlocked_players[players.index(name)] == False:  #check if the player is unlocked
              add_to_shop = True
        elif name in powerups: # since powerups aren't a one time purchase,  you can still buy it again even if you've bought it once.
            add_to_shop = True

        if add_to_shop:
            items.append({ "image": image.load(f"DATA/images/shop/item_{name}.png"),
                           "rect": Rect(SELECT[X], SELECT[Y], SELECT[W], SELECT[H]),
                           "name": name,
                           "price": shop_prices[shop_names.index(name)] 
                           })
            
            SELECT[Y] += SELECT[H] + SELECT[GAP] # spacing between select profiles

    
    # The user uses the mouse scroll wheel to scroll vertically through shop items:
    # Calculate the total height of all the items combined
    # to get the max limit to scroll downwards.
    scroll_height = 0
    for i in items:
        scroll_height += i["rect"][H] + SELECT[GAP] # the concept of needing a scroll height is the specific code I didn't come up with on my own.

    guy[Y] = 0  # keeps track of where the user is vertically in the "world" of the shop, just like in the game.
    scroll_speed = 10  # how fast items get scrolled 
    
    running["shop"] = True
    while running["shop"]:
        for e in event.get():
            if e.type == QUIT:
                running["shop"] = False
            if e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    if button_rect.collidepoint(e.pos): # back to menu
                        main_menu()
                        running["shop"] = False
                        
                    # Buying items
                    for i in items:
                        item_rect = i["rect"]
                        item_rect = item_rect.move(0, -guy[Y])
                        if item_rect.collidepoint(e.pos):
                            if player_coins[0] >= i["price"]:
                                player_coins[0] -= i["price"] # subtract cost of item
                                save_data("player_coins", player_coins)

                                if i["name"] in terrains:
                                    unlocked_terrains[terrains.index(i["name"])] = 1
                                    save_data("unlocked_terrains", unlocked_terrains)
                                    items.remove(i) # terrains are a one time purchase, so they get removed from the shop once purchased.
                                elif i["name"] in players:
                                    unlocked_players[players.index(i["name"])] = 1
                                    save_data("unlocked_players", unlocked_players)
                                    items.remove(i)

                                elif i["name"] in powerups: # powerups are not a one time purchase.
                                    powerup = i["name"]
                                    if powerup == "agility_plus":
                                        player_stats[AGILITY] += 1
                                    elif powerup == "agility_minus":
                                        player_stats[AGILITY] -= 1
                                        
                                    elif powerup == "speed_plus":
                                        player_stats[SPEED] += 1
                                    elif powerup == "speed_minus":
                                        player_stats[SPEED] -= 1

                                    elif powerup == "gems":
                                        player_stats[GEM_RESIST] -=1
                                    elif powerup == "coins":
                                        player_stats[COIN_RESIST] -= 1
                                        
                                    save_data("player_stats", player_stats)
                                        
                elif e.button == 4:  # Scroll up
                    guy[Y] -= scroll_speed
                    if guy[Y] < 0:
                        guy[Y] = 0
                elif e.button == 5:  # Scroll down
                    guy[Y] += scroll_speed
                    if guy[Y] > scroll_height-items[0]["image"].get_height():
                        guy[Y] = scroll_height-items[0]["image"].get_height()



        screen.blit(background_image, (0, 0))

        # Draw the select profiles for each item.
        for i in items:
            screen.blit(i["image"], (i["rect"][X],  i["rect"][Y] - guy[Y] ) )
            price_text = pixel_font18.render(str(i["price"]), True, BROWN) # display the price of the item 
            screen.blit(transform.scale(coin_image, (price_text.get_height(),price_text.get_height())), (i["rect"][X]+270, i["rect"][Y]+i["rect"][H]-48 - guy[Y]))
            screen.blit(price_text,(i["rect"][X]+300, i["rect"][Y]+i["rect"][H]-48 - guy[Y]))
        
        player_coins_text = pixel_font24.render(str(player_coins[0]), True, (255, 255, 255)) # display the amount of coins the player has earned.
        coin_start = WIDTH-coin_image.get_width()-player_coins_text.get_width()-BACKGROUND_SIZE
        screen.blit(transform.scale(coin_image, (BACKGROUND_SIZE, BACKGROUND_SIZE)), (coin_start, HEIGHT-24))
        screen.blit(player_coins_text, (coin_start+BACKGROUND_SIZE, HEIGHT-24))

        screen.blit(back_button, button_rect)
        display.flip()


    
def run_tutorial():
    """
    Game lore and a tutorial on how to play the game, presented as a parchment scroll that can be scrolled through.
    I got the code for the vertical scrolling code in the shop and the tutorial function
    from "100 Days of Code: The Complete Python Pro Bootcamp" on Udemy.
    
    """
    background_image = generate_background("green")

    scroll_start = image.load(f"DATA/images/tutorial/scroll_start.png") # top part of the parchment scroll
    scroll_end = image.load(f"DATA/images/tutorial/scroll_end.png") # bottom part of the parchment scroll

    scroll_images = [scroll_start] # This list will hold all the parts of the parchment scroll together.
    for s in range(5):
        scroll_images.append(image.load(f"DATA/images/tutorial/scroll ({s+1}).png")) # appending the middle parts together
    scroll_images.append(scroll_end)


    scroll_height = 0
    for i in scroll_images:
        scroll_height += i.get_height()

    guy[Y] = 0
    scroll_speed = 10

    running["tutorial"] = True
    while running["tutorial"]:
        for e in event.get():
            if e.type == QUIT:
                running["tutorial"] = False
                
            if e.type == MOUSEBUTTONDOWN:
                if e.button == 1:
                    if button_rect.collidepoint(e.pos):
                        main_menu()
                        running["tutorial"] = False
                        
                elif e.button == 4:  # Scroll up
                    guy[Y] -= scroll_speed
                    if guy[Y] < 0:
                        guy[Y] = 0
                elif e.button == 5:  # Scroll down
                    guy[Y] += scroll_speed
                    if guy[Y] > scroll_height-scroll_images[0].get_height():
                        guy[Y] = scroll_height-scroll_images[0].get_height()
                        

        screen.blit(background_image, (0, 0))

        offset = 0 # I needed an offset for the tutorial since I didn't have rects assigned to each scroll image like I had for the shop items.
        for i in scroll_images:
            screen.blit(i, ((WIDTH - i.get_width()) // 2, offset - guy[Y]))
            offset += i.get_height()

        screen.blit(back_button, button_rect)
        display.flip()

main_menu() # Start the game!
quit()
