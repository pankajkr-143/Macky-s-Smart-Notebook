import tkinter as tk
from tkinter import ttk, messagebox

class Dashboard:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dashboard UI"""
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for different sections
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Statistics tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")
        self.setup_stats_tab()
        
        # Categories tab
        self.categories_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.categories_frame, text="Categories")
        self.setup_categories_tab()
    
    def setup_stats_tab(self):
        """Setup statistics tab"""
        # Stats container
        stats_container = ttk.LabelFrame(self.stats_frame, text="Note Statistics")
        stats_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Total notes
        self.total_notes_label = ttk.Label(stats_container, text="Total Notes: 0")
        self.total_notes_label.pack(pady=5)
        
        # Pinned notes
        self.pinned_notes_label = ttk.Label(stats_container, text="Pinned Notes: 0")
        self.pinned_notes_label.pack(pady=5)
        
        # Notes by category
        self.category_frame = ttk.LabelFrame(stats_container, text="Notes by Category")
        self.category_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add refresh button
        ttk.Button(self.stats_frame, text="Refresh Stats", 
                  command=self.update_stats).pack(pady=10)
        
        # Initial stats update
        self.update_stats()
    
    def setup_categories_tab(self):
        """Setup categories management tab"""
        # Category list
        self.category_list = ttk.Treeview(self.categories_frame, 
                                        columns=("Name", "Color"),
                                        show="headings")
        self.category_list.heading("Name", text="Name")
        self.category_list.heading("Color", text="Color")
        self.category_list.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add category frame
        add_frame = ttk.Frame(self.categories_frame)
        add_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(add_frame, text="New Category:").pack(side=tk.LEFT, padx=5)
        self.new_category = ttk.Entry(add_frame)
        self.new_category.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Button(add_frame, text="Add", 
                  command=self.add_category).pack(side=tk.LEFT, padx=5)
        
        # Delete button
        ttk.Button(self.categories_frame, text="Delete Selected", 
                  command=self.delete_category).pack(pady=5)
        
        # Initial categories load
        self.refresh_categories()
    
    def update_stats(self):
        """Update statistics display"""
        stats = self.db_manager.get_note_stats()
        
        # Update total notes
        self.total_notes_label.config(text=f"Total Notes: {stats['total_notes']}")
        
        # Update pinned notes
        self.pinned_notes_label.config(text=f"Pinned Notes: {stats['pinned_notes']}")
        
        # Update category stats
        for widget in self.category_frame.winfo_children():
            widget.destroy()
        
        for category, count in stats['notes_by_category'].items():
            ttk.Label(self.category_frame, 
                     text=f"{category}: {count} notes").pack(pady=2)
    
    def refresh_categories(self):
        """Refresh category list"""
        # Clear current items
        for item in self.category_list.get_children():
            self.category_list.delete(item)
        
        # Get categories from database
        categories = self.db_manager.get_categories()
        
        # Add categories to list
        for category in categories:
            self.category_list.insert('', 'end', values=category)
    
    def add_category(self):
        """Add a new category"""
        name = self.new_category.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a category name")
            return
        
        if self.db_manager.create_category(name):
            self.new_category.delete(0, tk.END)
            self.refresh_categories()
            self.update_stats()
        else:
            messagebox.showerror("Error", "Category already exists")
    
    def delete_category(self):
        """Delete selected category"""
        selection = self.category_list.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a category to delete")
            return
        
        category = self.category_list.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete the category '{category}'?"):
            self.db_manager.delete_category(category)
            self.refresh_categories()
            self.update_stats() 