import os
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, g
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
 

def _db_engine():
    return (os.environ.get('DB_ENGINE') or 'mysql').strip().lower()

def _mysql_cfg():
    host = (os.environ.get('DB_HOST') or os.environ.get('MYSQL_HOST') or '127.0.0.1')
    port = int(os.environ.get('DB_PORT') or os.environ.get('MYSQL_PORT') or 3306)
    user = (os.environ.get('DB_USER') or os.environ.get('MYSQL_USER') or 'root')
    password = (os.environ.get('DB_PASS') or os.environ.get('MYSQL_PASSWORD') or '')
    db = (os.environ.get('DB_NAME') or os.environ.get('MYSQL_DB') or 'genricycle')
    return {'host': host, 'port': port, 'user': user, 'password': password, 'db': db}

class DBProxy:
    def __init__(self, conn, engine):
        self._conn = conn
        self._engine = engine
    def execute(self, sql, params=None):
        if self._engine == 'mysql':
            sql = sql.replace('?', '%s')
            cur = self._conn.cursor()
            cur.execute(sql, params or ())
            return cur
        else:
            return self._conn.execute(sql, params or ())
    def commit(self):
        self._conn.commit()
    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass
    def set_trace_callback(self, cb):
        pass
    @property
    def engine(self):
        return self._engine
    @property
    def raw(self):
        return self._conn

