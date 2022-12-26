import cx_Freeze

executables = [cx_Freeze.Executable("flappy_bird.py")]

cx_Freeze.setup(
    name="Flappy Bird",
    options={"build_exe": {"packages": ["pygame"],
                           "include_files": ["swoosh.ogg", "wing.ogg", "hit.ogg", "point.ogg", "die.wav", "swoosh.wav", "wing.wav", "point.wav", "hit.wav", "die.ogg", "score_font.ttf", "background.jpg", "bird.png", "uppipe.png", "downpipe.png", "ground.png", "highscore.txt"]}},
    executables = executables
)
