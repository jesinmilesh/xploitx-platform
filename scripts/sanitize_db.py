import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "CTFd", "ctfd.db")
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("UPDATE config SET value='' WHERE key IN ('mail_password', 'brevo_api_key')")
    conn.commit()
    print("Sanitized config entries. Changes:", conn.total_changes)
    
    # Verify
    c.execute("SELECT key, value FROM config WHERE key IN ('mail_password', 'brevo_api_key')")
    print("Current values:", c.fetchall())
    conn.close()
