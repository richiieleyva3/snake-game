import random
from turtle import Turtle, Screen
import time
from typing import Literal

DEFAULT_CONTROLS = ()

class Snake:
    parts_size = 1
    parts_outline = 2
    screen_width: int = 650
    screen_height: int = 650
    gap: int = 12
    margin: int = 15
    score_value: int = 0

    def __init__(self,
                 length: int = 3,
                 screen_width: int = screen_width,
                 screen_height: int = screen_height,
                 gap: int = gap,
                 parts_size: int = parts_size,
                 parts_outline: int = parts_outline,
                 color_wall: str = "red",
                 use_random_color: bool = True,
                 use_only_one_color: str = "white",
                 controls: dict[str, Literal["Up", "Down", "Left", "Right"]] = None,
                 margin: int = margin,
                 score_value: int = score_value
                ):
        """
        Initialize the snake game.
        :param length: It's the initial length of the snake. It's 3 by default.
        :param screen_width: It's the width of the screen. It's 650 by default.
        :param screen_height: It's the height of the screen. It's 650 by default.
        :param gap: It's the gap between the snake parts. It's 12 by default.
        :param parts_size: It's the size of the snake parts. It's 1 by default.
        :param parts_outline: It's the outline of the snake parts. It's 2 by default.
        :param color_wall: It's the color of the walls. It's "red" by default.
        :param use_random_color: It's a boolean value. If it's True, the snake parts will have a random color. If it's False, the snake parts will have the same color that use_only_one_color. It's True by default.
        :param use_only_one_color: It's the color of the snake parts. It's "white" by default. It's used if you use_random_color by False.
        :param controls: It's a dictionary with the controls of the snake. It's None by default. If you don't want to use the default controls { "w": "Up", "s": "Down", "a": "Left", "d": "Right" }, you can set it up, but you need to use a dictionary with the controls of the snake. For example, { "i": "Up", "k": "Down", "j": "Left", "l": "Right" }.
        """
        self.running = True
        self.game_over = False
        self.margin = margin
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.initial_length = length
        self.length = length
        self.grid_size = ((screen_width - 30) / 20)
        self.grid = {}
        self.create_grid()
        self.head_cell = (0, 0)
        self.grid_positions = [(-i, 0) for i in range(self.length)]
        self.parts = []
        self.parts_size = parts_size
        self.parts_outline = parts_outline
        self.walls = {}
        self.screen = Screen()
        self.use_random_color = use_random_color
        self.use_only_one_color = use_only_one_color
        self.colors = ["red", "orange", "yellow", "green", "blue", "purple"]
        self.direction = "Right"
        self.score_value = score_value
        self.high_score = None
        with open("high_score.txt", "r") as file:
            content = file.read()
            if content != "":
                self.high_score = int(content)
        if self.high_score is None:
            self.high_score = 0
            with open("high_score.txt", "w") as file:
                file.write(str(self.high_score))
        self.gap = gap  # 12
        self.initial_positions = self.create_initial_positions()
        self.color_wall = color_wall
        self.can_move = True
        self.score: Score = Score(score=self.score_value, high_score=self.high_score)
        self.food: Food = Food(food_size=self.parts_size,
                               food_outline=self.parts_outline,
                               grid=self.grid)
        self.controls = { "w": "Up", "s": "Down", "a": "Left", "d": "Right" }
        if controls is not None:
            self.controls = controls
        self.screen.listen()
        for key_char, action_name in self.controls.items():
            self.screen.onkey(key=key_char, fun=lambda action=action_name: self.move_snake(action))
        self.create()
        self.head = self.parts[0]
        self.move = {
            "Up": 90,
            "Down": 270,
            "Left": 180,
            "Right": 0,
        }

    def create_grid(self):
        """
        Creates a self.grid dictionary where the keys are tuples (i, j)
        with i, j integers, and each value contains the actual pixel coordinates
        centered at (0,0), as well as flags for snake and food
        """
        cell = self.parts_size * 20
        half_w = self.screen_width / 2
        half_h = self.screen_height / 2

        cols = int(self.screen_width // cell)
        rows = int(self.screen_height // cell)
        half_cols = cols // 2
        half_rows = rows // 2

        self.grid = {}
        for j in range(-half_rows, half_rows + 1):
            for i in range(-half_cols, half_cols + 1):
                x = i * cell
                y = j * cell

                if abs(x) > half_w - self.margin or abs(y) > half_h - self.margin:
                    continue

                self.grid[(i, j)] = {
                    "x": x,
                    "y": y,
                    "snake": False,
                    "food": False
                }

    def create(self):
        """
        Create the game screen, the walls, the snake and the initial position of the snake parts
        :return:
        """
        self.screen.setup(width=self.screen_width, height=self.screen_height + 20)
        self.screen.bgcolor("black")
        self.screen.title("Snake Game")
        self.screen.tracer(0)
        self.create_walls()
        self.create_snake()
        self.parts[0].color("#e8e8e8")
        self.parts[0].pencolor("black")
        self.parts[0].pendown()

    def create_walls(self):
        """
        Create the walls of the game, the borders of the screen using the size of the screen (window_width and window_height = 650 by default) and color of the wall (color_wall = "red" by default)
        """
        x_adjust = 3
        y_adjust = 2 # 2
        wall_x_pos = (self.screen_width / 2) - self.margin
        wall_y_pos = (self.screen_height / 2) - self.margin
        #wall_y_pos = (self.screen.window_height() / 2) - self.margin
        for i in range(1, 5):
            wall = Turtle()
            wall.shape("square")
            wall.color("black")
            wall.penup()
            wall.shapesize(stretch_wid=0.1, stretch_len=31)
            if i == 1:
                # Left wall
                wall.goto(-wall_x_pos - x_adjust, y_adjust - 5)
                wall.right(90)
                self.walls["Left"] = wall
            elif i == 2:
                # Right wall
                wall.goto(wall_x_pos - x_adjust, y_adjust - 5)
                wall.right(90)
                self.walls["Right"] = wall
            elif i == 4:
                # Top wall
                wall.goto(-x_adjust, wall_y_pos + y_adjust - 5)
                wall.right(180)
                self.walls["Top"] = wall
            elif i == 3:
                # Bottom wall
                wall.goto(-x_adjust, -wall_y_pos + y_adjust - 5)
                wall.right(180)
                self.walls["Bottom"] = wall
            #self.walls.append(wall)
            #self.walls[i] = wall
        for key, wall in self.walls.items():
            wall.color(self.color_wall)

    def create_initial_positions(self):
        """
        Create the initial positions of the snake parts using the length of the snake, the gap between parts and the size of the parts
        """
        x = 0
        y = 0
        positions = {0: {"x": 0, "y": 0}}
        for i in range(0, self.length):
            x = x - self.gap
            positions[i] = {"x": x * self.parts_size * 2, "y": y}
        return positions

    def create_snake(self):
        """
        Create the snake body using the initial positions and the length of the snake
        """
        # for i in range(self.length):
        #     self.create_new_part(i)
        self.parts = []
        for cell in self.grid_positions:
            self.create_new_part(cell)

    def move_snake(self, key: str):
        """
        Permits the snake to move in the direction indicated by the key.
        Change a direction if it's not opposite the current direction and if we haven't already turned in this frame.
        :param key: Set up a key to do one of these moves "Up", "Down", "Left" or "Right"
        """
        if not self.can_move:
            return
        if key not in self.controls.values():
            return

        self.can_move = False

        for i in range(len(self.parts) - 1, 0, -1):
            x = self.parts[i - 1].xcor()
            y = self.parts[i - 1].ycor()
            self.parts[i].goto(x, y)
        if key == "Up" and self.direction != "Down":
            self.head.setheading(self.move["Up"])
            self.direction = "Up"
        elif key == "Down" and self.direction != "Up":
            self.head.setheading(self.move["Down"])
            self.direction = "Down"
        elif key == "Left" and self.direction != "Right":
            self.head.setheading(self.move["Left"])
            self.direction = "Left"
        elif key == "Right" and self.direction != "Left":
            self.head.setheading(self.move["Right"])
            self.direction = "Right"

        self.can_move = False

    def forward(self):
        """
        Forward the snake and update the positions of the snake parts
        """
        for info in self.grid.values():
            info["snake"] = False

        deltas = {"Up": (0, +1),
                  "Down": (0, -1),
                  "Left": (-1, 0),
                  "Right": (+1, 0)}
        dx, dy = deltas[self.direction]

        new_head = (self.head_cell[0] + dx,
                    self.head_cell[1] + dy)

        if new_head not in self.grid:
            self.game_over = True
            return

        if self.tail_collision(new_head):
            self.game_over = True
            return

        self.grid_positions.insert(0, new_head)
        self.grid_positions.pop()

        for part, cell in zip(self.parts, self.grid_positions):
            if self.grid[cell]["snake"]:
                self.game_over = True
                return
            coord = self.grid[cell]
            part.goto(coord["x"], coord["y"])

        self.head_cell = new_head

        for cell in self.grid_positions:
            self.grid[cell]["snake"] = True

        self.can_move = True

    def wall_collision(self):
        """
        Check if the snake has collided with the walls.
        return: True if the snake has collided with the walls, False otherwise.
        """
        if self.walls["Right"].xcor() > self.head.xcor() > self.walls["Left"].xcor() and self.walls["Top"].ycor() > self.head.ycor() > self.walls["Bottom"].ycor():
            return True
        else:
            return False

    def tail_collision(self, new_head: tuple[int,int]) -> bool:
        """
        Check if the snake has collided with its tail.
        :return: True if the snake has collided with its tail, False otherwise.
        """
        return new_head in self.grid_positions[1:]

    def create_food(self):
        food_cords = {"x": random.uniform((-self.screen_width / 2) + 15, (self.screen_width / 2) - 15), "y": random.uniform((-self.screen_height / 2) + 15, (self.screen_height / 2) - 15)}
        self.food = Turtle()
        self.food.shape("circle")
        self.food.color("yellow")
        self.food.penup()
        self.food.goto(food_cords["x"], food_cords["y"])
        self.food.shapesize(stretch_wid=0.5, stretch_len=0.5)
        self.food.pendown()

    def food_collision(self):
        if self.food is not None:
            if self.head.distance(self.food) < self.parts_size * 20:
                return True
            else:
                return False
        return None

    def food_ate(self):
        """Repositions the food after it has been eaten."""
        if isinstance(self.food, Food):
            self.score_value += 1
            self.score.increase()
            tail_cell = self.grid_positions[-1]
            self.grid_positions.append(tail_cell)
            self.create_new_part(tail_cell)
            self.food.reposition()
        else:
             print("Error: self.food it's not an instant of Food.")

    def create_new_part(self, cell):
        """
        Create and position the new snake part in the cell (i,j).
        """
        new_part = Turtle("square")
        new_part.penup()
        new_part.shapesize(self.parts_size,
                           self.parts_size,
                           self.parts_outline)
        if self.use_random_color:
            new_part.color(random.choice(self.colors))
        else:
            new_part.color(self.use_only_one_color)
        new_part.pencolor("black")
        new_part.speed("fastest")

        coord = self.grid[cell]
        new_part.goto(coord["x"], coord["y"])

        self.parts.append(new_part)

    def restart(self):
        """
        Restart the game.
        """
        self.score.update_score()
        self.score.score = 0
        self.score.update_score()

        #for part in self.parts:
        #    part.goto(1000, 1000)
        # en lugar de moverlos apra que no se vean, los eliminamos
        for part in self.parts:
            part.hideturtle()
        self.parts.clear()

        self.game_over = False
        self.direction = "Right"
        self.length = self.initial_length

        self.head_cell = (0, 0)

        for cell_info in self.grid.values():
            cell_info["snake"] = False
            cell_info["food"] = False

        self.grid_positions = [(-i, 0) for i in range(self.length)]

        self.parts = []
        for cell in self.grid_positions:
            self.create_new_part(cell)
            self.grid[cell]["snake"] = True

        self.head = self.parts[0]

        if isinstance(self.food, Food):
             self.food.possible_positions()
             self.food.reposition()
        else:
             print("Advertencia: self.food no es una instancia de Food.") # Debería serlo si __init__ funcionó

        self.can_move = True


    def start(self):
        while self.running:
            self.screen.update()
            time.sleep(0.1)
            if self.food_collision():
                self.food_ate()
            if not self.game_over or not self.wall_collision():
                self.forward()
            else:
                self.restart()
        self.screen.exitonclick()

class Food(Turtle):
    def __init__(self, food_size = Snake.parts_size, food_outline = Snake.parts_outline, grid = None, margin = Snake.margin):
        super().__init__()
        self.food_size = food_size
        self.food_outline = food_outline
        self.grid = grid
        self.margin = margin

        self.shape("circle")
        self.shapesize(self.food_size, self.food_size, self.food_outline)
        self.color("yellow")
        self.pencolor("black")
        self.pendown()
        self.speed("fastest")

        self.free_cells: list[tuple[int, int]] = []
        self.possible_positions()
        self.reposition()

    def possible_positions(self):
        self.free_cells.clear()
        for cell, info in self.grid.items():
            if info.get("snake", False):
                continue
            self.free_cells.append(cell)

    def reposition(self):
        """
        Repositions the food after it has been eaten.
        """
        if not self.free_cells:
            self.possible_positions()
        cell = random.choice(self.free_cells)
        x = self.grid[cell]["x"]
        y = self.grid[cell]["y"]
        self.goto(x, y)

class Score(Turtle):
    def __init__(self, score: int = Snake.score_value, screen_height: int = Snake.screen_height, margin: int = Snake.margin, high_score: int = 0):
        super().__init__()
        self.score = score
        self.color("white")
        self.penup()
        self.hideturtle()
        self.high_score = high_score
        self.height = (screen_height / 2) - (margin * 2) + 10
        self.goto(0, self.height)
        self.write(f"Score: {self.score} | High score: {self.high_score}", align="center", font=("Courier", 16, "normal"))

    def increase(self):
        self.score += 1
        self.update_score()

    def update_score(self):
        self.clear()
        if self.score > self.high_score:
            self.high_score = self.score
            with open("high_score.txt", "w") as file:
                file.write(str(self.high_score))
        self.write(f"Score: {self.score} | High score: {self.high_score}", align="center", font=("Courier", 16, "normal"))
