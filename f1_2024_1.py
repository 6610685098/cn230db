import requests
import sqlite3

# กฤติเดช วิชัยดิษฐ 6610685098
# อาจจะรันช้าหน่อยนะครับ
# เป็นสถิติของการแข่งขัน Formula 1 BAHRAIN GRAND PRIX 2024 
# โดยมี API ของ อันดับนักแข่ง อันดับทีม และเวลารอบ Qualify

DB_FILE = 'f1_2024_1.db'
API_URL_DRIVER_STANDINGS = "http://ergast.com/api/f1/2024/1/driverStandings.json"
API_URL_CONSTRUCTOR_STANDINGS = "https://ergast.com/api/f1/2024/1/constructorStandings.json"
API_URL_QUALIFYING = "http://ergast.com/api/f1/2024/1/qualifying.json"

# fetch data จาก 3 API
def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data from {url}")
        exit()

def time_to_seconds(time_str):
    if time_str is None:
        return None
    minutes, seconds = time_str.split(":")
    return int(minutes) * 60 + float(seconds)

def format_time(seconds):
    if seconds is None:
        return None
    minutes = int(seconds // 60)
    sec = seconds % 60
    return f"{minutes}:{sec:06.3f}"

# สร้างตาราง นักแข่ง, โพลนักแข่ง, โพลทีม, ผล qualify
def create_tables(cursor):
    cursor.execute("DROP TABLE IF EXISTS drivers;")
    cursor.execute("DROP TABLE IF EXISTS standings;")
    cursor.execute("DROP TABLE IF EXISTS constructor_standings;")
    cursor.execute("DROP TABLE IF EXISTS qualifying_results;")

    cursor.execute("""
        CREATE TABLE drivers (
            driverId TEXT PRIMARY KEY,
            givenName TEXT,
            familyName TEXT,
            nationality TEXT,
            constructor TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE standings (
            driverId TEXT,
            position INTEGER,
            points REAL,
            wins INTEGER,
            FOREIGN KEY(driverId) REFERENCES drivers(driverId)
        );
    """)    
    cursor.execute("""
        CREATE TABLE constructor_standings (
            constructorId TEXT PRIMARY KEY,
            name TEXT,
            nationality TEXT,
            position INTEGER,
            points REAL,
            wins INTEGER
        );
    """)
    cursor.execute("""
        CREATE TABLE qualifying_results (
            driverId TEXT,
            position INTEGER,
            best_time REAL,
            Q1 TEXT,
            Q2 TEXT,
            Q3 TEXT,
            FOREIGN KEY(driverId) REFERENCES drivers(driverId)
        );
    """)

# ใส่ข้อมูลลงตาราง
def insert_driver_standings_data(cursor, standings):
    for standing in standings:
        driver = standing['Driver']
        constructor = standing['Constructors'][0]['name']

        driverId = driver['driverId']
        givenName = driver['givenName']
        familyName = driver['familyName']
        nationality = driver['nationality']
        position = int(standing['position'])
        points = float(standing['points'])
        wins = int(standing['wins'])

        cursor.execute("""
            INSERT OR IGNORE INTO drivers (driverId, givenName, familyName, nationality, constructor)
            VALUES (?, ?, ?, ?, ?)
        """, (driverId, givenName, familyName, nationality, constructor))

        cursor.execute("""
            INSERT INTO standings (driverId, position, points, wins)
            VALUES (?, ?, ?, ?)
        """, (driverId, position, points, wins))

def insert_constructor_standings_data(cursor,standings):
    for standing in standings:
        constructor = standing['Constructor']

        constructorId = constructor['constructorId']
        position = int(standing['position'])
        points = int(standing['points'])
        wins = int(standing['wins'])
        name = constructor['name']
        nationality = constructor['nationality']
        cursor.execute("""
            INSERT OR IGNORE INTO constructor_standings (constructorId, position, points, wins, name, nationality)
            VALUES (?, ?, ?, ?, ?, ?)
        """,(constructorId, position, points, wins, name, nationality))

def insert_qualifying_data(cursor, qualifying_results):
    for qual in qualifying_results:
        driver = qual['Driver']
        driverId = driver['driverId']
        position = int(qual['position'])
        
        # ✅ ดึง Q1 Q2 Q3 จาก qual
        q1 = qual.get('Q1')
        q2 = qual.get('Q2')
        q3 = qual.get('Q3')
      
        # หาเวลาที่ดีที่สุดจริง ๆ (min จาก Q1, Q2, Q3)
        times = []
        for t in [q1, q2, q3]:
            if t:
                times.append(time_to_seconds(t))
        
        best_time = min(times) if times else None

        cursor.execute("""
            INSERT OR IGNORE INTO drivers (driverId, givenName, familyName, nationality, constructor)
            VALUES (?, ?, ?, ?, ?)
        """, (driverId, driver['givenName'], driver['familyName'], driver['nationality'], None))

        cursor.execute("""
            INSERT INTO qualifying_results (driverId, position, best_time, Q1, Q2, Q3)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (driverId, position, best_time, q1, q2, q3))


# ฟังชั่นเกี่ยวกับสถิติ
def show_top_5_drivers(cursor):
    print("\n🏆 Top 5 drivers by points:")
    for row in cursor.execute("""
        SELECT d.givenName || ' ' || d.familyName AS name, d.constructor, s.points
        FROM drivers d JOIN standings s ON d.driverId = s.driverId
        ORDER BY s.points DESC
        LIMIT 5;
    """):
        print(row)    

def show_avg_points(cursor):
    cursor.execute("SELECT AVG(points) FROM standings;")
    avg_points = cursor.fetchone()[0]
    print(f"\n📊 Average points: {avg_points:.2f}")

def show_top_5_constructor(cursor):
    print("\n🏆 Top 5 constructions by points")
    for row in cursor.execute("""
        SELECT  name, points
        FROM constructor_standings
        ORDER BY points DESC
        LIMIT 5;
"""):
        print(row)

def show_constructor_first_last(cursor):
    print("\n🥇 First place:")
    row = cursor.execute("""
        SELECT name, points FROM constructor_standings ORDER BY position ASC LIMIT 1;
    """).fetchone()
    print(row)

    print("\n🥶 Last place:")
    row = cursor.execute("""
        SELECT name, points FROM constructor_standings ORDER BY position DESC LIMIT 1;
    """).fetchone()
    print(row)

def show_top_10_qualifiers(cursor):
    print("\n🏁 Top 10 Qualifiers:")
    print("-" * 70)
    print(f"| {'Pos':^3} | {'Driver ':<20} | {'Q1':^8} | {'Q2':^8} | {'Q3':^8} |")
    print("-" * 70)
    
    for row in cursor.execute("""
        SELECT q.position, d.givenName || ' ' || d.familyName AS name, q.Q1, q.Q2, q.Q3
        FROM qualifying_results q
        JOIN drivers d ON q.driverId = d.driverId
        ORDER BY q.position ASC
        LIMIT 10;
    """):
        pos, name, q1, q2, q3 = row
        q1 = q1 if q1 else "N/A"
        q2 = q2 if q2 else "N/A"
        q3 = q3 if q3 else "N/A"
        
        print(f"| {pos:^3} | {name:<20} | {q1:^8} | {q2:^8} | {q3:^8} |")
    
    print("-" * 70)

def show_fastest_quilifying_lap(cursor):
    print("\n🏎️  Fastest Qualifying lap")
    row = cursor.execute("""
        SELECT  d.givenName || ' ' || d.familyName AS name, best_time
        FROM qualifying_results q
        JOIN drivers d ON q.driverId = d.driverId
        ORDER BY q.best_time ASC
        LIMIT 1;
    """).fetchone()
    name, best_time = row
    print(f" {name}: {format_time(best_time)}")

def main():
    # 1️⃣ Fetch data
    driver_standings_data = fetch_data(API_URL_DRIVER_STANDINGS)
    driver_standings = driver_standings_data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

    constructor_standings_data = fetch_data(API_URL_CONSTRUCTOR_STANDINGS)
    constructor_standings = constructor_standings_data['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']
    
    qualifying_data = fetch_data(API_URL_QUALIFYING)
    qualifying_results = qualifying_data['MRData']['RaceTable']['Races'][0]['QualifyingResults']

    # 2️⃣ Setup database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    create_tables(cursor)

    # 3️⃣ Insert data
    insert_driver_standings_data(cursor, driver_standings)
    insert_constructor_standings_data(cursor,constructor_standings)
    insert_qualifying_data(cursor, qualifying_results)
    conn.commit()

    # 4️⃣ Show analytics
    show_top_5_drivers(cursor)
    show_avg_points(cursor)
    show_top_5_constructor(cursor)
    show_constructor_first_last(cursor)
    show_fastest_quilifying_lap(cursor)
    show_top_10_qualifiers(cursor)

    conn.close()

if __name__ == "__main__":
    main()
