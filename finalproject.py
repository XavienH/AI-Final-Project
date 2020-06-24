from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import curses
import sys
import random

from pycolab import ascii_art
from pycolab import cropping
from pycolab import human_ui
from pycolab import things as plab_things
from pycolab.prefab_parts import sprites as prefab_sprites

pedestrian_move_case = None
algorithm_case = None
testres = 0
flag = 0
level = None
north = 0
east = 0
west = 0
south = 0
steps = 0

# pylint: disable=line-too-long
MAZES_ART = [
    # Legend:
    #     '#': impassable walls.           
    #     'a - Y (excluding P)': pedestrians.
    #     'P': player starting location.
    #     ' ': boring old maze floor.
    #
    # Maze #0:
    ['#################',
     '#              *#',
     '#               #',
     '#               #',
     '#               #',
     '#    a          #',
     '#               #',
     '#               #',
     '#               #',
     '#P              #',
     '#################'],

    ['#################',
     '#              *#',
     '#               #',
     '#               #',
     '#            c  #',
     '#    a          #',
     '#               #',
     '#               #',
     '#               #',
     '#P              #',
     '#################'],

    ['#############################################',
     '#                                          *#',
     '#                     ######                #',
     '#                                           #',
     '#      #######                              #',
     '#                                           #',
     '#                                           #',
     '#                          #########        #',
     '#                   b                       #',
     '#        #                       a          #',
     '#        #                                  #',
     '#        #                  #          #    #',
     '#        #######            #          #    #',
     '#                           #          #    #',
     '#                                      #    #',
     '#                                           #',
     '#                                           #',
     '#P                                          #',
     '#############################################'],

    ['#############################################',
     '#                                          *#',
     '#                     ######                #',
     '#                                           #',
     '#      #######        b                     #',
     '#           a                               #',
     '#                                           #',
     '#                          #########        #',
     '#                                           #',
     '#        #                       d          #',
     '#        #                                  #',
     '#        #                  #          #    #',
     '#        #######            #          #    #',
     '#                           #          #    #',
     '#                                      #    #',
     '#         c                                 #',
     '#                                           #',
     '#P                                          #',
     '#############################################'],

    ['###################################################################################################',
     '#                                                                                                *#',
     '#                                                                                                 #',
     '#                                                                                                 #',
     '#                           ##########                                                            #',
     '#                                                                 ##################              #',
     '#                                                                                                 #',
     '#                                                               d                                 #',
     '#                                                                                                 #',
     '#                                                                                                 #',
     '#            #                                                                                    #',
     '#            #                                                                                    #',
     '#            #                                                                                    #',
     '#            #             #################                                                      #',
     '#            #                                                                  #                 #',
     '#            #                                                                  #        e        #',
     '#            #                                                                  #                 #',
     '#            #                                       #                          #                 #',
     '#                                  a                 #                          #                 #',
     '#                                                    #######                    #                 #',
     '#                                                                               #                 #',
     '#                                                                               #                 #',
     '#                                                                               #                 #',
     '#      ##############                                                           #                 #',
     '#      #                                                                                          #',
     '#      #                                                                                          #',
     '#                                                                                                 #',
     '#P                                                                                                #',
     '###################################################################################################'],

    ['###################################################################################################',
     '#                                                                                                *#',
     '#                                                                                                 #',
     '#                                                                                                 #',
     '#                           ##########                                                            #',
     '#                                                                 ##################              #',
     '#                                                                                                 #',
     '#                                                               d                                 #',
     '#                                   c                                                             #',
     '#                                                                                                 #',
     '#            #                                                                                    #',
     '#            #                                                                                    #',
     '#            #                                                                                    #',
     '#            #             #################                                                      #',
     '#     b      #                                                                  #           e     #',
     '#            #                                                                  #                 #',
     '#            #                                                                  #                 #',
     '#            #                                       #                          #                 #',
     '#                                  a                 #                          #                 #',
     '#                                                    #######                    #                 #',
     '#                                                                               #                 #',
     '#                                                                               #                 #',
     '#                                                                               #                 #',
     '#      ##############                                                           #                 #',
     '#      #                                                                                          #',
     '#      #                                                                                          #',
     '#                                                                                                 #',
     '#P                                                                                                #',
     '###################################################################################################'],
]

