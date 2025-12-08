import pygame
import sys

pygame.init()

# =======================
# 基本設定
# =======================
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("長庚大學校園導覽遊戲")

clock = pygame.time.Clock()

# Debug Mode（F1 切換）
debug_mode = False
# F2：終端機座標顯示開關
show_pos = False

# =======================
#  載入地圖
# =======================
map_img = pygame.image.load("assets/map.png").convert_alpha()
MAP_W, MAP_H = map_img.get_width(), map_img.get_height()
print("MAP SIZE =", MAP_W, MAP_H)

# =======================
#  小地圖 Mini-map
# =======================
MINI_SCALE = 0.075
mini_map = pygame.transform.scale(
    map_img,
    (int(MAP_W * MINI_SCALE), int(MAP_H * MINI_SCALE))
)
mini_pos = (WIDTH - mini_map.get_width() - 20, 20)

# =======================
#  玩家 Sprite 讀取
# =======================
player_sprite = pygame.image.load("assets/player.png").convert_alpha()
SPRITE_W = player_sprite.get_width() // 3
SPRITE_H = player_sprite.get_height() // 4


def detect_foot_offset(sprite_img):
    w = SPRITE_W
    h = SPRITE_H
    max_bottom = 0

    for r in range(4):
        for c in range(3):
            frame = sprite_img.subsurface(c*w, r*h, w, h)
            for y in range(h - 1, -1, -1):
                for x in range(w):
                    if frame.get_at((x, y)).a > 0:
                        max_bottom = max(max_bottom, y)
                        break
                else:
                    continue
                break
    return (h - 1) - max_bottom


FOOT_OFFSET = detect_foot_offset(player_sprite)

player_x, player_y = MAP_W // 2, MAP_H // 2
player_speed = 4
direction = 2
anim_frame = 1
move_counter = 0

