import sqlite3

# Connect to database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check if DistilGPT2 already exists
cursor.execute("SELECT * FROM chatbot_aimodel WHERE model_id = 'distilgpt2'")
existing = cursor.fetchone()

if existing:
    print(f"✅ DistilGPT2 already exists in database")
else:
    # Insert DistilGPT2
    from datetime import datetime
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        INSERT INTO chatbot_aimodel (name, model_id, provider, description, use_cases, strength, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) """, 
        (
        'DistilGPT2 (Local)',
        'distilgpt2',
        'local',
        'Local lightweight GPT-2 model with RAG support',
        'Document Q&A,Offline usage,Privacy-focused chat',
        'Runs locally with document context',
        1,
        now,
        now
    ))
    conn.commit()
    print(f"✅ Successfully added DistilGPT2 to database")

# List all models
print("\nAll models in database:")
cursor.execute("SELECT id, name, provider, model_id, is_active FROM chatbot_aimodel")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} ({row[2]}) - {row[3]} - Active: {row[4]}")

conn.close()
