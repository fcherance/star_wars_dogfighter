# -*- coding: utf-8 -*-
"""
Created on Sat May 19 22:36:56 2018

@author: bettmensch
"""

'''This file contains the sprite classes used in the game STAR WARS DOGFIGHTER.
It contains the \'MaskedSprite\' class which functions as a functional base class
for the more refined custom classes \'PlayerSprite\', \'EnemySprite\' and \'LaserSprite\'.'''

from pygame.sprite import Sprite, Group
from math import cos, sin, pi

import pygame as pg
import numpy as np

class MaskedSprite(Sprite):
    
    def __init__(self,screen,image_path,laser_beams_group,*groups,**initial_values):
        '''image: path to sprite image
        *groups: optional (unnamed) list of groups the sprite will be added to
                          when created
        **initial_values: Options are angle, speed, left and top. Allows specific
                            placement/orientation/status at creation'''
                            
        # initialize and add to groups if sensible
        Sprite.__init__(self,*groups)
        
        # attach screen
        self.screen = screen
        
        # attach laser beam 'basket' group
        self.laser_beams = laser_beams_group

        # get and attach image as pygame surface; initialize rotated image storage
        self._original_image = pg.image.load(image_path)
        self.image = pg.image.load(image_path)
        
        # get and attach positional rectangle
        self.rect = self.image.get_rect()
        
        # get and attach mask
        self.mask = pg.mask.from_surface(self.image)
        
        # set default initial values where necessary
        self._speed = 0 # needed to keep track of speed
        self._angle = 0 # needed to kepp track of angle
        self._center = np.array([0,0]).astype('float') # needed to recenter image after rotation
        
        # work through initial values if sensible
        if 'angle' in initial_values.keys():
            self.rotate_ip(initial_values['angle'])
        if 'speed' in initial_values.keys():
            self._speed = initial_values['speed']
        if 'center' in initial_values.keys():
            self._center = np.array(initial_values['center']).astype('float')
            self.rect.center = self._center
        
    def rotate_ip(self,d_angle):
        '''Rotates the sprite in place based on differential angle d_angle. Updates
        the image, rect and angle attribute accordingly.'''
        
        if d_angle == 0:
            # do nothing
            pass
        else:
            # get new angle
            angle = self._angle + d_angle
            
            # rotate sprite image by angle
            self.image = pg.transform.rotate(self._original_image,
                                             angle)
            
            # update the positional rect
            self.rect = self.image.get_rect()
            self.rect.center = self._center
            
            # update mask
            self.mask = pg.mask.from_surface(self.image)
            
            # update angle attribute
            self._angle = angle
            
    def move_ip(self,d_speed):
        '''Moves the sprite in place. Takes a differential speed d_speed and calculates
        new speed if necessary. Then calculates the unit direction vector based
        on current angle nad moves the sprite accordingly.'''
        
        # get new speed (might be old speed if d_speed = 0)
        speed = self._speed + d_speed
        
        # convert self._angle attribute to radian for cos & sin functions
        angle_degrees = self._angle * pi / 180
            
        # get velocity vector
        velocity = np.array([cos(angle_degrees),-sin(angle_degrees)]) * speed
        
        # move sprite by moving sprite's _center attribute and updating rect
        # (necessary bc floats smaller than 1 get rounded)
        self._center += velocity
        self.rect.center = self._center

        # wrap around screen edges if necessary  
        screen_width  = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        if self.rect.left > screen_width:
            self._center[0] = -self.rect.width / 2 # equivalent of setting rect.right = 0, analogous for the other cases
        elif self.rect.right  < 0:
            self._center[0] = screen_width + self.rect.width / 2
        if self.rect.bottom < 0:
            self._center[1] = screen_height + self.rect.height / 2
        elif self.rect.top > screen_height:
            self._center[1] = 0 - self.rect.height / 2
        
        # update speed attribute
        self._speed = speed
                
