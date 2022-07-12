#!/usr/bin/env python
# coding: utf-8



#Module Imports
import pygame as pg
import numpy as np
import time
import sys
import random


class Settings():
        
    def __init__(self, width, height, scale, font_size, fps, prob):
    
        #Window Display
        self.WIDTH, self.HEIGHT = width, height
        self.scale = scale
        self.rows = self.HEIGHT//self.scale
        self.cols = self.WIDTH//self.scale
        self.SCREEN = pg.display.set_mode((self.WIDTH,self.HEIGHT))
        pg.display.set_caption("Conway's Game of Life")

        
        #Colours
        self.colour_dict = {
        'standard':{
        'BLACK': (0,0,0), 
        'GREY' : (60,60,60),
        'WHITE' : (255,255,255),
                },
        'funky':{
        'RED': (255,0,0),
        'LIGHT ORANGE': (255, 195,0),
        'ORANGE': (255,125,0),
        'YELLOW': (255,255,0),
        'GREEN': (125,255,0),
        'GREEN DARK': (0,200,0),
        'TURQUOISE': (0,155,160),
        'CYAN': (0,255,255),
        'OCEAN': (0,125,255),
        'BLUE': (0,100,255),
        'DEEP BLUE': (0,0,255),
        'VIOLET': (125,0,255),
        'PURPLE': (155, 0 , 255),
        'MAGENTA': (255,0,255),
        'RASPBERRY': (255,0,125)
        }}
        
        self.rainbow_list = list(self.colour_dict['funky'].keys())

        
        
        #Fonts & Menu
        pg.font.init()
        self.font_size = font_size
        self.font = pg.font.SysFont('Arial', self.font_size)
        self.menu_surf = pg.Surface((self.WIDTH, self.HEIGHT))
        
    

        #Runtime
        self.FPS = fps
        self.clock = pg.time.Clock()
        self.prob = prob
        

    def blit_to_screen(self, window, pos_x, pos_y, text, colour=(211,211,211)):
        window.blit(self.font.render(text, True, colour),(pos_x, pos_x*pos_y))
                              

    def write_to_menu_surf(self):
        self.blit_to_screen(self.menu_surf, self.scale, 2,  '      Menu')
        self.blit_to_screen(self.menu_surf, self.scale, 5,  'm:             Show/Hide Menu')
        self.blit_to_screen(self.menu_surf, self.scale, 7,  'left click:    Draw Cells')
        self.blit_to_screen(self.menu_surf, self.scale, 9,  'right click:  Erase Cells')
        self.blit_to_screen(self.menu_surf, self.scale, 11, 'space:       Run/Pause')
        self.blit_to_screen(self.menu_surf, self.scale, 13, 'x:               Reset')
        self.blit_to_screen(self.menu_surf, self.scale, 15, 'r:               Randomise')
        self.blit_to_screen(self.menu_surf, self.scale, 17, 'f:                Funky Time')      
                              




class Cell():
    
    def __init__(self, state=False):
        #True = Alive, False = Dead 
        self.state = state      



class Grid():
    
    def create_empty_2d_array(self, rows, cols):
        return np.full(shape=(rows, cols),fill_value=None)

    
    def screen_colour_fill(self, screen, board, colours, rows, cols, scale, funky, rgb_loop, pause):
        
        for r in range(rows):

            for c in range(cols):

                if board[r][c].state == True:
                    if not funky:
                        #In pygame positions pass as an (X,Y) coordinate, so flip position in draw.rect 
                        pg.draw.rect(screen, colours['standard']['WHITE'], (c*scale, r*scale, scale-1,scale-1))
                    else:
                        pg.draw.rect(screen, colours['funky'][rgb_loop], (c*scale, r*scale, scale-1,scale-1))
                    
                else:
                    
                    pg.draw.rect(screen, colours['standard']['BLACK'], (c*scale, r*scale, scale-1, scale-1))
                    
                    
    def fill_array_with_cells(self, board, rows, cols, rand=None, prob=None):

            for r in range(rows):

                for c in range(cols):

                    board[r][c] = Cell()

                    if rand: 
                        if random.random() < prob:
                            board[r][c].state = True
                            
            return board
                



