from db import get_db_path, init_db

if __name__ == "__main__":
    db_path = get_db_path()
    print(f"Initializing database at {db_path}")
    init_db()
