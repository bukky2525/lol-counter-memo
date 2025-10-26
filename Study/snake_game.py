'''import pygame
import random
import numpy as np
import pickle  # Q-tableの保存と読み込みに使用

pygame.init()

# ゲームの設定
width = 800
height = 600
snake_block = 20
snake_speed = 15

# 色の定義
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

# ゲーム画面の設定
dis = pygame.display.set_mode((width, height))
pygame.display.set_caption('Snake Game')

# フォントの設定
font_style = pygame.font.SysFont("arial", 30)
score_font = pygame.font.SysFont("arial", 40)

# Q-learningの設定
action_size = 4
learning_rate = 0.1
discount_factor = 0.9
epsilon = 1.0
min_epsilon = 0.01
epsilon_decay = 0.995
q_table = {}

# Q-tableの保存と読み込み
q_table_file = "q_table.pkl"

def load_q_table():
    global q_table
    try:
        with open(q_table_file, "rb") as f:
            q_table = pickle.load(f)
    except FileNotFoundError:
        q_table = {}

def save_q_table():
    with open(q_table_file, "wb") as f:
        pickle.dump(q_table, f)

# Q値を取得する関数
def get_q_value(state, action):
    state_action = (state, action)
    if state_action not in q_table:
        q_table[state_action] = 0.0
    return q_table[state_action]

# Q値を更新する関数
def update_q_value(state, action, value):
    state_action = (state, action)
    q_table[state_action] = value

# 状態を取得する関数
def get_state(snake, foodx, foody):
    head_x, head_y = snake[0]
    return (head_x, head_y, foodx, foody)

# 行動選択関数
def choose_action(state):
    if random.uniform(0, 1) < epsilon:
        return random.randint(0, action_size - 1)
    else:
        q_values = [get_q_value(state, a) for a in range(action_size)]
        return np.argmax(q_values)

# 蛇を描画する関数
def our_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(dis, green, [x[0], x[1], snake_block, snake_block])

# スコアを表示する関数
def display_score(score):
    value = score_font.render(f"Score: {score}", True, white)
    dis.blit(value, [0, 0])

def gameLoop():
    global epsilon
    game_over = False

    load_q_table()  # Q-tableを読み込む

    while not game_over:
        game_close = False

        x1 = width / 2
        y1 = height / 2

        x1_change = 0
        y1_change = 0

        snake_list = []
        length_of_snake = 1

        # 初期状態で蛇の頭を追加
        snake_list.append([x1, y1])

        foodx = round(random.randrange(0, width - snake_block) / snake_block) * snake_block
        foody = round(random.randrange(0, height - snake_block) / snake_block) * snake_block

        clock = pygame.time.Clock()

        # 訪問した位置を追跡するための辞書
        visited_positions = {}
        max_visits = 3  # 同じ位置を訪れる最大回数

        while not game_close:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = True

            # snake_listが空でないことを確認
            if snake_list:
                state = get_state(snake_list, foodx, foody)
                action = choose_action(state)

                if action == 0:  # 上
                    x1_change = 0
                    y1_change = -snake_block
                elif action == 1:  # 下
                    x1_change = 0
                    y1_change = snake_block
                elif action == 2:  # 左
                    x1_change = -snake_block
                    y1_change = 0
                elif action == 3:  # 右
                    x1_change = snake_block
                    y1_change = 0

            if x1 >= width or x1 < 0 or y1 >= height or y1 < 0:
                game_close = True
            x1 += x1_change
            y1 += y1_change
            dis.fill(blue)
            pygame.draw.rect(dis, yellow, [foodx, foody, snake_block, snake_block])
            snake_head = [x1, y1]
            snake_list.append(snake_head)
            if len(snake_list) > length_of_snake:
                del snake_list[0]

            for x in snake_list[:-1]:
                if x == snake_head:
                    game_close = True

            our_snake(snake_block, snake_list)
            display_score(length_of_snake - 1)

            pygame.display.update()

            # 現在の位置を追跡
            current_position = (x1, y1)
            if current_position in visited_positions:
                visited_positions[current_position] += 1
            else:
                visited_positions[current_position] = 1

            # 同じ位置を一定回数以上訪れた場合、報酬を加算しない
            if visited_positions[current_position] > max_visits:
                reward = 0
            else:
                reward = 0
                if x1 == foodx and y1 == foody:
                    foodx = round(random.randrange(0, width - snake_block) / snake_block) * snake_block
                    foody = round(random.randrange(0, height - snake_block) / snake_block) * snake_block
                    length_of_snake += 1
                    reward = 20  # 餌を取ったときの報酬を増加

                # 餌に近づくときの報酬を追加
                current_distance = np.sqrt((x1 - foodx)**2 + (y1 - foody)**2)
                prev_distance = np.sqrt((x1 - x1_change - foodx)**2 + (y1 - y1_change - foody)**2)
                if current_distance < prev_distance:
                    reward += 5  # 餌に近づいたときの報酬

            next_state = get_state(snake_list, foodx, foody)
            current_q = get_q_value(state, action)
            next_q_values = [get_q_value(next_state, a) for a in range(action_size)]
            max_next_q = max(next_q_values)
            new_q = current_q + learning_rate * (reward + discount_factor * max_next_q - current_q)
            update_q_value(state, action, new_q)

            # 蛇が一定距離離れた場合、訪問履歴をリセット
            if current_distance > snake_block * 5:
                visited_positions.clear()

            if epsilon > min_epsilon:
                epsilon *= epsilon_decay

            clock.tick(snake_speed)

    save_q_table()  # Q-tableを保存する
    pygame.quit()
    quit()

if __name__ == "__main__":
    gameLoop()
'''