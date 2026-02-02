import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog
import tempfile
import subprocess
from datetime import datetime
import winsound

# ---------------- CONFIG ---------------- #

OWNER_USERNAME = "admin"
OWNER_PASSWORD = "admin123"

SECURE_FOLDER = os.path.join(tempfile.gettempdir(), "SecureZone")
AUDIT_LOG_FILE = "session_audit.log"

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DOCUMENT_TYPES = ["Aadhaar", "PAN", "Voter ID", "Resume", "Other"]

selected_document_type = None
session_active = False
workspace = None

# ---------------- AUDIT LOG ---------------- #

def write_audit_log(action):
    if not os.path.exists(SECURE_FOLDER):
        return
    with open(os.path.join(SECURE_FOLDER, AUDIT_LOG_FILE), "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {action}\n")

# ---------------- SECURITY ALERT ---------------- #

def security_alert(message):
    # Beep 3 times
    for _ in range(3):
        winsound.Beep(1000, 500)
    messagebox.showerror("SECURITY ALERT", message)
    write_audit_log(f"SECURITY ALERT: {message}")

# ---------------- UTIL ---------------- #

def create_secure_folder():
    if not os.path.exists(SECURE_FOLDER):
        os.mkdir(SECURE_FOLDER)

def delete_secure_folder():
    if os.path.exists(SECURE_FOLDER):
        shutil.rmtree(SECURE_FOLDER)

# ---------------- PROGRESS BAR ---------------- #

def show_progress(title="Loading...", duration=3):
    """
    Shows a rectangular filling animation for `duration` seconds.
    """
    progress_win = tk.Toplevel(workspace)
    progress_win.title(title)
    progress_win.geometry("500x150")
    progress_win.resizable(False, False)
    progress_win.configure(bg="#f8fafc")
    progress_win.grab_set()  # Block other interactions

    tk.Label(
        progress_win,
        text=title,
        font=("Segoe UI", 16, "bold"),
        bg="#f8fafc"
    ).pack(pady=20)

    canvas = tk.Canvas(progress_win, width=400, height=30, bg="#e5e7eb", highlightthickness=0)
    canvas.pack(pady=10)

    # The filling rectangle (starts with width 0)
    fill = canvas.create_rectangle(0, 0, 0, 30, fill="#4f46e5", width=0)

    # Animate filling
    steps = 100
    delay = duration / steps
    for i in range(1, steps + 1):
        canvas.coords(fill, 0, 0, 4*i, 30)  # increase width gradually
        progress_win.update()
        progress_win.after(int(delay * 1000))

    progress_win.destroy()

# ---------------- ADMIN: ADD FILES ---------------- #

def admin_add_files():
    if not session_active:
        messagebox.showerror("Access Denied", "No active session")
        return

    files = filedialog.askopenfilenames(
        title="Admin: Add files to Secure Zone"
    )

    for file in files:
        shutil.copy(file, SECURE_FOLDER)
        write_audit_log(f"ADMIN added file: {os.path.basename(file)}")

    messagebox.showinfo(
        "Session-Bound Access",
        "Files added and accessible ONLY for this session"
    )

# ---------------- ADMIN: USER DATA INTAKE ---------------- #

def admin_user_data_intake():
    if not session_active:
        messagebox.showerror("Session Expired", "No active session")
        return

    intake = tk.Toplevel(workspace)
    intake.title("Secure User Data Intake")
    intake.geometry("700x600")
    intake.configure(bg="#f8fafc")

    write_audit_log("Admin opened User Data Intake Workspace")

    tk.Label(
        intake,
        text="📝 User Personal Information Intake",
        font=("Segoe UI", 20, "bold"),
        bg="#f8fafc"
    ).pack(pady=20)

    tk.Label(
        intake,
        text="Select Information Type",
        font=("Segoe UI", 14, "bold"),
        bg="#f8fafc"
    ).pack(anchor="w", padx=40)

    info_type = tk.StringVar()
    info_type.set(DOCUMENT_TYPES[0])

    tk.OptionMenu(intake, info_type, *DOCUMENT_TYPES).pack(
        anchor="w", padx=40, pady=10
    )

    tk.Label(
        intake,
        text="Enter User Information (typed directly, not uploaded)",
        font=("Segoe UI", 14, "bold"),
        bg="#f8fafc"
    ).pack(anchor="w", padx=40, pady=(20, 5))

    text_area = tk.Text(
        intake,
        height=15,
        font=("Segoe UI", 12),
        wrap="word"
    )
    text_area.pack(fill="both", expand=True, padx=40)

    def save_to_secure_folder():
        content = text_area.get("1.0", tk.END).strip()

        if not content:
            messagebox.showerror("Empty Data", "No information entered")
            return

        filename = f"{info_type.get()}_UserData_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path = os.path.join(SECURE_FOLDER, filename)

        if not os.path.commonpath([file_path, SECURE_FOLDER]) == SECURE_FOLDER:
            security_alert("Attempt to save user data outside Secure Zone!")
            return

        # Show saving animation
        show_progress("Saving Data...", duration=1.5)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"Document Type: {info_type.get()}\n")
            f.write(f"Captured At: {datetime.now()}\n\n")
            f.write(content)

        write_audit_log(f"User data captured as {filename}")

        messagebox.showinfo(
            "Securely Stored",
            f"User information saved inside Secure Zone\n\n{filename}"
        )

        text_area.delete("1.0", tk.END)

    tk.Button(
        intake,
        text="💾 Save to Secure Folder",
        font=("Segoe UI", 14, "bold"),
        bg="#16a34a",
        fg="white",
        height=2,
        command=save_to_secure_folder
    ).pack(pady=25)

