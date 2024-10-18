import tkinter as tk
from tkinter import messagebox, filedialog
import re

# Main
root = tk.Tk()
root.title("M3U Group Title Editor")

# Fönsterstorlek
root.geometry("600x400")

# Listor för group titles
all_group_titles = []
selected_group_titles = []

# Funktion för att uppdatera listbox
def update_listbox(listbox, items):
    listbox.delete(0, tk.END)
    for item in items:
        listbox.insert(tk.END, item)

# Funktion för att ladda .m3u och ta ut group-titles
def load_m3u_file():
    global all_group_titles
    file_path = filedialog.askopenfilename(filetypes=[("M3U files", "*.m3u")])
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            # Ta ut unika group-titles
            all_group_titles = []
            for line in lines:
                match = re.search(r'group-title="([^"]+)"', line)
                if match:
                    group_title = match.group(1)
                    if group_title not in all_group_titles:
                        all_group_titles.append(group_title)

            update_listbox(left_listbox, all_group_titles)
            messagebox.showinfo("Success", f"Loaded {len(all_group_titles)} group titles from the file.")
            
            # Lagra sökväg och rader
            left_listbox.file_path = file_path
            left_listbox.lines = lines

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load the file: {e}")

# Funktion för att föra över från vänstra containern till högra
def transfer_selected():
    selected_indices = left_listbox.curselection()
    selected_titles = [left_listbox.get(i) for i in selected_indices]
    for title in selected_titles:
        if title in all_group_titles:
            all_group_titles.remove(title)
            selected_group_titles.append(title)

    update_listbox(left_listbox, all_group_titles)
    update_listbox(right_listbox, selected_group_titles)

# Funktion för att spara filtrerad .m3u fil
def save_m3u_file():
    if not hasattr(left_listbox, 'file_path') or not hasattr(left_listbox, 'lines'):
        messagebox.showerror("Error", "Please load an .m3u file first.")
        return

    file_path = left_listbox.file_path
    lines = left_listbox.lines

    # Samla ihop group-titles som ska sparas
    kept_group_titles = selected_group_titles

    # Filtrera rader
    new_lines = []
    skip_next = False
    for line in lines:
        if skip_next:
            skip_next = False
            continue

        match = re.search(r'group-title="([^"]+)"', line)
        if match:
            group_title = match.group(1)
            if group_title in kept_group_titles:
                new_lines.append(line)
            else:
                skip_next = True 
        else:
            new_lines.append(line)

    # Skriv rader till ny fil
    try:
        new_file_path = file_path.replace(".m3u", "_filtered.m3u")
        with open(new_file_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
        messagebox.showinfo("Success", f"The file has been saved as: {new_file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save the file: {e}")

# Layout
top_frame = tk.Frame(root)
middle_frame = tk.Frame(root)
bottom_frame = tk.Frame(root)
top_frame.pack(pady=5)
middle_frame.pack(fill="both", expand=True, padx=10, pady=5)
bottom_frame.pack(pady=5)

# Browse-knapp
browse_button = tk.Button(top_frame, text="Browse for .m3u file", command=load_m3u_file)
browse_button.pack()

# Containers
left_listbox = tk.Listbox(middle_frame, selectmode="multiple", exportselection=False)
left_scrollbar = tk.Scrollbar(middle_frame, orient="vertical", command=left_listbox.yview)
left_listbox.configure(yscrollcommand=left_scrollbar.set)

right_listbox = tk.Listbox(middle_frame, selectmode="multiple", exportselection=False)
right_scrollbar = tk.Scrollbar(middle_frame, orient="vertical", command=right_listbox.yview)
right_listbox.configure(yscrollcommand=right_scrollbar.set)

left_listbox.pack(side="left", fill="both", expand=True)
left_scrollbar.pack(side="left", fill="y")
right_listbox.pack(side="right", fill="both", expand=True)
right_scrollbar.pack(side="right", fill="y")

# Transfer-knapp
transfer_button = tk.Button(middle_frame, text=">>", command=transfer_selected)
transfer_button.pack(padx=5)

# Save-knapp
save_button = tk.Button(bottom_frame, text="Save", command=save_m3u_file)
save_button.pack()

root.mainloop()