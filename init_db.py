import pymysql
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()

# Passlib 1.7.4 has compatibility issues with bcrypt 4.0+. 
# We can use bcrypt directly for hashing in this script to avoid the error.

def hash_password(password: str) -> str:
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def init_db():
    conn = pymysql.connect(
        host=os.environ.get("MYSQL_HOST"),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE")
    )
    cursor = conn.cursor()
    
    # Read SQL file
    # Ensure db/init.sql uses 'CREATE TABLE IF NOT EXISTS' to avoid data loss
    with open("db/init.sql", "r") as f:
        sql_content = f.read()
        
    # Split by semicolon to execute multiple statements
    statements = sql_content.split(';')
    
    for statement in statements:
        if statement.strip():
            try:
                cursor.execute(statement)
            except Exception as e:
                # Log error but don't stop execution unless critical
                print(f"Error executing statement: {e}")
    
    # Check if admin exists
    # Check if tb_user exists first to avoid error if table creation failed
    try:
        cursor.execute("SHOW TABLES LIKE 'tb_user'")
        if cursor.fetchone():
            cursor.execute("SELECT * FROM tb_user WHERE username = 'admin'")
            if not cursor.fetchone():
                hashed_password = hash_password("admin")
                print(f"Creating default admin user with hashed password...")
                cursor.execute("INSERT INTO tb_user (username, password) VALUES (%s, %s)", ("admin", hashed_password))
    except Exception as e:
        print(f"Error checking/creating admin user: {e}")
        
    conn.commit()
    conn.close()
    print("Database initialized.")

if __name__ == "__main__":
    init_db()