# ---------------- UPLOAD HELPER ---------------- #

def upload_helper():
    if not session_active:
        messagebox.showerror("Session Expired", "No active session")
        return

    file = filedialog.askopenfilename(
        title="Upload from Secure Zone only",
        initialdir=SECURE_FOLDER
    )

    if not file:
        return

    if not os.path.commonpath([file, SECURE_FOLDER]) == SECURE_FOLDER:
        security_alert("Attempt to use a file outside Secure Zone!")
        return

    # Show uploading animation
    show_progress("Preparing File for Upload...", duration=1.5)

    write_audit_log(f"Secure file selected for upload: {os.path.basename(file)}")

    messagebox.showinfo(
        "Upload Ready",
        f"Use this file for upload:\n{os.path.basename(file)}"
    )

# ---------------- SECURE VIEWER ---------------- #

def open_secure_viewer():
    if not session_active:
        messagebox.showerror("Session Expired", "Secure files not accessible")
        return

    write_audit_log("Secure Viewer opened")

    viewer = tk.Toplevel(workspace)
    viewer.title("Secure Folder (Session Bound)")
    viewer.geometry("600x420")
    viewer.configure(bg="#f1f5f9")

    tk.Label(
        viewer,
        text="🔒 Secure Folder (Accessible during session only)",
        font=("Segoe UI", 16, "bold"),
        bg="#f1f5f9"
    ).pack(pady=10)

    file_list = tk.Listbox(viewer, font=("Segoe UI", 12))
    file_list.pack(expand=True, fill="both", padx=20, pady=10)

    def refresh_files():
        file_list.delete(0, tk.END)
        for f in os.listdir(SECURE_FOLDER):
            if f != AUDIT_LOG_FILE:
                file_list.insert(tk.END, f)

    refresh_files()

    tk.Button(
        viewer,
        text="🔄 Refresh",
        command=refresh_files
    ).pack(pady=5)

# ---------------- PRINT SECURE FILE ---------------- #

def print_secure_file():
    if not session_active:
        messagebox.showerror("Session Expired", "No active session")
        return

    file = filedialog.askopenfilename(
        title="Select file to print",
        initialdir=SECURE_FOLDER
    )

    if not file:
        return

    if not os.path.commonpath([file, SECURE_FOLDER]) == SECURE_FOLDER:
        security_alert("Attempt to print a file outside Secure Zone!")
        return

    # Show printing animation
    show_progress("Preparing Print...", duration=1.5)

    write_audit_log(f"Printed file: {os.path.basename(file)}")

    try:
        if os.name == 'nt':
            os.startfile(file, "print")
        else:
            subprocess.Popen(["lpr", file])
    except Exception as e:
        messagebox.showerror("Print Error", f"Failed to print file:\n{e}")

# ---------------- WORKSPACE ---------------- #

def end_session():
    global session_active
    write_audit_log("Session ended")
    session_active = False
    delete_secure_folder()
    workspace.destroy()
    show_dashboard()

def open_browser():
    if not session_active:
        messagebox.showerror("Session Expired", "No active session")
        return

    # Show browser loading animation
    show_progress("Opening Browser...", duration=2)

    write_audit_log("Browser opened")
    subprocess.Popen([
        CHROME_PATH,
        "--incognito",
        f"--download.default_directory={SECURE_FOLDER}",
        "https://www.google.com"
    ])

def logout_from_workspace():
    global session_active
    if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout? Session will end."):
        write_audit_log("Admin logged out from Secure Workspace")
        session_active = False
        delete_secure_folder()
        workspace.destroy()
        show_login()

