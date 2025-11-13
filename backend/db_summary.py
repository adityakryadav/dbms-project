import os
import json
import sqlite3

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, 'storage', 'genricycle.db')

def summarize_db(db_path):
    if not os.path.exists(db_path):
        return {'error': 'db not found', 'path': db_path}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()]
    summary = {}
    for t in tables:
        cols = cur.execute(f"PRAGMA table_info({t})").fetchall()
        fks = cur.execute(f"PRAGMA foreign_key_list({t})").fetchall()
        count = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        sample = [dict(r) for r in cur.execute(f"SELECT * FROM {t} LIMIT 5").fetchall()]
        summary[t] = {
            'columns': [{'cid':c[0],'name':c[1],'type':c[2],'notnull':c[3],'dflt_value':c[4],'pk':c[5]} for c in cols],
            'foreign_keys': [{'id':fk[0],'seq':fk[1],'table':fk[2],'from':fk[3],'to':fk[4],'on_update':fk[5],'on_delete':fk[6],'match':fk[7]} for fk in fks],
            'row_count': int(count),
            'sample_rows': sample
        }
    conn.close()
    return {'db_path': db_path, 'tables': tables, 'summary': summary}

if __name__ == '__main__':
    result = summarize_db(DB_PATH)
    print(json.dumps(result, indent=2, ensure_ascii=False))