# For dramatic effect, none of the levels start the game with the first
# observation centred on the player; instead, the view in the window is shifted
# such that the player is this many rows, columns away from the centre.
STARTER_OFFSET = [(0, 0),  # For level 0
                  (0, 0),    # For level 1
                  (0, 0),    # For level 2
                  (0, 0),
                  (0, 0),    # For level 2
                  (0, 0)]    # For level 3


# These colours are only for humans to see in the CursesUi.
COLOUR_FG = {' ': (0, 0, 0),        # Default black background
             '@': (999, 862, 110),  # Shimmering golden coins
             '#': (950, 500, 200),    # Walls of the maze
             'a': (900, 100, 700),    
             'b': (900, 100, 700),  
             'c': (222, 623, 999),
             'd': (900, 100, 700),
             'e': (900, 100, 700),
             # 'f': (999, 0, 780),  
             # 'g': (987, 623, 145),
             # 'h': (999, 0, 780),
             # 'i': (999, 0, 780),
             # 'j': (999, 0, 780),  
             # 'k': (987, 623, 145),
             # 'l': (999, 0, 780),
             # 'm': (999, 0, 780),
             # 'n': (999, 0, 780),  
             # 'o': (987, 623, 145),
             # 'p': (999, 0, 780),
             # 'q': (999, 0, 780),
             # 'r': (999, 0, 780),  
             # 's': (987, 623, 145),
             # 't': (999, 0, 780),
             # 'u': (999, 0, 780),
             # 'v': (999, 0, 780),  
             # 'w': (987, 623, 145),
             # 'x': (999, 0, 780),
             # 'y': (999, 0, 780),
             # 'z': (999, 0, 780),  
             # 'A': (987, 623, 145),
             # 'B': (999, 0, 780),
             # 'C': (999, 0, 780),
             # 'D': (999, 0, 780),  
             # 'E': (987, 623, 145),
             # 'F': (987, 623, 145),
             # 'G': (999, 0, 780),
             # 'H': (999, 0, 780),
             # 'I': (999, 0, 780),  
             # 'J': (987, 623, 145),
             # 'K': (987, 623, 145),
             # 'L': (999, 0, 780),
             # 'M': (999, 0, 780),
             # 'N': (999, 0, 780),  
             # 'O': (987, 623, 145),
             # 'Q': (987, 623, 145),
             # 'R': (999, 0, 780),
             # 'S': (999, 0, 780),
             # 'T': (999, 0, 780),  
             # 'U': (987, 623, 145),
             # 'V': (987, 623, 145),
             # 'W': (999, 0, 780),
             # 'X': (999, 0, 780),
             # 'Y': (999, 0, 780),
            #'*': (300, 300, 300),  
             } 

class Pedestrians_pos():
  def __init__(self, row, col, mask_flag):
    self.row = row
    self.col = col
    self.mask_flag = mask_flag             

