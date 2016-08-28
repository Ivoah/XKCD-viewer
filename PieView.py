import ui
import math

class PieView(ui.View):
    def __init__(self):
        self.value = 0

    def set_value(self, value):
        self.value = value
        self.set_needs_display()

    def draw(self):
        path = ui.Path()
        path.move_to(self.width/2, self.height/2)
        path.add_arc(self.width/2, self.height/2, min(self.width, self.height)/2, -math.pi/2, self.value*(2*math.pi) - math.pi/2)
        ui.set_color(self.tint_color)
        path.fill()
