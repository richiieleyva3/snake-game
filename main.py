from snake_brain import Snake

snake = Snake(
    color_wall = "red",
    use_random_color = False,
    use_only_one_color = "white",
    length= 3,
    controls =
                {
                    "w": "Up",
                    "Up": "Up",
                    "s": "Down",
                    "Down": "Down",
                    "a": "Left",
                    "Left": "Left",
                    "d": "Right",
                    "Right": "Right"
                }
              )
snake.start()