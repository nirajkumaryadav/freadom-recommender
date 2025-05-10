import sqlite3
import pandas as pd
import json
import os

# Define the database path using an absolute path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'freadom.db')

def create_database():
    """Create and initialize the database with sample data"""
    # Check if database already exists
    if os.path.exists(DB_PATH):
        # Delete existing empty database
        os.remove(DB_PATH)
        print("Removed empty database file.")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create tables
    c.execute('''
    CREATE TABLE IF NOT EXISTS content (
        id INTEGER PRIMARY KEY,
        title TEXT,
        text TEXT,
        author TEXT,
        genre TEXT,
        topics TEXT,
        reading_level REAL,
        age_range TEXT,
        popularity INTEGER
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        age INTEGER,
        reading_level REAL,
        interests TEXT,
        history TEXT
    )
    ''')
    
    # Sample content data
    sample_content = [
        (1, "The Magic Tree", "Once upon a time, there was a magical tree that could grow any fruit you wished for. A young girl named Lily discovered the tree in her backyard. Every day she would ask for a different fruit, and the tree would provide it. One day, she asked for a golden apple, and to her surprise, the tree produced it. The golden apple had magical powers that allowed Lily to talk to animals.", 
         "Jane Smith", "Fantasy", json.dumps(["magic", "nature", "adventure"]), 2.5, "6-8", 42),
        
        (2, "Space Explorers", "Captain Alex and his crew flew to the distant galaxy in search of new planets. Their spaceship, The Discovery, was equipped with the latest technology. They discovered a planet with purple oceans and green clouds. The inhabitants were friendly and showed them around. The explorers learned about their advanced society and shared information about Earth.", 
         "Tom Brown", "Science Fiction", json.dumps(["space", "science", "adventure"]), 3.2, "7-9", 38),
        
        (3, "My Pet Dog", "My dog Spot is my best friend. He likes to play ball in the yard. Spot has brown fur and a white patch on his head. Every morning, he wakes me up by licking my face. I take him for walks in the park, and he likes to chase squirrels. Spot knows many tricks like sit, stay, and roll over. I love my dog very much.", 
         "Sarah Johnson", "Non-fiction", json.dumps(["animals", "pets", "friendship"]), 1.8, "5-7", 56),
        
        (4, "The Lost Dinosaur", "The baby dinosaur couldn't find his mother. He walked through the forest calling for her. Other dinosaurs tried to help him. A friendly pterodactyl flew high to look for his mother. A triceratops let him ride on his back. Finally, they found his mother drinking water at the lake. The baby dinosaur was so happy to be reunited with his family.", 
         "Michael Davis", "Adventure", json.dumps(["dinosaurs", "family", "adventure"]), 2.1, "6-8", 48),
        
        (5, "The Ocean's Secrets", "Deep under the sea, scientists discovered a hidden world. Using their submarine, they explored coral reefs teeming with colorful fish. They documented new species never seen before. The team collected water samples to study the ocean's chemistry. Their research helps us understand the importance of protecting ocean ecosystems from pollution and climate change.", 
         "Emma Wilson", "Educational", json.dumps(["ocean", "science", "discovery"]), 3.8, "8-10", 35),
        
        (6, "Robots of the Future", "In the year 2100, robots help humans with everything. They clean houses, teach in schools, and even cook meals. One special robot named Zevo can understand human emotions. Zevo helps a shy boy named Max make friends at school. Together, they learn that both humans and robots have special qualities that make them unique.", 
         "David Chen", "Science Fiction", json.dumps(["robots", "future", "friendship"]), 2.8, "7-9", 41),
        
        (7, "The Secret Garden Party", "Lisa planned a surprise party in her garden for her best friend's birthday. She decorated the trees with colorful ribbons and paper lanterns. She baked a chocolate cake with strawberry frosting. When her friend arrived, everyone jumped out and yelled 'Surprise!' They played games, ate cake, and had the best garden party ever.", 
         "Patricia Lopez", "Realistic Fiction", json.dumps(["friendship", "celebration", "surprises"]), 2.0, "5-7", 39),
        
        (8, "Animals of the African Savanna", "The African savanna is home to many fascinating animals. Lions hunt in groups called prides. Giraffes use their long necks to eat leaves from tall trees. Elephants travel in family groups led by the oldest female. Zebras have unique stripe patterns that help them hide from predators. The savanna ecosystem depends on each animal playing its important role.", 
         "Robert King", "Educational", json.dumps(["animals", "nature", "geography"]), 3.5, "8-10", 44),
        
        (9, "The Little Inventor", "Maria loved to invent things. She collected old toys and broken appliances to use as parts. In her workshop, she built a machine that could sort her toys by color. When the school science fair was announced, Maria decided to make a robot that could water plants automatically. Her invention won first prize, and her teacher encouraged her to keep inventing.", 
         "Carlos Rodriguez", "Inspirational", json.dumps(["science", "creativity", "perseverance"]), 2.4, "6-8", 52),
        
        (10, "The Mystery of the Missing Cookies", "Someone was taking cookies from the cookie jar, and Detective Sam was on the case. He found crumbs leading to his sister's room, but she wasn't there. He discovered more clues: a stuffed teddy bear with chocolate smudges and tiny footprints in the hallway. Following the trail, Sam found his little brother sharing the cookies with his teddy bear at a tea party.", 
         "Laura Taylor", "Mystery", json.dumps(["mystery", "problem-solving", "family"]), 2.3, "6-8", 47)
    ]
    
    # Sample user data
    sample_users = [
        (1, "Alex", 7, 2.3, json.dumps(["adventure", "animals", "space"]), json.dumps([1, 3])),
        (2, "Maya", 9, 3.5, json.dumps(["science", "magic", "mystery"]), json.dumps([2, 5])),
        (3, "Ethan", 6, 1.9, json.dumps(["dinosaurs", "pets", "space"]), json.dumps([3, 4])),
        (4, "Sophia", 8, 2.7, json.dumps(["friendship", "animals", "mystery"]), json.dumps([7, 10])),
        (5, "Noah", 10, 3.8, json.dumps(["science", "robots", "discovery"]), json.dumps([5, 6]))
    ]
    
    # Insert sample data
    c.executemany('INSERT OR REPLACE INTO content VALUES (?,?,?,?,?,?,?,?,?)', sample_content)
    c.executemany('INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?)', sample_users)
    
    conn.commit()
    conn.close()
    
    print("Database created successfully with sample data!")

