import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_name='notes.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.current_user_id = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish connection to the database"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        # Notes table with user_id
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                category TEXT,
                is_pinned BOOLEAN DEFAULT 0,
                is_archived BOOLEAN DEFAULT 0,
                tags TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Categories table with user_id
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                color TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, name)
            )
        ''')
        
        # Tags table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Note-Tag relationship table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS note_tags (
                note_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (note_id) REFERENCES notes (id),
                FOREIGN KEY (tag_id) REFERENCES tags (id),
                PRIMARY KEY (note_id, tag_id)
            )
        ''')
        
        self.conn.commit()
    
    def set_current_user(self, user_id):
        """Set the current user ID"""
        self.current_user_id = user_id
    
    def create_note(self, title, content, category=None, tags=None):
        """Create a new note"""
        if not self.current_user_id:
            raise ValueError("No user logged in")
            
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create category if it doesn't exist
        if category:
            self.create_category(category)
            
        self.cursor.execute('''
            INSERT INTO notes (user_id, title, content, created_at, modified_at, category)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.current_user_id, title, content, current_time, current_time, category))
        
        note_id = self.cursor.lastrowid
        
        if tags:
            self.add_tags_to_note(note_id, tags)
        
        self.conn.commit()
        return note_id
    
    def update_note(self, note_id, title=None, content=None, category=None, tags=None):
        """Update an existing note"""
        if not self.current_user_id:
            raise ValueError("No user logged in")
            
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create category if it doesn't exist
        if category:
            self.create_category(category)
        
        if title or content or category:
            update_fields = []
            values = []
            
            if title:
                update_fields.append("title = ?")
                values.append(title)
            if content:
                update_fields.append("content = ?")
                values.append(content)
            if category:
                update_fields.append("category = ?")
                values.append(category)
            
            update_fields.append("modified_at = ?")
            values.append(current_time)
            values.extend([note_id, self.current_user_id])
            
            query = f'''
                UPDATE notes 
                SET {', '.join(update_fields)}
                WHERE id = ? AND user_id = ?
            '''
            self.cursor.execute(query, values)
        
        if tags is not None:
            self.update_note_tags(note_id, tags)
        
        self.conn.commit()
    
    def delete_note(self, note_id):
        """Delete a note"""
        if not self.current_user_id:
            raise ValueError("No user logged in")
            
        self.cursor.execute('''
            DELETE FROM notes 
            WHERE id = ? AND user_id = ?
        ''', (note_id, self.current_user_id))
        self.cursor.execute('DELETE FROM note_tags WHERE note_id = ?', (note_id,))
        self.conn.commit()
    
    def get_note(self, note_id):
        """Get a single note by ID"""
        if not self.current_user_id:
            raise ValueError("No user logged in")
            
        self.cursor.execute('''
            SELECT * FROM notes 
            WHERE id = ? AND user_id = ?
        ''', (note_id, self.current_user_id))
        return self.cursor.fetchone()
    
    def get_all_notes(self, category=None, tags=None, search_term=None):
        """Get all notes with optional filtering"""
        if not self.current_user_id:
            raise ValueError("No user logged in")
            
        query = 'SELECT * FROM notes WHERE user_id = ?'
        params = [self.current_user_id]
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        if search_term:
            query += ' AND (title LIKE ? OR content LIKE ?)'
            search_pattern = f'%{search_term}%'
            params.extend([search_pattern, search_pattern])
        
        query += ' ORDER BY is_pinned DESC, modified_at DESC'
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def create_category(self, name, color=None):
        """Create a new category"""
        if not self.current_user_id:
            raise ValueError("No user logged in")
            
        try:
            self.cursor.execute('''
                INSERT INTO categories (user_id, name, color)
                VALUES (?, ?, ?)
            ''', (self.current_user_id, name, color))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_categories(self):
        """Get all categories for current user"""
        if not self.current_user_id:
            raise ValueError("No user logged in")
            
        self.cursor.execute('''
            SELECT name, color FROM categories
            WHERE user_id = ?
            ORDER BY name
        ''', (self.current_user_id,))
        return self.cursor.fetchall()
    
    def delete_category(self, name):
        """Delete a category"""
        if not self.current_user_id:
            raise ValueError("No user logged in")
            
        self.cursor.execute('''
            DELETE FROM categories
            WHERE user_id = ? AND name = ?
        ''', (self.current_user_id, name))
        self.conn.commit()
    
    def add_tags_to_note(self, note_id, tags):
        """Add tags to a note"""
        for tag in tags:
            # Insert tag if it doesn't exist
            self.cursor.execute('''
                INSERT OR IGNORE INTO tags (name)
                VALUES (?)
            ''', (tag,))
            
            # Get tag ID
            self.cursor.execute('SELECT id FROM tags WHERE name = ?', (tag,))
            tag_id = self.cursor.fetchone()[0]
            
            # Create note-tag relationship
            self.cursor.execute('''
                INSERT OR IGNORE INTO note_tags (note_id, tag_id)
                VALUES (?, ?)
            ''', (note_id, tag_id))
    
    def update_note_tags(self, note_id, tags):
        """Update tags for a note"""
        # Remove existing tags
        self.cursor.execute('DELETE FROM note_tags WHERE note_id = ?', (note_id,))
        
        # Add new tags
        if tags:
            self.add_tags_to_note(note_id, tags)
    
    def get_note_tags(self, note_id):
        """Get all tags for a note"""
        self.cursor.execute('''
            SELECT t.name
            FROM tags t
            JOIN note_tags nt ON t.id = nt.tag_id
            WHERE nt.note_id = ?
        ''', (note_id,))
        return [row[0] for row in self.cursor.fetchall()]
    
    def toggle_pin(self, note_id):
        """Toggle pin status of a note"""
        if not self.current_user_id:
            raise ValueError("No user logged in")
            
        self.cursor.execute('''
            UPDATE notes
            SET is_pinned = NOT is_pinned
            WHERE id = ? AND user_id = ?
        ''', (note_id, self.current_user_id))
        self.conn.commit()
    
    def get_note_stats(self):
        """Get statistics about notes"""
        if not self.current_user_id:
            raise ValueError("No user logged in")
            
        stats = {}
        
        # Total notes
        self.cursor.execute('''
            SELECT COUNT(*) FROM notes
            WHERE user_id = ?
        ''', (self.current_user_id,))
        stats['total_notes'] = self.cursor.fetchone()[0]
        
        # Notes by category
        self.cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM notes
            WHERE user_id = ?
            GROUP BY category
        ''', (self.current_user_id,))
        stats['notes_by_category'] = dict(self.cursor.fetchall())
        
        # Pinned notes
        self.cursor.execute('''
            SELECT COUNT(*) FROM notes
            WHERE user_id = ? AND is_pinned = 1
        ''', (self.current_user_id,))
        stats['pinned_notes'] = self.cursor.fetchone()[0]
        
        return stats
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close() 