def make_game(level):
  """Builds and returns a Better Scrolly Maze game for the selected level."""
  return ascii_art.ascii_art_to_game(
      MAZES_ART[level], what_lies_beneath=' ',
      sprites={
          'P': PlayerSprite,
          'a': PedSprite,
          'b': PedSprite,
          'c': PedSprite,
          'd': PedSprite,
          'e': PedSprite,
          '*': PedSprite,
          # 'f': PedSprite,
          # 'g': PedSprite,
          # 'h': PedSprite,
          # 'i': PedSprite,
          # 'j': PedSprite,
          # 'k': PedSprite,
          # 'l': PedSprite,
          # 'm': PedSprite,
          # 'n': PedSprite, 'o': PedSprite, 'p': PedSprite, 'q': PedSprite, 'r': PedSprite, 's': PedSprite,
          # 't': PedSprite, 'u': PedSprite, 'v': PedSprite, 'w': PedSprite, 'x': PedSprite, 'y': PedSprite,
          # 'z': PedSprite, 'A': PedSprite, 'B': PedSprite, 'C': PedSprite, 'D': PedSprite, 'E': PedSprite,
          # 'F': PedSprite, 'G': PedSprite, 'H': PedSprite, 'I': PedSprite, 'J': PedSprite, 'K': PedSprite,
          # 'L': PedSprite, 'M': PedSprite, 'N': PedSprite, 'O': PedSprite, 'Y': PedSprite, 'Q': PedSprite,
          # 'R': PedSprite, 'S': PedSprite, 'T': PedSprite, 'U': PedSprite, 'V': PedSprite,
          # 'W': PedSprite, 'X': PedSprite, 'Y': PedSprite, '*': PedSprite
          },
      update_schedule=['P', 'a', 'b', 'c', 'd', 'e', '*'],
      #, 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'P', '*'],
      z_order='Pabcde*')
  #fghijklmnopqrstuvwxyzABCDEFGHIJKLMNOQRSTUVWXY*


def make_croppers(level):

  if level == 0:
    return [
        # The player view.
        cropping.ScrollingCropper(rows=11, cols=17, to_track=['P'], initial_offset=STARTER_OFFSET[level])]
  elif level == 1:
    return [cropping.ScrollingCropper(rows=11, cols=17, to_track=['P'], initial_offset=STARTER_OFFSET[level])]
  elif level == 2:
    return [cropping.ScrollingCropper(rows=19, cols=45, to_track=['P'], initial_offset=STARTER_OFFSET[level])]
  elif level == 3:
    return [cropping.ScrollingCropper(rows=19, cols=45, to_track=['P'], initial_offset=STARTER_OFFSET[level])]
  elif level == 4:
    return [cropping.ScrollingCropper(rows=29, cols=99, to_track=['P'], initial_offset=STARTER_OFFSET[level])]
  elif level == 5:
    return [cropping.ScrollingCropper(rows=29, cols=99, to_track=['P'], initial_offset=STARTER_OFFSET[level])]  
  # elif level == 3:
  #   return [cropping.ScrollingCropper(rows=29, cols=106, to_track=['P'], initial_offset=STARTER_OFFSET[level])]  

