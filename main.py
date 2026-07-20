"""
main.py
The main desktop application window (Tkinter).
Run this file to start the app: python main.py
"""

import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

import database
import face_utils


class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Face Recognition Attendance System")
        self.root.geometry("520x420")
        self.root.resizable(False, False)

        title = tk.Label(root, text="Attendance System", font=("Arial", 20, "bold"))
        title.pack(pady=20)

        self.status_var = tk.StringVar(value="Ready.")

        btn_style = {"width": 30, "height": 2, "font": ("Arial", 11)}

        tk.Button(root, text="1. Register Student", command=self.register_student, **btn_style).pack(pady=8)
        tk.Button(root, text="2. Take Attendance", command=self.take_attendance, **btn_style).pack(pady=8)
        tk.Button(root, text="3. View Today's Attendance", command=self.view_today, **btn_style).pack(pady=8)
        tk.Button(root, text="4. Export All Attendance to CSV", command=self.export_csv, **btn_style).pack(pady=8)

        status_label = tk.Label(root, textvariable=self.status_var, fg="blue", wraplength=480)
        status_label.pack(pady=15)

    def set_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()

    # ---------------------------------------------------------------
    def register_student(self):
        roll_no = simpledialog.askstring("Roll Number", "Enter student's roll number:")
        if not roll_no:
            return
        name = simpledialog.askstring("Name", "Enter student's full name:")
        if not name:
            return

        self.set_status("Opening camera... look at the camera and press SPACE to capture. Press 'q' to cancel.")
        messagebox.showinfo(
            "Instructions",
            "The camera window will open.\n\n"
            "- Look straight at the camera\n"
            "- Press SPACE to capture a photo (do this 5 times, slightly changing angle each time)\n"
            "- Press 'q' to cancel at any time"
        )

        encoding = face_utils.capture_face_encoding(status_callback=self.set_status)

        if encoding is None:
            self.set_status("Registration cancelled.")
            return

        success = database.add_student(roll_no, name, encoding)
        if success:
            self.set_status(f"Student '{name}' ({roll_no}) registered successfully.")
        else:
            self.set_status(f"Error: roll number '{roll_no}' already exists.")

    # ---------------------------------------------------------------
    def take_attendance(self):
        students = database.get_all_students()
        if not students:
            messagebox.showwarning("No students", "Please register at least one student first.")
            return

        self.set_status("Opening camera for attendance... press 'q' in the video window when done.")

        def on_recognized(student_id, roll_no, name):
            database.mark_attendance(student_id)

        face_utils.run_attendance_session(students, on_recognized, status_callback=self.set_status)
        self.set_status("Attendance session finished.")

    # ---------------------------------------------------------------
    def view_today(self):
        today = datetime.date.today()
        records = database.get_attendance_by_date(today)

        window = tk.Toplevel(self.root)
        window.title(f"Attendance - {today}")
        window.geometry("450x400")

        columns = ("roll_no", "name", "time", "status")
        tree = ttk.Treeview(window, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, width=100)
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        if not records:
            tk.Label(window, text="No attendance recorded yet today.").pack(pady=10)
        else:
            for roll_no, name, time, status in records:
                tree.insert("", "end", values=(roll_no, name, str(time), status))

    # ---------------------------------------------------------------
    def export_csv(self):
        records = database.get_all_attendance()
        if not records:
            messagebox.showinfo("No data", "No attendance records to export yet.")
            return

        filename = f"attendance_export_{datetime.date.today()}.csv"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("Roll No,Name,Date,Time,Status\n")
            for roll_no, name, date, time, status in records:
                f.write(f"{roll_no},{name},{date},{time},{status}\n")

        self.set_status(f"Exported to {filename}")
        messagebox.showinfo("Export complete", f"Attendance exported to:\n{filename}")


if __name__ == "__main__":
    print("Initializing database...")
    database.init_db()
    print("Database ready. Launching app...")

    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
