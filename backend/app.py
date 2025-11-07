import os
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, g

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, 'storage', 'genricycle.db')

def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        g._db = db
    return db

def close_db(e=None):
    db = getattr(g, '_db', None)
    if db is not None:
        db.close()

def init_db():
    os.makedirs(os.path.join(BASE_DIR, 'storage'), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript(
        '''
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            role TEXT DEFAULT 'customer',
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            line1 TEXT,
            city TEXT,
            pincode TEXT,
            is_default INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT,
            name TEXT NOT NULL,
            generic_name TEXT,
            brand TEXT,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            category_id INTEGER,
            image_url TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            total_amount REAL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            medicine_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY(medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_id INTEGER,
            type TEXT,
            amount REAL,
            status TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS reward_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            points_balance INTEGER DEFAULT 0,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT,
            experience_years INTEGER,
            consultation_fee REAL,
            image_url TEXT
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            scheduled_at TEXT,
            status TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS labs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT,
            contact TEXT
        );

        CREATE TABLE IF NOT EXISTS lab_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            lab_id INTEGER,
            FOREIGN KEY(lab_id) REFERENCES labs(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS lab_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lab_test_id INTEGER NOT NULL,
            scheduled_at TEXT,
            status TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(lab_test_id) REFERENCES lab_tests(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS recycle_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            facility_name TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            pincode TEXT,
            status TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        '''
    )

    # Ensure optional columns exist on users table
    c.execute("PRAGMA table_info(users)")
    existing_cols = {row[1] for row in c.fetchall()}
    if 'language' not in existing_cols:
        try:
            c.execute("ALTER TABLE users ADD COLUMN language TEXT")
        except Exception:
            pass
    if 'currency' not in existing_cols:
        try:
            c.execute("ALTER TABLE users ADD COLUMN currency TEXT")
        except Exception:
            pass

    # Seed basic data if empty
    # Categories
    c.execute('SELECT COUNT(*) FROM categories')
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO categories(name) VALUES(?)', [
            ('Pain Relief',), ('Antibiotic',), ('Diabetes',), ('Vitamins',), ('Cardiovascular',), ('Antiseptic',), ('Digestive',), ('Prescription',)
        ])

    # Medicines
    c.execute('SELECT COUNT(*) FROM medicines')
    if c.fetchone()[0] == 0:
        # Map category names to ids
        c.execute('SELECT id, name FROM categories')
        cat_map = {row[1]: row[0] for row in c.fetchall()}
        medicines = [
            ('paracetamol', 'Paracetamol 500mg Tablets', 'Paracetamol', 'Bell\'s', 'Pain relief and fever reducer.', 45.0, 1000, cat_map['Pain Relief'], 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=200&h=200&fit=crop&crop=center'),
            ('ibuprofen', 'Ibuprofen 400mg Tablets', 'Ibuprofen', 'Generic', 'NSAID for pain and inflammation.', 65.0, 800, cat_map['Pain Relief'], 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=200&h=200&fit=crop&crop=center'),
            ('amoxicillin', 'Amoxicillin 500mg Capsules', 'Amoxicillin', 'Generic', 'Broad-spectrum antibiotic.', 120.0, 500, cat_map['Antibiotic'], 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200&h=200&fit=crop&crop=center'),
            ('metformin', 'Metformin 500mg Tablets', 'Metformin', 'Generic', 'Type 2 diabetes management.', 75.0, 1200, cat_map['Diabetes'], 'https://images.unsplash.com/photo-1576671081837-49000212a370?w=200&h=200&fit=crop&crop=center'),
            ('vitamin-d', 'Vitamin D3 1000 IU Tablets', 'Cholecalciferol', 'Generic', 'Bone health and immunity support.', 350.0, 300, cat_map['Vitamins'], 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=200&h=200&fit=crop&crop=center'),
            ('atorvastatin', 'Atorvastatin 20mg Tablets', 'Atorvastatin', 'Generic', 'Cholesterol management.', 180.0, 600, cat_map['Cardiovascular'], 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200&h=200&fit=crop&crop=center'),
            ('omeprazole', 'Omeprazole 20mg Tablets', 'Omeprazole', 'Generic', 'Acid reflux treatment.', 95.0, 700, cat_map['Digestive'], 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=200&h=200&fit=crop&crop=center'),
            ('betadine', 'Betadine Povidone-Iodine Ointment', 'Povidone-Iodine', 'Betadine', 'Antiseptic ointment.', 180.0, 250, cat_map['Antiseptic'], 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=200&h=200&fit=crop&crop=center'),
            ('insulin', 'Generic Semglee Insulin Glargine', 'Insulin Glargine', 'Semglee', 'Long-acting insulin.', 1250.0, 100, cat_map['Prescription'], 'https://images.unsplash.com/photo-1576671081837-49000212a370?w=200&h=200&fit=crop&crop=center')
        ]
        c.executemany('''
            INSERT INTO medicines(slug, name, generic_name, brand, description, price, stock, category_id, image_url)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', medicines)

    # Doctors
    c.execute('SELECT COUNT(*) FROM doctors')
    if c.fetchone()[0] == 0:
        doctors = [
            ('Aisha Khan', 'Dermatology', 8, 199.0, 'https://randomuser.me/api/portraits/women/33.jpg'),
            ('Ravi Verma', 'General Medicine', 12, 199.0, 'https://randomuser.me/api/portraits/men/32.jpg'),
            ('Neha Sharma', 'Pediatrics', 6, 199.0, 'https://randomuser.me/api/portraits/women/65.jpg')
        ]
        c.executemany('''
            INSERT INTO doctors(name, specialty, experience_years, consultation_fee, image_url)
            VALUES(?, ?, ?, ?, ?)
        ''', doctors)

    # Labs and Lab Tests
    c.execute('SELECT COUNT(*) FROM labs')
    if c.fetchone()[0] == 0:
        labs = [
            ('SRL Diagnostics', 'Mumbai', '+91-90000-00001'),
            ('Lal PathLabs', 'Delhi', '+91-90000-00002')
        ]
        c.executemany('INSERT INTO labs(name, city, contact) VALUES(?, ?, ?)', labs)
        c.execute('SELECT id, name FROM labs')
        labs_map = {row[1]: row[0] for row in c.fetchall()}
        lab_tests = [
            ('Complete Blood Count (CBC)', 'Hematology', 399.0, labs_map['SRL Diagnostics']),
            ('Lipid Profile', 'Biochemistry', 699.0, labs_map['Lal PathLabs']),
            ('Thyroid Profile (T3, T4, TSH)', 'Hormone', 499.0, labs_map['SRL Diagnostics'])
        ]
        c.executemany('INSERT INTO lab_tests(name, category, price, lab_id) VALUES(?, ?, ?, ?)', lab_tests)

    conn.commit()
    conn.close()


app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')

@app.before_request
def before_request():
    get_db()

@app.teardown_appcontext
def teardown_db(exception):
    close_db()

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/api/medicines')
def api_medicines():
    db = get_db()
    rows = db.execute('''
        SELECT m.id, m.slug, m.name, m.generic_name, m.brand, m.description, m.price, m.stock, m.image_url,
               c.name as category_name
        FROM medicines m
        LEFT JOIN categories c ON m.category_id = c.id
        ORDER BY m.name ASC
    ''').fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/categories')
def api_categories():
    db = get_db()
    rows = db.execute('SELECT id, name FROM categories ORDER BY name').fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/doctors')
def api_doctors():
    db = get_db()
    rows = db.execute('SELECT id, name, specialty, experience_years, consultation_fee, image_url FROM doctors ORDER BY name').fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/lab-tests')
def api_lab_tests():
    db = get_db()
    rows = db.execute('''
        SELECT lt.id, lt.name, lt.category, lt.price, l.name AS lab_name, l.city
        FROM lab_tests lt
        LEFT JOIN labs l ON lt.lab_id = l.id
        ORDER BY lt.name
    ''').fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/user', methods=['GET', 'POST'])
def api_user():
    db = get_db()
    if os.environ.get('FLASK_ENV') == 'development':
        db.set_trace_callback(print)
    from flask import request
    if request.method == 'GET':
        email = request.args.get('email')
        if not email:
            return jsonify({'error': 'email query param required'}), 400
        row = db.execute('SELECT id, name, email, phone, role, language, currency, created_at FROM users WHERE email = ?', (email,)).fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        return jsonify(dict(row))
    else:
        data = request.get_json(force=True) or {}
        name = data.get('name') or 'User'
        email = data.get('email')
        phone = data.get('phone')
        role = data.get('role') or 'customer'
        language = data.get('language')
        currency = data.get('currency')
        if not email:
            return jsonify({'error': 'email is required'}), 400
        # Upsert by email
        existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            db.execute('UPDATE users SET name = ?, phone = ?, role = ?, language = ?, currency = ? WHERE id = ?',
                       (name, phone, role, language, currency, existing['id']))
            db.commit()
            row = db.execute('SELECT id, name, email, phone, role, language, currency, created_at FROM users WHERE id = ?', (existing['id'],)).fetchone()
            return jsonify({'status': 'updated', 'user': dict(row)})
        else:
            db.execute('INSERT INTO users(name, email, phone, role, language, currency) VALUES(?, ?, ?, ?, ?, ?)',
                       (name, email, phone, role, language, currency))
            db.commit()
            row = db.execute('SELECT id, name, email, phone, role, language, currency, created_at FROM users WHERE email = ?', (email,)).fetchone()
            return jsonify({'status': 'created', 'user': dict(row)}), 201


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)