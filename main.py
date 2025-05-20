import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
from db_manager import DatabaseManager
from editor import NoteEditor
from auth import AuthManager, AuthWindow
from dashboard import Dashboard

class SmartNotebook:
    def __init__(self, root):
        self.root = root
        self.root.title("Macky's Smart Notebook")
        self.root.geometry("1920x1080")
        
        # Initialize managers
        self.auth_manager = AuthManager()
        self.db_manager = DatabaseManager()
        
        # Show login window
        self.show_login()
    
    def show_login(self):
        """Show login window"""
        self.root.withdraw()  # Hide main window
        AuthWindow(self.root, self.auth_manager, self.on_login_success)
    
    def on_login_success(self):
        """Handle successful login"""
        self.root.deiconify()  # Show main window
        self.db_manager.set_current_user(self.auth_manager.current_user['id'])
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main UI"""
        # Configure styles for themes
        self.style = ttk.Style()
        self.set_theme('light') # Default theme
        
        # Create header
        self.header_frame = ttk.Frame(self.root)
        self.header_frame.pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Label(self.header_frame, text="Macky's Smart Notebook", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        # Real-time clock in header
        self.time_label = ttk.Label(self.header_frame, text="", anchor=tk.E)
        self.time_label.pack(side=tk.RIGHT)
        self.update_time()
        
        # Create main container
        self.main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create sidebar
        self.sidebar = ttk.Frame(self.main_container, width=200)
        self.main_container.add(self.sidebar, weight=1)
        
        # Create main content area
        self.content_area = ttk.Frame(self.main_container)
        self.main_container.add(self.content_area, weight=4)
        
        self.setup_sidebar()
        self.setup_content_area()
        
        # Initialize note editor
        self.note_editor = NoteEditor(self.content_area, self.db_manager, self.refresh_note_list)
        
        # Create footer
        self.footer_frame = ttk.Frame(self.root)
        self.footer_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Developer details in footer
        ttk.Label(self.footer_frame, text="Developed by: Pankaj Kumar").pack(side=tk.LEFT, padx=10)
        ttk.Label(self.footer_frame, text="Contact: mrmacky143@gmail.com").pack(side=tk.LEFT, padx=10)
        
        # Load initial notes
        self.refresh_note_list()
    
    def update_time(self):
        """Update the time label in the header"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"Current Time: {now}")
        self.root.after(1000, self.update_time) # Update every 1 second
    
    def set_theme(self, theme_name):
        """Apply the specified theme"""
        if theme_name == 'light':
            self.style.theme_use('default') # Use default theme
            # Add custom light theme configurations if needed
        elif theme_name == 'dark':
            # Example dark theme styles (you might need to define more)
            self.style.theme_use('clam') # clam theme is often used as a base for custom themes
            self.style.configure('.', background='#333', foreground='#ddd')
            self.style.configure('TFrame', background='#333')
            self.style.configure('TLabel', background='#333', foreground='#ddd')
            self.style.configure('TButton', background='#555', foreground='#ddd')
            self.style.map('TButton', background=[('active', '#777')])
            self.style.configure('Treeview', background='#555', foreground='#ddd', fieldbackground='#555')
            self.style.map('Treeview', background=[('selected', '#777')])
            self.style.configure('Treeview.Heading', background='#666', foreground='#ddd')
            # You would need to add more configurations for other widgets (Entry, Combobox, etc.)
            
    def setup_sidebar(self):
        """Setup the sidebar with navigation buttons and categories"""
        # User info
        user_frame = ttk.Frame(self.sidebar)
        user_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(user_frame, 
                 text=f"Welcome, {self.auth_manager.current_user['username']}").pack()
        ttk.Button(user_frame, text="Logout", 
                  command=self.logout).pack(pady=5)
        
        # New Note button
        new_note_btn = ttk.Button(self.sidebar, text="New Note", 
                                 command=self.create_new_note)
        new_note_btn.pack(pady=10, padx=5, fill=tk.X)
        
        # Dashboard button
        dashboard_btn = ttk.Button(self.sidebar, text="Dashboard", 
                                 command=self.show_dashboard)
        dashboard_btn.pack(pady=5, padx=5, fill=tk.X)
        
        # Search frame
        search_frame = ttk.Frame(self.sidebar)
        search_frame.pack(pady=10, padx=5, fill=tk.X)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(fill=tk.X)
        
        # Categories section
        categories_frame = ttk.LabelFrame(self.sidebar, text="Categories")
        categories_frame.pack(pady=10, padx=5, fill=tk.BOTH, expand=True)
        
        # Add category button
        add_cat_btn = ttk.Button(categories_frame, text="+ Add Category",
                                command=self.add_new_category)
        add_cat_btn.pack(pady=5, padx=5, fill=tk.X)
        
        # Create a frame for category buttons with scrollbar
        cat_buttons_frame = ttk.Frame(categories_frame)
        cat_buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar for categories
        cat_scrollbar = ttk.Scrollbar(cat_buttons_frame)
        cat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create canvas for category buttons
        self.cat_canvas = tk.Canvas(cat_buttons_frame)
        self.cat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure canvas scrollbar
        self.cat_canvas.configure(yscrollcommand=cat_scrollbar.set)
        cat_scrollbar.configure(command=self.cat_canvas.yview)
        
        # Create frame inside canvas for category buttons
        self.cat_buttons_container = ttk.Frame(self.cat_canvas)
        self.cat_canvas.create_window((0, 0), window=self.cat_buttons_container, anchor='nw')
        
        # Bind canvas resize
        self.cat_buttons_container.bind('<Configure>', 
            lambda e: self.cat_canvas.configure(scrollregion=self.cat_canvas.bbox("all")))
        
        # Load initial categories
        self.refresh_categories()
        
        # Theme selection buttons
        theme_frame = ttk.LabelFrame(self.sidebar, text="Theme")
        theme_frame.pack(pady=10, padx=5, fill=tk.X)
        
        ttk.Button(theme_frame, text="Light", command=lambda: self.set_theme('light')).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        ttk.Button(theme_frame, text="Dark", command=lambda: self.set_theme('dark')).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
    
    def add_new_category(self):
        """Add a new category"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Category")
        dialog.geometry("300x100")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Category Name:").pack(pady=5)
        category_entry = ttk.Entry(dialog)
        category_entry.pack(pady=5, padx=5, fill=tk.X)
        
        def save_category():
            category_name = category_entry.get().strip()
            if category_name:
                if self.db_manager.create_category(category_name):
                    self.refresh_categories()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Category already exists!")
        
        ttk.Button(dialog, text="Add", command=save_category).pack(pady=5)
        category_entry.focus_set()
    
    def refresh_categories(self):
        """Refresh the category buttons in the sidebar"""
        # Clear existing category buttons
        for widget in self.cat_buttons_container.winfo_children():
            widget.destroy()
        
        # Get categories from database
        categories = self.db_manager.get_categories()
        
        # Add "All Notes" button at the top
        all_notes_btn = ttk.Button(self.cat_buttons_container, text="All Notes",
                                  command=lambda: self.filter_by_category(None))
        all_notes_btn.pack(pady=2, padx=5, fill=tk.X)
        
        # Add category buttons
        for category in categories:
            btn = ttk.Button(self.cat_buttons_container, text=category[0],
                           command=lambda c=category[0]: self.filter_by_category(c))
            btn.pack(pady=2, padx=5, fill=tk.X)
    
    def setup_content_area(self):
        """Setup the main content area with note list"""
        # Create note list
        self.note_list = ttk.Treeview(self.content_area, 
                                     columns=("Title", "Category", "Modified"),
                                     show="headings")
        self.note_list.heading("Title", text="Title")
        self.note_list.heading("Category", text="Category")
        self.note_list.heading("Modified", text="Last Modified")
        self.note_list.column("Title", width=200)
        self.note_list.column("Category", width=100)
        self.note_list.column("Modified", width=150)
        self.note_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar to note list
        scrollbar = ttk.Scrollbar(self.content_area, orient=tk.VERTICAL, 
                                 command=self.note_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.note_list.configure(yscrollcommand=scrollbar.set)
        
        # Bind double-click event to open note
        self.note_list.bind("<Double-1>", self.open_note)
    
    def create_new_note(self):
        """Create a new note"""
        self.note_editor.clear_editor()
        self.note_list.selection_remove(*self.note_list.selection())
    
    def open_note(self, event):
        """Open selected note"""
        selection = self.note_list.selection()
        if selection:
            note_id = self.note_list.item(selection[0])['values'][0]
            self.note_editor.load_note(note_id)
    
    def filter_by_category(self, category):
        """Filter notes by category"""
        self.refresh_note_list(category=category)
    
    def on_search_change(self, *args):
        """Handle search input changes"""
        search_term = self.search_var.get()
        self.refresh_note_list(search_term=search_term)
    
    def refresh_note_list(self, category=None, search_term=None):
        """Refresh the note list with current filters"""
        # Clear current items
        for item in self.note_list.get_children():
            self.note_list.delete(item)
        
        # Get notes from database
        notes = self.db_manager.get_all_notes(category=category, search_term=search_term)
        
        # Add notes to list
        for note in notes:
            self.note_list.insert('', 'end', values=(
                note[0],  # id
                note[2],  # title
                note[6] or "Uncategorized",  # category
                note[5]   # modified_at
            ))
    
    def show_dashboard(self):
        """Show dashboard window"""
        dashboard_window = tk.Toplevel(self.root)
        dashboard_window.title("Dashboard")
        dashboard_window.geometry("800x600")
        
        dashboard = Dashboard(dashboard_window, self.db_manager)
    
    def logout(self):
        """Handle user logout"""
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            self.auth_manager.logout()
            self.db_manager.set_current_user(None)
            
            # Clear UI
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Show login window
            self.show_login()
    
    def __del__(self):
        """Cleanup when the application closes"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()

def main():
    root = tk.Tk()
    app = SmartNotebook(root)
    root.mainloop()

if __name__ == "__main__":
    main() 