class ConwayLogic():
    
    def get_neighbours(self, r, c, rows, cols, board):
    
            total = 0

            for n in range(-1,2):
                for m in range(-1,2):

                    row_wrap = (r + n + rows) % (rows)
                    col_wrap = (c + m + cols)  % (cols)

                    if board[row_wrap][col_wrap].state == True:
                        total+=1

            if board[r][c].state ==True:
                total -=1

            return total
    

    def get_cell_next_state(self, r, c, rows, cols, scale, board):
        
        neighbour_total = self.get_neighbours(r, c, rows, cols, board)

        if board[r][c].state == True:
            
            #RULE: ANY LIVE CELL WITH N < 2 OR N > 3 DIES
            if neighbour_total>3 or neighbour_total < 2:
                return False
            
            #RULE: ANY LIVE CELL WITH N ==2 OR N ==3 LIVES
            if neighbour_total == 2 or neighbour_total == 3:
                return True


        #RULE: ANY DEAD CELL WITH N == 3 LIVES
        if board[r][c].state == False:
            if neighbour_total == 3:
                return True
            #ELSE DEAD REMAIN DEAD
            else:
                return False
        
                                    
        
        
    def get_board_next_gen(self, rows, cols, scale, board1, board2):

                for r in range(rows):

                    for c in range(cols):

                        board2[r][c].state = self.get_cell_next_state(r, c, rows, cols, scale, board1)

                board1, board2 = board2, board1

                return board1, board2    
                


#use all helper classes to execute game logic
class RunGame():
    
    def __init__(self, settings, grid, conway):
        
        self.settings = settings
        self.grid     = grid
        self.conway   = conway
    

    
    def set_board(self, rand=None, prob=None):
    
        board = self.grid.create_empty_2d_array(self.settings.rows, self.settings.cols)

        self.grid.fill_array_with_cells(board, self.settings.rows, self.settings.cols, rand, prob)
                    
        return board
        
    
    
    def mouse_handler(self, board):
        #pos = row, col
        pos = pg.mouse.get_pos()
        
        #FLIP X/Y of pos
        #now pos=(col,row)
        pos = (pos[1]//self.settings.scale, pos[0]//self.settings.scale)

        cell = board[pos[0]][pos[1]]

        #DRAW
        if pg.mouse.get_pressed()[0]:
            if cell.state == False:
                board[pos[0]][pos[1]].state = True
        #ERASE
        if pg.mouse.get_pressed()[2]:
            if cell.state == True:
                board[pos[0]][pos[1]].state =False
        
    
    
    def rgb_iter(self, rgb_loop, pause):   
        #adjust for time delay in processing when game is not paused 
        if pause:
            rgb_loop+=0.1

        else:
            rgb_loop+=1    
        
        if rgb_loop>len(self.settings.rainbow_list)-1:
            rgb_loop = 0
            
        return rgb_loop
        
        
        
    def draw_menu_surf_to_screen(self):
        self.settings.menu_surf.fill((0,0,0))
        self.settings.write_to_menu_surf()
        self.settings.menu_surf.set_colorkey((0,0,0))
        self.settings.SCREEN.blit(self.settings.menu_surf, (0,0))
                
                
        
    def run(self):
            
        #board_1 for display, board2_ for next gen swapping
        board_1 = self.set_board()
        board_2 = self.set_board()
        
        #Event loop variables
        pause = True
        show_menu = True
        funky = False
        rgb_loop = 0

        
        while True:
            
            for event in pg.event.get():

                    #QUIT ===================================================================================
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()


                    #MOUSE DRAW =============================================================================
                    if pg.mouse.get_pressed():
                        self.mouse_handler(board_1)


                    #PLAY/PAUSE =============================================================================
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_SPACE:
                            pause = not pause


                    #MENU ===================================================================================
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_m:
                            show_menu = not show_menu
                            
                    #RESET===================================================================================
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_x:
                            board_1 = self.set_board()
                            
                    #RANDOMISE BOARD ========================================================================
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_r:
                            board_1 = self.set_board(rand=True, prob=self.settings.prob)
                            
                    
                    #FUNKY TIME==============================================================================
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_f:
                            funky = not funky
                            

            #GET BOARD NEXT GENERATION / PLAY GAME ==========================================================
            if not pause:

                board_1, board_2 = self.conway.get_board_next_gen(self.settings.rows, self.settings.cols, self.settings.scale, board_1, board_2)
        
                
            #SCREEN UPDATES =================================================================================
            self.settings.SCREEN.fill((0,0,0))
            
            if funky:
            
                rgb_loop = self.rgb_iter(rgb_loop, pause)            

            self.grid.screen_colour_fill(self.settings.SCREEN, board_1, self.settings.colour_dict, self.settings.rows, self.settings.cols, self.settings.scale, funky, self.settings.rainbow_list[int(rgb_loop)],pause)                
            
            if show_menu:

                self.draw_menu_surf_to_screen()
            

                
                    
                
            #PUSH UPDATES TO MAIN DISPLAY =================================================================
            pg.display.update()

                



class Main():
    
    def main():
        
        s = Settings(800, 600, 10, 13, 60, 0.2)
        g = Grid()
        c = ConwayLogic()
        
        r = RunGame(s, g, c)
        r.run()
    

    if __name__ == '__main__':
        main()