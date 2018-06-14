# -*- coding: utf-8 -*-
"""
Created on Sat May 19 22:36:56 2018

@author: bettmensch
"""

'''This file contains the sprite classes used in the game STAR WARS DOGFIGHTER.
It contains the \'MaskedSprite\' class which functions as a functional base class
for all viewable sprite objects in the game.
The FighterSprite class serves as a sub-base class for the spaceship/fighter plane
sprites (either player or pc controlled) \'PlayerSprite\' and \'EnemySprite\'.
The \'LaserSprite\' class is based directly on the MaskedSprite class.'''

from basic_sprite_class import BasicSprite
from animation_classes import BasicAnimation, TrackingAnimation
from weapons_classes import LaserCannon
from math import cos, sin, pi

import pygame as pg
import numpy as np



class ShipSprite(BasicSprite):
    '''Base sprite class for both the player's and the enemy ship(s).'''
    
    _muzzle_flash_lifetime_in_seconds = 0.1
    
    def __init__(self,
                 fps,
                 screen,
                 original_images,
                 laser_cannon_offsets,
                 laser_fire_modes,
                 laser_group,
                 laser_sound,
                 original_laser_beam_images,
                 laser_range_in_seconds,
                 laser_speed_in_seconds,
                 laser_rate_in_seconds,
                 original_muzzle_flash_images,
                 muzzle_flash_seconds_per_image,
                 explosion_sound,
                 original_explosion_images,
                 explosion_seconds_per_image,
                 engine_flame_offsets,
                 original_engine_flame_images,
                 engine_flame_seconds_per_image,
                 animation_group,
                 *groups,
                 center = np.zeros(2),
                 angle = 0,
                 speed = 0,
                 d_angle_degrees_per_second = 20,
                 d_speed_pixel_per_second = 10,
                 max_speed_pixel_per_second = 20,
                 is_transparent = True,
                 transparent_color = (255,255,255)):
    
        '''Arguments:
            
            fps: frames per second ratio of surrounding pygame
             screen: the main screen the game is displayed on (pygame Surface).
                    Needed to 'wrap' sprites around edges to produce 'donut topology'.
            original_images: list of surface objects that will be used to display the sprite.
                    By default, the first list element will be used.
            laser_cannon_offsets: array of relative pixel positions of sprite's gun muzzles w.r.t
                    sprite skin's center.
            laser_fire_modes: dictionary of meta data specifyinh the ship's possible fire modes.
            laser_group: pygame Group object. Any laser created by the ShipSprite's firing method
                    will be added to this group to help track laser fire collisions.
            laser_sound: pygame.mixer.Sound object. Will be played by the ShipSprite's firing method.
            laser_original_images: The original_images sequence that will be passed to the MissileSprite
                    object created by the ShipSprite's firing method. A list of pygame surfaces.
            laser_range_in_seconds: effectively the laser weapon range of the ship sprite. When the 
                    ShipSprite's firing method creates a MissileSprite, this value will be passed to it
                    as its lifetime_in_seconds argument.
            laser_speed_in_seconds: this value will be added to personal _speed attribute value at time
                    of firing cannon. The sum of those values will be passed to the MissileSprite as initial
                    _speed value.
            laser_rate_in_seconds: number of lasers that the ShipSprite can fire per second (i.e. rate of fire)
            explosion_group: pygame Group object. When ShipSprite is terminated, an explosion animation will be created
                    and added to this group.
            explosion_sound: pygame.mixer.Sound object. Will be played for the explosion animation
            original_explosion_images: list of surface objets that will be used to display the explosion animation
                    at time of ShipSprite's death.
            explosion_seconds_per_image: seconds_per_image value that will be passed to the 
                    explosion animation at time of ShipSprite's death
            *groups: tuple of pygame Group objects. The sprite will add itself to each of these
                    when initialized.
            center: initial position of center of sprite's rectangle (numpy float-type array of shape (2,)).
                    Sets the sprite's initial position on the 'screen' surface.
            angle: initial orientation of sprite in degrees. Angle is taken counter-clockwise, with
                    an angle of zero meaning no rotation of the original surface.
            speed: initial speed of sprite (pixels per second). scaler of float type.
                    Default is 0.
            d_angle_degrees_per_second: Rate of change for ShipSprite's angle (in degrees, per second).
            d_speed_pixel_per_second: Rate of change for ShipSprite's speed (in pixels/second, per second).
            max_speed_pixel_per_second: Maximum speed for ShipSprite (in pixels per second).
            is_transparent: transparency flag. If set, pixels colored in the 'transparent_color'
                    color argument in the surfaces contained in 'original_images' will be made transparent.
                    Default is True
            transparent_color: tuple specifiying the color key considered as transparent if 'is_transparent'
                    is set to true. Default to (255,255,255), which corresponds to the color white.'''
                    
        # initialize and add to groups if sensible
        BasicSprite.__init__(self,
                             fps,
                             screen,
                             original_images,
                             *groups,
                             center=center,
                             angle=angle,
                             speed=speed,
                             is_transparent=is_transparent,
                             transparent_color=transparent_color)
        
        # set laser fire meta data attributes            
        self._original_laser_fire_modes = laser_fire_modes
        self._laser_sound = laser_sound
        
        # intialize and attach laser weapons
        self._laser_cannons = []
        
        for laser_cannon_offset in laser_cannon_offsets * self._size_factor:
            # for each weapon offset in the ship skin's meta data, we create and 
            # attach a LaserCannon object
            self._laser_cannons.append(LaserCannon(ship_sprite=self,
                                                     cannon_offset=laser_cannon_offset,
                                                     cannon_fire_rate=laser_rate_in_seconds,
                                                     cannon_range_in_seconds=laser_range_in_seconds,
                                                     cannon_projectile_speed_in_seconds=laser_speed_in_seconds,
                                                     cannon_projectile_group=laser_group,
                                                     original_laser_beam_images=original_laser_beam_images,
                                                     original_muzzle_flash_images=original_muzzle_flash_images,
                                                     muzzle_flash_animation_spi=muzzle_flash_seconds_per_image))


        # attach animations group to sprite
        self._animation_group = animation_group
        
        # set attributes for explosion animation at death
        self._explosion_sound = explosion_sound
        self._original_explosion_images = original_explosion_images
        self._explosion_seconds_per_image = explosion_seconds_per_image
        
        # set attributes for engine animation when moving
        self._engine_flame_offsets = engine_flame_offsets
        self._original_engine_flame_images = original_engine_flame_images
        self._engine_flame_seconds_per_image = engine_flame_seconds_per_image
        
        # set motion control attributes
        self._d_angle_degrees_per_frame = d_angle_degrees_per_second / self._fps
        self._d_speed_pixel_per_frame = d_speed_pixel_per_second / self._fps
        self._max_speed_pixel_per_frame = max_speed_pixel_per_second / self._fps
        
        # set initial fire mode to coupled cannons, set cannon index to 0
        self._fire_mode_index = 1
        self._cannon_index = 0
        
        # create engine flame animation(s)
        self._engine_animations = []
        
        if self._speed:
            self._create_engine_animations()
            
    def _toggle_fire_mode(self):
        '''Util function that takes an integer and uses it to set one of the at least
        2 different laser fire modes ('single' or 'coupled').'''
        
        print('Fire mode toggled!')
                                     
        # switch to next fire mode
        self._fire_mode_index = (self._fire_mode_index + 1) % len(self._original_laser_fire_modes)
        
        # set cannon index back to zero to avoid out of bounds indices when downsampling fire mode
        self._cannon_index = 0  
        
        print('fire mode index:',self._fire_mode_index)
        print('cannon settings in this mode:', len(self._original_laser_fire_modes[self._fire_mode_index]))
        print('cannon index:', self._cannon_index)
        
    def _create_engine_animations(self):
        '''Util method to create engine animations.'''
        
        for engine_flame_offset in self._engine_flame_offsets:
            self._engine_animations.append(TrackingAnimation(self._fps,
                                                             self._screen,
                                                             self._original_engine_flame_images,
                                                             self._engine_flame_seconds_per_image,
                                                             self,
                                                             engine_flame_offset * self._size_factor,
                                                             self._animation_group,
                                                             looping = True))
        
    def get_gunner_commands(self):
        '''Returns True if ShipSprite should fire, or False otherwise.
        For the ShipSprite base class trivially always returns False.
        For more sophisticated classes, this method will handle player input
        or an AI gunner and return a non-trivial boolean.'''
        
        return False
    
    def _get_next_cannons(self):
        '''Util function that returns a list of laser cannons next in line to be fired.'''
        
        # get index set for cannons lined up to fir enext
        laser_cannon_index_set = self._original_laser_fire_modes[self._fire_mode_index][self._cannon_index]
        
        print('laser cannon index set:',laser_cannon_index_set)
        
        return [self._laser_cannons[i] for i in laser_cannon_index_set]
    
    def _pause_next_cannons(self):
        '''Util function that makes the set of cannons which are next in line
        to fire wait an appropriate amount of time to guarantee evenly spaced fire.'''
        
        # get number of salves per cycle for current firing mode
        n_salves = len(self._original_laser_fire_modes[self._fire_mode_index])
        
        for next_cannon in self._get_next_cannons():
            now = pg.time.get_ticks()
            mil_seconds_per_shot = 1000 / next_cannon._rate_of_fire
            next_cannon._time_of_last_shot = now - (n_salves - 1) / n_salves * mil_seconds_per_shot

    def fire(self):
        '''Creates a MissileSprite objects at SpriteShip's specified locations
        of gun muzzles.'''
        
        # play laser sound
        self._laser_sound.play()
        
        print('fire mode index:',self._fire_mode_index)
        print('cannon settings in this mode:', len(self._original_laser_fire_modes[self._fire_mode_index]))
        print('cannon index:', self._cannon_index)
        
        # fire cannons
        [laser_cannon.fire() for laser_cannon in self._get_next_cannons()]
        
        # update cannon index within current fire mode
        self._cannon_index = (self._cannon_index + 1) % len(self._original_laser_fire_modes[self._fire_mode_index])
        
        # update cannons next in line so they wait as approrpiate
        self._pause_next_cannons()
        
    def _handle_engine_animation(self):
        '''Util function that handles engine animation w.r.t speed changes.'''
        
        if not self._speed and len(self._engine_animations):
            # removes sprite's engine flames animations from all groups
            [engine_flame.kill() for engine_flame in self._engine_animations]  
            
            # empty engine animations list
            self._engine_animations = []
            
        elif self._speed and not len(self._engine_animations):
            # create new engine animations
            self._create_engine_animations()
        
    def update(self):
        '''Base class update plus additional ShipSprite specific updates.'''
        
        # call base class update method
        BasicSprite.update(self)
        
        # get command to fire from custom method
        command_to_fire = self.get_gunner_commands()
        
        # if command to fire was given, check if cannons are ready; if so, fire
        if command_to_fire and np.mean([cannon.is_ready() for cannon in self._get_next_cannons()]):
            # fire the cannon(s)
            self.fire()
            
        # delete/recreate engine animation based on current speed
        self._handle_engine_animation()

            
    def kill(self):
        '''Base class kill method plus moving explosion animation.'''
        
        # play sound of explosion
        self._explosion_sound.play()
        
        # remove self from all groups
        BasicSprite.kill(self)
        
        # removes sprite's engine flames animations from all groups
        [engine_flame.kill() for engine_flame in self._engine_animations]
        
        # create explosion animation
        BasicAnimation(self._fps,
                      self._screen,
                      self._original_explosion_images,
                      self._explosion_seconds_per_image,
                      self._animation_group,
                      center = self._center,
                      angle = self._angle,
                      speed = self._speed * self._fps) # animation expects pixel/second speed unit
        