class PlayerSprite(prefab_sprites.MazeWalker):
  def __init__(self, corner, position, character):
    """Constructor: just tells `MazeWalker` we can't walk through walls."""
    super(PlayerSprite, self).__init__(
        corner, position, character, impassable='#')

  def update(self, actions, board, layers, backdrop, things, the_plot):
    if algorithm_case != 0 and actions != 5:
      actions = 20

    if algorithm_case == 1:
      if level < 6 and level != 0:
        row, col = self.position
        rowA, colA = things['a'].position
        rowB, colB = things['b'].position
        rowC, colC = things['c'].position
        rowD, colD = things['d'].position
        rowE, colE = things['e'].position
        global flag
        global steps
        if abs(row-rowA) + abs(col-colA) >= 6 and abs(row-rowB) + abs(col-colB) >= 6 and abs(row-rowC) + abs(col-colC) >= 4 and abs(row-rowD) + abs(col-colD) >= 6 and abs(row-rowE) + abs(col-colE) >= 6:
          flag = random.choice([0, 1])
          if layers['#'][row-1, col]: 
            steps = steps + 1
            self._east(board, the_plot)
          elif layers['#'][row, col+1]:
            steps = steps + 1
            self._east(board, the_plot)    
          elif flag == 0:
              flag = random.choice([0, 1]) #made it that it is more likely for flag = 1       
          if flag == 0:
            steps = steps + 1
            self._north(board, the_plot)
          else:
            steps = steps + 1
            self._east(board, the_plot)
        elif abs(row-1-rowA) + abs(col-colA) >= 5 and abs(row-1-rowB) + abs(col-colB) >= 5 and abs(row-1-rowC) + abs(col-colC) >= 3 and abs(row-1-rowD) + abs(col-colD) >= 5 and abs(row-1-rowE) + abs(col-colE) >= 5:  
          if layers[' '][row-1, col] or layers['*'][row-1, col]: 
            steps = steps + 1
            self._north(board, the_plot)
          elif abs(row-rowA) + abs(col+1-colA) >= 5 and abs(row-rowB) + abs(col+1-colB) >= 5 and abs(row-rowC) + abs(col+1-colC) >= 3 and abs(row-rowD) + abs(col+1-colD) >= 5 and abs(row-rowE) + abs(col+1-colE) >= 5:
            if layers[' '][row, col+1] or layers['*'][row, col+1]: 
              steps = steps + 1
              self._east(board, the_plot)  
        elif abs(row-rowA) + abs(col+1-colA) >= 5 and abs(row-rowB) + abs(col+1-colB) >= 5 and abs(row-rowC) + abs(col+1-colC) >= 3 and abs(row-rowD) + abs(col+1-colD) >= 5 and abs(row-rowE) + abs(col+1-colE) >= 5:
          if layers[' '][row, col+1] and layers['*'][row, col+1]: 
            steps = steps + 1
            self._east(board, the_plot)  
          else: 
            steps = steps + 1
            self._east(board, the_plot)
        elif abs(row-rowA) + abs(col-colA) >= 4 and abs(row-rowB) + abs(col-colB) >= 4 and abs(row-rowC) + abs(col-colC) >= 2 and abs(row-rowD) + abs(col-colD) and abs(row-rowE) + abs(col-colE) >= 4:
          if abs(row-rowA) + abs(col+1-colA) >= 5 and abs(row-rowB) + abs(col+1-colB) >= 5 and abs(row-rowC) + abs(col+1-colC) >= 3 and abs(row-rowD) + abs(col+1-colD) >= 5 and abs(row-rowE) + abs(col+1-colE) >= 5: 
            if layers['#'][row, col+1]: 
              if layers[' '][row-1, col] and layers['*'][row-1, col] and abs(row-1-rowA) + abs(col-colA) >= 5 and abs(row-1-rowB) + abs(col-colB) >= 5 and abs(row-1-rowC) + abs(col-colC) >= 3 and abs(row-1-rowD) + abs(col-colD) >= 5 and abs(row-1-rowE) + abs(col-colE) >= 5:
                steps = steps + 1
                self._north(board, the_plot)
              elif layers[' '][row+1, col] and layers['*'][row+1, col]and abs(row+1-rowA) + abs(col-colA) >= 5 and abs(row+1-rowB) + abs(col-colB) >= 5 and abs(row+1-rowC) + abs(col-colC) >= 3 and abs(row+1-rowD) + abs(col-colD) >= 5 and abs(row+1-rowE) + abs(col-colE) >= 5:  
                steps = steps + 1
                self._south(board, the_plot)
              elif layers[' '][row, col-1] and layers['*'][row, col-1] and abs(row-rowA) + abs(col-1-colA) >= 5 and abs(row-rowB) + abs(col-1-colB) >= 5 and abs(row-rowC) + abs(col-1-colC) >= 3 and abs(row-rowD) + abs(col-1-colD) >= 5 and abs(row-rowE) + abs(col-1-colE) >= 5: 
                steps = steps + 1
                self._west(board, the_pot)  
            else: self._east(board, the_plot)
          elif abs(row-1-rowA) + abs(col-colA) >= 5 and abs(row-1-rowB) + abs(col-colB) >= 5 and abs(row-1-rowC) + abs(col-colC) >= 3 and abs(row-1-rowD) + abs(col-colD) >= 5 and abs(row-1-rowE) + abs(col-colE) >= 5:
            if layers['#'][row-1, col]:
              if layers[' '][row+1, col] and layers['*'][row+1, col] and abs(row+1-rowA) + abs(col-colA) >= 5 and abs(row+1-rowB) + abs(col-colB) >= 5 and abs(row+1-rowC) + abs(col-colC) >= 3 and abs(row+1-rowD) + abs(col-colD) >= 5 and abs(row+1-rowE) + abs(col-colE) >= 5:
                steps = steps + 1
                self._south(board, the_plot)
              elif layers[' '][row, col-1] and layers['*'][row, col-1] and abs(row-rowA) + abs(col-1-colA) >= 5 and abs(row-rowB) + abs(col-1-colB) >= 5 and abs(row-rowC) + abs(col-1-colC) >= 3 and abs(row-rowD) + abs(col-1-colD) >= 5 and abs(row-rowE) + abs(col-1-colE) >= 5: 
                steps = steps + 1
                self._west(board, the_plot)                 
            else: 
              steps = steps + 1
              self._north(board, the_plot)
          elif abs(row+1-rowA) + abs(col-colA) >= 5 and abs(row+1-rowB) + abs(col-colB) >= 5 and abs(row+1-rowC) + abs(col-colC) >= 3 and abs(row+1-rowD) + abs(col-colD) >= 5 and abs(row+1-rowE) + abs(col-colE) >= 5:
            if layers['#'][row+1, col]: 
              if layers[' '][row, col-1] and layers['*'][row, col-1] and abs(row-rowA) + abs(col-1-colA) >= 5 and abs(row-rowB) + abs(col-1-colB) >= 5 and abs(row-rowC) + abs(col-1-colC) >= 3 and abs(row-rowD) + abs(col-1-colD) >= 5 and abs(row-rowE) + abs(col-1-colE) >= 5: 
                steps = steps + 1
                self._west(board, the_plot)     
            else: 
              steps = steps + 1
              self._south(board, the_plot)
          elif abs(row-rowA) + abs(col-1-colA) >= 5 and abs(row-rowB) + abs(col-1-colB) >= 5 and abs(row-rowC) + abs(col-1-colC) >= 3 and abs(row-rowD) + abs(col-1-colD) >= 5 and abs(row-rowE) + abs(col-1-colE) >= 5: 
            if layers['#'][row, col-1]: 
              #steps = steps + 1
              self._stay(board, the_plot)
            else: 
              steps = steps + 1
              self._west(board, the_plot)  
     
      elif level == 0:
        row, col = self.position
        rowA, colA = things['a'].position
        if abs(row-rowA) + abs(col-colA) >= 6:
          flag = random.choice([0, 1])
          if flag == 0 and layers[' '][row, col+1] or layers['*'][row, col+1]: 
              steps = steps + 1
              self._east(board, the_plot)
          else: 
            steps = steps + 1
            self._north(board, the_plot)
        elif abs(row-1-rowA) + abs(col-colA) >= 5:
          if layers[' '][row-1, col]: 
            steps = steps + 1
            self._north(board, the_plot)
          elif abs(row-rowA) + abs(col+1-colA) >= 5 and layers[' '][row, col+1]: 
            steps = steps + 1
            self._east(board, the_plot)
        elif abs(row-rowA) + abs(col+1-colA) >= 5:
          if layers[' '][row, col+1]: 
            steps = steps + 1
            self._east(board, the_plot)
        elif abs(row-rowA) + abs(col-colA) >= 4:
          if abs(row-1-rowA) + abs(col-colA) >= 5 and layers[' '][row-1, col]: 
            steps = steps + 1
            self._north(board, the_plot)
          elif abs(row-rowA) + abs(col+1-colA) >= 5 and layers[' '][row, col+1]: 
            steps = steps + 1
            self._east(board, the_plot)
          elif abs(row-rowA) + abs(col-1-colA) >= 5 and layers[' '][row, col-1]:
            steps = steps + 1
            self._west(board, the_plot)
          elif abs(row+1-rowA) + abs(col-colA) >= 5 and layers[' '][row+1, col]:
            steps = steps + 1
            self._south(board, the_plot)
          else: 
            #steps = steps + 1
            self._stay(board, the_plot)      
     #   if abs(row-rowA) + abs(col-colA) >= 6 and abs(row-rowB) + abs(col-colB) >= 6 and abs(row-rowD) + abs(col-colD) >= 6 and abs(row-rowD) + abs(col-colD) and abs(row-rowE) + abs(col-colE):

                           
    if actions == 0:    # go upward
      steps = steps + 1
      self._north(board, the_plot)
    elif actions == 1:  # go downward
      steps = steps + 1
      self._south(board, the_plot)
    elif actions == 2:  # go leftward
      steps = steps + 1
      self._west(board, the_plot)
    elif actions == 3:  # go rightward
      steps = steps + 1
      self._east(board, the_plot)
    elif actions == 4:  # stay put
      steps = steps + 1
      self._stay(board, the_plot)
    elif actions == 5:    # just quit
      the_plot.terminate_episode()
    else:
      steps = steps + 1
      self._stay(board, the_plot)


