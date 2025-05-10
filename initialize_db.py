import os
from database import create_database

# Delete the database file if it exists but is empty
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'freadom.db')
if os.path.exists(db_path) and os.path.getsize(db_path) == 0:
    os.remove(db_path)
    print("Removed empty database file.")

# Create the database
create_database()