# =======================
# Camera 跟隨
# =======================
def get_camera_offset():
    target_x = player_x + SPRITE_W // 2
    target_y = player_y + SPRITE_H // 2

    cam_x = max(0, min(target_x - WIDTH // 2, MAP_W - WIDTH))
    cam_y = max(0, min(target_y - HEIGHT // 2, MAP_H - HEIGHT))

    return cam_x, cam_y


# =======================
# 建築物 hitbox（已校正）
# =======================
npcs = {
    "管理大樓": pygame.Rect(650, 738, 250, 220),
    "第一醫學大樓": pygame.Rect(900, 880, 250, 240),
    "第二醫學大樓": pygame.Rect(750, 880, 250, 240),
    "工學大樓": pygame.Rect(1150, 900, 250, 220),
    "圖書館": pygame.Rect(1080, 700, 250, 240),
    "文物館": pygame.Rect(630, 950, 250, 220),

    "明德宿舍": pygame.Rect(350, 350, 300, 250),
    "莒德宿舍": pygame.Rect(1350, 400, 300, 240),
    "育德宿舍": pygame.Rect(1850, 650, 260, 220),
    "崇德宿舍": pygame.Rect(2100, 650, 260, 220),
    "雲德宿舍": pygame.Rect(1950, 700, 260, 220),
    "男教職員宿舍": pygame.Rect(2250, 720, 220, 200),

    "活動中心": pygame.Rect(1500, 950, 420, 350),
    "籃球場": pygame.Rect(1350, 1000, 240, 200),
    "運動場": pygame.Rect(1700, 1150, 600, 500),
    "網球場": pygame.Rect(1000, 300, 260, 180),
    "羽球館": pygame.Rect(1900, 450, 260, 180),
    "景觀湖": pygame.Rect(800, 1200, 320, 260),

    "校門口": pygame.Rect(450, 1600, 500, 350),
    "機車停車場": pygame.Rect(350, 1250, 350, 260),
    "汽車停車場": pygame.Rect(650, 1500, 420, 300),
    "公車站": pygame.Rect(1150, 1100, 250, 180),
    "創辦人紀念公園": pygame.Rect(900, 1150, 300, 240),
}

npc_text = {
    "管理大樓": "管理大樓：企管、資管、醫管主要上課地點。",
    "第一醫學大樓": "第一醫學大樓：基礎醫學課程與實驗室集中地。",
    "第二醫學大樓": "第二醫學大樓：臨床與高年級醫學生課程。",
    "工學大樓": "工學大樓：資工、電機、化工主要教室所在地。",
    "圖書館": "圖書館：借書、自習、討論室熱門地點。",
    "文物館": "文物館：台塑企業與校史展示館。",

    "明德宿舍": "明德宿舍：安靜、靠近木棧道與網球場。",
    "莒德宿舍": "莒德宿舍：靠近運動區的男宿舍。",
    "育德宿舍": "育德宿舍：女生宿舍，生活便利。",
    "崇德宿舍": "崇德宿舍：交通便利的宿舍區中心。",
    "雲德宿舍": "雲德宿舍：鄰近操場及活動中心。",
    "男教職員宿舍": "男教職員宿舍：教職員居住區。",

    "活動中心": "活動中心：社團、健身房、多功能活動場館。",
    "籃球場": "籃球場：最熱門的運動場地之一。",
    "運動場": "運動場：體育課、運動會與夜跑場地。",
    "網球場": "網球場：體育課與網球隊訓練場。",
    "羽球館": "羽球館：體育課與社團使用空間。",
    "景觀湖": "景觀湖：著名散步與拍照景點。",

    "校門口": "校門口：公車、校車主要出入口。",
    "機車停車場": "機車停車場：學生主要停車區。",
    "汽車停車場": "汽車停車場：教職員與訪客使用。",
    "公車站": "公車站：往醫院、科大、桃園方向。",
    "創辦人紀念公園": "創辦人紀念公園：校園綠地休憩區。",
}

current_msg = ""

# =======================
# 畫角色
# =======================
def draw_player(camera):
    frame_rect = pygame.Rect(anim_frame * SPRITE_W, direction * SPRITE_H, SPRITE_W, SPRITE_H)
    frame = player_sprite.subsurface(frame_rect)
    scaled = pygame.transform.scale(frame, (SPRITE_W // 2, SPRITE_H // 2))

    screen.blit(
        scaled,
        (player_x - camera[0], player_y - camera[1] + FOOT_OFFSET // 2)
    )

# =======================
# 下方資訊欄
# =======================
font = pygame.font.SysFont("Microsoft YaHei", 28)

def draw_message_bar():
    pygame.draw.rect(screen, (255, 255, 255), (0, HEIGHT - 70, WIDTH, 70))
    pygame.draw.line(screen, (0, 0, 0), (0, HEIGHT - 70), (WIDTH, HEIGHT - 70), 2)

    msg = font.render(current_msg, True, (0, 0, 0))
    screen.blit(msg, (20, HEIGHT - 55))


# =======================
# 主迴圈
# =======================
while True:
    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                debug_mode = not debug_mode
                print("Debug Mode =", debug_mode)

            if event.key == pygame.K_F2:
                show_pos = not show_pos
                print("Show Position =", show_pos)

    # Move
    moving = False
    keys = pygame.key.get_pressed()

    if keys[pygame.K_w]: player_y -= player_speed; direction = 0; moving = True
    if keys[pygame.K_s]: player_y += player_speed; direction = 2; moving = True
    if keys[pygame.K_a]: player_x -= player_speed; direction = 1; moving = True
    if keys[pygame.K_d]: player_x += player_speed; direction = 3; moving = True

    if moving:
        move_counter += 1
        if move_counter % 10 == 0:
            anim_frame = (anim_frame + 1) % 3
    else:
        anim_frame = 1

    # Clamp bounds
    player_x = max(0, min(player_x, MAP_W - SPRITE_W))
    player_y = max(0, min(player_y, MAP_H - SPRITE_H))

    camera = get_camera_offset()

    # Draw map
    screen.blit(map_img, (-camera[0], -camera[1]))

    # Hitbox（修正版）
    current_msg = ""

    player_rect = pygame.Rect(
        player_x,
        player_y,
        SPRITE_W // 2,
        SPRITE_H // 2
    )

    for name, rect in npcs.items():
        if player_rect.colliderect(rect):
            current_msg = npc_text[name]

        if debug_mode:
            debug_rect = pygame.Rect(
                rect.x - camera[0],
                rect.y - camera[1],
                rect.w,
                rect.h
            )
            pygame.draw.rect(screen, (255, 255, 0), debug_rect, 2)

    # Draw player
    draw_player(camera)

    # Mini-map
    screen.blit(mini_map, mini_pos)
    mini_px = int(player_x / MAP_W * mini_map.get_width()) + mini_pos[0]
    mini_py = int(player_y / MAP_H * mini_map.get_height()) + mini_pos[1]
    pygame.draw.circle(screen, (255, 0, 0), (mini_px, mini_py), 4)

    # Bottom Message Bar
    draw_message_bar()

    # F2：終端機即時座標輸出
    if show_pos:
        print(f"Player World Pos = ({player_x}, {player_y})")

    pygame.display.update()
    clock.tick(60)
