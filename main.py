import pygame
import sys

pygame.init()

# 視窗大小
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("長庚大學校園導覽遊戲")

clock = pygame.time.Clock()

# =======================
#  載入大型地圖
# =======================
map_img = pygame.image.load("assets/map.png").convert_alpha()
MAP_W, MAP_H = map_img.get_width(), map_img.get_height()

print("MAP SIZE =", MAP_W, MAP_H)

# =======================
#  Mini-map（可選）
# =======================
MINI_SCALE = 0.075
mini_map = pygame.transform.scale(map_img, (int(MAP_W * MINI_SCALE), int(MAP_H * MINI_SCALE)))
mini_pos = (WIDTH - mini_map.get_width() - 20, 20)

# =======================
#   玩家 Sprite 設定
# =======================
player_sprite = pygame.image.load("assets/player.png").convert_alpha()

SPRITE_W = player_sprite.get_width() // 3
SPRITE_H = player_sprite.get_height() // 4

# ------------ 自動偵測腳底（前面你確定要） ------------
def detect_foot_offset(sprite_img):
    w = SPRITE_W
    h = SPRITE_H
    max_bottom = 0

    for r in range(4):
        for c in range(3):
            frame = sprite_img.subsurface(c*w, r*h, w, h)
            for y in range(h-1, -1, -1):
                for x in range(w):
                    if frame.get_at((x, y)).a > 0:
                        max_bottom = max(max_bottom, y)
                        break
                else:
                    continue
                break

    return (h - 1) - max_bottom

FOOT_OFFSET = detect_foot_offset(player_sprite)

player_x, player_y = MAP_W // 2, MAP_H // 2  # 角色出生點（地圖中央）
player_speed = 4
anim_frame = 0
direction = 2
move_counter = 0


# =======================
#       Camera 跟隨系統
# =======================
def get_camera_offset():
    """讓角色保持螢幕中心（基於 sprite 中心）"""

    # 角色中心（不包含 FOOT_OFFSET）
    target_x = player_x + SPRITE_W // 2
    target_y = player_y + SPRITE_H // 2

    # camera 要對準角色中心
    cam_x = target_x - WIDTH // 2
    cam_y = target_y - HEIGHT // 2

    # 限制 camera 不超出地圖
    cam_x = max(0, min(cam_x, MAP_W - WIDTH))
    cam_y = max(0, min(cam_y, MAP_H - HEIGHT))

    return cam_x, cam_y




# =======================
#     NPC 區域（套用地圖座標）
# =======================
npcs = {
    "管理大樓": pygame.Rect(900, 600, 80, 80),
    "圖書館": pygame.Rect(1100, 550, 80, 80),
    "工學大樓": pygame.Rect(1200, 650, 80, 80),
    "活動中心": pygame.Rect(1500, 800, 120, 120)
}

npc_text = {
    "管理大樓": "管理大樓：商管系主要上課地點。",
    "圖書館": "圖書館：安靜自習、借書的好地方！",
    "工學大樓": "工學大樓：資工、電機主要教室。",
    "活動中心": "活動中心：社團、活動、健身房。"
}

current_msg = ""


# =======================
#  畫角色
# =======================
def draw_player(camera):
    frame_rect = pygame.Rect(anim_frame * SPRITE_W, direction * SPRITE_H, SPRITE_W, SPRITE_H)
    
    # 取出該格 sprite
    frame = player_sprite.subsurface(frame_rect)

    # 縮小 50%
    scaled_frame = pygame.transform.scale(frame, (SPRITE_W // 2, SPRITE_H // 2))

    # 縮小後的位置（要微調讓腳底仍然踩地）
    screen.blit(
        scaled_frame,
        (
            player_x - camera[0],
            player_y - camera[1] + FOOT_OFFSET // 2   # offset 也等比例縮小
        )
    )



# =======================
#  下方說明欄（永久顯示）
# =======================
font = pygame.font.SysFont("Microsoft YaHei", 28)

def draw_message_bar():
    pygame.draw.rect(screen, (255, 255, 255), (0, HEIGHT - 70, WIDTH, 70))
    pygame.draw.line(screen, (0, 0, 0), (0, HEIGHT - 70), (WIDTH, HEIGHT - 70), 2)

    msg = font.render(current_msg, True, (0, 0, 0))
    screen.blit(msg, (20, HEIGHT - 55))


# =======================
#        遊戲主迴圈
# =======================
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    moving = False
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]:
        player_y -= player_speed
        direction = 0
        moving = True
    if keys[pygame.K_s]:
        player_y += player_speed
        direction = 2
        moving = True
    if keys[pygame.K_a]:
        player_x -= player_speed
        direction = 1
        moving = True
    if keys[pygame.K_d]:
        player_x += player_speed
        direction = 3
        moving = True

    if moving:
        move_counter += 1
        if move_counter % 10 == 0:
            anim_frame = (anim_frame + 1) % 3
    else:
        anim_frame = 1

    # 限制人物不能走出大地圖
    player_x = max(0, min(player_x, MAP_W - SPRITE_W))
    player_y = max(0, min(player_y, MAP_H - SPRITE_H))

    # Camera 跟隨
    camera = get_camera_offset()

    # =======================
    #   繪製地圖（依照 camera 偏移）
    # =======================
    screen.blit(map_img, (-camera[0], -camera[1]))

    # NPC 檢測（記得用地圖座標）
    current_msg = ""
    player_rect = pygame.Rect(player_x, player_y, SPRITE_W, SPRITE_H)

    for name, rect in npcs.items():
        if player_rect.colliderect(rect):
            current_msg = npc_text[name]

        # 畫 NPC 區域（畫面座標 = 地圖座標 - camera）
        debug_rect = pygame.Rect(rect.x - camera[0], rect.y - camera[1], rect.w, rect.h)
        pygame.draw.rect(screen, (255, 255, 0), debug_rect, 2)

    # 畫角色
    draw_player(camera)

    # Mini-map
    screen.blit(mini_map, mini_pos)
    mini_px = int(player_x / MAP_W * mini_map.get_width()) + mini_pos[0]
    mini_py = int(player_y / MAP_H * mini_map.get_height()) + mini_pos[1]
    pygame.draw.circle(screen, (255, 0, 0), (mini_px, mini_py), 4)

    # 下方說明欄（永久顯示）
    draw_message_bar()

    pygame.display.update()
    clock.tick(60)
