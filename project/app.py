import os
import psycopg2
from flask import Flask, render_template, jsonify, request
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = Flask(__name__)

# 🔴 PASTE YOUR NEON CONNECTION STRING HERE
DATABASE_URL = "postgresql://neondb_owner:npg_3HLnPmU8OhBj@ep-rough-star-afrioj1n-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if not conn: return
    cur = conn.cursor()
    
    # 1. Inventory Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id SERIAL PRIMARY KEY,
            item_key TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            qty INT NOT NULL,
            min_qty INT NOT NULL
        );
    """)
    
    # 2. Ambulances Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ambulances (
            id TEXT PRIMARY KEY,
            fuel FLOAT DEFAULT 100.0,
            health FLOAT DEFAULT 100.0,
            supplies_ok BOOLEAN DEFAULT TRUE,
            status TEXT DEFAULT 'IDLE'
        );
    """)

    # 3. Incidents Table (with 4-Point Logging)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            t0 TIMESTAMPTZ,
            t1 TIMESTAMPTZ,
            t2 TIMESTAMPTZ,
            t3 TIMESTAMPTZ,
            status TEXT DEFAULT 'PENDING',
            x FLOAT DEFAULT 50.0,
            y FLOAT DEFAULT 50.0
        );
    """)

    # Auto-Migration for X/Y if missing
    try:
        cur.execute("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS x FLOAT DEFAULT 50.0;")
        cur.execute("ALTER TABLE incidents ADD COLUMN IF NOT EXISTS y FLOAT DEFAULT 50.0;")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Migration Note: {e}")
    
    # Seed Data
    cur.execute("SELECT count(*) FROM inventory")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO inventory (item_key, name, qty, min_qty) VALUES ('bandages', 'Trauma Bandages', 50, 10)")
        cur.execute("INSERT INTO inventory (item_key, name, qty, min_qty) VALUES ('oxygen', 'Oxygen Tanks', 20, 5)")

    cur.execute("SELECT count(*) FROM ambulances")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO ambulances (id) VALUES ('AMB-01'), ('AMB-02'), ('AMB-03')")

    conn.commit()
    cur.close()
    conn.close()
    print("✅ System Ready")

with app.app_context():
    init_db()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/state', methods=['GET'])
def get_state():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT * FROM ambulances ORDER BY id")
    ambs = cur.fetchall()
    
    cur.execute("SELECT * FROM inventory")
    inv = {item['item_key']: item for item in cur.fetchall()}

    # Get Log History (Last 20)
    cur.execute("SELECT * FROM incidents ORDER BY t0 DESC LIMIT 20")
    logs = cur.fetchall()

    # Get Queue: calls that are PENDING or being processed
    cur.execute("SELECT * FROM incidents WHERE status != 'CLOSED' ORDER BY t0 ASC")
    active_incidents = cur.fetchall()
    
    cur.close()
    conn.close()
    return jsonify({'ambulances': ambs, 'inventory': inv, 'logs': logs, 'active_incidents': active_incidents})

@app.route('/api/incident', methods=['POST'])
def handle_incident():
    data = request.json
    action = data.get('action') 
    conn = get_db_connection()
    cur = conn.cursor()

    if action == 'create':
        cur.execute("INSERT INTO incidents (id, t0, status, x, y) VALUES (%s, NOW(), 'PENDING', %s, %s) ON CONFLICT DO NOTHING", 
                    (data['id'], data['x'], data['y']))
    
    elif action == 'dispatch':
        cur.execute("UPDATE incidents SET t1 = NOW(), status = 'DISPATCHED' WHERE id = %s", (data['id'],))
        cur.execute("UPDATE ambulances SET status = 'DISPATCHED' WHERE id = %s", (data['unit_id'],))
    
    elif action == 'arrive':
        cur.execute("UPDATE incidents SET t2 = NOW(), status = 'ON SCENE' WHERE id = %s", (data['id'],))
        cur.execute("UPDATE ambulances SET status = 'ONSCENE' WHERE id = %s", (data['unit_id'],))
    
    elif action == 'transport':
        cur.execute("UPDATE incidents SET status = 'TRANSPORTING' WHERE id = %s", (data['id'],))
        cur.execute("UPDATE ambulances SET status = 'TRANSPORTING' WHERE id = %s", (data['unit_id'],))

    elif action == 'close':
        cur.execute("UPDATE incidents SET t3 = NOW(), status = 'CLOSED' WHERE id = %s", (data['id'],))
        # Deduct resources upon return
        cur.execute("""
            UPDATE ambulances 
            SET status = 'IDLE', 
                supplies_ok = FALSE, 
                fuel = fuel - 25, 
                health = health - 15 
            WHERE id = %s
        """, (data['unit_id'],))

    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/maintenance', methods=['POST'])
def maintenance():
    data = request.json
    amb_id = data['id']
    action = data['type']
    conn = get_db_connection()
    cur = conn.cursor()
    
    if action == 'refuel':
        cur.execute("UPDATE ambulances SET fuel = 100 WHERE id = %s", (amb_id,))
    elif action == 'repair':
        cur.execute("UPDATE ambulances SET health = 100 WHERE id = %s", (amb_id,))
    
    elif action == 'restock':
        # 🟢 NEW: Check inventory levels first!
        cur.execute("SELECT item_key, qty FROM inventory WHERE item_key IN ('bandages', 'oxygen')")
        stock = {row[0]: row[1] for row in cur.fetchall()}

        # Only proceed if BOTH items have stock > 0
        if stock.get('bandages', 0) > 0 and stock.get('oxygen', 0) > 0:
            cur.execute("UPDATE inventory SET qty = qty - 1 WHERE item_key IN ('bandages', 'oxygen')")
            cur.execute("UPDATE ambulances SET supplies_ok = TRUE WHERE id = %s", (amb_id,))
        else:
            conn.close()
            # Return error to frontend
            return jsonify({'status': 'error', 'message': 'Hospital Inventory Empty!'}), 400

    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/inventory/add', methods=['POST'])
def add_inventory():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE inventory SET qty = qty + %s WHERE item_key = %s", (data['qty'], data['item_key']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)