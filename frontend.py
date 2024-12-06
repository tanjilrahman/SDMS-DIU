from tkinter import *
from tkinter import ttk, messagebox
import backend
import sqlite3
import json


# Tooltip function for better UX
def create_tooltip(widget, text):
    tooltip = Toplevel(widget)
    tooltip.withdraw()
    tooltip.overrideredirect(True)
    tooltip_label = Label(tooltip, text=text, bg="lightyellow", fg="black", relief="solid", borderwidth=1, padx=5, pady=3)
    tooltip_label.pack()

    def show_tooltip(event):
        tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        tooltip.deiconify()

    def hide_tooltip(event):
        tooltip.withdraw()

    widget.bind("<Enter>", show_tooltip)
    widget.bind("<Leave>", hide_tooltip)


# Get content of the selected row
def get_selected_row(event):
    global selected_tuple
    selected_item = tree.selection()
    if selected_item:
        selected_tuple = tree.item(selected_item[0])['values']
        clear_entries()
        e1.insert(END, selected_tuple[1])  # First Name
        e2.insert(END, selected_tuple[2])  # Last Name
        e3.insert(END, selected_tuple[3])  # Term
        e4.insert(END, selected_tuple[4])  # GPA


# Command functions
def view_command():
    tree.delete(*tree.get_children())
    for row in backend.view():
        tree.insert("", "end", values=row)


def view_high_gpa_command():
    tree.delete(*tree.get_children())
    for row in backend.view_high_gpa_students():
        tree.insert("", "end", values=row)


