#!/usr/bin/env python
# coding: utf-8

# In[5]:


import unittest
import Conway 
import pygame as pg
import numpy as np
import random


# In[7]:


class Test(unittest.TestCase):
    
    
    #CELL ========================================================================================
    def test_cell_creation(self):
        c = Conway.Cell()
        self.assertIsInstance(c, Conway.Cell)
        self.assertEqual(c.state, False)
        

    #SETTINGS ========================================================================================
    def test_settings_display(self):
            s = Conway.Settings(800, 600, 10, 13, 60, 0.2)

            #Screen is actively renderable and may be visible to user
            self.assertEqual(pg.display.get_active(), True)
            
            #Screen Dimensions
            self.assertEqual(s.SCREEN.get_size(), (800,600))
            
            #Screen Dimensions scaling up from bytes
            length = s.SCREEN.get_bytesize() * s.SCREEN.get_width() * s.SCREEN.get_height()
            b0 = s.SCREEN.get_view("0")
            self.assertEqual(b0.length, length)
            
            
    
    def test_settings_blit(self):
            s = Conway.Settings(800, 600, 10, 13, 60, 0.2)
            
            def draw_menu():   
                s.menu_surf.fill((0,0,0))
                s.write_to_menu_surf()
                s.menu_surf.set_colorkey((0,0,0))
                s.SCREEN.blit(s.menu_surf, (0,0))
                
            
            #test pixel colouring with coloured rects 
            pg.draw.rect(s.SCREEN, (200,200,200), (0,0,30,30))
            self.assertEqual(s.SCREEN.get_at((0,0)), (200,200,200))
            
            #test font rendering functions and menu  
            #via pixel colouring of menu text rendering on the layered menu surface  
            draw_menu()
            self.assertEqual(s.SCREEN.get_at((12,140)), (159,159,159))
            
            
            #test colour_dict and correctness of colour rendering on screen by rectangle drawing
            rgb_iter=0
            for k,v in s.colour_dict['funky'].items():
                pg.draw.rect(s.SCREEN, v,(0,0,30,30))
                self.assertEqual(s.SCREEN.get_at((0,0)), v)
                
                #test creation of rainbow list
                self.assertEqual(k,s.rainbow_list[rgb_iter])
                rgb_iter+=1
            
            
            for v in s.colour_dict['standard'].values():
                pg.draw.rect(s.SCREEN, v,(0,0,30,30))
                self.assertEqual(s.SCREEN.get_at((0,0)), v)

            
            
            
    #GRID ========================================================================================
    def test_grid_creation(self):
            g = Conway.Grid()
            s = Conway.Settings(800, 600, 10, 13, 60, 0.2)

            
            row_test = s.HEIGHT//s.scale #60
            col_test = s.WIDTH//s.scale #80
            
            #array creation func test 
            arr = g.create_empty_2d_array(row_test, col_test)
            self.assertTrue(np.array_equal(arr, np.full(shape=(row_test, col_test),fill_value=None)))
            
            
    
    def test_grid_array_filling_with_cells(self):
            g = Conway.Grid()
            s = Conway.Settings(800, 600, 10, 13, 60, 0.2)
                        
            row_test = s.HEIGHT//s.scale #60
            col_test = s.WIDTH//s.scale #80
            arr = g.create_empty_2d_array(row_test, col_test)

            
            #test filling of array with Cell objects
            #by testing random column position in each row of array for existence of Cell 
            g.fill_array_with_cells(arr, row_test, col_test)
            for i in range(row_test):
                self.assertTrue(arr[i][random.randint(0,col_test-1)], Conway.Cell())
            
            
            #test screen colour fill func by turning random cell True
            #and checking colour rendering on Screen in that position
            rand_row = random.randint(0,row_test)
            rand_col = random.randint(0,col_test) 
            arr[rand_row][rand_col].state = True

            g.screen_colour_fill(s.SCREEN, arr, s.colour_dict, row_test, col_test, s.scale, False, 0, False)

            self.assertEqual(s.SCREEN.get_at((rand_col*s.scale, rand_row*s.scale)), (255,255,255))

            
            
            
    #CONWAY LOGIC ========================================================================================
    def test_conway_get_neighbours(self):
            g = Conway.Grid()
            s = Conway.Settings(800, 600, 10, 13, 60, 0.2)
            conwaylogic = Conway.ConwayLogic()
            
            row_test = s.HEIGHT//s.scale #60
            col_test = s.WIDTH//s.scale #80
            arr = g.create_empty_2d_array(row_test, col_test)
            g.fill_array_with_cells(arr, row_test, col_test)
            
            #testing last cell in board in bottom right position for max wrap around testing
            #catch any positional errors prior which will ultimately affect last cell 
            r = 0
            c = col_test-1
            
            #loop around cell and activate neighbour, from 0 to 8 neighbours in all directions
            neighbour_count = 0
            for n in range(-1,2):
                for m in range(-1,2):
                    
                    row_wrap = (r + n + row_test) % (row_test)
                    col_wrap = (c + m + col_test)  % (col_test)

                    if (row_wrap, col_wrap) == (r,c):
                        continue
                        
                    arr[row_wrap][col_wrap].state = True 
                    neighbour_count += 1
                    
                    self.assertEqual((conwaylogic.get_neighbours(r, c, row_test, col_test, arr)), neighbour_count)

                    
    def test_conway_get_dead_cell_next_state(self):
            g = Conway.Grid()
            s = Conway.Settings(800, 600, 10, 13, 60, 0.2)
            conwaylogic = Conway.ConwayLogic()
            
            row_test = s.HEIGHT//s.scale #60
            col_test = s.WIDTH//s.scale #80
            
            arr = g.create_empty_2d_array(row_test, col_test)
            g.fill_array_with_cells(arr, row_test, col_test)
            
            r = 0
            c = col_test-1
            target_cell = arr[r][c]
            
        
            
            #DEAD CELL RULE TEST
            neighbour_count = 0
            
            for n in range(-1,2):
                
                for m in range(-1,2):
                
                    target_cell.state=False
                
                    row_wrap = (r + n + row_test)  % (row_test)
                    col_wrap = (c + m + col_test)  % (col_test)
                    

                    if (row_wrap, col_wrap) == (r,c):
                        continue
                                       
                    #RULE 1 TEST: ANY DEAD CELL WITH 2<N<3 REMAINS DEAD
                    if neighbour_count < 2 or neighbour_count > 3:
                        self.assertEqual(conwaylogic.get_cell_next_state(r,c, row_test,col_test, s.scale, arr),False)
                    
                    #RULE 2 TEST: ANY DEAD CELL WITH N == 3 LIVES
                    if neighbour_count == 3:
                        self.assertEqual(conwaylogic.get_cell_next_state(r,c, row_test,col_test, s.scale, arr),True)
                    
                    
                    arr[row_wrap][col_wrap].state = True 
                    neighbour_count += 1
                    


                

    def test_conway_get_live_cell_next_state(self):
            g = Conway.Grid()
            s = Conway.Settings(800, 600, 10, 13, 60, 0.2)
            conwaylogic = Conway.ConwayLogic()
        
            row_test = s.HEIGHT//s.scale #60
            col_test = s.WIDTH//s.scale #80
            
            arr = g.create_empty_2d_array(row_test, col_test)
            g.fill_array_with_cells(arr, row_test, col_test)
            
            r = 0
            c = col_test-1
            target_cell = arr[r][c]
            
            
            neighbour_count = 0
            
            for n in range(-1,2):
                
                for m in range(-1,2):
                
                    target_cell.state=True
                
                    row_wrap = (r + n + row_test)  % (row_test)
                    col_wrap = (c + m + col_test)  % (col_test)
                    

                    if (row_wrap, col_wrap) == (r,c):
                        continue
                                       
                    #RULE 1 TEST: ANY LIVE CELL WITH N==2 OR N==3 REMAINS LIVE
                    if neighbour_count == 2 or neighbour_count == 3:
                        self.assertEqual(conwaylogic.get_cell_next_state(r,c, row_test,col_test, s.scale, arr),True)
                    
                    #RULE 2 TEST: ANY DEAD CELL WITH N == 3 LIVES
                    if neighbour_count<2 or neighbour_count>3:
                        self.assertEqual(conwaylogic.get_cell_next_state(r,c, row_test,col_test, s.scale, arr),False)
                    
                    
                    arr[row_wrap][col_wrap].state = True 
                    neighbour_count += 1

                    
    def test_conway_board_next_gen(self):
            g = Conway.Grid()
            s = Conway.Settings(800, 600, 10, 13, 60, 0.2)
            conwaylogic = Conway.ConwayLogic()
        
            row_test = s.HEIGHT//s.scale #60
            col_test = s.WIDTH//s.scale #80
            
            arr1 = g.create_empty_2d_array(row_test, col_test)
            g.fill_array_with_cells(arr1, row_test, col_test)
            
            arr2 = g.create_empty_2d_array(row_test, col_test)
            g.fill_array_with_cells(arr2, row_test, col_test)
            
            arr3 = g.create_empty_2d_array(row_test, col_test)
            g.fill_array_with_cells(arr3, row_test, col_test)
            
            r = 0
            c = col_test-1
            
            #For each row in first board array randomly change approx half the cells state to true
            for i in range(row_test):
                for j in range(col_test//2):
                    arr1[i][random.randint(0,c)].state=True

                
            #update arr3 with correct logic on how cells should update   
            for r in range(row_test):
                
                    for c in range(col_test):
                
                        arr3[r][c].state = conwaylogic.get_cell_next_state(r, c, row_test, col_test, s.scale, arr1)
            
            #use func from Conway script to update arr2
            arr2 = conwaylogic.get_board_next_gen(row_test, col_test, s.scale, arr1, arr2)[0]
            
            
            #test if each Cell for correct test logic implementation and func in Conway script are equal
            for r in range(row_test):
                
                    for c in range(col_test):
                                            
                            self.assertEqual(arr2[r][c].state, arr3[r][c].state)
                



if __name__== '__main__':
    unittest.main()
    
    


    
    


# In[ ]:




