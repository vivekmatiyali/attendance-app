# AI Face Recognition Attendance System

A desktop app that takes student attendance automatically using face recognition,
built with Python, OpenCV, MySQL, and Tkinter.

## What it does

1. **Register Student** — capture a student's face via webcam and store it in MySQL.
2. **Take Attendance** — opens the webcam, recognizes registered students in real time,
   and automatically marks them present for today (once per day per student).
3. **View Today's Attendance** — see who's been marked present today.
4. **Export to CSV** — export the full attendance history to a spreadsheet-friendly file.

---

## Step 1: Install MySQL

If you don't already have MySQL installed:
- Windows/Mac: install **MySQL Community Server** from https://dev.mysql.com/downloads/
- During setup, set a root password and remember it — you'll need it in Step 3.

You do **not** need to create the database manually — the app creates it automatically
the first time it runs.

---

## Step 2: Install Python dependencies

Open a terminal/command prompt in this folder and run:

```bash
pip install -r requirements.txt
```

**Important note about `face_recognition` on Windows:**
This library depends on `dlib`, which sometimes fails to install directly via pip on Windows
because it needs a C++ compiler. If `pip install face_recognition` fails:

1. Install **CMake**: https://cmake.org/download/
2. Install **Visual Studio Build Tools** (choose "Desktop development with C++") from
   https://visualstudio.microsoft.com/visual-cpp-build-tools/
3. Then re-run `pip install -r requirements.txt`

On Mac/Linux this usually installs without extra steps.

---

## Step 3: Configure your database connection

Open `config.py` and update this section with your own MySQL password:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",   # <-- change this
    "database": "attendance_db"
}
```

---

## Step 4: Run the app

```bash
python main.py
```

The first time it runs, it will automatically create the `attendance_db` database
and the two tables it needs (`students` and `attendance`).

---

## How to use it

### Registering a student
1. Click **"1. Register Student"**
2. Enter their roll number and name
3. A camera window opens — look at the camera and press **SPACE** 5 times
   (slightly turn your head between captures for a more reliable match)
4. Press **q** any time to cancel

### Taking attendance
1. Click **"2. Take Attendance"**
2. The camera opens and continuously scans for faces
3. Recognized students are marked present automatically (green box + name shown)
4. Unrecognized faces show a red box labeled "Unknown"
5. Press **q** in the camera window to end the session

### Viewing / exporting
- **"3. View Today's Attendance"** shows a table of everyone marked present today
- **"4. Export All Attendance to CSV"** saves the full history as a `.csv` file
  in the same folder, which you can open in Excel

---

## Project files

| File | Purpose |
|---|---|
| `main.py` | The GUI — run this to start the app |
| `database.py` | All MySQL queries (create tables, save students, mark/read attendance) |
| `face_utils.py` | Webcam + face recognition logic |
| `config.py` | Your database password and app settings (camera index, match sensitivity) |
| `requirements.txt` | Python packages needed |

---

## Troubleshooting

- **"Access denied for user 'root'"** → your password in `config.py` is wrong.
- **Camera doesn't open** → try changing `CAMERA_INDEX` in `config.py` from `0` to `1`.
- **Recognizes the wrong student / everyone as "Unknown"** → adjust `FACE_MATCH_TOLERANCE`
  in `config.py`. Lower it (e.g. `0.4`) for stricter matching, raise it (e.g. `0.6`) if it's
  failing to recognize registered students.
- **Bad lighting causes misdetection** → register students in the same lighting
  conditions they'll be scanned in for attendance.

---

## Possible next steps (once this is working)

- Add a login screen for teachers
- Add "class" or "subject" tracking so one student can have attendance per-subject
- Add a monthly attendance percentage report
- Package into a `.exe` using `pyinstaller` so it runs without a Python install
