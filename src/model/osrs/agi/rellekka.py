from .agility import OSRSAgility

class OSRSRellekkaAgi(OSRSAgility):
    def __init__(self) -> None:
        self.Obstacle = ["RoughWall", "Gap1", "Tightrope1", "Gap2", "Gap3", "Tightrope2", "PileOfFish"]
        self.Mouseover_Text = ["Climb", "Leap", "Cross", "Hurdle", "Jump-in"]
        self.DropPoints = ["Tightrope1", "Gap2"]
        super().__init__("Rellekka Agility", "Face south and start near starting point")