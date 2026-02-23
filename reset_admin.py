import pymysql
import os
import bcrypt
from dotenv import load_dotenv

load_dotenv()

def hash_password(password: str) -> str:
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def reset_admin():
    conn = pymysql.connect(
        host=os.environ.get("MYSQL_HOST"),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE")
    )
    cursor = conn.cursor()
    
    username = input("Enter admin username (default: admin): ").strip() or "admin"
    password = input("Enter new password: ").strip()
    
    if not password:
        print("Password cannot be empty.")
        return
        
    hashed_password = hash_password(password)
    
    # Check if user exists
    cursor.execute("SELECT id FROM tb_user WHERE username = %s", (username,))
    result = cursor.fetchone()
    
    if result:
        # Update existing user
        cursor.execute("UPDATE tb_user SET password = %s WHERE username = %s", (hashed_password, username))
        print(f"Password for user '{username}' has been updated.")
    else:
        # Create new user
        print(f"User '{username}' not found. Creating new admin user...")
        cursor.execute("INSERT INTO tb_user (username, password) VALUES (%s, %s)", (username, hashed_password))
        print(f"User '{username}' created successfully.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    reset_admin()
