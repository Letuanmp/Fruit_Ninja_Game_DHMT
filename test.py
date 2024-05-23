import pygame
import math
import random
import sys

# Khởi tạo các thông số cơ bản
xWin = 600
yWin = 600
img_path = 'images/'
fps = 10
win_size = (xWin, yWin)

# Khởi tạo cửa sổ game
pygame.display.set_icon(pygame.image.load(img_path + 'icon.png'))  # Đặt icon cho cửa sổ game
pygame.display.set_caption("Fruit Ninja")  # Đặt tiêu đề cho cửa sổ game

pygame.init()  # Khởi tạo các mô-đun của Pygame
win = pygame.display.set_mode(win_size)  # Tạo cửa sổ với kích thước đã định

# Khởi tạo phông chữ và điểm số
score = 0
font = pygame.font.SysFont(None, 36)  # Khởi tạo phông chữ với kích thước 36

# Danh sách các loại trái cây
fruit_list = {
    0: 'watermelon',
    1: 'banana',
    2: 'peach',
    3: 'basaha',
    4: 'apple',
    5: 'boom'
}

# Kích thước tối đa của đuôi dao
max_tail_size = 5

class knife:
    def __init__(self, win):
        self.pos = pygame.mouse.get_pos()  # Lấy vị trí hiện tại của con trỏ chuột
        self.drag = True
        self.win = win
        self.tail_size = 0
        self.tail = []  # Danh sách lưu vị trí đuôi dao
        self.width = 7
        self.height = 7
        self.default_size = (7, 7)
        self.angle = 0
        self.enable_cut = False  # Biến kiểm tra dao có thể cắt hay không
        self.image = pygame.Surface(self.default_size)
        self.rect = self.image.get_rect()
        self.rect.top = self.pos[1]
        self.rect.bottom = self.pos[1] + self.height
        self.rect.left = self.pos[0]
        self.rect.right = self.pos[0] + self.width
        self.flash = pygame.image.load(img_path + 'flash.png')  # Hình ảnh vết cắt

    def sharp(self):
        return self.enable_cut

    def enable_cutting(self):
        self.enable_cut = True

    def disable_cutting(self):
        self.enable_cut = False

    def draw(self):
        size = 7
        factor = 0.8
        if self.drag:
            for pos in reversed(self.tail):
                pygame.draw.rect(self.win, (255, 255, 255), (pos[0], pos[1], size, size))  # Vẽ đuôi dao
                size = factor * size

    def find_angle(self):
        if len(self.tail) > 2:
            try:
                self.angle = math.atan(abs((self.tail[-1][1] - self.tail[-2][1]) / (self.tail[-1][0] - self.tail[-2][0])))
            except:
                self.angle = math.pi / 2

            # Xác định góc của dao dựa vào vị trí của đuôi dao
            if self.tail[-1][1] < self.tail[-2][1] and self.tail[-1][0] > self.tail[-2][0]:
                self.angle = abs(self.angle)
            elif self.tail[-1][1] < self.tail[-2][1] and self.tail[-1][0] < self.tail[-2][1]:
                self.angle = math.pi - self.angle
            elif self.tail[-1][1] > self.tail[-2][1] and self.tail[-1][0] < self.tail[-2][0]:
                self.angle = math.pi + abs(self.angle)
            elif self.tail[-1][1] > self.tail[-2][1] and self.tail[-1][0] > self.tail[-2][0]:
                self.angle = (math.pi * 2) - self.angle
            else:
                self.angle = 0

    def update_react(self):
        self.rect.top = self.pos[1]
        self.rect.bottom = self.pos[1] + self.height
        self.rect.left = self.pos[0]
        self.rect.right = self.pos[0] + self.width

    def update(self):
        self.pos = pygame.mouse.get_pos()
        self.update_react()

        if self.tail_size < max_tail_size:
            self.tail.append(self.pos)
            self.tail_size += 1
        else:
            self.tail.pop(0)  # Xóa phần tử đầu tiên
            self.tail.append(self.pos)

        self.find_angle()
        self.draw()

    def cut(self):
        rotatedFlash = pygame.transform.rotate(self.flash, self.angle * 180 / math.pi)  # Xoay hình ảnh vết cắt theo góc dao
        rotflash = rotatedFlash.get_rect()
        rotflash.center = tuple(self.pos)
        self.win.blit(rotatedFlash, rotflash)  # Vẽ hình ảnh vết cắt lên cửa sổ game

