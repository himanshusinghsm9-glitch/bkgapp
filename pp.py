"""
Bachpan Kid's Garden - Attendance & Leave App
------------------------------------
Features:
1. Add Student (Name, Gmail, Mobile Number)
2. Mark Attendance (Present/Absent)
3. Apply for Leave
4. Director Admin Panel (login required) - sab data ek jagah dekhne ke liye
   Username: Directer
   Password: Directer

Data ab SQLite database (school_data.db) mein save hota hai - zyada reliable
aur file corrupt hone ka chance kam hota hai.
"""

import sqlite3
from datetime import date

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.core.window import Window

DB_FILE = "school_data.db"

# Director login credentials
DIRECTOR_USERNAME = "Directer"
DIRECTOR_PASSWORD = "Directer"


# -------------------- Database Setup --------------------

def get_conn():
    return sqlite3.connect(DB_FILE)


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gmail TEXT,
            mobile TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            reason TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_student(name, gmail, mobile):
    conn = get_conn()
    conn.execute("INSERT INTO students (name, gmail, mobile) VALUES (?, ?, ?)", (name, gmail, mobile))
    conn.commit()
    conn.close()


def get_students():
    conn = get_conn()
    rows = conn.execute("SELECT name, gmail, mobile FROM students ORDER BY name").fetchall()
    conn.close()
    return rows


def add_attendance(name, d, status):
    conn = get_conn()
    conn.execute("INSERT INTO attendance (name, date, status) VALUES (?, ?, ?)", (name, d, status))
    conn.commit()
    conn.close()


def get_attendance():
    conn = get_conn()
    rows = conn.execute("SELECT name, date, status FROM attendance ORDER BY date DESC").fetchall()
    conn.close()
    return rows


def add_leave(name, d, reason):
    conn = get_conn()
    conn.execute("INSERT INTO leaves (name, date, reason) VALUES (?, ?, ?)", (name, d, reason))
    conn.commit()
    conn.close()


def get_leaves():
    conn = get_conn()
    rows = conn.execute("SELECT name, date, reason FROM leaves ORDER BY date DESC").fetchall()
    conn.close()
    return rows


def get_student_names():
    return [row[0] for row in get_students()]


def show_popup(title, message):
    popup = Popup(title=title, content=Label(text=message), size_hint=(0.85, 0.4))
    popup.open()


# -------------------- Home Screen --------------------

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=25, spacing=12)

        layout.add_widget(Label(text="Bachpan Kid's Garden", font_size=26, size_hint=(1, 0.22)))

        buttons = [
            ("Add Student", "add_student"),
            ("Mark Attendance", "attendance"),
            ("Apply for Leave", "leave"),
            ("View Records", "records"),
            ("Director Login", "director_login"),
        ]
        for text, screen_name in buttons:
            btn = Button(text=text, size_hint=(1, 0.13), font_size=18)
            btn.bind(on_press=lambda inst, s=screen_name: self.go(s))
            layout.add_widget(btn)

        self.add_widget(layout)

    def go(self, screen_name):
        self.manager.current = screen_name


# -------------------- Add Student Screen --------------------

class AddStudentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=30, spacing=15)

        layout.add_widget(Label(text="Add Student", font_size=24, size_hint=(1, 0.15)))

        self.name_input = TextInput(hint_text="Student Name", multiline=False, size_hint=(1, 0.1))
        layout.add_widget(self.name_input)

        self.gmail_input = TextInput(hint_text="Gmail ID", multiline=False, size_hint=(1, 0.1))
        layout.add_widget(self.gmail_input)

        self.mobile_input = TextInput(hint_text="Mobile Number", multiline=False, size_hint=(1, 0.1), input_filter="int")
        layout.add_widget(self.mobile_input)

        btn_add = Button(text="Add Student", size_hint=(1, 0.12))
        btn_add.bind(on_press=self.add)
        layout.add_widget(btn_add)

        btn_back = Button(text="Back to Home", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.go_home)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def add(self, instance):
        name = self.name_input.text.strip()
        gmail = self.gmail_input.text.strip()
        mobile = self.mobile_input.text.strip()
        if not name:
            show_popup("Error", "Please enter student name")
            return
        add_student(name, gmail, mobile)
        show_popup("Saved", f"{name} added successfully")
        self.name_input.text = ""
        self.gmail_input.text = ""
        self.mobile_input.text = ""

    def go_home(self, instance):
        self.manager.current = "home"


