from sqlalchemy import create_engine
print("Connecting...")
try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5433/personal_guru')
    conn = engine.connect()
    print("Success")
    conn.close()
except Exception as e:
    print(f"Failed: {e}")
