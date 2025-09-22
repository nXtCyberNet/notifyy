import psycopg2

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "root",
    "host": "34.131.223.3",
    "port": 5432
}
PG_HOST = DB_CONFIG["host"]
PG_DB = DB_CONFIG["dbname"]
PG_USER = DB_CONFIG["user"]
PG_PASSWORD = DB_CONFIG["password"]

data = [
    (1, 'Rohan', 'rohanx01', 'rohantech2005@gmail.com'),
    (2, 'Arya', 'arya_dev', 'cybernet27001@gmail.com'),
    (3, 'Maya', 'maya123', 'unknowndev2005@gmail.com'),
    (4, 'Dev', 'coder_dev', 'rohantech2005@gmail.com'),
    (5, 'Nia', 'nia007', 'cybernet27001@gmail.com')
]

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# Step 1: Create the table
cur.execute("""
    CREATE TABLE IF NOT EXISTS info (
        orderid INT PRIMARY KEY,
        name VARCHAR(50),
        username VARCHAR(50),
        email VARCHAR(100)
    );
""")

# Step 2: Insert data
cur.executemany("""
    INSERT INTO info (orderid, name, username, email)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (orderid) DO NOTHING;
""", data)

# Step 3: Add phone_no column if not exists
try:
    cur.execute("ALTER TABLE info ALTER COLUMN fmc_token TYPE VARCHAR(200);")
    print("✅ 'fcm_token' column altered to VARCHAR(200).")
except psycopg2.errors.UndefinedColumn:
    conn.rollback()
    try:
        cur.execute("ALTER TABLE info ADD COLUMN fmc_token VARCHAR(200);")
        print("✅ 'fcm_token' column added as VARCHAR(200).")
    except psycopg2.errors.DuplicateColumn:
        conn.rollback()
        print("⚠️ 'fcm_token' column already exists.")


# Step 4: Update all rows with the same phone number
# cur.execute("UPDATE info SET phone_no = '8287903601';")

# Finalize
conn.commit()
cur.close()
conn.close()

print("✅ Data inserted and phone number updated.")