class PlayerSprite(MaskedSprite):
        
    d_angle = 1 # rotation rate for this sprite type (in degrees)
    d_speed = 0.5 # acceleration rate for this sprite type
    max_speed = 20 # max speed for this sprite type
    laser_speed = 15 # speed of fired laser beams relative to sprite
    laser_lifetime = 50 # number of frames a laser beam lasts before 'dissolving'
    weapon_cool_down = 50 # number of frames between shots
    
    def __init__(self,screen,image_path,laser_beams_group,*groups,**initial_values):
        '''Repeat original init to add some attributes'''
        
        MaskedSprite.__init__(self,screen,image_path,laser_beams_group,*groups,**initial_values)
        
        self.weapon_cooling = 0
        
    def get_player_controls(self):
        '''Gets player control input and converts into angle and speed
        differentials d_angle and d_speed, as well as fire command.'''
            
        # get all keys currently down
        pressed_keys = pg.key.get_pressed()
            
        # get angle differential
        if pressed_keys[pg.K_LEFT] and not pressed_keys[pg.K_RIGHT]:
            d_angle = self.__class__.d_angle
        elif pressed_keys[pg.K_RIGHT] and not pressed_keys[pg.K_LEFT]:
            d_angle = -self.__class__.d_angle
        else:
            d_angle = 0
            
        # get speed differential
        if pressed_keys[pg.K_UP] and not pressed_keys[pg.K_DOWN]:
            # dont accelerate above sprite's max speed
            d_speed = min(self.__class__.d_speed,self.__class__.max_speed - self._speed)
        elif pressed_keys[pg.K_DOWN] and not pressed_keys[pg.K_UP]:
            # dont decelarate to going backwards
            d_speed = -min(self.__class__.d_speed,self._speed)
        else:
            d_speed = 0
            
        # get fire command
        if pressed_keys[pg.K_SPACE]:
            fire_cannon = True
        else:
            fire_cannon = False
            
        return d_angle, d_speed, fire_cannon
    
    def use_cannon(self,fire_cannon):
        '''Fires the cannon if firing flag 'fire_cannon' is True by creating a
        LaserSprite object with appropriate initial values near sprite's cannon
        guns' tips. When fleshing out the full game, every laser should be added
        to a player_laser group or similar that keeps track of alive player laser,
        and similarly for enemy lasers. This means the MaskedSprite needs additional
        __init__ arguments to pass groups.
        Returns remaining weapon cool down time.'''
        
        if fire_cannon and not self.weapon_cooling:
            # fire laser beam: set arguments for laser __init__
            laser_screen = self.screen
            laser_lifetime = self.__class__.laser_lifetime
            laser_speed = self._speed + self.__class__.laser_speed
            laser_angle = self._angle
            laser_center = self._center
            
            # fire laser beam: create laserSprite instance
            LaserSprite(laser_screen,'.\\graphics\\laser.bmp',laser_lifetime,
                        self.laser_beams,
                        speed=laser_speed,
                        angle=laser_angle,
                        center=laser_center)
            
            # set cool down counter to maximum after weapon use
            self.weapon_cooling = self.__class__.weapon_cool_down
    
    def update(self):
        '''Updates the sprites position based on player control input. Also fires
        cannon when necessary.'''
        
        # handle player controls
        d_angle, d_speed, fire_cannon = self.get_player_controls()
            
        # rotate sprite if necessary
        self.rotate_ip(d_angle)
        
        # move player sprite
        self.move_ip(d_speed)
            
        # fire cannon if necessary
        self.use_cannon(fire_cannon)
        
        # update weapon cooling counter but keep at minimum 0
        if self.weapon_cooling > 0:
            self.weapon_cooling -= 1
            
class LaserSprite(MaskedSprite):
    
    def __init__(self,screen,image_path,time_left,*groups,**initial_values):
        
        MaskedSprite.__init__(self,screen,image_path,None,*groups,**initial_values)
        
        self.time_left = time_left
    
    def update(self):
        '''Updates the sprite's position.'''
        
        # update timer
        self.time_left -= 1
        
        # self-destruct if timer has reached 0
        if not self.time_left:
            self.kill()
        
        # move the laser beam at constant speed
        self.move_ip(0)
        
        
            
# demo gam states here
import sys, pygame, os

os.chdir('C:\\Users\\bettmensch\\GitReps\\star_wars_dogfighter')

pygame.init()

# create clock    
clock = pg.time.Clock()

white = 255, 255, 255
fps = 40

# initialize main screen
size = width, height = 620, 540 # screen size
screen = pg.display.set_mode(size)

player_sprite = Group()
player_lasers = Group()

player = PlayerSprite(screen,'.\\graphics\\ship_2.bmp',player_lasers,player_sprite,angle=-45)
               
while 1:
    # check for exit events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
    
    # update player
    player_sprite.update()
    
    # update player lasers
    player_lasers.update()

    # draw new game state    
    screen.fill(white) # paint over old game state
    player_sprite.draw(screen) # draw all player sprite
    player_lasers.draw(screen) # draw all player laser sprites
               
    # flip canvas
    pg.display.flip()
    
    # control pace
    clock.tick(fps)