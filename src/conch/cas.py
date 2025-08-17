import os
import hashlib
import sqlite3
from typing import Optional

MAX_SIZE = 4 * 1024 * 1024  # 4MB

class CAS:
    def __init__(self, root: str):
        self.root = root
        self.store_dir = os.path.join(root, 'store')
        self.db_path = os.path.join(root, 'index.db')
        os.makedirs(self.store_dir, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS pinned (
            hash TEXT PRIMARY KEY
        )''')
        conn.commit()
        conn.close()

    def _hash_content(self, content: str) -> str:
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _get_path(self, hash_: str) -> str:
        prefix = hash_[:2]
        dir_path = os.path.join(self.store_dir, prefix)
        os.makedirs(dir_path, exist_ok=True)
        return os.path.join(dir_path, hash_)

    def put(self, content: str) -> Optional[str]:
        if not isinstance(content, str):
            raise ValueError('Only plaintext is allowed')
        if len(content.encode('utf-8')) > MAX_SIZE:
            raise ValueError('Content too large (>4MB)')
        hash_ = self._hash_content(content)
        path = self._get_path(hash_)
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
        return hash_

    def get(self, hash_: str) -> Optional[str]:
        path = self._get_path(hash_)
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def pin(self, hash_: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO pinned (hash) VALUES (?)', (hash_,))
        conn.commit()
        conn.close()
