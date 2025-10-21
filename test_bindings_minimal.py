#!/usr/bin/env python3
"""
Minimal test - do BINDINGS work at all in MultiLineInput?
"""

from textual.app import App
from textual.widget import Widget
from textual.binding import Binding
from textual.reactive import reactive
import sys

class TestWidget(Widget):
    """Minimal widget to test BINDINGS"""

    BINDINGS = [
        Binding("up", "test_up", "Test up", show=False),
        Binding("down", "test_down", "Test down", show=False),
    ]

    test_value = reactive(0)

    def __init__(self):
        super().__init__()
        self.can_focus = True

    def render(self):
        return f"Test Value: {self.test_value}\nPress UP/DOWN arrows\nPress Q to quit"

    def action_test_up(self):
        sys.stderr.write(f"\n✅ action_test_up FIRED! value={self.test_value}\n")
        sys.stderr.flush()
        self.test_value -= 1
        self.refresh()

    def action_test_down(self):
        sys.stderr.write(f"\n✅ action_test_down FIRED! value={self.test_value}\n")
        sys.stderr.flush()
        self.test_value += 1
        self.refresh()

class TestApp(App):
    """Minimal app to test BINDINGS"""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def compose(self):
        yield TestWidget()

    def on_mount(self):
        self.query_one(TestWidget).focus()

if __name__ == "__main__":
    print("Testing if BINDINGS work in Textual...")
    print("If UP/DOWN arrows change the value, BINDINGS work!")
    print("Watch stderr for debug messages...")
    app = TestApp()
    app.run()
