from game import AlienShooter

window_width,window_height = 1200,800
world_width,world_height = 1800,1200
fps=60

game = AlienShooter(window_width=window_width,window_height=window_height,world_height=world_height,world_width=world_width,fps=fps,sound=True)

while True:
    game.step()