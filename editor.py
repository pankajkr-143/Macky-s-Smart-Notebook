import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkfont
from datetime import datetime
import os

class NoteEditor:
    def __init__(self, parent, db_manager, refresh_callback):
        self.parent = parent
        self.db_manager = db_manager
        self.refresh_callback = refresh_callback
        self.current_note_id = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the editor UI components"""
        # Create main frame
        self.editor_frame = ttk.Frame(self.parent)
        self.editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create toolbar
        self.create_toolbar()
        
        # Create title entry
        self.title_frame = ttk.Frame(self.editor_frame)
        self.title_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.title_frame, text="Title:").pack(side=tk.LEFT)
        self.title_entry = ttk.Entry(self.title_frame)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Create category selection
        self.category_frame = ttk.Frame(self.editor_frame)
        self.category_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.category_frame, text="Category:").pack(side=tk.LEFT)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(self.category_frame, textvariable=self.category_var)
        self.category_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Add new category button
        self.add_category_btn = ttk.Button(self.category_frame, text="+", width=3,
                                         command=self.add_new_category)
        self.add_category_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_categories()
        
        # Create text editor
        self.text_frame = ttk.Frame(self.editor_frame)
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create text widget with scrollbar
        self.text_editor = tk.Text(self.text_frame, wrap=tk.WORD, undo=True)
        self.scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL, command=self.text_editor.yview)
        self.text_editor.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create status bar
        self.status_bar = ttk.Label(self.editor_frame, text="Ready", anchor=tk.W)
        self.status_bar.pack(fill=tk.X, padx=5, pady=2)
        
        # Bind events
        self.text_editor.bind('<KeyRelease>', self.update_status)
        self.title_entry.bind('<KeyRelease>', self.update_status)
        
    def add_new_category(self):
        """Add a new category"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add New Category")
        dialog.geometry("300x100")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Category Name:").pack(pady=5)
        category_entry = ttk.Entry(dialog)
        category_entry.pack(pady=5, padx=5, fill=tk.X)
        
        def save_category():
            category_name = category_entry.get().strip()
            if category_name:
                if self.db_manager.create_category(category_name):
                    self.refresh_categories()
                    self.category_var.set(category_name)
                    dialog.destroy()
                    self.refresh_callback() # Refresh main note list
                else:
                    messagebox.showerror("Error", "Category already exists!")
        
        ttk.Button(dialog, text="Add", command=save_category).pack(pady=5)
        category_entry.focus_set()
    
    def refresh_categories(self):
        """Refresh the category combobox with available categories"""
        categories = self.db_manager.get_categories()
        category_names = [cat[0] for cat in categories]  # Get category names
        
        # Add default categories if they don't exist
        default_categories = ["Work", "Personal", "Study", "Ideas", "Tasks", "Important", "Reference"]
        for cat in default_categories:
            if cat not in category_names:
                self.db_manager.create_category(cat)
        
        # Refresh categories again after adding defaults
        categories = self.db_manager.get_categories()
        category_names = [cat[0] for cat in categories]
        
        self.category_combo['values'] = category_names
        if category_names and not self.category_var.get():
            self.category_combo.set(category_names[0])
    
    def create_toolbar(self):
        """Create the formatting toolbar"""
        self.toolbar = ttk.Frame(self.editor_frame)
        self.toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        # Bold button
        self.bold_btn = ttk.Button(self.toolbar, text="B", width=3, command=self.toggle_bold)
        self.bold_btn.pack(side=tk.LEFT, padx=2)
        
        # Italic button
        self.italic_btn = ttk.Button(self.toolbar, text="I", width=3, command=self.toggle_italic)
        self.italic_btn.pack(side=tk.LEFT, padx=2)
        
        # Underline button
        self.underline_btn = ttk.Button(self.toolbar, text="U", width=3, command=self.toggle_underline)
        self.underline_btn.pack(side=tk.LEFT, padx=2)
        
        # Separator
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Save button
        self.save_btn = ttk.Button(self.toolbar, text="Save", command=self.save_note)
        self.save_btn.pack(side=tk.LEFT, padx=2)
        
        # Save to file button
        self.save_file_btn = ttk.Button(self.toolbar, text="Save to File", 
                                      command=self.save_to_file)
        self.save_file_btn.pack(side=tk.LEFT, padx=2)
        
        # Delete button
        self.delete_btn = ttk.Button(self.toolbar, text="Delete", command=self.delete_note)
        self.delete_btn.pack(side=tk.LEFT, padx=2)
    
    def toggle_bold(self):
        """Toggle bold formatting"""
        try:
            current_tags = self.text_editor.tag_names("sel.first")
            if "bold" in current_tags:
                self.text_editor.tag_remove("bold", "sel.first", "sel.last")
            else:
                self.text_editor.tag_add("bold", "sel.first", "sel.last")
                self.text_editor.tag_configure("bold", font=tkfont.Font(weight="bold"))
        except tk.TclError:
            pass
    
    def toggle_italic(self):
        """Toggle italic formatting"""
        try:
            current_tags = self.text_editor.tag_names("sel.first")
            if "italic" in current_tags:
                self.text_editor.tag_remove("italic", "sel.first", "sel.last")
            else:
                self.text_editor.tag_add("italic", "sel.first", "sel.last")
                self.text_editor.tag_configure("italic", font=tkfont.Font(slant="italic"))
        except tk.TclError:
            pass
    
    def toggle_underline(self):
        """Toggle underline formatting"""
        try:
            current_tags = self.text_editor.tag_names("sel.first")
            if "underline" in current_tags:
                self.text_editor.tag_remove("underline", "sel.first", "sel.last")
            else:
                self.text_editor.tag_add("underline", "sel.first", "sel.last")
                self.text_editor.tag_configure("underline", underline=1)
        except tk.TclError:
            pass
    
    def update_status(self, event=None):
        """Update the status bar with word count and other information"""
        content = self.text_editor.get("1.0", tk.END)
        words = len(content.split())
        chars = len(content)
        self.status_bar.config(text=f"Words: {words} | Characters: {chars}")
    
    def load_note(self, note_id):
        """Load a note into the editor"""
        self.current_note_id = note_id
        note = self.db_manager.get_note(note_id)
        
        if note:
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, note[2])  # title
            
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert("1.0", note[3])  # content
            
            # Set category if it exists
            if note[6]:  # category
                self.category_var.set(note[6])
            
            self.update_status()
    
    def save_note(self):
        """Save the current note"""
        title = self.title_entry.get().strip()
        content = self.text_editor.get("1.0", tk.END).strip()
        category = self.category_var.get()
        
        if not title:
            messagebox.showerror("Error", "Title cannot be empty!")
            return
        
        if not category:
            messagebox.showerror("Error", "Please select a category!")
            return
        
        if self.current_note_id:
            # Update existing note
            self.db_manager.update_note(
                self.current_note_id,
                title=title,
                content=content,
                category=category
            )
        else:
            # Create new note
            self.current_note_id = self.db_manager.create_note(
                title=title,
                content=content,
                category=category
            )
        
        self.status_bar.config(text="Note saved successfully!")
        self.refresh_callback() # Refresh main note list
    
    def delete_note(self):
        """Delete the current note"""
        if not self.current_note_id:
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this note?"):
            self.db_manager.delete_note(self.current_note_id)
            self.clear_editor()
            self.status_bar.config(text="Note deleted successfully!")
            self.refresh_callback() # Refresh main note list after deletion
    
    def clear_editor(self):
        """Clear the editor"""
        self.current_note_id = None
        self.title_entry.delete(0, tk.END)
        self.text_editor.delete("1.0", tk.END)
        self.category_var.set('')
        self.update_status()
    
    def save_to_file(self):
        """Save the current note to a text file"""
        title = self.title_entry.get().strip()
        content = self.text_editor.get("1.0", tk.END).strip()
        
        if not title:
            messagebox.showerror("Error", "Title cannot be empty!")
            return
        
        # Get save location from user
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"{title}.txt"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {title}\n")
                    f.write(f"Category: {self.category_var.get()}\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("\n" + "="*50 + "\n\n")
                    f.write(content)
                self.status_bar.config(text=f"Note saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}") 