def get_user_data(user_id):
    """Get user data from the database"""
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM users WHERE id = {user_id}"
    user_data = pd.read_sql_query(query, conn)
    conn.close()
    
    if not user_data.empty:
        # Parse JSON strings
        user_data['interests'] = user_data['interests'].apply(json.loads)
        user_data['history'] = user_data['history'].apply(json.loads)
        return user_data.iloc[0]
    return None

def get_all_content():
    """Get all content from the database"""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM content"
    content_data = pd.read_sql_query(query, conn)
    conn.close()
    
    # Parse JSON strings
    content_data['topics'] = content_data['topics'].apply(json.loads)
    return content_data

def get_content_by_ids(content_ids):
    """Get content items by their IDs"""
    if not content_ids:
        return pd.DataFrame()
        
    ids_str = ",".join(map(str, content_ids))
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM content WHERE id IN ({ids_str})"
    content_data = pd.read_sql_query(query, conn)
    conn.close()
    
    # Parse JSON strings
    content_data['topics'] = content_data['topics'].apply(json.loads)
    return content_data

def get_users():
    """Get all users from the database"""
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT id, name, age, reading_level FROM users"
    users = pd.read_sql_query(query, conn)
    conn.close()
    return users

def update_user_history(user_id, content_id):
    """Add a content item to user's reading history"""
    user = get_user_data(user_id)
    if user is None:
        return False
    
    history = user['history']
    if content_id not in history:
        history.append(content_id)
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET history = ? WHERE id = ?", 
              (json.dumps(history), user_id))
    conn.commit()
    conn.close()
    return True

if __name__ == "__main__":
    create_database()