def view_log_command():
    '''Show the log of updates from data1_log table in a new window with a table view and more readable data.'''
    # Fetch logs from the database
    conn = sqlite3.connect("Students.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM data1_log")
    rows = cur.fetchall()
    conn.close()

    # Mapping of column abbreviations to full names
    column_map = {
        "fn": "First Name",
        "ln": "Last Name",
        "term": "Term",
        "gpa": "GPA",
        "grade": "Grade",
        "id": "ID"
    }

    # Create a new popup window
    log_window = Toplevel(wind)
    log_window.title("Update Logs")
    log_window.geometry("1000x400")

    # Add a label for the title
    log_label = Label(log_window, text="Update Logs", font=("Arial", 16, "bold"), fg="blue")
    log_label.pack(pady=10)

    # Create a Treeview widget to display logs in a table
    tree = ttk.Treeview(
        log_window,
        columns=("Log ID", "Old Data", "New Data", "Change Time"),
        show="headings"
    )
    tree.heading("Log ID", text="Log ID")
    tree.heading("Old Data", text="Old Data")
    tree.heading("New Data", text="New Data")
    tree.heading("Change Time", text="Change Time")
    tree.column("Log ID", width=50, anchor="center")
    tree.column("Old Data", width=400, anchor="center")
    tree.column("New Data", width=400, anchor="center")
    tree.column("Change Time", width=150, anchor="center")

    # Format and insert logs into the Treeview
    for row in rows:
        log_id = row[0]
        old_data = json.loads(row[1]) if row[1] else {}
        new_data = json.loads(row[2]) if row[2] else {}
        change_time = row[3]

        # Map keys to their full names
        old_data_str = ', '.join([f"{column_map.get(key, key)}: {value}" for key, value in old_data.items()])
        new_data_str = ', '.join([f"{column_map.get(key, key)}: {value}" for key, value in new_data.items()])

        # Insert formatted row into Treeview
        tree.insert("", "end", values=(log_id, old_data_str, new_data_str, change_time))

    # Add a scrollbar to the Treeview
    scroll = Scrollbar(log_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    scroll.pack(side=RIGHT, fill=Y)

    # Pack the Treeview widget
    tree.pack(fill=BOTH, expand=True, padx=10, pady=10)


def search_command():
    tree.delete(*tree.get_children())
    for row in backend.search(fn.get(), ln.get(), term.get(), gpa.get()):
        tree.insert("", "end", values=row)
    clear_entries()


def add_command():
    if fn.get() and ln.get() and term.get() and gpa.get():
        backend.insert(fn.get(), ln.get(), term.get(), gpa.get())
        clear_entries()
        view_command()
        messagebox.showinfo("Success", "Student added successfully!")
    else:
        messagebox.showerror("Error", "All fields are required!")


def update_command():
    if selected_tuple:
        backend.update(selected_tuple[0], fn.get(), ln.get(), term.get(), gpa.get())
        clear_entries()
        view_command()
        messagebox.showinfo("Success", "Student updated successfully!")
    else:
        messagebox.showerror("Error", "No student selected!")


def delete_command():
    if selected_tuple:
        backend.delete(selected_tuple[0])
        clear_entries()
        view_command()
        messagebox.showinfo("Success", "Student deleted successfully!")
    else:
        messagebox.showerror("Error", "No student selected!")


def delete_data_command():
    backend.delete_data()
    view_command()
    messagebox.showinfo("Success", "All student records deleted!")


def clear_entries():
    e1.delete(0, END)
    e2.delete(0, END)
    e3.delete(0, END)
    e4.delete(0, END)


def clear_command():
    tree.delete(*tree.get_children())
    clear_entries()


# Create main window
wind = Tk()
wind.title("Student Database Management System")
wind.geometry("550x700")
wind.resizable(True, True)

# Variables
fn = StringVar()
ln = StringVar()
term = StringVar()
gpa = StringVar()

# Frames for better layout
top_frame = Frame(wind, pady=10)
top_frame.pack(fill=X)

middle_frame = Frame(wind, padx=20, pady=10)
middle_frame.pack(fill=X)

listbox_frame = Frame(wind, pady=10)
listbox_frame.pack(fill=BOTH, expand=True)

button_frame = Frame(wind, pady=10)
button_frame.pack(fill=X)

# Title
title_label = Label(top_frame, text="Student Database", font=("Arial", 20, "bold"), fg="blue")
title_label.pack()

# Input labels and entry fields
Label(middle_frame, text="ID").grid(row=0, column=0, padx=5, pady=5, sticky=W)
e1 = Entry(middle_frame, textvariable=fn, width=20)
e1.grid(row=0, column=1, padx=5, pady=5)

Label(middle_frame, text="First Name").grid(row=0, column=0, padx=5, pady=5, sticky=W)
e1 = Entry(middle_frame, textvariable=fn, width=20)
e1.grid(row=0, column=1, padx=5, pady=5)

Label(middle_frame, text="Last Name").grid(row=0, column=2, padx=5, pady=5, sticky=W)
e2 = Entry(middle_frame, textvariable=ln, width=20)
e2.grid(row=0, column=3, padx=5, pady=5)

Label(middle_frame, text="Term").grid(row=1, column=0, padx=5, pady=5, sticky=W)
e3 = Entry(middle_frame, textvariable=term, width=20)
e3.grid(row=1, column=1, padx=5, pady=5)

Label(middle_frame, text="GPA").grid(row=1, column=2, padx=5, pady=5, sticky=W)
e4 = Entry(middle_frame, textvariable=gpa, width=20)
e4.grid(row=1, column=3, padx=5, pady=5)


# Treeview for students display
tree = ttk.Treeview(listbox_frame, columns=("ID", "First Name", "Last Name", "Term", "GPA", "Grade"), show="headings")
tree.heading("ID", text="ID")
tree.heading("First Name", text="First Name")
tree.heading("Last Name", text="Last Name")
tree.heading("Term", text="Term")
tree.heading("GPA", text="GPA")
tree.heading("Grade", text="Grade")
tree.column("ID", width=20)
tree.column("First Name", width=120)
tree.column("Last Name", width=120)
tree.column("Term", width=100)
tree.column("GPA", width=60)
tree.column("Grade", width=60)
tree.pack(fill=BOTH, expand=True, padx=10, pady=10)

# Bind a row click to get data
tree.bind("<ButtonRelease-1>", get_selected_row)

# Buttons for actions
# Buttons
buttons = [
    ("View All", view_command, "View all student records"),
    ("Search", search_command, "Search students by fields"),
    ("Add New", add_command, "Add a new student record"),
    ("Update", update_command, "Update selected student record"),
    ("Delete", delete_command, "Delete selected student record"),
    ("Clear List", clear_command, "Clear the listbox"),
    ("High GPA Students", view_high_gpa_command, "View students with GPA > 3.0"),
    ("View Logs", view_log_command, "View update logs"),
    ("Delete All", delete_data_command, "Delete all student records"),
    ("Exit", wind.destroy, "Exit the application")
]

for idx, (text, cmd, tooltip_text) in enumerate(buttons):
    btn = Button(button_frame, text=text, width=15, command=cmd)
    btn.grid(row=idx // 4, column=idx % 4, padx=10, pady=5)
    create_tooltip(btn, tooltip_text)

# Start the application
wind.mainloop()
