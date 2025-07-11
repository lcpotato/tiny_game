import tkinter as tk
from tkinter import messagebox
import random

class Minesweeper:
    def __init__(self, root):
        self.root = root
        self.root.title("扫雷")
        self.root.resizable(False, False)
        
        # 确保中文显示正常
        self.font = ('SimHei', 15, 'bold')
        
        # 游戏常量
        self.GRID_SIZE = 30
        self.GRID_COUNT = 15
        self.MINE_COUNT = 40
        
        # 游戏变量
        self.first_click = True
        self.game_over = False
        self.victory = False
        self.flags_used = 0
        
        # 创建界面
        self.create_widgets()
        self.reset_game()
    
    def create_widgets(self):
        """创建游戏界面组件"""
        # 顶部信息栏
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 剩余地雷数显示
        self.mines_label = tk.Label(self.top_frame, text=f"剩余地雷: {self.MINE_COUNT}", font=self.font)
        self.mines_label.pack(side=tk.LEFT)
        


        ###----------------


        # 时间显示
        #self.time_counter = tk.Label(self.top_frame, text=f"时间: 00：00", font=self.font)                          #####时间模块
        #self.time_counter.pack(side=tk.RIGHT,padx=(0, 10))

        ###-------------------------


        # 重置按钮
        self.reset_button = tk.Button(self.top_frame, text="重置", font=self.font, command=self.reset_game)
        self.reset_button.pack(side=tk.RIGHT,padx=(0, 80))
        
        # 游戏区域
        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(padx=10, pady=10)
        
        # 创建网格按钮
        self.buttons = []
        for y in range(self.GRID_COUNT):
            row = []
            for x in range(self.GRID_COUNT):
                btn = tk.Button(
                    self.game_frame, 
                    #text="⬜",
                    width=2, 
                    height=1, 
                    font=self.font,
                    relief=tk.RAISED
                )
                btn.grid(row=y, column=x, padx=1, pady=1)
                btn.bind('<Button-1>', lambda event, x=x, y=y: self.on_left_click(x, y))
                btn.bind('<Button-3>', lambda event, x=x, y=y: self.on_right_click(x, y))
                btn.bind('<Enter>', lambda e, b=btn: b.config(bg='lightblue'))
                btn.bind('<Leave>', lambda e, b=btn: b.config(bg='SystemButtonFace'))
                row.append(btn)
            self.buttons.append(row)
    
    def reset_game(self):
        """重置游戏状态"""
        self.first_click = True
        self.game_over = False
        self.victory = False
        self.flags_used = 0
        
        # 更新剩余地雷数
        self.mines_label.config(text=f"剩余地雷: {self.MINE_COUNT}")
        
        # 创建空白网格
        self.grid = [[0 for _ in range(self.GRID_COUNT)] for _ in range(self.GRID_COUNT)]
        self.revealed = [[False for _ in range(self.GRID_COUNT)] for _ in range(self.GRID_COUNT)]
        self.flagged = [[False for _ in range(self.GRID_COUNT)] for _ in range(self.GRID_COUNT)]
        
        # 重置按钮外观
        for y in range(self.GRID_COUNT):
            for x in range(self.GRID_COUNT):
                self.buttons[y][x].config(
                    text="", 
                    bg="SystemButtonFace", 
                    relief=tk.RAISED,
                    state=tk.NORMAL
                )
    
    def generate_mines(self, exclude_x, exclude_y):
        
        # 计算3x3区域边界
        min_x = max(0, exclude_x - 1)
        max_x = min(self.GRID_COUNT - 1, exclude_x + 1)
        min_y = max(0, exclude_y - 1)
        max_y = min(self.GRID_COUNT - 1, exclude_y + 1)
        
        # 初始化候选空格列表（周围8个方向无地雷的格子）
        safe_candidates = []
        
        # 收集所有可能的位置（排除3x3区域）
        possible_cells = []
        
        for x in range(self.GRID_COUNT):
            for y in range(self.GRID_COUNT):
                # 排除3x3区域内的格子
                if min_x <= x <= max_x and min_y <= y <= max_y:
                    continue
                    
                possible_cells.append((x, y))
        
        # 找出3x3区域内可以作为空格的候选位置
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                # 检查周围8个方向是否都在3x3区域外
                is_safe = True
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                            
                        nx, ny = x + dx, y + dy
                        # 如果周围格子不在3x3区域内，标记为不安全
                        if not (min_x <= nx <= max_x and min_y <= ny <= max_y):
                            is_safe = False
                            break
                    if not is_safe:
                        break
                        
                if is_safe:
                    safe_candidates.append((x, y))
        
        # 确保候选空格包含点击位置本身
        if (exclude_x, exclude_y) not in safe_candidates:
            safe_candidates.append((exclude_x, exclude_y))
        
        # 从候选空格中选择至少3个（包括点击位置）
        if len(safe_candidates) >= 3:
            safe_spots = random.sample(safe_candidates, 3)
            # 确保点击位置在选择中
            if (exclude_x, exclude_y) not in safe_spots:
                safe_spots[0] = (exclude_x, exclude_y)
        else:
            # 如果候选不足，添加点击位置并补充其他位置
            safe_spots = [(exclude_x, exclude_y)]
            # 补充其他位置（按距离排序）
            remaining = [
                (x, y) for x in range(min_x, max_x + 1)
                for y in range(min_y, max_y + 1)
                if (x, y) != (exclude_x, exclude_y)
            ]
            # 按距离排序
            remaining.sort(key=lambda p: (p[0] - exclude_x)**2 + (p[1] - exclude_y)**2)
            safe_spots.extend(remaining[:2])  # 取最近的两个
        
        # 计算3x3区域内需要填充的地雷数
        mines_in_3x3_area = min(
            3,  # 限制3x3区域内最多3个地雷，确保有足够空格
            len([(x, y) for x in range(min_x, max_x + 1) 
                for y in range(min_y, max_y + 1) 
                if (x, y) not in safe_spots])
        )
        
        # 选择3x3区域内的地雷位置（排除安全空格）
        possible_mines_in_3x3 = [
            (x, y) for x in range(min_x, max_x + 1)
            for y in range(min_y, max_y + 1)
            if (x, y) not in safe_spots
        ]
        
        mines_in_3x3 = []
        if possible_mines_in_3x3 and mines_in_3x3_area > 0:
            mines_in_3x3 = random.sample(possible_mines_in_3x3, mines_in_3x3_area)
        
        # 计算还需要放置的地雷数
        remaining_mines = self.MINE_COUNT - len(mines_in_3x3)
        
        # 随机选择3x3区域外的地雷位置
        outside_mines = random.sample(possible_cells, remaining_mines)
        
        # 设置地雷
        mine_positions = mines_in_3x3 + outside_mines
        
        # 确保所有安全空格周围8个方向无地雷
        for x, y in safe_spots:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                        
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.GRID_COUNT and 0 <= ny < self.GRID_COUNT:
                        if (nx, ny) in mine_positions:
                            mine_positions.remove((nx, ny))
        
        # 最终设置所有地雷位置
        for x, y in mine_positions:
            self.grid[x][y] = -1
        
        # 计算每个格子周围的地雷数
        self.calculate_neighbor_mines()
        
    
    def calculate_neighbor_mines(self):
        """计算每个格子周围的地雷数"""
        for x in range(self.GRID_COUNT):
            for y in range(self.GRID_COUNT):
                if self.grid[x][y] == -1:
                    continue
                
                count = 0
                # 检查周围的8个方向
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.GRID_COUNT and 0 <= ny < self.GRID_COUNT:
                            if self.grid[nx][ny] == -1:
                                count += 1
                
                self.grid[x][y] = count
    
    def reveal_cell(self, x, y, is_first_click=False):
        """翻开格子"""
        # 如果已经翻开或标记，不做处理
        if self.revealed[x][y] or self.flagged[x][y]:
            return
        
        # 翻开格子
        self.revealed[x][y] = True
        
        # 如果是地雷，游戏结束
        if self.grid[x][y] == -1:
            self.game_over = True
            self.show_all_mines()
            messagebox.showinfo("游戏结束", "你踩到地雷了!")
            return
        
        # 更新按钮外观
        if self.grid[x][y] == 0:
            self.buttons[y][x].config(
                text="", 
                bg="lightgray", 
                relief=tk.SUNKEN,
                state=tk.DISABLED
            )
            
            # 如果是第一次点击，自动翻开周围的空格子
            if is_first_click:
                # 计算3x3区域
                min_x = max(0, x - 1)
                max_x = min(self.GRID_COUNT - 1, x + 1)
                min_y = max(0, y - 1)
                max_y = min(self.GRID_COUNT - 1, y + 1)
                
                # 翻开3x3区域内的所有格子
                for nx in range(min_x, max_x + 1):
                    for ny in range(min_y, max_y + 1):
                        self.reveal_cell(nx, ny)
            else:
                # 递归翻开周围的空格子
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.GRID_COUNT and 0 <= ny < self.GRID_COUNT:
                            self.reveal_cell(nx, ny)

        else:
            # 根据数字设置不同颜色
            colors = ["black", "blue", "green", "red", 
                     "purple", "maroon", "cyan", "navy"]
            self.buttons[y][x].config(
                text=str(self.grid[x][y]), 
                fg=colors[self.grid[x][y] - 1],
                bg="lightgray", 
                relief=tk.SUNKEN,
                state=tk.DISABLED
            )
        
        # 检查是否胜利
        self.check_victory()
    
    def toggle_flag(self, x, y):
        """切换标记状态"""
        # 如果已经翻开，不做处理
        if self.revealed[x][y]:
            return
        
        # 切换标记状态
        self.flagged[x][y] = not self.flagged[x][y]
        
        if self.flagged[x][y]:
            self.buttons[y][x].config(text="🚩", bg="yellow")
            self.flags_used += 1
        else:
            self.buttons[y][x].config(text="", bg="SystemButtonFace")
            self.flags_used -= 1
        
        # 更新剩余地雷数
        self.mines_label.config(text=f"剩余地雷: {self.MINE_COUNT - self.flags_used}")
        
        # 检查是否胜利
        self.check_victory()
    
    def show_all_mines(self):
        """显示所有地雷"""
        for x in range(self.GRID_COUNT):
            for y in range(self.GRID_COUNT):
                if self.grid[x][y] == -1:
                    self.buttons[y][x].config(text="💣", bg="red")
    
    def check_victory(self):
        """检查是否胜利"""
        for x in range(self.GRID_COUNT):
            for y in range(self.GRID_COUNT):
                # 如果有未翻开的非地雷格子，游戏未胜利
                if not self.revealed[x][y] and self.grid[x][y] != -1:
                    return False
                # 如果有标记错误的格子，游戏未胜利
                if self.flagged[x][y] and self.grid[x][y] != -1:
                    return False
        
        # 所有非地雷格子都已翻开，游戏胜利
        self.victory = True
        self.show_all_mines()
        messagebox.showinfo("恭喜", "你赢了!")
        return True
    
    def on_left_click(self, x, y):
        """处理左键点击"""
        if self.game_over or self.victory:
            return
        
        # 第一次点击不会踩到地雷
        if self.first_click:
            self.first_click = False
            self.generate_mines(x, y)
            # 第一次点击时传入特殊标记
            self.reveal_cell(x, y, True)
        else:
            self.reveal_cell(x, y)
    
    def on_right_click(self, x, y):
        """处理右键点击"""
        if self.game_over or self.victory:
            return
        
        self.toggle_flag(x, y)

if __name__ == "__main__":
    root = tk.Tk()
    game = Minesweeper(root)
    root.mainloop()    