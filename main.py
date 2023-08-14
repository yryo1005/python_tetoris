# ライブラリのインポート
import pygame
import sys
import copy
import random

# pygameの初期化
pygame.init()

# フレームレート
frame_rate = 30

# ウィンドウの設定. 縦:横=1:2になるように設定する
# ウィンドウの横幅
SCREEN_WIDTH = 300
# ウィンドウの縦幅
SCREEN_HEIGHT = 600

# グリッド数の設定. 縦:横=1:2になるように設定する
# 水平方向のグリッド数
NUM_HORIZONTAL_GRID = 10
# 垂直方向のグリッド数
NUM_VERTICAL_GRID = 20

# グリッドサイズ
# 水平方向のグリッドの大きさ
HORIZONTAL_GRID_SIZE = SCREEN_WIDTH // NUM_HORIZONTAL_GRID
# 垂直方向のグリッドの大きさ
VERTICAL_GRID_SIZE = SCREEN_HEIGHT // NUM_VERTICAL_GRID

# ゲーム画面の状態を格納する配列
STATE = [[0] * NUM_HORIZONTAL_GRID for _ in range(NUM_VERTICAL_GRID)]

# スクリーンを定義
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# カラーマップの作成
c_map = {"black" : (0, 0, 0),
         "white" : (255, 255, 255),
         "red" : (255, 0, 0),
         "green" : (0, 255, 0),
         "blue" : (0, 0, 255)}

# グリッド線を描画する関数
def draw_grid():
    # 垂直方向の線を描画
    for X in range(0, SCREEN_WIDTH, HORIZONTAL_GRID_SIZE):
        pygame.draw.line(screen, c_map["white"], (X, 0), (X, SCREEN_HEIGHT))
    # 水平方向の線を描画
    for Y in range(0, SCREEN_HEIGHT, VERTICAL_GRID_SIZE):
        pygame.draw.line(screen, c_map["white"], (0, Y), (SCREEN_WIDTH, Y))

# テトロミノを描画する関数
def draw_tetoromino(STATE):
    for Y in range(NUM_VERTICAL_GRID):
        for X in range(NUM_HORIZONTAL_GRID):
            
            if STATE[Y][X] == 0: continue
            # キューブを定義
            cube = pygame.Rect(X * HORIZONTAL_GRID_SIZE, Y * VERTICAL_GRID_SIZE,
                               HORIZONTAL_GRID_SIZE, VERTICAL_GRID_SIZE)
            # キューブを描画
            pygame.draw.rect(screen, c_map["red"], cube)

# テトロミノを状態に反映する関数
def update_state(STATE, t):
    for Y in range(t.height):
        for X in range(t.width):
            if t.shape[Y][X] == 0: continue

            STATE[t.y + Y][t.x + X] = 1

# テトロミノが横一列揃っていれば消す関数
def delete_column(STATE):
    i = NUM_VERTICAL_GRID - 1
    while i >= 0:
        flag = True
        for X in range(NUM_HORIZONTAL_GRID):
            if STATE[i][X] == 0:
                flag = False
                break
        
        if not flag:
            i -= 1
            continue

        # １行丸ごと消す
        if flag:
            for X in range(NUM_HORIZONTAL_GRID):
                STATE[i][X] = 0
        
        # その行より上の行を一つ下にずらす
        for Y in range(i, 0, -1):
            for X in range(NUM_HORIZONTAL_GRID):
                if Y == 0:
                    STATE[Y][X] = 0
                else:
                    STATE[Y][X] = STATE[Y - 1][X]