def show_workspace():
    global workspace, session_active
    session_active = True

    write_audit_log(f"Session started | {selected_document_type}")

    workspace = tk.Tk()
    workspace.state("zoomed")
    workspace.configure(bg="#f8fafc")

    header = tk.Frame(workspace, bg="#1e3a8a", height=90)
    header.pack(fill="x")

    tk.Label(
        header,
        text="🔒 Secure Workspace",
        fg="white",
        bg="#1e3a8a",
        font=("Segoe UI", 26, "bold")
    ).pack(side="left", padx=30)

    body = tk.Frame(workspace, bg="#f8fafc")
    body.pack(expand=True)

    def big_btn(text, cmd, color="#4f46e5"):
        return tk.Button(
            body,
            text=text,
            font=("Segoe UI", 16, "bold"),
            bg=color,
            fg="white",
            width=38,
            height=2,
            relief="flat",
            command=cmd
        )

    tk.Label(
        body,
        text="⚠ Upload personal files ONLY via Secure Zone",
        font=("Segoe UI", 12, "bold"),
        fg="#b91c1c",
        bg="#f8fafc"
    ).pack(pady=10)

    big_btn("📂 Open Secure Folder (Session Bound)", open_secure_viewer).pack(pady=10)
    big_btn("🌐 Open Secure Browser", open_browser).pack(pady=10)
    big_btn("📤 Upload from Secure Zone", upload_helper, "#0ea5e9").pack(pady=10)
    big_btn("🖨 Print from Secure Folder", print_secure_file, "#f59e0b").pack(pady=10)
    big_btn("➕ Admin: Add Files to Secure Zone", admin_add_files, "#16a34a").pack(pady=10)
    big_btn("📝 Admin: User Data Intake (No File Upload)", admin_user_data_intake, "#0f766e").pack(pady=10)
    big_btn("⛔ End Session", end_session, "#dc2626").pack(pady=10)
    big_btn("🚪 Logout", logout_from_workspace, "#dc2626").pack(pady=40)  # <-- NEW LOGOUT BUTTON

    workspace.mainloop()

# ---------------- DOCUMENT TYPE ---------------- #

def confirm_doc():
    global selected_document_type
    if not doc_var.get():
        messagebox.showerror("Required", "Select document type")
        return
    selected_document_type = doc_var.get()
    doc.destroy()
    show_workspace()

def select_document_type():
    global doc, doc_var
    create_secure_folder()

    doc = tk.Tk()
    doc.state("zoomed")
    doc.configure(bg="#eef2ff")

    card = tk.Frame(doc, bg="white", padx=50, pady=40)
    card.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        card,
        text="📄 Select Document Type",
        font=("Segoe UI", 24, "bold"),
        bg="white"
    ).pack(pady=20)

    doc_var = tk.StringVar()

    for d in DOCUMENT_TYPES:
        tk.Radiobutton(
            card,
            text=d,
            variable=doc_var,
            value=d,
            font=("Segoe UI", 15),
            bg="white"
        ).pack(anchor="w", pady=6)

    tk.Button(
        card,
        text="Start Secure Session",
        font=("Segoe UI", 16, "bold"),
        bg="#4f46e5",
        fg="white",
        relief="flat",
        height=2,
        width=25,
        command=confirm_doc
    ).pack(pady=25)

    doc.mainloop()

# ---------------- DASHBOARD ---------------- #

def start_session():
    dashboard.destroy()
    select_document_type()

def logout():
    dashboard.destroy()
    show_login()

def show_dashboard():
    global dashboard
    dashboard = tk.Tk()
    dashboard.state("zoomed")
    dashboard.configure(bg="#eef2ff")

    tk.Label(
        dashboard,
        text="Secure Print Zone",
        font=("Segoe UI", 30, "bold"),
        bg="#eef2ff"
    ).pack(pady=80)

    def dash_btn(text, cmd):
        return tk.Button(
            dashboard,
            text=text,
            font=("Segoe UI", 18, "bold"),
            bg="#4f46e5",
            fg="white",
            width=28,
            height=2,
            relief="flat",
            command=cmd
        )

    dash_btn("▶ Start New Session", start_session).pack(pady=20)
    dash_btn("🚪 Logout", logout).pack(pady=20)

    dashboard.mainloop()

# ---------------- LOGIN ---------------- #

def authenticate():
    if user.get() == OWNER_USERNAME and pwd.get() == OWNER_PASSWORD:
        login.destroy()
        show_dashboard()
    else:
        messagebox.showerror("Error", "Invalid credentials")

def show_login():
    global login, user, pwd
    login = tk.Tk()
    login.state("zoomed")
    login.configure(bg="#1e1e2f")

    card = tk.Frame(login, bg="white", padx=60, pady=50)
    card.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        card,
        text="🔐 Owner Login",
        font=("Segoe UI", 26, "bold"),
        bg="white"
    ).pack(pady=25)

    user = tk.Entry(card, font=("Segoe UI", 15))
    user.pack(fill="x", pady=10)

    pwd = tk.Entry(card, font=("Segoe UI", 15), show="*")
    pwd.pack(fill="x", pady=10)

    tk.Button(
        card,
        text="Login",
        font=("Segoe UI", 16, "bold"),
        bg="#4f46e5",
        fg="white",
        relief="flat",
        height=2,
        command=authenticate
    ).pack(fill="x", pady=25)

    login.mainloop()

# ---------------- START ---------------- #

show_login()