class PlayerShipSprite(ShipSprite):
    '''Class representing the player's sprite. Based on general ShipSprite class.
    
    For a description of the arguments of the PlayerShipSprite's __init__ method,
    please see the documentation of the base class (ShipSprite).'''
    
    
    def get_pilot_commands(self):
        '''Handles directional player controls, i. e. steering and accelerating.
        Returns a tuple of scalar floats (d_angle,d_speed), giving the change in
        degrees (counter-clockwise) per frame and the change in speed in pixels/frame^2,
        respectively.'''
        
        # get all keys currently down
        pressed_keys = pg.key.get_pressed()
            
        # get angle differential
        if pressed_keys[pg.K_LEFT] and not pressed_keys[pg.K_RIGHT]:
            # turn left
            d_angle = self._d_angle_degrees_per_frame
        elif pressed_keys[pg.K_RIGHT] and not pressed_keys[pg.K_LEFT]:
            # turn right            
            d_angle = -self._d_angle_degrees_per_frame
        else:
            # dont turn            
            d_angle = 0
            
        # get speed differential
        if pressed_keys[pg.K_UP] and not pressed_keys[pg.K_DOWN]:
            # dont accelerate above sprite's max speed
            d_speed = min(self._d_speed_pixel_per_frame,
                          self._max_speed_pixel_per_frame - self._speed)
        elif pressed_keys[pg.K_DOWN] and not pressed_keys[pg.K_UP]:
            # dont decelarate to going backwards
            d_speed = -min(self._d_speed_pixel_per_frame,
                           self._speed)
        else:
            # dont change speed
            d_speed = 0
            
        return d_angle, d_speed
    
    def get_gunner_commands(self):
        '''Handles shooting player controls, i.e. firing lasers.
        Returns True if player has the space bar pressed, and False
        otherwise'''
        
        # space bar is pressed, fire command is given
        return pg.key.get_pressed()[pg.K_SPACE]
        