# -------------------- Attendance Screen --------------------

class AttendanceScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=30, spacing=15)

        layout.add_widget(Label(text="Mark Attendance", font_size=24, size_hint=(1, 0.15)))

        self.name_spinner = Spinner(
            text="Select Student", values=[], size_hint=(1, 0.1)
        )
        layout.add_widget(self.name_spinner)

        self.date_input = TextInput(text=str(date.today()), hint_text="Date (YYYY-MM-DD)", multiline=False, size_hint=(1, 0.1))
        layout.add_widget(self.date_input)

        btn_row = BoxLayout(size_hint=(1, 0.12), spacing=10)
        btn_present = Button(text="Present", background_color=(0.2, 0.7, 0.2, 1))
        btn_present.bind(on_press=lambda x: self.mark("Present"))
        btn_absent = Button(text="Absent", background_color=(0.8, 0.2, 0.2, 1))
        btn_absent.bind(on_press=lambda x: self.mark("Absent"))
        btn_row.add_widget(btn_present)
        btn_row.add_widget(btn_absent)
        layout.add_widget(btn_row)

        btn_back = Button(text="Back to Home", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.go_home)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def on_pre_enter(self, *args):
        self.name_spinner.values = get_student_names()
        self.name_spinner.text = "Select Student"

    def mark(self, status):
        name = self.name_spinner.text
        d = self.date_input.text.strip()
        if not name or name == "Select Student":
            show_popup("Error", "Please select student name")
            return
        add_attendance(name, d, status)
        show_popup("Saved", f"{name} marked {status} on {d}")
        self.name_spinner.text = "Select Student"

    def go_home(self, instance):
        self.manager.current = "home"


# -------------------- Leave Screen --------------------

class LeaveScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=30, spacing=15)

        layout.add_widget(Label(text="Apply for Leave", font_size=24, size_hint=(1, 0.15)))

        self.name_spinner = Spinner(
            text="Select Student", values=[], size_hint=(1, 0.1)
        )
        layout.add_widget(self.name_spinner)

        self.date_input = TextInput(text=str(date.today()), hint_text="Leave Date (YYYY-MM-DD)", multiline=False, size_hint=(1, 0.1))
        layout.add_widget(self.date_input)

        self.reason_input = TextInput(hint_text="Reason for leave", multiline=True, size_hint=(1, 0.3))
        layout.add_widget(self.reason_input)

        btn_submit = Button(text="Submit Leave Application", size_hint=(1, 0.12))
        btn_submit.bind(on_press=self.submit)
        layout.add_widget(btn_submit)

        btn_back = Button(text="Back to Home", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.go_home)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def on_pre_enter(self, *args):
        self.name_spinner.values = get_student_names()
        self.name_spinner.text = "Select Student"

    def submit(self, instance):
        name = self.name_spinner.text
        d = self.date_input.text.strip()
        reason = self.reason_input.text.strip()
        if not name or name == "Select Student" or not reason:
            show_popup("Error", "Please select student and fill reason")
            return
        add_leave(name, d, reason)
        show_popup("Submitted", f"Leave application submitted for {name}")
        self.name_spinner.text = "Select Student"
        self.reason_input.text = ""

    def go_home(self, instance):
        self.manager.current = "home"


# -------------------- Records Screen (student-facing, view only) --------------------

class RecordsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.add_widget(self.layout)

    def on_pre_enter(self, *args):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="Records", font_size=24, size_hint=(1, 0.1)))

        scroll = ScrollView(size_hint=(1, 0.75))
        grid = GridLayout(cols=1, spacing=8, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        grid.add_widget(Label(text="[b]-- Attendance --[/b]", markup=True, size_hint_y=None, height=30))
        for name, d, status in get_attendance():
            grid.add_widget(Label(text=f"{d} | {name} | {status}", size_hint_y=None, height=30))

        grid.add_widget(Label(text="[b]-- Leave Applications --[/b]", markup=True, size_hint_y=None, height=30))
        for name, d, reason in get_leaves():
            grid.add_widget(Label(text=f"{d} | {name} | {reason}", size_hint_y=None, height=30))

        scroll.add_widget(grid)
        self.layout.add_widget(scroll)

        btn_back = Button(text="Back to Home", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.go_home)
        self.layout.add_widget(btn_back)

    def go_home(self, instance):
        self.manager.current = "home"


# -------------------- Director Login Screen --------------------

class DirectorLoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=30, spacing=15)

        layout.add_widget(Label(text="Director Login", font_size=24, size_hint=(1, 0.2)))

        self.user_input = TextInput(hint_text="Username", multiline=False, size_hint=(1, 0.12))
        layout.add_widget(self.user_input)

        self.pass_input = TextInput(hint_text="Password", multiline=False, password=True, size_hint=(1, 0.12))
        layout.add_widget(self.pass_input)

        btn_login = Button(text="Login", size_hint=(1, 0.12))
        btn_login.bind(on_press=self.login)
        layout.add_widget(btn_login)

        btn_back = Button(text="Back to Home", size_hint=(1, 0.1))
        btn_back.bind(on_press=self.go_home)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def login(self, instance):
        if self.user_input.text.strip() == DIRECTOR_USERNAME and self.pass_input.text.strip() == DIRECTOR_PASSWORD:
            self.user_input.text = ""
            self.pass_input.text = ""
            self.manager.current = "director_panel"
        else:
            show_popup("Login Failed", "Galat username ya password")

    def go_home(self, instance):
        self.manager.current = "home"


# -------------------- Director Panel (admin view of everything) --------------------

class DirectorPanelScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.add_widget(self.layout)

    def on_pre_enter(self, *args):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="Director Panel", font_size=24, size_hint=(1, 0.08)))

        scroll = ScrollView(size_hint=(1, 0.8))
        grid = GridLayout(cols=1, spacing=8, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        grid.add_widget(Label(text="[b]-- Students --[/b]", markup=True, size_hint_y=None, height=30))
        for name, gmail, mobile in get_students():
            grid.add_widget(Label(text=f"{name} | {gmail} | {mobile}", size_hint_y=None, height=30))

        grid.add_widget(Label(text="[b]-- Attendance --[/b]", markup=True, size_hint_y=None, height=30))
        for name, d, status in get_attendance():
            grid.add_widget(Label(text=f"{d} | {name} | {status}", size_hint_y=None, height=30))

        grid.add_widget(Label(text="[b]-- Leave Applications --[/b]", markup=True, size_hint_y=None, height=30))
        for name, d, reason in get_leaves():
            grid.add_widget(Label(text=f"{d} | {name} | {reason}", size_hint_y=None, height=30))

        scroll.add_widget(grid)
        self.layout.add_widget(scroll)

        btn_logout = Button(text="Logout to Home", size_hint=(1, 0.1))
        btn_logout.bind(on_press=self.go_home)
        self.layout.add_widget(btn_logout)

    def go_home(self, instance):
        self.manager.current = "home"


# -------------------- Main App --------------------

class AttendanceApp(App):
    title = "Bachpan Kid's Garden"

    def build(self):
        init_db()
        Window.size = (400, 700)
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddStudentScreen(name="add_student"))
        sm.add_widget(AttendanceScreen(name="attendance"))
        sm.add_widget(LeaveScreen(name="leave"))
        sm.add_widget(RecordsScreen(name="records"))
        sm.add_widget(DirectorLoginScreen(name="director_login"))
        sm.add_widget(DirectorPanelScreen(name="director_panel"))
        return sm


if __name__ == "__main__":
    AttendanceApp().run()