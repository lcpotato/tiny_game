import tkinter as tk
from tkinter import messagebox
import random
import time

class game_2048:
    def __init__(self, root):
        self.root = root
        self.root.title("2048")
        self.root.resizable(False, False)
        self.font = ('SimHei', 15, 'bold')
        self.small_font = ('SimHei', 10)

        self.GRID_SIZE = 45
        self.GRID_COUNT = 6
        self.CELL_SIZE = 70
        
        self.game_over = False
        self.victory = False
        self.start_time = None
        self.timer_id = None
        self.score = 0
        self.best_score = 0
        self.largestnum = 0
        
        self.create_widgets()
        self.reset_game()
        
    def create_widgets(self):
        # 创建游戏标题
        self.title_frame = tk.Frame(self.root, bg="#faf8ef")
        self.title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.title_label = tk.Label(self.title_frame, text="2048", font=('SimHei', 40, 'bold'), bg="#faf8ef", fg="#776e65")
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        # 创建分数区域
        self.score_frame = tk.Frame(self.title_frame, bg="#bbada0", padx=10, pady=5)
        self.score_frame.pack(side=tk.RIGHT)
        
        self.score_title = tk.Label(self.score_frame, text="分数", font=self.small_font, bg="#bbada0", fg="#eee4da")
        self.score_title.pack()
        
        self.score_value = tk.Label(self.score_frame, text="0", font=self.font, bg="#bbada0", fg="white")
        self.score_value.pack()
        
        # 创建最高分区域
        self.best_frame = tk.Frame(self.title_frame, bg="#bbada0", padx=10, pady=5)
        self.best_frame.pack(side=tk.RIGHT, padx=10)
        
        self.best_title = tk.Label(self.best_frame, text="最高分", font=self.small_font, bg="#bbada0", fg="#eee4da")
        self.best_title.pack()
        
        self.best_value = tk.Label(self.best_frame, text="0", font=self.font, bg="#bbada0", fg="white")
        self.best_value.pack()
        
        # 创建操作按钮
        self.control_frame = tk.Frame(self.root, bg="#faf8ef")
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.new_game_btn = tk.Button(self.control_frame, text="新游戏", font=self.font, bg="#8f7a66", fg="white", command=self.reset_game)
        self.new_game_btn.pack(side=tk.LEFT)
        
        # 创建时间显示
        self.time_frame = tk.Frame(self.control_frame, bg="#faf8ef")
        self.time_frame.pack(side=tk.RIGHT)
        
        self.time_label = tk.Label(self.time_frame, text="时间: 00:00", font=self.small_font, bg="#faf8ef")
        self.time_label.pack()
        
        # 创建游戏网格背景
        self.grid_bg = tk.Canvas(self.root, width=self.GRID_SIZE*self.GRID_COUNT, height=self.GRID_SIZE*self.GRID_COUNT, bg="#bbada0", highlightthickness=0)
        self.grid_bg.pack(padx=10, pady=10)
        
        # 创建单元格
        self.cells = []
        self.cell_labels = []
        for i in range(self.GRID_COUNT):
            row_cells = []
            row_labels = []
            for j in range(self.GRID_COUNT):
                x1 = j * self.GRID_SIZE
                y1 = i * self.GRID_SIZE
                x2 = x1 + self.GRID_SIZE
                y2 = y1 + self.GRID_SIZE
                
                # 创建单元格背景
                cell_id = self.grid_bg.create_rectangle(x1, y1, x2, y2, fill="#cdc1b4", outline="")
                row_cells.append(cell_id)
                
                # 创建单元格标签
                label_id = self.grid_bg.create_text(x1 + self.GRID_SIZE/2, y1 + self.GRID_SIZE/2, text="", font=self.font)
                row_labels.append(label_id)
                
            self.cells.append(row_cells)
            self.cell_labels.append(row_labels)
            
        # 绑定键盘事件
        self.root.bind("<Key>", self.key_press)
        
    def reset_game(self):
        # 重置游戏状态
        self.game_over = False
        self.victory = False
        self.score = 0
        self.score_value.config(text="0")
        self.largestnum = 0
        
        # 初始化游戏网格
        self.grid = [[0 for _ in range(self.GRID_COUNT)] for _ in range(self.GRID_COUNT)]
        
        # 随机生成两个初始数字
        self.add_new_tile()
        self.add_new_tile()
        
        # 更新显示
        self.update_grid_cells()
        
        # 重置计时器
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.start_time = time.time()
        self.update_timer()
        
    def add_new_tile(self):
        # 查找所有空单元格
        empty_cells = []
        for i in range(self.GRID_COUNT):
            for j in range(self.GRID_COUNT):
                if self.grid[i][j] == 0:
                    empty_cells.append((i, j))
        
        if empty_cells:
            i, j = random.choice(empty_cells)
            
            # 根据当前最大数字决定新方块的概率分布
            rand = random.random()
            
            if self.largestnum >= 256:
                if rand < 0.2:
                    value = 32
                elif rand < 0.3:
                    value = 16
                elif rand < 0.35:
                    value = 128
                elif rand < 0.4:
                    value = 2
                else:
                    # 剩下的概率均等分配给4和8
                    value = 4 if random.random() < 0.5 else 8
                    
            elif self.largestnum >= 32:
                if rand < 0.05:
                    value = 32
                elif rand < 0.15:
                    value = 16
                elif rand < 0.25:
                    value = 8
                elif rand < 0.3:
                    value = 2
                else:
                    value = 4
                    
            elif self.largestnum >= 8:
                if rand < 0.1:
                    value = 8
                elif rand < 0.3:
                    value = 4
                else:
                    value = 2
            else:
                # 默认情况：90%概率生成2，10%概率生成4
                value = 2 if rand < 0.9 else 4
            
            self.grid[i][j] = value
    
    def update_grid_cells(self):
        # 定义不同数字的颜色
        colors = {
            0: "#cdc1b4",
            2: "#eee4da",
            4: "#ede0c8",
            8: "#f2b179",
            16: "#f59563",
            32: "#f67c5f",
            64: "#f65e3b",
            128: "#edcf72",
            256: "#edcc61",
            512: "#edc850",
            1024: "#edc53f",
            2048: "#edc22e",
            4096: "#3c3a32",
            8192: "#3c3a32"
        }
        
        # 更新每个单元格的颜色和数字
        for i in range(self.GRID_COUNT):
            for j in range(self.GRID_COUNT):
                value = self.grid[i][j]
                # 更新单元格背景颜色
                self.grid_bg.itemconfig(self.cells[i][j], fill=colors.get(value, "#3c3a32"))
                
                # 更新单元格文本
                text = "" if value == 0 else str(value)
                self.grid_bg.itemconfig(self.cell_labels[i][j], text=text, fill="#776e65" if value <= 4 else "white")
                
       
            
    def key_press(self, event):
        if self.game_over or self.victory:
            # 胜利/结束后仅响应"新游戏"按钮，键盘操作失效（按回车键可重新开始）
            if event.keysym == 'Return':
                self.reset_game()
            return
            
        key = event.keysym
        
        # 记录移动前的网格状态
        old_grid = [row[:] for row in self.grid]
        
        # 根据按键方向移动网格
        move_functions = {
            'Up': self.move_up,
            'Down': self.move_down,
            'Left': self.move_left,
            'Right': self.move_right
        }
        
        if key in move_functions:
            move_functions[key]()
        else:
            return
            
        # 如果移动后网格发生变化，添加新数字并更新显示
        if old_grid != self.grid:
            # 更新最大数字
            self.largestnum = max(max(row) for row in self.grid)
            self.add_new_tile()
            self.update_grid_cells()
            self.check_game_state()
            
    def move(self, get_cells):
        """通用移动方法，get_cells是一个函数，用于获取需要处理的行或列"""
        for cells in get_cells():
            # 合并相同数字
            for k in range(1, len(cells)):
                i, j = cells[k]
                if self.grid[i][j] != 0:
                    # 移动直到遇到非空单元格或边界
                    pos = k
                    while pos > 0:
                        prev_i, prev_j = cells[pos-1]
                        if self.grid[prev_i][prev_j] == 0:
                            # 移动
                            self.grid[prev_i][prev_j] = self.grid[i][j]
                            self.grid[i][j] = 0
                            i, j = prev_i, prev_j
                            pos -= 1
                        else:
                            break
                    
                    # 检查是否可以合并
                    if pos > 0:
                        prev_i, prev_j = cells[pos-1]
                        if self.grid[prev_i][prev_j] == self.grid[i][j]:
                            self.grid[prev_i][prev_j] *= 2
                            self.score += self.grid[prev_i][prev_j]
                            self.grid[i][j] = 0
                            self.score_value.config(text=str(self.score))
                            if self.score > self.best_score:
                                self.best_score = self.score
                                self.best_value.config(text=str(self.best_score))
    
    def move_up(self):
        def get_cells():
            return [
                [(i, j) for i in range(self.GRID_COUNT)]
                for j in range(self.GRID_COUNT)
            ]
        self.move(get_cells)
    
    def move_down(self):
        def get_cells():
            return [
                [(i, j) for i in range(self.GRID_COUNT-1, -1, -1)]
                for j in range(self.GRID_COUNT)
            ]
        self.move(get_cells)
    
    def move_left(self):
        def get_cells():
            return [
                [(i, j) for j in range(self.GRID_COUNT)]
                for i in range(self.GRID_COUNT)
            ]
        self.move(get_cells)
    
    def move_right(self):
        def get_cells():
            return [
                [(i, j) for j in range(self.GRID_COUNT-1, -1, -1)]
                for i in range(self.GRID_COUNT)
            ]
        self.move(get_cells)
    
    def check_game_state(self):
        # 检查是否获胜
        for i in range(self.GRID_COUNT):
            for j in range(self.GRID_COUNT):
                if self.grid[i][j] >= 2048:
                    self.victory = True
                    # 显示胜利弹窗
                    messagebox.showinfo("恭喜！", "你成功合成了2048！")
                    return
        
        # 检查是否还有空格子
        for i in range(self.GRID_COUNT):
            for j in range(self.GRID_COUNT):
                if self.grid[i][j] == 0:
                    return
        
        # 检查是否还能移动
        for i in range(self.GRID_COUNT):
            for j in range(self.GRID_COUNT-1):
                if self.grid[i][j] == self.grid[i][j+1]:
                    return
        
        for j in range(self.GRID_COUNT):
            for i in range(self.GRID_COUNT-1):
                if self.grid[i][j] == self.grid[i+1][j]:
                    return
        
        # 如果都不满足，游戏结束
        self.game_over = True
        messagebox.showinfo("游戏结束", "没有可移动的格子了！")
    
    def update_timer(self):
        if not self.game_over and not self.victory:
            elapsed_time = time.time() - self.start_time
            minutes, seconds = divmod(int(elapsed_time), 60)
            self.time_label.config(text=f"时间: {minutes:02d}:{seconds:02d}")
            self.timer_id = self.root.after(1000, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    game = game_2048(root)
    root.mainloop()
