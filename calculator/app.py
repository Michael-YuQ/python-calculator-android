import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW


class Calculator(toga.App):
    def startup(self):
        self.current_input = ""
        
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # 显示屏
        self.display = toga.TextInput(
            readonly=True,
            style=Pack(padding=5, height=60, font_size=24)
        )
        main_box.add(self.display)
        
        # 按钮布局
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', 'C', '+'],
            ['=']
        ]
        
        for row in buttons:
            row_box = toga.Box(style=Pack(direction=ROW, padding=2))
            for label in row:
                btn = toga.Button(
                    label,
                    on_press=self.on_button_press,
                    style=Pack(flex=1, padding=2, height=50, font_size=18)
                )
                row_box.add(btn)
            main_box.add(row_box)
        
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
    
    def on_button_press(self, widget):
        label = widget.label
        
        if label == 'C':
            self.current_input = ""
            self.display.value = ""
        elif label == '=':
            try:
                result = str(eval(self.current_input))
                self.display.value = result
                self.current_input = result
            except:
                self.display.value = "Error"
                self.current_input = ""
        else:
            self.current_input += label
            self.display.value = self.current_input


def main():
    return Calculator()
