from .agility import OSRSAgility

class OSRSSeersAgi(OSRSAgility):
    def __init__(self) -> None:
        self.Obstacle = ["Wall", "Gap1", "Tightrope", "Gap2", "Gap3", "Edge"]
        self.Mouseover_Text = ["Jump", "Cross", "Climb-up"]
        self.DropPoints = ["Gap1", "Tightrope"]
        super().__init__("Seers Agility", "Start at the entrance of Seers Village bank.")