def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        import pymysql
        cfg = _mysql_cfg()
        try:
            conn = pymysql.connect(host=cfg['host'], port=cfg['port'], user=cfg['user'], password=cfg['password'], database=cfg['db'], cursorclass=pymysql.cursors.DictCursor, autocommit=False)
        except Exception:
            tmp = pymysql.connect(host=cfg['host'], port=cfg['port'], user=cfg['user'], password=cfg['password'], cursorclass=pymysql.cursors.DictCursor, autocommit=True)
            cur = tmp.cursor()
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{cfg['db']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            tmp.close()
            conn = pymysql.connect(host=cfg['host'], port=cfg['port'], user=cfg['user'], password=cfg['password'], database=cfg['db'], cursorclass=pymysql.cursors.DictCursor, autocommit=False)
        g._db = DBProxy(conn, 'mysql')
    return g._db

def close_db(e=None):
    db = getattr(g, '_db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass

def init_db():
    eng = _db_engine()
    if eng == 'sqlite':
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
        conn.commit()
        # migrate optional columns
        c.execute("PRAGMA table_info(users)")
        existing_cols = {row[1] for row in c.fetchall()}
        if 'password_hash' not in existing_cols:
            try:
                c.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
            except Exception:
                pass
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
        # seed
        c.execute('SELECT COUNT(*) FROM categories')
        if c.fetchone()[0] == 0:
            c.executemany('INSERT INTO categories(name) VALUES(?)', [
                ('Pain Relief',), ('Antibiotic',), ('Diabetes',), ('Vitamins',), ('Cardiovascular',), ('Antiseptic',), ('Digestive',), ('Prescription',)
            ])
        c.execute('SELECT COUNT(*) FROM medicines')
        if c.fetchone()[0] == 0:
            c.execute('SELECT id, name FROM categories')
            cat_map = {row[1]: row[0] for row in c.fetchall()}
            medicines = [
                ('paracetamol', 'Paracetamol 500mg Tablets', 'Paracetamol', "Bell's", 'Pain relief and fever reducer.', 45.0, 1000, cat_map['Pain Relief'], 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=200&h=200&fit=crop&crop=center'),
                ('ibuprofen', 'Ibuprofen 400mg Tablets', 'Ibuprofen', 'Generic', 'NSAID for pain and inflammation.', 65.0, 800, cat_map['Pain Relief'], 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=200&h=200&fit=crop&crop=center'),
                ('amoxicillin', 'Amoxicillin 500mg Capsules', 'Amoxicillin', 'Generic', 'Broad-spectrum antibiotic.', 120.0, 500, cat_map['Antibiotic'], 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200&h=200&fit=crop&crop=center'),
                ('metformin', 'Metformin 500mg Tablets', 'Metformin', 'Generic', 'Type 2 diabetes management.', 75.0, 1200, cat_map['Diabetes'], 'https://images.unsplash.com/photo-1576671081837-49000212a370?w=200&h=200&fit=crop&crop=center'),
                ('vitamin-d', 'Vitamin D3 1000 IU Tablets', 'Cholecalciferol', 'Generic', 'Bone health and immunity support.', 350.0, 300, cat_map['Vitamins'], 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=200&h=200&fit=crop&crop=center'),
                ('atorvastatin', 'Atorvastatin 20mg Tablets', 'Atorvastatin', 'Generic', 'Cholesterol management.', 180.0, 600, cat_map['Cardiovascular'], 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200&h=200&fit=crop&crop=center'),
            ]
            c.executemany('''
                INSERT INTO medicines(slug, name, generic_name, brand, description, price, stock, category_id, image_url)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', medicines)
        c.execute('SELECT COUNT(*) FROM doctors')
        if c.fetchone()[0] == 0:
            doctors = [
                ('Aisha Khan', 'Dermatology', 8, 199.0, 'https://randomuser.me/api/portraits/women/33.jpg'),
                ('Ravi Verma', 'General Medicine', 12, 199.0, 'https://randomuser.me/api/portraits/men/32.jpg'),
                ('Neha Sharma', 'Pediatrics', 6, 199.0, 'https://randomuser.me/api/portraits/women/65.jpg')
            ]
            c.executemany('INSERT INTO doctors(name, specialty, experience_years, consultation_fee, image_url) VALUES(?, ?, ?, ?, ?)', doctors)
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
    else:
        import pymysql
        cfg = _mysql_cfg()
        tmp = pymysql.connect(host=cfg['host'], port=cfg['port'], user=cfg['user'], password=cfg['password'], cursorclass=pymysql.cursors.DictCursor, autocommit=True)
        cur0 = tmp.cursor()
        cur0.execute(f"CREATE DATABASE IF NOT EXISTS `{cfg['db']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        tmp.close()
        conn = pymysql.connect(host=cfg['host'], port=cfg['port'], user=cfg['user'], password=cfg['password'], database=cfg['db'], cursorclass=pymysql.cursors.DictCursor, autocommit=False)
        c = conn.cursor()
        stmts = [
            '''CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE,
                phone VARCHAR(64),
                role VARCHAR(64) DEFAULT 'customer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS addresses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                line1 VARCHAR(255),
                city VARCHAR(128),
                pincode VARCHAR(32),
                is_default TINYINT(1) DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(128) UNIQUE NOT NULL
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS medicines (
                id INT AUTO_INCREMENT PRIMARY KEY,
                slug VARCHAR(128),
                name VARCHAR(255) NOT NULL,
                generic_name VARCHAR(255),
                brand VARCHAR(255),
                description TEXT,
                price DECIMAL(10,2) NOT NULL,
                stock INT DEFAULT 0,
                category_id INT,
                image_url VARCHAR(512),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE SET NULL
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                status VARCHAR(64) DEFAULT 'pending',
                total_amount DECIMAL(10,2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS order_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                medicine_id INT NOT NULL,
                quantity INT NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY(medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                order_id INT,
                type VARCHAR(64),
                amount DECIMAL(10,2),
                status VARCHAR(64),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE SET NULL
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS reward_points (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT UNIQUE NOT NULL,
                points_balance INT DEFAULT 0,
                updated_at TIMESTAMP NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS doctors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                specialty VARCHAR(128),
                experience_years INT,
                consultation_fee DECIMAL(10,2),
                image_url VARCHAR(512)
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                doctor_id INT NOT NULL,
                scheduled_at TIMESTAMP NULL,
                status VARCHAR(64),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS labs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                city VARCHAR(128),
                contact VARCHAR(64)
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS lab_tests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(128),
                price DECIMAL(10,2),
                lab_id INT,
                FOREIGN KEY(lab_id) REFERENCES labs(id) ON DELETE SET NULL
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS lab_orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                lab_test_id INT NOT NULL,
                scheduled_at TIMESTAMP NULL,
                status VARCHAR(64),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(lab_test_id) REFERENCES lab_tests(id) ON DELETE CASCADE
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS delivery_persons (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                phone VARCHAR(64),
                vehicle_type VARCHAR(64),
                active TINYINT(1) DEFAULT 1
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS deliveries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                delivery_person_id INT,
                address_id INT,
                status VARCHAR(64) DEFAULT 'scheduled',
                scheduled_at TIMESTAMP NULL,
                picked_at TIMESTAMP NULL,
                delivered_at TIMESTAMP NULL,
                FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY(delivery_person_id) REFERENCES delivery_persons(id) ON DELETE SET NULL,
                FOREIGN KEY(address_id) REFERENCES addresses(id) ON DELETE SET NULL
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS doctor_availability (
                id INT AUTO_INCREMENT PRIMARY KEY,
                doctor_id INT NOT NULL,
                day_of_week TINYINT NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS lab_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lab_order_id INT NOT NULL,
                result_summary TEXT,
                result_url VARCHAR(512),
                status VARCHAR(64) DEFAULT 'pending',
                reported_at TIMESTAMP NULL,
                FOREIGN KEY(lab_order_id) REFERENCES lab_orders(id) ON DELETE CASCADE
            ) ENGINE=InnoDB''',
            '''CREATE TABLE IF NOT EXISTS recycle_requests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                facility_name VARCHAR(255),
                phone VARCHAR(64),
                address VARCHAR(255),
                city VARCHAR(128),
                pincode VARCHAR(32),
                status VARCHAR(64),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB''',
        ]
        for s in stmts:
            c.execute(s)
        conn.commit()
        c.execute('SELECT COUNT(*) AS c FROM users')
        if (c.fetchone().get('c') or 0) == 0:
            c.execute("INSERT INTO users(name, email, phone, role) VALUES(%s, %s, %s, %s)", ('Test User', 'test@example.com', '+91-90000-00000', 'customer'))
        c.execute('SELECT id FROM users LIMIT 1')
        user_id = c.fetchone()['id']
        c.execute('SELECT COUNT(*) AS c FROM addresses')
        if (c.fetchone().get('c') or 0) == 0:
            c.execute("INSERT INTO addresses(user_id, line1, city, pincode, is_default) VALUES(%s, %s, %s, %s, %s)", (user_id, '221B Baker Street', 'Delhi', '110001', 1))
        c.execute('SELECT id FROM addresses WHERE user_id = %s ORDER BY id LIMIT 1', (user_id,))
        addr_id = c.fetchone()['id']
        c.execute('SELECT id, price FROM medicines LIMIT 1')
        mrow = c.fetchone()
        med_id = mrow['id']
        med_price = mrow['price']
        c.execute('SELECT COUNT(*) AS c FROM orders')
        if (c.fetchone().get('c') or 0) == 0:
            c.execute('INSERT INTO orders(user_id, status, total_amount) VALUES(%s, %s, %s)', (user_id, 'pending', med_price))
        c.execute('SELECT id FROM orders WHERE user_id = %s ORDER BY id LIMIT 1', (user_id,))
        order_id = c.fetchone()['id']
        c.execute('SELECT COUNT(*) AS c FROM order_items WHERE order_id = %s', (order_id,))
        if (c.fetchone().get('c') or 0) == 0:
            c.execute('INSERT INTO order_items(order_id, medicine_id, quantity, price) VALUES(%s, %s, %s, %s)', (order_id, med_id, 1, med_price))
        c.execute('SELECT COUNT(*) AS c FROM delivery_persons')
        if (c.fetchone().get('c') or 0) == 0:
            c.execute('INSERT INTO delivery_persons(name, phone, vehicle_type) VALUES(%s, %s, %s)', ('Rahul Kumar', '+91-90000-00003', 'Bike'))
        c.execute('SELECT id FROM delivery_persons ORDER BY id LIMIT 1')
        dp_id = c.fetchone()['id']
        c.execute('SELECT COUNT(*) AS c FROM deliveries')
        if (c.fetchone().get('c') or 0) == 0:
            c.execute('INSERT INTO deliveries(order_id, delivery_person_id, address_id, status, scheduled_at) VALUES(%s, %s, %s, %s, NOW())', (order_id, dp_id, addr_id, 'scheduled'))
        c.execute('SELECT id FROM doctors ORDER BY id LIMIT 1')
        drow = c.fetchone()
        if drow:
            doc_id = drow['id']
            c.execute('SELECT COUNT(*) AS c FROM doctor_availability WHERE doctor_id = %s', (doc_id,))
            if (c.fetchone().get('c') or 0) == 0:
                c.execute("INSERT INTO doctor_availability(doctor_id, day_of_week, start_time, end_time) VALUES(%s, %s, %s, %s)", (doc_id, 1, '10:00:00', '16:00:00'))
            c.execute('SELECT COUNT(*) AS c FROM appointments')
            if (c.fetchone().get('c') or 0) == 0:
                c.execute('INSERT INTO appointments(user_id, doctor_id, scheduled_at, status) VALUES(%s, %s, NOW(), %s)', (user_id, doc_id, 'scheduled'))
        c.execute('SELECT id FROM lab_tests ORDER BY id LIMIT 1')
        ltrow = c.fetchone()
        if ltrow:
            lt_id = ltrow['id']
            c.execute('SELECT COUNT(*) AS c FROM lab_orders')
            if (c.fetchone().get('c') or 0) == 0:
                c.execute('INSERT INTO lab_orders(user_id, lab_test_id, scheduled_at, status) VALUES(%s, %s, NOW(), %s)', (user_id, lt_id, 'scheduled'))
            c.execute('SELECT id FROM lab_orders ORDER BY id LIMIT 1')
            lo_id = c.fetchone()['id']
            c.execute('SELECT COUNT(*) AS c FROM lab_results WHERE lab_order_id = %s', (lo_id,))
            if (c.fetchone().get('c') or 0) == 0:
                c.execute('INSERT INTO lab_results(lab_order_id, result_summary, status, reported_at) VALUES(%s, %s, %s, NOW())', (lo_id, 'All parameters within normal range', 'completed'))
        conn.commit()
        # migrate optional columns on users for app features
        c.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = 'users'")
        rows = c.fetchall()
        existing_cols = { (r.get('column_name') or r.get('COLUMN_NAME')) for r in rows } if rows and isinstance(rows[0], dict) else { r[0] for r in rows }
        if 'password_hash' not in existing_cols:
            try:
                c.execute("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)")
            except Exception:
                pass
        if 'language' not in existing_cols:
            try:
                c.execute("ALTER TABLE users ADD COLUMN language VARCHAR(16)")
            except Exception:
                pass
        if 'currency' not in existing_cols:
            try:
                c.execute("ALTER TABLE users ADD COLUMN currency VARCHAR(16)")
            except Exception:
                pass
        conn.commit()
        # seed
        c.execute('SELECT COUNT(*) AS c FROM categories')
        if (c.fetchone().get('c') or 0) == 0:
            c.executemany('INSERT INTO categories(name) VALUES(%s)', [
                ('Pain Relief',), ('Antibiotic',), ('Diabetes',), ('Vitamins',), ('Cardiovascular',), ('Antiseptic',), ('Digestive',), ('Prescription',)
            ])
        c.execute('SELECT COUNT(*) AS c FROM medicines')
        if (c.fetchone().get('c') or 0) == 0:
            c.execute('SELECT id, name FROM categories')
            cat_map = {row['name']: row['id'] for row in c.fetchall()}
            medicines = [
                ('paracetamol', 'Paracetamol 500mg Tablets', 'Paracetamol', "Bell's", 'Pain relief and fever reducer.', 45.0, 1000, cat_map['Pain Relief'], 'https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=200&h=200&fit=crop&crop=center'),
                ('ibuprofen', 'Ibuprofen 400mg Tablets', 'Ibuprofen', 'Generic', 'NSAID for pain and inflammation.', 65.0, 800, cat_map['Pain Relief'], 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=200&h=200&fit=crop&crop=center'),
                ('amoxicillin', 'Amoxicillin 500mg Capsules', 'Amoxicillin', 'Generic', 'Broad-spectrum antibiotic.', 120.0, 500, cat_map['Antibiotic'], 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200&h=200&fit=crop&crop=center'),
                ('metformin', 'Metformin 500mg Tablets', 'Metformin', 'Generic', 'Type 2 diabetes management.', 75.0, 1200, cat_map['Diabetes'], 'https://images.unsplash.com/photo-1576671081837-49000212a370?w=200&h=200&fit=crop&crop=center'),
                ('vitamin-d', 'Vitamin D3 1000 IU Tablets', 'Cholecalciferol', 'Generic', 'Bone health and immunity support.', 350.0, 300, cat_map['Vitamins'], 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=200&h=200&fit=crop&crop=center'),
                ('atorvastatin', 'Atorvastatin 20mg Tablets', 'Atorvastatin', 'Generic', 'Cholesterol management.', 180.0, 600, cat_map['Cardiovascular'], 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=200&h=200&fit=crop&crop=center'),
            ]
            c.executemany('''
                INSERT INTO medicines(slug, name, generic_name, brand, description, price, stock, category_id, image_url)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', medicines)
        c.execute('SELECT COUNT(*) AS c FROM doctors')
        if (c.fetchone().get('c') or 0) == 0:
            doctors = [
                ('Aisha Khan', 'Dermatology', 8, 199.0, 'https://randomuser.me/api/portraits/women/33.jpg'),
                ('Ravi Verma', 'General Medicine', 12, 199.0, 'https://randomuser.me/api/portraits/men/32.jpg'),
                ('Neha Sharma', 'Pediatrics', 6, 199.0, 'https://randomuser.me/api/portraits/women/65.jpg')
            ]
            c.executemany('INSERT INTO doctors(name, specialty, experience_years, consultation_fee, image_url) VALUES(%s, %s, %s, %s, %s)', doctors)
        c.execute('SELECT COUNT(*) AS c FROM labs')
        if (c.fetchone().get('c') or 0) == 0:
            labs = [
                ('SRL Diagnostics', 'Mumbai', '+91-90000-00001'),
                ('Lal PathLabs', 'Delhi', '+91-90000-00002')
            ]
            c.executemany('INSERT INTO labs(name, city, contact) VALUES(%s, %s, %s)', labs)
            c.execute('SELECT id, name FROM labs')
            labs_map = {row['name']: row['id'] for row in c.fetchall()}
            lab_tests = [
                ('Complete Blood Count (CBC)', 'Hematology', 399.0, labs_map['SRL Diagnostics']),
                ('Lipid Profile', 'Biochemistry', 699.0, labs_map['Lal PathLabs']),
                ('Thyroid Profile (T3, T4, TSH)', 'Hormone', 499.0, labs_map['SRL Diagnostics'])
            ]
            c.executemany('INSERT INTO lab_tests(name, category, price, lab_id) VALUES(%s, %s, %s, %s)', lab_tests)
        conn.commit()


app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')

@app.before_request
def before_request():
    get_db()

@app.teardown_appcontext
def teardown_db(exception):
    close_db()

@app.route('/')
def index():
    # Serve the reorganized home page explicitly from pages/home
    home_dir = os.path.join(BASE_DIR, 'pages', 'home')
    return send_from_directory(home_dir, 'index.html')

@app.route('/api/db/summary')
def api_db_summary():
    db = get_db()
    if db.engine == 'sqlite':
        tables_rows = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
        tables = [r['name'] if isinstance(r, sqlite3.Row) else r[0] for r in tables_rows]
        summary = {}
        for t in tables:
            cols = db.execute(f"PRAGMA table_info({t})").fetchall()
            fks = db.execute(f"PRAGMA foreign_key_list({t})").fetchall()
            count = db.execute(f"SELECT COUNT(*) AS c FROM {t}").fetchone()[0]
            sample = db.execute(f"SELECT * FROM {t} LIMIT 5").fetchall()
            summary[t] = {
                'columns': [
                    {
                        'cid': c['cid'] if isinstance(c, sqlite3.Row) else c[0],
                        'name': c['name'] if isinstance(c, sqlite3.Row) else c[1],
                        'type': c['type'] if isinstance(c, sqlite3.Row) else c[2],
                        'notnull': c['notnull'] if isinstance(c, sqlite3.Row) else c[3],
                        'dflt_value': c['dflt_value'] if isinstance(c, sqlite3.Row) else c[4],
                        'pk': c['pk'] if isinstance(c, sqlite3.Row) else c[5],
                    } for c in cols
                ],
                'foreign_keys': [
                    {
                        'id': fk['id'] if isinstance(fk, sqlite3.Row) else fk[0],
                        'seq': fk['seq'] if isinstance(fk, sqlite3.Row) else fk[1],
                        'table': fk['table'] if isinstance(fk, sqlite3.Row) else fk[2],
                        'from': fk['from'] if isinstance(fk, sqlite3.Row) else fk[3],
                        'to': fk['to'] if isinstance(fk, sqlite3.Row) else fk[4],
                        'on_update': fk['on_update'] if isinstance(fk, sqlite3.Row) else fk[5],
                        'on_delete': fk['on_delete'] if isinstance(fk, sqlite3.Row) else fk[6],
                        'match': fk['match'] if isinstance(fk, sqlite3.Row) else fk[7],
                    } for fk in fks
                ],
                'row_count': count,
                'sample_rows': [dict(r) for r in sample],
            }
        return jsonify({'db_path': DB_PATH, 'tables': tables, 'summary': summary})
    else:
        tables_rows = db.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE() AND table_type='BASE TABLE' ORDER BY table_name").fetchall()
        tables = [r['table_name'] for r in tables_rows]
        summary = {}
        for t in tables:
            cols = db.execute("SELECT column_name, data_type, is_nullable, column_default, column_key FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = ? ORDER BY ordinal_position", (t,)).fetchall()
            fks = db.execute(
                "SELECT k.constraint_name, k.table_name, k.column_name, k.referenced_table_name, k.referenced_column_name, rc.update_rule, rc.delete_rule "
                "FROM information_schema.key_column_usage k "
                "LEFT JOIN information_schema.referential_constraints rc "
                "ON k.constraint_name = rc.constraint_name AND k.table_schema = rc.constraint_schema "
                "WHERE k.table_schema = DATABASE() AND k.table_name = ? AND k.referenced_table_name IS NOT NULL",
                (t,)
            ).fetchall()
            ct = db.execute(f"SELECT COUNT(*) AS c FROM {t}").fetchone()
            count = ct.get('c') if isinstance(ct, dict) else (ct[0] if ct else 0)
            sample_rows = db.execute(f"SELECT * FROM {t} LIMIT 5").fetchall()
            summary[t] = {
                'columns': [
                    {
                        'name': c.get('column_name'),
                        'type': c.get('data_type'),
                        'notnull': 0 if (c.get('is_nullable') == 'YES') else 1,
                        'dflt_value': c.get('column_default'),
                        'pk': 1 if (c.get('column_key') == 'PRI') else 0,
                    } for c in cols
                ],
                'foreign_keys': [
                    {
                        'table': fk.get('referenced_table_name'),
                        'from': fk.get('column_name'),
                        'to': fk.get('referenced_column_name'),
                        'on_update': fk.get('update_rule'),
                        'on_delete': fk.get('delete_rule'),
                    } for fk in fks
                ],
                'row_count': int(count or 0),
                'sample_rows': list(sample_rows),
            }
        cfg = _mysql_cfg()
        dsn = {'host': cfg['host'], 'port': cfg['port'], 'db': cfg['db'], 'user': cfg['user']}
        return jsonify({'db_path': dsn, 'tables': tables, 'summary': summary})

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

@app.route('/api/user', methods=['GET', 'POST', 'DELETE'])
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
    elif request.method == 'POST':
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
    else:  # DELETE
        data = request.get_json(silent=True) or {}
        email = data.get('email') or request.args.get('email')
        if not email:
            return jsonify({'error': 'email is required to delete'}), 400
        user = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if not user:
            return jsonify({'error': 'not found'}), 404
        db.execute('DELETE FROM users WHERE id = ?', (user['id'],))
        db.commit()
        return jsonify({'status': 'deleted'}), 200

@app.route('/api/auth/signup', methods=['POST'])
def api_auth_signup():
    db = get_db()
    from flask import request
    data = request.get_json(force=True) or {}
    name = data.get('name') or 'User'
    email = data.get('email')
    password = data.get('password')
    role = data.get('role') or 'customer'
    phone = data.get('phone')
    language = data.get('language')
    currency = data.get('currency')
    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400
    existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
    if existing:
        return jsonify({'error': 'account already exists'}), 409
    pwd_hash = generate_password_hash(password)
    db.execute('INSERT INTO users(name, email, phone, role, language, currency, password_hash) VALUES(?, ?, ?, ?, ?, ?, ?)',
               (name, email, phone, role, language, currency, pwd_hash))
    db.commit()
    row = db.execute('SELECT id, name, email, phone, role, language, currency, created_at FROM users WHERE email = ?', (email,)).fetchone()
    return jsonify({'status': 'created', 'user': dict(row)}), 201

@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    db = get_db()
    from flask import request
    data = request.get_json(force=True) or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400
    row = db.execute('SELECT id, name, email, phone, role, language, currency, created_at, password_hash FROM users WHERE email = ?', (email,)).fetchone()
    if not row:
        return jsonify({'error': 'not found'}), 404
    if not row['password_hash'] or not check_password_hash(row['password_hash'], password):
        return jsonify({'error': 'incorrect password'}), 401
    user = {k: row[k] for k in ['id', 'name', 'email', 'phone', 'role', 'language', 'currency', 'created_at']}
    return jsonify({'status': 'ok', 'user': user})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)