class EnemyShipSprite(ShipSprite):
    '''Based on ShipSprite class. Represents an enemy ship during game.'''
    
    def __init__(self,
                 fps,
                 screen,
                 original_images,
                 laser_cannon_offsets,
                 laser_fire_modes,
                 laser_group,
                 laser_sound,
                 original_laser_beam_images,
                 laser_range_in_seconds,
                 laser_speed_in_seconds,
                 laser_rate_in_seconds,
                 original_muzzle_flash_images,
                 muzzle_flash_seconds_per_image,
                 explosion_sound,
                 original_explosion_images,
                 explosion_seconds_per_image,
                 engine_flame_offsets,
                 original_engine_flame_images,
                 engine_flame_seconds_per_image,
                 animation_group,
                 player_ship_sprite,
                 piloting_cone_sine,
                 gunning_cone_sine,
                 *groups,
                 center = np.zeros(2),
                 angle = 0,
                 speed = 0,
                 d_angle_degrees_per_second = 20,
                 d_speed_pixel_per_second = 10,
                 max_speed_pixel_per_second = 20,
                 is_transparent = True,
                 transparent_color = (255,255,255)):
    
        '''Arguments: All as in base class's (ShipSprite) __init__ method, except
        for 
            player_ship_sprite: PlayerShipSprite object representing the player during game.
                                Used for EnemyShipSprite's piloting and gunning methods.
            piloting_cone_sine: Sine of half of cone representing the enemy pilot's field of sight.
                If pilot can not see the PlayerShipSprite, he will turn to get him back into
                view.
            gunning_cone_sine: Sine of half of the cone representing the enemy gunner's target sight.
                If PlayerShipSprite is within this cone, gunner will attempt to fire cannon.'''
                                
        ShipSprite.__init__(self,
                            fps,
                            screen,
                            original_images,
                            laser_cannon_offsets,
                            laser_fire_modes,
                            laser_group,
                            laser_sound,
                            original_laser_beam_images,
                            laser_range_in_seconds,
                            laser_speed_in_seconds,
                            laser_rate_in_seconds,
                            original_muzzle_flash_images,
                            muzzle_flash_seconds_per_image,
                            explosion_sound,
                            original_explosion_images,
                            explosion_seconds_per_image,
                            engine_flame_offsets,
                            original_engine_flame_images,
                            engine_flame_seconds_per_image,
                            animation_group,
                             *groups,
                             center = center,
                             angle = angle,
                             speed = speed,
                             d_angle_degrees_per_second = d_angle_degrees_per_second,
                             d_speed_pixel_per_second = d_speed_pixel_per_second,
                             max_speed_pixel_per_second = max_speed_pixel_per_second,
                             is_transparent = is_transparent,
                             transparent_color = transparent_color)
        
                # attach the player's sprite object
        self._player_sprite = player_ship_sprite
        
        # attach the AI cone sines
        self._piloting_cone_sine = piloting_cone_sine
        self._gunning_cone_sine = gunning_cone_sine
        
    def use_radar(self):
        '''Util method used by piloting and gunning methods. Yields player position
        relative to the enemy sprite by calculating the projection of the 
        enemy -> player connecting line on the vector orthogonal to the enemy's
        current direction of flight. This allows the enemy to see whether to turn
        left or right to get closer to the player.'''
        
        # get own directional unit vector
        # convert angle to radian
        angle_radian = self._angle * pi / 180
        
        # get unit directional vector
        unit_direction = np.array([cos(angle_radian),
                              -sin(angle_radian)])
    
        # get clockwise oriented orthonormal to unit directional vector
        clockwise_ortnorm_direction = np.array([unit_direction[1],
                                                -unit_direction[0]])
        
        # get clockwise rotated orthogonal to unit vector pointing towards player position
        towards_player_vector = (self._player_sprite._center - self._center)
        unit_towards_player_vector = towards_player_vector / np.linalg.norm(towards_player_vector)
        
        # turn towards player, whichever way is more aligned with current direction of movement
        projection_on_ortnorm = np.dot(clockwise_ortnorm_direction,
                                       unit_towards_player_vector)
        
        return projection_on_ortnorm
    
    def get_pilot_commands(self):
        '''See parent FighterSprite class doc for this method.'''
        
        # have a look at the radar to see where player sprite is
        projection_on_ortnorm = self.use_radar()

        # turn towards player, whichever way is more aligned with current direction of movement        
        if projection_on_ortnorm > self._piloting_cone_sine:
            # turn left
            d_angle = self._d_angle_degrees_per_frame
        elif projection_on_ortnorm < -self._piloting_cone_sine:
            # turn right
            d_angle = - self._d_angle_degrees_per_frame
        else:
            # continue straight on
            d_angle = 0
            
        # currently no logic to control AI acceleration
        d_speed = 0
        
        return d_angle, d_speed
        
    def get_gunner_commands(self):
        '''See parent FighterSprite class doc for this method.'''
        
        # have a look at the radar to see where player sprite is
        projection_on_ortnorm = self.use_radar()
        
        # if player within 'cone of reasonable accuracy', attempt to fire cannon.
        # Otherwise, dont attempt to fire cannon
        return -self._gunning_cone_sine < projection_on_ortnorm < self._gunning_cone_sine