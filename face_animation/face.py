# face_animation/face.py

import pygame
import sys
import queue
import os

class FaceAnimator:
    def __init__(self, face_image_path, mouth_image_path,
                 window_size=(1200, 800),
                 min_scale=1.0, max_scale=3.0):
        self.face_image_path = face_image_path
        self.mouth_image_path = mouth_image_path
        self.window_size = window_size
        self.min_scale = min_scale
        self.max_scale = max_scale
        self._amplitude_queue = queue.Queue()
        self.running = True

    def update_amplitude(self, ampl):
        self._amplitude_queue.put(ampl)

    def run(self):
        pygame.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = '50,50'
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Robot Face")
        
        
        
        # Load and flip face image
        self.face_img = pygame.image.load(self.face_image_path).convert_alpha()
        self.face_img = pygame.transform.flip(self.face_img, True, False)
        face_scale = 1.0
        new_face_width = int(self.face_img.get_width() * face_scale)
        new_face_height = int(self.face_img.get_height() * face_scale)
        self.face_img = pygame.transform.scale(self.face_img, (new_face_width, new_face_height))
        self.face_rect = self.face_img.get_rect(
            center=(self.window_size[0]//2, self.window_size[1]//2)
        )
        
        # Load and flip mouth image
        self.mouth_img = pygame.image.load(self.mouth_image_path).convert_alpha()
        self.mouth_img = pygame.transform.flip(self.mouth_img, True, False)
        # Scale mouth 2x
        mouth_base_scale = 2.0
        base_mouth_width = int(self.mouth_img.get_width() * mouth_base_scale)
        base_mouth_height = int(self.mouth_img.get_height() * mouth_base_scale)
        self.mouth_img = pygame.transform.scale(self.mouth_img, (base_mouth_width, base_mouth_height))
        
        # Position mouth further down (right) on the face
        mouth_horizontal_offset = 400  # Increased from 200 to 400
        mouth_vertical_offset = 50     # Keep the same vertical offset
        self.mouth_rect = self.mouth_img.get_rect(
            center=(self.window_size[0]//2 + mouth_horizontal_offset, 
                   self.window_size[1]//2 + mouth_vertical_offset)
        )

        self.clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

            self.screen.fill((0, 0, 0))
            self.screen.blit(self.face_img, self.face_rect)
            
            scale_factor = self.min_scale
            if not self._amplitude_queue.empty():
                amplitude = self._amplitude_queue.get_nowait()
                mapped_scale = self.min_scale + (amplitude/3000.0)*(self.max_scale - self.min_scale)
                scale_factor = max(self.min_scale, min(mapped_scale, self.max_scale))
            
            new_w = int(self.mouth_img.get_width() * scale_factor)
            new_h = int(self.mouth_img.get_height() * scale_factor)
            mouth_scaled = pygame.transform.scale(self.mouth_img, (new_w, new_h))
            scaled_rect = mouth_scaled.get_rect(
                center=(self.window_size[0]//2 + mouth_horizontal_offset, 
                       self.window_size[1]//2 + mouth_vertical_offset)
            )
            self.screen.blit(mouth_scaled, scaled_rect)
            
            pygame.display.flip()
            self.clock.tick(30)

        pygame.quit()

    def stop(self):
        self.running = False