class PedSprite(prefab_sprites.MazeWalker):
 
  def __init__(self, corner, position, character):
    """Constructor: list impassables, initialise direction."""
    super(PedSprite, self).__init__(
        corner, position, character, impassable='#')
    # Choose our initial direction based on our character value.
    # self._initialState = ord(character)%2
    self._initialState = 0

  def update(self, actions, board, layers, backdrop, things, the_plot):
    global north
    global east
    global west
    global south

    if pedestrian_move_case == 0:
      self._stay(board, the_plot)      
      if self.position == things['P'].position:
        original_stdout = sys.stdout
        with open('out.txt', 'a+') as f:
          sys.stdout = f 
          print("Success!", int(steps/2))
          sys.stdout = original_stdout 
        print("Success!") 
        the_plot.terminate_episode()

    if pedestrian_move_case == 2:
      if self.character != '*':
        row, col = self.position
        rowP, colP = things['P'].position   
        if abs(row-rowP) + abs(col-colP) <= 3 and (row != 0 and col != 0): 
          the_plot.terminate_episode()
          original_stdout = sys.stdout
          with open('out.txt', 'a+') as f:
            sys.stdout = f 
            print("FAILURE!")
            sys.stdout = original_stdout
          print("FAILURE!")  
        elif self.position == things['P'].position:
          the_plot.terminate_episode()
        global flag   
        flag = random.choice([0, 1])
        if layers['#'][row-1, col]: 
          if layers[' '][row, col-1]:
            self._west(board, the_plot)
        elif flag == 0:
          flag = random.choice([0, 1]) #made it that it is more likely for flag = 1       
        if flag == 0:
          if layers[' '][row+1, col]:
            self._south(board, the_plot)
        else:
          if layers[' '][row, col-1]:
            self._west(board, the_plot)
      if self.position == things['P'].position:
          original_stdout = sys.stdout
          with open('out.txt', 'a+') as f:
            sys.stdout = f 
            print("Success!", int(steps/2))
            sys.stdout = original_stdout 
          print('Success!')
          the_plot.terminate_episode()                     

    if pedestrian_move_case == 1:
      if self.character != '*':

       # if the_plot.frame % 2:
       #   self._stay(board, the_plot) 
       #   return

          # If there is a wall next to us, we ought to switch direction.
        row, col = self.position
        # C wears a mask so social distancing can be decreaased
        rowC, colC = things['c'].position
        rowP, colP = things['P'].position
        if row != rowC or col != colC:
          flg = 0
          if abs(row-rowP) + abs(col-colP) <= 3 and (row != 0 and col != 0):     
            the_plot.terminate_episode()
            original_stdout = sys.stdout
            with open('out.txt', 'a+') as f:
              sys.stdout = f 
              print("FAILURE!")
              sys.stdout = original_stdout
            print("FAILURE!")
        else:
          if abs(row-rowP) + abs(col-colP) <= 1 and (row != 0 and col != 0): 
            the_plot.terminate_episode()
            original_stdout = sys.stdout
            with open('out.txt', 'a+') as f:
              sys.stdout = f 
              print("FAILURE!")
              sys.stdout = original_stdout
            print("FAILURE!")

        # if layers['#'][row, col-1]: self._initialState = True
        # if layers['#'][row, col+1]: self._initialState = False


        if layers['*'][row-1, col] or layers['*'][row+1, col] or layers['*'][row, col-1] or layers['*'][row, col+1]:
          if(layers[' '][row+1, col]):
            self._south(board, the_plot)

        if not layers['#'][row-1, col] and not layers['#'][row+1, col] and not layers['#'][row, col-1] and not layers['#'][row, col+1]:
          randnum = random.choice([1, 2, 3, 4, 5])
          if(randnum == 1):
            if(layers[' '][row, col-1]):
              self._west(board, the_plot)
          elif(randnum == 2):
            if(layers[' '][row, col+1]):
              self._east(board, the_plot)
          elif(randnum == 3):
            if(layers[' '][row-1, col]):
              self._north(board, the_plot)
          elif(randnum == 4):
            if(layers[' '][row+1, col]):
              self._south(board, the_plot)
          else:
            self._stay(board, the_plot)  

        else:
          if layers['#'][row-1, col] and layers['#'][row, col+1]:
            # print("hi")
            # self._south(board, the_plot)
            if not layers['#'][row+1, col+1]:
              if layers[' '][row+1, col]:
                self._south(board, the_plot)
            elif not layers['#'][row-1, col-1]:
              if layers[' '][row, col-1]:
                self._west(board, the_plot)
            else:
              randnum = random.choice([1, 2])
              if(randnum == 1):
                if layers[' '][row+1, col]:
                  self._south(board, the_plot)
              else:
                if layers[' '][row, col-1]:
                  self._west(board, the_plot)

          elif layers['#'][row+1, col] and layers['#'][row, col+1]:
            # self._west(board, the_plot)
            if not layers['#'][row+1, col-1]:
              if layers[' '][row, col-1]:
                self._west(board, the_plot)
            elif not layers['#'][row-1, col+1]:
              if layers[' '][row-1, col]:
                self._north(board, the_plot)
            else:
              randnum = random.choice([1, 2])
              if(randnum == 1):
                if layers[' '][row, col-1]:
                  self._west(board, the_plot)
              else:
                if layers[' '][row-1, col]:
                  self._north(board, the_plot)

          elif layers['#'][row+1, col] and layers['#'][row, col-1]:
            # self._north(board, the_plot)
            if not layers['#'][row-1, col-1]:
              if layers[' '][row-1, col]:
                self._north(board, the_plot)
            elif not layers['#'][row+1, col+1]:
              if layers[' '][row, col+1]:
                self._east(board, the_plot)
            else:
              randnum = random.choice([1, 2])
              if(randnum == 1):
                if layers[' '][row-1, col]:
                  self._north(board, the_plot)
              else:
                if layers[' '][row, col+1]:
                  self._east(board, the_plot)

          elif layers['#'][row-1, col] and layers['#'][row, col-1]:
            # self._east(board, the_plot)
            if not layers['#'][row-1, col+1]:
              if layers[' '][row, col+1]:
                self._east(board, the_plot)
            elif not layers['#'][row+1, col-1]:
              if layers[' '][row+1, col]:
                self._south(board, the_plot)
            else:
              randnum = random.choice([1, 2])
              if(randnum == 1):
                if layers[' '][row, col+1]:
                  self._east(board, the_plot)
              else:
                if layers[' '][row+1, col]:
                  self._south(board, the_plot)

          elif (north == 0 and layers['#'][row, col-1]) and (not layers['#'][row-1, col] or not layers['*'][row-1, col]):
            if layers[' '][row, col+1]:
              self._east(board, the_plot)
            # print("first")
            # north = 20
            # self._initialState = 1
          elif (east == 0 and layers['#'][row-1, col]) and (not layers['#'][row, col+1] or not layers['*'][row, col+1]):
            if layers[' '][row+1, col]:
              self._south(board, the_plot)
            # print("second")
            # east = 20
          elif (south == 0 and layers['#'][row, col+1]) and (not layers['#'][row+1, col] or not layers['*'][row+1, col]):
            if layers[' '][row, col-1]:
              self._west(board, the_plot)
            # print("third")
            # south = 20
          elif (layers['#'][row+1, col]) and (not layers['#'][row, col-1] or not layers['*'][row, col-1]):
            # if west != 0:
            #   randnum = random.choice([1, 2, 3, 4, 5])
            #   if(randnum == 1):
            #     self._west(board, the_plot)
            #   elif(randnum == 2):
            #     self._east(board, the_plot)
            #   elif(randnum == 3):
            #     self._north(board, the_plot)
            #   elif(randnum == 4):
            #     self._south(board, the_plot)
            #   else:
            #     self._stay(board, the_plot)
            # else:
            if layers[' '][row-1, col]:
              self._north(board, the_plot)
            # print("fourth")
            # west = 10
          # else:
          #   self._stay(board, the_plot)

          # print(north)
          if north > 0:
            north -= 1
          if east > 0:
            east -= 1
          if south > 0:
            south -= 1
          if west > 0:
            west -= 1


        # randnum = random.choice([1, 2, 3, 4, 5])
        # if(randnum == 1):
        #   self._west(board, the_plot)
        # elif(randnum == 2):
        #   self._east(board, the_plot)
        # elif(randnum == 3):
        #   self._north(board, the_plot)
        # elif(randnum == 4):
        #   self._south(board, the_plot)
        # else:
        #   self._stay(board, the_plot)       
      #  (self._east if self._initialState else self._west)(board, the_plot)
      #  if self.position == things['P'].position: the_plot.terminate_episode()
      else:
        if self.position == things['P'].position: 
          original_stdout = sys.stdout
          with open('out.txt', 'a+') as f:
            sys.stdout = f 
            print("Success!", int(steps/2))
            sys.stdout = original_stdout
          print('Success!')
          the_plot.terminate_episode()

def main(argv=()):
  global level
  global pedestrian_move_case
  global algorithm_case
  global testres
  level = int(argv[1]) if len(argv) > 1 else 0

  #PEDESTRIAN_MOVE_CASE:
  #0 = NOT MOVING
  #1 = MOVING RANDOMLY
  #2 = MOVING TO THE DIRECTION OF PLAYER'S STARTING POSITION
  pedestrian_move_case = int(argv[2]) if len(argv) > 2 else 1

  #Lists of algorithms implemented:
  #0 = Manually play with arrow keys!
  #1 = Use algorithm!
  algorithm_case = int(argv[3]) if len(argv) > 1 else 1

  # Build the game.
  game = make_game(level)
  croppers = make_croppers(level)
  ui = human_ui.CursesUi(
      keys_to_actions={curses.KEY_UP: 0, curses.KEY_DOWN: 1, curses.KEY_LEFT: 2, curses.KEY_RIGHT: 3, -1: 4,'q': 5, 'Q': 5},
      delay=100, colour_fg=COLOUR_FG,
      croppers=croppers)
  ui.play(game)

if __name__ == '__main__':
  main(sys.argv)
