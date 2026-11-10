from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
import re

class XRankApp(App):
    def build(self):
        self.variables = {}
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title
        title = Label(text='x-RANK CODE EDITOR', size_hint_y=None, height=40, bold=True, font_size=20)
        layout.add_widget(title)

        # Code Editor
        self.editor = TextInput(
            text='let count = 1\nwhile count < 4 {\nshow (count)\nlet count = count + 1\n}',
            multiline=True, font_size=18, size_hint_y=0.6
        )
        layout.add_widget(self.editor)

        # Buttons row
        btn_row = BoxLayout(size_hint_y=None, height=50, spacing=10)
        run_btn = Button(text='RUN CODE', background_color=(0, 0.6, 0, 1))
        run_btn.bind(on_press=self.run_code)
        about_btn = Button(text='ABOUT x-RANK', background_color=(0, 0.3, 0.8, 1))
        about_btn.bind(on_press=self.show_about)
        btn_row.add_widget(run_btn)
        btn_row.add_widget(about_btn)
        layout.add_widget(btn_row)

        # Output
        layout.add_widget(Label(text='TERMINAL OUTPUT:', size_hint_y=None, height=30, bold=True))
        self.output = Label(text='Press RUN CODE', font_size=18, halign='left', valign='top', size_hint_y=None)
        self.output.bind(texture_size=self.output.setter('size'))
        scroll = ScrollView(size_hint_y=0.5)
        scroll.add_widget(self.output)
        layout.add_widget(scroll)

        return layout

    def show_about(self, instance):
        about_text = (
            "x-RANK v0.1\n"
            "By Phinehas Siakeni - Moi's Bridge, Kenya\n"
            "Formula: C(n,t,d) = Who, When, Where\n\n"
            "WHAT IT CAN DO TODAY:\n"
            "- let name = value  (remember)\n"
            "- show (text) / show (variable)\n"
            "- while loop\n"
            "- Maths: + - * / ( )\n"
            "- # for comments\n\n"
            "WHAT IT CANNOT DO YET:\n"
            "- No if / else yet\n"
            "- Does NOT fix typos yet. It says Error, not 'Did you mean...'\n"
            "- No apps yet\n"
            "- No full C(n,t,d) protection yet - Future Intention\n\n"
            "MISSION: A language that speaks clear English,\n"
            "for children below 13, that remedies errors,\n"
            "not just copies them."
        )
        popup = Popup(title='About x-Rank', content=Label(text=about_text, halign='left', valign='top'), size_hint=(0.9, 0.9))
        popup.open()

    def run_code(self, instance):
        code = self.editor.text
        lines = code.split('\n')
        self.variables = {}
        out = []
        i = 0
        try:
            while i < len(lines):
                line = lines[i].strip()
                if not line or line.startswith('#'):
                    i += 1
                    continue

                # WHILE LOOP
                if line.startswith('while'):
                    # while count < 4 {
                    cond = line.replace('while', '').replace('{', '').strip()
                    # collect body until }
                    body = []
                    i += 1
                    while i < len(lines) and '}' not in lines[i]:
                        body.append(lines[i].strip())
                        i += 1
                    # run loop max 100 times to protect phone
                    count_loop = 0
                    while self.eval_expr(cond) and count_loop < 100:
                        for bline in body:
                            self.exec_line(bline, out)
                        count_loop += 1
                    i += 1
                    continue

                self.exec_line(line, out)
                i += 1

            if not out:
                self.output.text = "Code ran with no output statements."
            else:
                self.output.text = "\n".join([str(x) for x in out])
        except Exception as e:
            self.output.text = f"Error (line {i+1}): {e}"

    def exec_line(self, line, out):
        line = line.strip()
        if not line or line.startswith('#'):
            return
        # show ( ... )
        m = re.match(r'show\s*\(\s*(.+)\s*\)', line)
        if m:
            inside = m.group(1).strip()
            # show ("text")
            if inside.startswith('"') and inside.endswith('"'):
                out.append(inside[1:-1])
            elif inside in self.variables:
                out.append(str(self.variables[inside]))
            else:
                # try maths
                try:
                    out.append(str(self.eval_expr(inside)))
                except:
                    raise Exception(f"'{inside}' unrecognized.")
            return
        # let x = ...
        m = re.match(r'let\s+(\w+)\s*=\s*(.+)', line)
        if m:
            name = m.group(1)
            expr = m.group(2).strip()
            # let x = "text"
            if expr.startswith('"') and expr.endswith('"'):
                self.variables[name] = expr[1:-1]
            else:
                self.variables[name] = self.eval_expr(expr)
            return
        raise Exception(f"cannot work out '{line}'")

    def eval_expr(self, expr):
        # Replace variables with values
        for k, v in self.variables.items():
            # only replace whole word
            expr = re.sub(r'\b' + k + r'\b', str(v), expr)
        # Allow only safe chars
        if re.search(r'[^0-9+\-*/().<>=!&| ]', expr):
            # Could be boolean, allow True/False
            pass
        return eval(expr, {"__builtins__": {}})

if __name__ == '__main__':
    XRankApp().run()