class fruit:
    def __init__(self, name, win, cut=False):
        self.name = name
        self.image = pygame.image.load(img_path + name + '.png')
        self.rect = self.image.get_rect()
        self.width, self.height = self.image.get_size()

        self.cut = cut
        self.pos = [random.randint(self.width, xWin - self.width), yWin + (self.height + 1) // 2]
        self.update_react()

        self.win = win
        self.destroy = False

        self.time = 0
        self.time_step = random.uniform(0.15, 0.2)
        self.spos = [self.pos[0], self.pos[1]]

        # Xác định góc bắn ban đầu của trái cây
        if self.pos[0] > (xWin // 2):
            self.s_angle = random.uniform(math.pi / 2, math.pi / 2 + math.pi / 18)
        else:
            self.s_angle = random.uniform(4 * math.pi / 9, math.pi / 2)

        self.speed = random.randint(int(0.14 * yWin), int(0.16 * yWin))
        self.svelx = self.speed * math.cos(self.s_angle)
        self.svely = -self.speed * math.sin(self.s_angle)

        self.time_limit = (-self.svely + math.sqrt(self.svely ** 2 + 16 * self.spos[1])) / 8
        self.angle = 0
        if self.svelx > 0:
            self.angle_speed = -5
        else:
            self.angle_speed = 5

    def stop(self, angle=0):
        self.spos = [self.pos[0], self.pos[1]]
        self.time = 0
        self.s_angle = angle
        self.angle_speed = 1

    def change_image(self, name):
        self.image = pygame.image.load(img_path + name + '.png')

    def change_xspeed(self, speed):
        self.svelx = speed

    def change_yspeed(self, speed):
        self.svely = speed

    def change_rot_speed(self, speed):
        self.angle_speed = speed

    def rotate(self, angle):
        self.angle = angle

    def update_react(self):
        self.rect.top = self.pos[1]
        self.rect.bottom = self.pos[1] + self.height
        self.rect.left = self.pos[0]
        self.rect.right = self.pos[0] + self.width

    def draw(self):
        rotatedSurf = pygame.transform.rotate(self.image, self.angle)  # Xoay hình ảnh trái cây theo góc hiện tại
        rotFruit = rotatedSurf.get_rect()
        rotFruit.center = tuple(self.pos)
        self.win.blit(rotatedSurf, rotFruit)  # Vẽ trái cây lên cửa sổ game

    def physic(self):
        gravity = 5

        # Cập nhật vị trí của trái cây dựa vào vật lý
        if (self.time <= self.time_limit):
            self.time += self.time_step
            self.pos[0] = self.spos[0] + self.svelx * (self.time)
            self.pos[1] = self.spos[1] + self.svely * (self.time) + (gravity * (self.time ** 2))
        else:
            self.destroy = True

    def update(self):
        self.angle = (self.angle + self.angle_speed) % 360
        self.physic()
        self.update_react()
        self.draw()

    def copy(self):
        newfr = fruit(self.name, self.win, self.cut)
        newfr.pos = self.pos
        newfr.update_react()

        newfr.time = self.time
        newfr.time_step = self.time_step
        newfr.spos = self.spos

        newfr.s_angle = self.s_angle

        newfr.speed = self.speed
        newfr.svelx = self.svelx
        newfr.svely = self.svely
        newfr.angle = self.angle
        return newfr

def draw_score():
    score_text = font.render("Score: " + str(score), True, (255, 255, 255))
    win.blit(score_text, (10, 10))  # Vẽ điểm số lên góc trên bên trái của cửa sổ game

def draw_miss(fallen_fruits):
    score_text = font.render("X: " + str(fallen_fruits), True, (255, 0, 0))
    win.blit(score_text, (500, 10))  # Vẽ điểm số lên góc trên bên trái của cửa sổ game

def draw_game_over():
    over_text = font.render("Game Over! Click to Retry or Quit", True, (255, 0, 0))
    win.blit(over_text, (xWin // 2 - over_text.get_width() // 2, yWin // 2 - over_text.get_height() // 2))

def collision_handler(knf, frt):
    # Tạo hai đối tượng trái cây mới đại diện cho hai nửa trái cây sau khi bị cắt
    top_fruit = frt.copy()
    bot_fruit = frt.copy()

    print(frt)

    # Cập nhật thuộc tính cho nửa trên của trái cây
    top_fruit.cut = True
    top_fruit.change_image(top_fruit.name + '-2')
    top_fruit.svely = -0.3 * fps / 20 * abs(top_fruit.svely)

    # Cập nhật thuộc tính cho nửa dưới của trái cây
    bot_fruit.cut = True
    bot_fruit.change_image(bot_fruit.name + '-1')
    bot_fruit.svely = -0.3 * fps / 20 * abs(bot_fruit.svely)

    # Xác định góc phân tách dựa trên hướng di chuyển của dao
    shoot_angle = math.pi / 6
    if (frt.angle >= (2 * math.pi - math.pi / 2) and frt.angle <= math.pi / 2):
        top_fruit.stop(shoot_angle)
        top_fruit.rotate(2 * math.pi - math.pi / 2)
        bot_fruit.stop(math.pi - shoot_angle)
        bot_fruit.rotate(math.pi / 2)
        top_fruit.svelx = -abs((0.08 * yWin) * math.cos(shoot_angle))
        bot_fruit.svelx = abs((0.08 * yWin) * math.cos(shoot_angle))
    else:
        top_fruit.stop(math.pi - math.pi / 18)
        top_fruit.rotate(2 * math.pi - math.pi / 2)
        bot_fruit.stop(math.pi / 18)
        bot_fruit.rotate(math.pi / 2)
        top_fruit.svelx = abs((0.08 * yWin) * math.cos(math.pi / 18))
        bot_fruit.svelx = -abs((0.08 * yWin) * math.cos(math.pi / 18))
    global score
    score += 1  # Tăng điểm số khi chém trái cây
    draw_score()  # Vẽ lại điểm số mới
    return top_fruit, bot_fruit


def clip_line(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    def compute_region_code(x, y):
        code = 0
        if x < xmin:
            code |= 1
        elif x > xmax:
            code |= 2
        if y < ymin:
            code |= 4
        elif y > ymax:
            code |= 8
        return code

    code1 = compute_region_code(x1, y1)
    code2 = compute_region_code(x2, y2)
    print(code1, code2)

    if code1 == 0 and code2 == 0:
        return x1, y1, x2, y2

    if code1 & code2 != 0:
        return None

    while True:
        if code1 == 0 and code2 == 0:
            return x1, y1, x2, y2

        if code1 & code2 != 0:
            return None

        code_out = code1 if code1 != 0 else code2

        if code_out & 1:
            x = xmin
            y = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
        elif code_out & 2:
            x = xmax
            y = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
        elif code_out & 4:
            y = ymin
            x = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
        elif code_out & 8:
            y = ymax
            x = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)

        if code_out == code1:
            x1, y1 = x, y
            code1 = compute_region_code(x1, y1)
        else:
            x2, y2 = x, y
            code2 = compute_region_code(x2, y2)


def knife_fruit_collision(knf, frt):
    # Khung giới hạn của cửa sổ game
    xmin, ymin = 0, 0
    xmax, ymax = xWin, yWin

    # Tọa độ của dao
    x1, y1 = knf.rect.topleft
    x2, y2 = knf.rect.bottomright

    # Tọa độ của trái cây
    x3, y3 = frt.rect.topleft
    x4, y4 = frt.rect.bottomright

    # Cắt đoạn thẳng dao với khung hình chữ nhật
    result = clip_line(x1, y1, x2, y2, xmin, ymin, xmax, ymax)
    print(result)
    if result:
        x1, y1, x2, y2 = result
    else:
        return False

    # Cắt đoạn thẳng trái cây với khung hình chữ nhật
    result = clip_line(x3, y3, x4, y4, xmin, ymin, xmax, ymax)
    if result:
        x3, y3, x4, y4 = result
    else:
        return False

    # Kiểm tra va chạm
    return not (x2 < x3 or x4 < x1 or y2 < y3 or y4 < y1)

def game_over():
    win.fill((0, 0, 0))  # Xóa màn hình với màu đen
    font_large = pygame.font.SysFont(None, 48)
    game_over_text = font_large.render("Game Over", True, (255, 0, 0))
    win.blit(game_over_text, (xWin // 2 - game_over_text.get_width() // 2, yWin // 2 - game_over_text.get_height() // 2))

    # Tạo các nút "Retry" và "Quit"
    retry_text = font.render("Retry", True, (255, 255, 255))
    
    text_rect = retry_text.get_rect(center=(xWin // 2, yWin // 2 + 50))
    win.blit(retry_text, text_rect)

    quit_text = font.render("Quit", True, (255, 255, 255))
    quit_text_rect = quit_text.get_rect(center=(xWin // 2, yWin // 2 + 100))
    win.blit(quit_text, quit_text_rect)

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if text_rect.collidepoint(mouse_pos):  # Kiểm tra nếu người chơi bấm vào nút Retry
                    game_loop()
                elif quit_text_rect.collidepoint(mouse_pos):  # Kiểm tra nếu người chơi bấm vào nút Quit
                    pygame.quit()
                    sys.exit()

def game_loop():
    pygame.init()  # Khởi tạo các mô-đun của Pygame
    run = True
    win = pygame.display.set_mode(win_size)  # Tạo cửa sổ với kích thước đã định

    background = pygame.image.load(img_path + 'background.png')  # Tải hình nền
    knf = knife(win)  # Tạo đối tượng dao
    fruits = []

    global score  # Đảm bảo sử dụng biến toàn cục 'score'
    score = 0  # Reset score at the start of the game
    fallen_fruits = 0

    while True:
        num_fruits = random.randint(0, 4)
        for i in range(num_fruits + 1):
            option = random.randint(0, 5)
            fruits.append(fruit(fruit_list[option], win))  # Tạo các đối tượng trái cây ngẫu nhiên

        while fruits != [] and run:
            pygame.time.delay(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    knf.enable_cutting()  # Kích hoạt chế độ cắt khi nhấn chuột
                elif event.type == pygame.MOUSEBUTTONUP:
                    knf.disable_cutting()  # Vô hiệu hóa chế độ cắt khi nhả chuột

            win.blit(pygame.transform.scale(background, (xWin, yWin)), (0, 0))  # Vẽ hình nền lên cửa sổ
            knf.update()  # Cập nhật trạng thái và vẽ dao

            for fr in fruits:
                fr.update()  # Cập nhật trạng thái và vẽ trái cây
                if pygame.sprite.collide_rect(knf, fr) == True and knf.sharp() and not fr.cut:
                    if knife_fruit_collision(knf, fr):
                        top, bot = collision_handler(knf, fr)  # Xử lý va chạm, tạo hai nửa trái cây
                        fruits.append(top)
                        fruits.append(bot)
                        fruits.remove(fr)
                        knf.cut()  # Vẽ vết cắt

                if fr.destroy == True:
                    if not fr.cut == True:
                        fallen_fruits += 1  # Tăng số lượng trái cây đã rơi
                    fruits.remove(fr)  # Loại bỏ trái cây nếu đã bị phá hủy

                if fallen_fruits >= 3:
                    game_over()
                    break
                
                if run == False:
                    pygame.quit()
            
            draw_score()  # Vẽ điểm số lên cửa sổ game
            draw_miss(fallen_fruits)
            pygame.display.update()  # Cập nhật cửa sổ game
game_loop()