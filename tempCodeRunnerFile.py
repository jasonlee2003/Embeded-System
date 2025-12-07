import pygame
import sys

pygame.init()

# 視窗大小
WIDTH, HEIGHT = 1600, 1147
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("長庚大學校園導覽遊戲")

clock = pygame.time.Clock()

# =======================
#  載入地圖與 Mini-map
# =======================
map_img = pygame.image.load("assets/map.png")
map_img = pygame.transform.scale(map_img, (WIDTH, HEIGHT))

# Mini-map (縮小 15%)
MINI_SCALE = 0.15
mini_map = pygame.transform.scale(
    map_img,
    (int(WIDTH * MINI_SCALE), int(HEIGHT * MINI_SCALE))
)

mini_w, mini_h = mini_map.get_size()
mini_pos = (WIDTH - mini_w - 20, 20)  # 右上角


# =======================
#     玩家 Sprite 設定
# =======================
player_sprite = pygame.image.load("assets/player.png").convert_alpha()
SPRITE_W, SPRITE_H = player_sprite.get_width() // 3, player_sprite.get_height() // 4

player_x, player_y = 300, 150
player_speed = 4
anim_frame = 0
direction = 2  # 0=Up,1=Left,2=Down,3=Right
move_counter = 0

OFFSET_Y = -16   # 根據你人物高度，自行微調，大概 -8 ~ -16

def draw_player():
    global anim_frame
    frame_rect = pygame.Rect(anim_frame * SPRITE_W, direction * SPRITE_H, SPRITE_W, SPRITE_H)
    screen.blit(player_sprite, (player_x, player_y + OFFSET_Y), frame_rect)



# =======================
#         NPC 列表
# =======================
npcs = {
    "管理大樓": pygame.Rect(430, 260, 50, 50),
    "圖書館": pygame.Rect(550, 250, 50, 50),
    "工學大樓": pygame.Rect(610, 310, 50, 50),
    "第一醫學大樓": pygame.Rect(480, 330, 50, 50),
    "第二醫學大樓": pygame.Rect(380, 330, 50, 50),
    "學生活動中心": pygame.Rect(850, 350, 70, 70),
    "英德宿舍": pygame.Rect(900, 200, 70, 70),
    "至德宿舍": pygame.Rect(820, 190, 70, 70),
    "承德宿舍": pygame.Rect(960, 250, 70, 70),
    "體育館": pygame.Rect(780, 420, 80, 80),
    "運動場": pygame.Rect(940, 420, 150, 200),
    "青蛙塘": pygame.Rect(350, 550, 80, 80),
    "機車停車場": pygame.Rect(200, 600, 100, 80),
    "校門口": pygame.Rect(150, 690, 120, 40)
}

npc_text = {
    "管理大樓": "管理大樓：商管系主要上課地點。",
    "圖書館": "圖書館：安靜自習、借書的好地方！",
    "工學大樓": "工學大樓：資工、電機主要教室。",
    "第一醫學大樓": "第一醫學大樓：基礎醫學的核心建築。",
    "第二醫學大樓": "第二醫學大樓：臨床技能教室。",
    "學生活動中心": "活動中心：社團、活動、健身房。",
    "英德宿舍": "英德宿舍：男生宿舍（明德/英德）。",
    "至德宿舍": "至德宿舍：女生宿舍。",
    "承德宿舍": "承德宿舍：教職員與研究生宿舍。",
    "體育館": "體育館：籃球、羽球、桌球應有盡有。",
    "運動場": "運動場：操場、田徑練習場。",
    "青蛙塘": "青蛙塘：校園熱門拍照景點！",
    "機車停車場": "機車停車場：學生最常用入口。",
    "校門口": "校門口：歡迎來到長庚大學！"
}

font = pygame.font.SysFont("Microsoft YaHei", 24)

def show_message(text):
    pygame.draw.rect(screen, (255, 255, 255), (0, HEIGHT - 60, WIDTH, 60))
    msg = font.render(text, True, (0, 0, 0))
    screen.blit(msg, (20, HEIGHT - 45))


# =======================
#        遊戲主迴圈
# =======================
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 移動控制
    keys = pygame.key.get_pressed()
    moving = False

    if keys[pygame.K_w]:
        direction = 0
        player_y -= player_speed
        moving = True
    if keys[pygame.K_s]:
        direction = 2
        player_y += player_speed
        moving = True
    if keys[pygame.K_a]:
        direction = 1
        player_x -= player_speed
        moving = True
    if keys[pygame.K_d]:
        direction = 3
        player_x += player_speed
        moving = True

    if moving:
        move_counter += 1
        if move_counter % 10 == 0:  # 動畫速度
            anim_frame = (anim_frame + 1) % 3
    else:
        anim_frame = 1  # 靜止時中間格

    # 邊界限制
    player_x = max(0, min(WIDTH - SPRITE_W, player_x))
    player_y = max(0, min(HEIGHT - SPRITE_H, player_y))

    # 繪製畫面
    screen.blit(map_img, (0, 0))

    # 畫 NPC
    for name, rect in npcs.items():
        pygame.draw.rect(screen, (255, 255, 0), rect, 2)

    # 畫玩家
    draw_player()

    # 偵測 NPC
    speaking = None
    player_rect = pygame.Rect(player_x, player_y, SPRITE_W, SPRITE_H)
    for name, rect in npcs.items():
        if player_rect.colliderect(rect):
            speaking = name

    if speaking:
        show_message(npc_text[speaking])

    # ========== Mini-map ==========
    screen.blit(mini_map, mini_pos)

    # 玩家在 mini-map 的位置
    mini_px = int(player_x * MINI_SCALE) + mini_pos[0]
    mini_py = int(player_y * MINI_SCALE) + mini_pos[1]
    pygame.draw.circle(screen, (255, 0, 0), (mini_px, mini_py), 4)

    pygame.display.update()
    clock.tick(60)
