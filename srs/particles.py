# using pygame ig
import pygame
import os
import math
import random
import torch


try:
    pygame.init()
    window_width = 800
    window_height = 600
    screen = pygame.display.set_mode((window_width,window_height))
    clock = pygame.time.Clock()



    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # srs/ -> project root
    img_set = ["v1_back_view.png",  "v1_front.png", "v1_side.png"]
    img_set_path = []
    for _ in img_set:
        img_set_path.append(os.path.join(BASE_DIR, "assets", _))

    font = pygame.font.SysFont("sans", 22)

    text_surface = font.render("hello world", True , (255, 255, 255))

    back = pygame.transform.scale(pygame.image.load(img_set_path[0]).convert_alpha(), (400,400))
    front= pygame.transform.scale(pygame.image.load(img_set_path[1]).convert_alpha(), (400,400))
    right_side = pygame.transform.scale(pygame.image.load(img_set_path[2]).convert_alpha(), (400, 400))
    left_side = pygame.transform.flip(pygame.transform.scale(pygame.image.load(img_set_path[2]).convert_alpha(), (400, 400)), flip_x= True, flip_y=False)

    frames = [front, right_side, back, left_side]

    frame_count = 0
    frame_stall = 30
    p1_x = window_width //2
    p1_y = window_height //2



except KeyboardInterrupt : 
    pass

# variables

frame_x, frame_y = 200, 100

g           = 2.2
bounce      = 0.8
radius      = 5
running     = True
g_friction   = 0.8 
air_friction = 0.9
mouse_power = 0.3
pull_distant = 60
push_power = 0.002

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {torch.cuda.get_device_name}")

PARTICLE_COUNT = 2000
    

    # making a tensors that hold positions, tensor that hold velocity

pos = torch.stack([
    torch.randint(radius, window_width-radius, (PARTICLE_COUNT,), dtype=torch.float32 , device=device), #x cor gen
    torch.randint(radius, window_height-radius, (PARTICLE_COUNT,), dtype=torch.float32 , device=device)  #y cor gen
], dim=1)

vel = torch.zeros((PARTICLE_COUNT, 2), dtype=torch.float32, device=device)

#update particle handler

def update_paticle (pos, vel, dt, mouse_x, mouse_y, mouse_pressed):
    # applying forces
    vel[:, 1] += g * dt   #gravity applications
    vel[:, 0] *= (air_friction ** dt)

    pos += vel

    # ==========================================
    # 3. ROBUST WALL COLLISIONS
    # ==========================================
    # Left & Right Bounds
    hit_left = pos[:, 0] <= radius
    hit_right = pos[:, 0] >= window_width - radius

    pos[hit_left, 0] = radius
    pos[hit_right, 0] = window_width - radius
    
    # Reverse velocity only if heading into the wall
    vel[hit_left & (vel[:, 0] < 0), 0] *= -bounce
    vel[hit_right & (vel[:, 0] > 0), 0] *= -bounce

    # Top & Bottom Bounds
    hit_top = pos[:, 1] <= radius
    hit_bottom = pos[:, 1] >= window_height - radius

    pos[hit_top, 1] = radius
    pos[hit_bottom, 1] = window_height - radius

    vel[hit_top & (vel[:, 1] < 0), 1] *= -bounce
    vel[hit_bottom & (vel[:, 1] > 0), 1] *= -bounce
        # cool thing here is making a check on py array [ conditions, dimensions] pretty cool

    # mouse interaction 

    if mouse_pressed:
        mouse_pos = torch.tensor([mouse_x, mouse_y], dtype=torch.float32, device=device)
        diff = mouse_pos - pos  # vector of distance
        # dist is  a 1d array that have size [particale cont, 1] this hold all distance
        dist = torch.norm(diff, dim = 1, keepdim=True)  # true distance tensor

        valid = (dist<= pull_distant) & (dist>= pull_distant/2)
        dir_vector = diff/dist

        vel[valid.squeeze()] += dir_vector[valid.squeeze()] * mouse_power

    # -- partcle to particle collisions logic -- 

    diff_p = pos.unsqueeze(1) - pos.unsqueeze(0)
    dist_matrix = torch.norm(diff_p, dim = 2)

    min_distance = radius * 2
    mask = (dist_matrix < min_distance) & (dist_matrix >0)

    if mask.any():
        overlap = min_distance - dist_matrix
        overlap_mask = mask.unsqueeze(2).float()
        norm_dir = diff_p / (dist_matrix.unsqueeze(2) + 1e-8)

        correction = norm_dir   * overlap.unsqueeze(2) * push_power * overlap_mask
        pos -= correction.sum(dim=1)
        pos += correction.sum(dim=0)
        vel_diff = vel.unsqueeze(1) - vel.unsqueeze(0)
        
        # Find velocity component along the collision normal
        vel_normal = torch.sum(vel_diff * norm_dir, dim=2, keepdim=True)
        
        # Only bounce if they are actually moving toward each other (vel_normal < 0)
        approaching = (vel_normal < 0).float() * overlap_mask
        
        # Calculate bounce impulse (using your bounce factor)
        impulse = norm_dir * vel_normal * (1.0 + bounce) * 0.2 * approaching
        
        # Apply impulse to velocities
        vel -= impulse.sum(dim=1)
        vel += impulse.sum(dim=0)

    return pos, vel


while running:
    dt = clock.tick(60) / 1000
    frame_count += 1    

    mouse_pressed = False
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_x, mouse_y = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:
        mouse_pressed = True

    po, vel = update_paticle(pos, vel, dt, mouse_x, mouse_y, mouse_pressed)

    #bring back to cpu the possitions
    pos_cpu = pos.cpu().numpy()

    

    screen.fill((0,0,0))
    
    # text
    text_surface = font.render(f"time second: {frame_count//60}", True, (255, 255, 255))
    screen.blit(text_surface, (550, 50))
    

    chosen_frame =  (frame_count % frame_stall)* len(frames) // frame_stall   
    screen.blit(frames[chosen_frame], (frame_x, frame_y))

    #   drawing particle 

    for i in range(PARTICLE_COUNT):
        pygame.draw.circle(screen, (225, 40, 4), (int(pos_cpu[i,0]),int(pos_cpu[i,1]) ), radius)  

    ball_text_count = font.render(f"balls   : {PARTICLE_COUNT}", True, (255, 255, 255))
    screen.blit(ball_text_count , (550, 80))
    
    
    pygame.display.flip()

pygame.quit()
