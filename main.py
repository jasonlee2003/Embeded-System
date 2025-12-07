import pygame
import sys

pygame.init()

# 視窗大小
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("長庚大學校園導覽遊戲")

# 載入地圖
map_img = pygame.image.load("assets/map.png")
map_img = pygame.transform.scale(map_img, (WIDTH, HEIGHT))

# 玩家
player = pygame.Rect(600, 300, 35, 35)
PLAYER_COLOR = (50, 120, 255)

# NPC 點位（建築物標點）
npcs = {
    "管理大樓": pygame.Rect(430, 260, 40, 40),
    "圖書館": pygame.Rect(550, 250, 40, 40),
    "工學大樓": pygame.Rect(610, 310, 40, 40),
    "學生活動中心": pygame.Rect(850, 350, 40, 40),
    "宿舍區": pygame.Rect(900, 200, 60, 60),
}

npc_text = {
    "管理大樓": "管理大樓：一樓是系辦，常開會的地方！",
    "圖書館": "圖書館：有自習室、書籍、電腦區。",
    "工學大樓": "工學大樓：資工系、電機系上課地點。",
    "學生活動中心": "學生活動中心：社團、健身房、熱門活動都在這。",
    "宿舍區": "宿舍：明德、至德、承德，學生的第二個家！",
}

font = pygame.font.SysFont("Microsoft YaHei", 24)

clock = pygame.time.Clock()

# 顯示對話框
def show_message(text):
    msg = font.render(text, True, (0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255), (0, HEIGHT - 50, WIDTH, 50))
    screen.blit(msg, (20, HEIGHT - 40))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 玩家移動
    keys = pygame.key.get_pressed()
    speed = 5

    if keys[pygame.K_w]:
        player.y -= speed
    if keys[pygame.K_s]:
        player.y += speed
    if keys[pygame.K_a]:
        player.x -= speed
    if keys[pygame.K_d]:
        player.x += speed

    # 邊界限制
    player.x = max(0, min(WIDTH - player.width, player.x))
    player.y = max(0, min(HEIGHT - player.height, player.y))

    screen.blit(map_img, (0, 0))

    # 畫 NPC 區域（簡單用透明框示意）
    for name, rect in npcs.items():
        pygame.draw.rect(screen, (255, 255, 0), rect, 2)

    # 畫玩家
    pygame.draw.rect(screen, PLAYER_COLOR, player)

    # 偵測 NPC 互動
    speaking = None
    for name, rect in npcs.items():
        if player.colliderect(rect):
            speaking = name

    if speaking:
        show_message(npc_text[speaking])

    pygame.display.update()
    clock.tick(60)
