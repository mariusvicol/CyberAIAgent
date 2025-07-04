import psycopg2
from psycopg2 import sql, extras
import bcrypt
import re

class UserManager:
    def __init__(self, db_config):
        self.db_config = db_config

    def connect(self):
        return psycopg2.connect(**self.db_config)

    def validate_username(self, username):
        # Username să conțină doar litere, cifre, underscore, min 3 caractere
        return re.match(r"^\w{3,}$", username) is not None

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

    def create_user(self, username, password):
        if not self.validate_username(username):
            raise ValueError("Invalid username format.")
        hashed_pw = self.hash_password(password)
        try:
            with self.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                        (username, hashed_pw)
                    )
                    conn.commit()
        except psycopg2.Error as e:
            # Log error intern, nu afișa detalii utilizatorului
            print(f"Database error: {e}")
            raise

    def authenticate_user(self, username, password):
        try:
            with self.connect() as conn:
                with conn.cursor(cursor_factory=extras.DictCursor) as cur:
                    cur.execute(
                        "SELECT password_hash FROM users WHERE username = %s",
                        (username,)
                    )
                    row = cur.fetchone()
                    if row is None:
                        return False
                    return self.check_password(password, row['password_hash'])
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            return False

# Exemplu de folosire:
if __name__ == "__main__":
    db_config = {
        "dbname": "mydb",
        "user": "myuser",
        "password": "mypassword",
        "host": "localhost",
        "port": 5432,
    }

    manager = UserManager(db_config)

    # Creare user securizat
    try:
        manager.create_user("valid_user123", "S3cureP@ssw0rd!")
        print("User created successfully.")
    except Exception as e:
        print("Failed to create user:", e)

    # Autentificare user
    is_authenticated = manager.authenticate_user("valid_user123", "S3cureP@ssw0rd!")
    print("Authentication success:", is_authenticated)