shapes = [
    [[1, 1], [1, 1]],
    [[0, 1], [1, 1]],
    [[1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[1], [1], [1], [1]]
]

class Tetromino:
    def __init__(self):
        # 規定の形からテトロミノの形をランダムに選択
        self.shape = random.choice( shapes )
        # テトロミノの縦幅
        self.height = len(self.shape)
        # テトロミノの横幅
        self.width = len(self.shape[0])

        # テトロミノのy座標
        self.y = 0
        # テトロミノのx座標
        self.x = 0

        # 自由落下させるかのフラグ
        self.free_fall = True
    
    # 横方向に移動する関数
    def move_horizontal(self, STATE, move_right = True):
        
        move_flag = True

        # テトロミノの端がゲーム画面の端
        if move_right and self.x + self.width >= NUM_HORIZONTAL_GRID or \
            not move_right and self.x <= 0:
            move_flag = False
        
        # 各キューブが移動できるか確認
        else:
            for Y in range(self.height):
                for X in range(self.width):
                    if self.shape[Y][X] == 0: continue

                    if move_right and STATE[self.y + Y][self.x + X + 1] == 1 or \
                        not move_right and STATE[self.y + Y][self.x + X - 1] == 1:
                        move_flag = False
                        break
                
                if not move_flag: break
        
        # 移動
        if move_flag:
            if move_right:
                self.x += 1
            else:
                self.x -= 1
        
    # 縦方向に移動する関数
    def move_vartical(self, STATE):
        move_flag = True

        # テトロミノの下端がゲーム画面の下端であるか
        if self.y + self.height >= NUM_VERTICAL_GRID:
            move_flag = False
            # 自動落下しないようにする
            self.free_fall = False
        
        # 各キューブが移動できるか
        else:
            for Y in range(self.height):
                for X in range(self.width):
                    if self.shape[Y][X] == 0: continue

                    if STATE[self.y + Y + 1][self.x + X] == 1:
                        move_flag = False
                        self.free_fall = False
                
                if not move_flag: break
        
        # 移動
        if move_flag:
            self.y += 1
    
    def move(self, STATE, events):
        for E in events:
            # イベントがキー入力なら
            if E.type == pygame.KEYDOWN:
                # キー入力が上なら
                if E.key == pygame.K_UP:
                    self.rotate(STATE)

                # キー入力が下キーなら
                if E.key == pygame.K_DOWN:
                    self.move_vartical(STATE)
                
                # キー入力が右キーなら
                if E.key == pygame.K_RIGHT:
                    self.move_horizontal(STATE, move_right = True)
                
                # キー入力が左なら
                if E.key == pygame.K_LEFT:
                    self.move_horizontal(STATE, move_right = False)
    
    def fall(self, STATE):
        self.move_vartical(STATE)

        return self.free_fall

    def draw(self, STATE):
        for Y in range(self.height):
            for X in range(self.width):
                if self.shape[Y][X] == 0: continue

                STATE[self.y + Y][self.x + X] = 1
    
    # テトロミノを回転する関数
    def rotate(self, STATE):
        tmp_shape = list()
        for X in range(self.width - 1, -1, -1):
            tmp = list()
            for Y in range(self.height):
                tmp.append(self.shape[Y][X])
            tmp_shape.append(tmp)
        
        tmp_height = self.width
        tmp_width = self.height

        rotate_flag = True
        if self.y + tmp_height > NUM_VERTICAL_GRID or \
           self.x + tmp_width > NUM_HORIZONTAL_GRID:
            rotate_flag = False
        elif rotate_flag:
            for Y in range(tmp_height):
                for X in range(tmp_width):
                    if tmp_shape[Y][X] == 0: continue

                    if STATE[self.y + Y][self.x + X] == 1:
                        rotate_flag = False
                        break

                if not rotate_flag: break
        
        # 回転
        if rotate_flag:
            self.shape = tmp_shape
            self.height = tmp_height
            self.width = tmp_width

# テトロミノを生成
t = Tetromino()
# フレーム数を数える変数
flame_count = 0

# ゲームループ
while True:
    # 全てのイベントを取得する
    # イベント : キー入力やマウス入力
    events = pygame.event.get()

    for E in events:
        # イベントがキー入力なら
        if E.type == pygame.KEYDOWN:
            # キー入力がエスケープキーなら
            if E.key == pygame.K_ESCAPE:
                # 終了操作
                pygame.quit()
                sys.exit()

    # 状態をコピー
    tmp_STATE = copy.deepcopy(STATE)

    # テトロミノを操作
    t.move(tmp_STATE, events)

    # テトロミノを状態に反映
    t.draw(tmp_STATE)

    # ゲーム画面を黒で塗りつぶす
    screen.fill(c_map["black"])

    # キューブを書く
    draw_tetoromino(tmp_STATE)

    # グリッド線を書く
    draw_grid()

    # スクリーンを更新する
    pygame.display.update()
    # 遅延する
    pygame.time.delay(1000 // frame_rate)

    # テトロミノの高さを更新
    # 10フレームに1度自動落下する
    flag = True
    if not flame_count % 10:
        flag = t.fall(STATE)

    # テトロミノが縦方向に移動できなくなったら
    if not flag:
        # 状態を更新
        update_state(STATE, t)
        # 状態の横一列が揃っていたら削除
        delete_column(STATE)
        # 新しいテトロミノを生成
        t = Tetromino()

    # フレーム数を更新
    flame_count += 1