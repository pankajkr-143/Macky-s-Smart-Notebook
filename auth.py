import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import os

class AuthManager:
    def __init__(self, db_name='notes.db'):
        self.db_name = db_name
        self.current_user = None
        self.init_auth_db()
    
    def init_auth_db(self):
        """Initialize authentication database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, password, email=None):
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            hashed_password = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, password, email)
                VALUES (?, ?, ?)
            ''', (username, hashed_password, email))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def login(self, username, password):
        """Login user"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        hashed_password = self.hash_password(password)
        
        cursor.execute('''
            SELECT id, username FROM users
            WHERE username = ? AND password = ?
        ''', (username, hashed_password))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            self.current_user = {'id': user[0], 'username': user[1]}
            return True
        return False
    
    def logout(self):
        """Logout current user"""
        self.current_user = None

class AuthWindow:
    def __init__(self, parent, auth_manager, on_login_success):
        self.parent = parent
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success
        
        self.window = tk.Toplevel(parent)
        self.window.title("Login / Register")
        self.window.geometry("300x400")
        self.window.resizable(False, False)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the authentication UI"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Login tab
        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="Login")
        self.setup_login_tab()
        
        # Register tab
        self.register_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.register_frame, text="Register")
        self.setup_register_tab()
    
    def setup_login_tab(self):
        """Setup login tab UI"""
        # Username
        ttk.Label(self.login_frame, text="Username:").pack(pady=5)
        self.login_username = ttk.Entry(self.login_frame)
        self.login_username.pack(pady=5)
        
        # Password
        ttk.Label(self.login_frame, text="Password:").pack(pady=5)
        self.login_password = ttk.Entry(self.login_frame, show="*")
        self.login_password.pack(pady=5)
        
        # Login button
        ttk.Button(self.login_frame, text="Login", command=self.handle_login).pack(pady=20)
    
    def setup_register_tab(self):
        """Setup register tab UI"""
        # Username
        ttk.Label(self.register_frame, text="Username:").pack(pady=5)
        self.register_username = ttk.Entry(self.register_frame)
        self.register_username.pack(pady=5)
        
        # Email
        ttk.Label(self.register_frame, text="Email:").pack(pady=5)
        self.register_email = ttk.Entry(self.register_frame)
        self.register_email.pack(pady=5)
        
        # Password
        ttk.Label(self.register_frame, text="Password:").pack(pady=5)
        self.register_password = ttk.Entry(self.register_frame, show="*")
        self.register_password.pack(pady=5)
        
        # Confirm Password
        ttk.Label(self.register_frame, text="Confirm Password:").pack(pady=5)
        self.register_confirm_password = ttk.Entry(self.register_frame, show="*")
        self.register_confirm_password.pack(pady=5)
        
        # Register button
        ttk.Button(self.register_frame, text="Register", command=self.handle_register).pack(pady=20)
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if self.auth_manager.login(username, password):
            self.on_login_success()
            self.window.destroy()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def handle_register(self):
        """Handle registration attempt"""
        username = self.register_username.get().strip()
        email = self.register_email.get().strip()
        password = self.register_password.get()
        confirm_password = self.register_confirm_password.get()
        
        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if self.auth_manager.register(username, password, email):
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.notebook.select(0)  # Switch to login tab
        else:
            messagebox.showerror("Error", "Username or email already exists") 