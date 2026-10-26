import csv
from pathlib import Path
from db import get_conn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "powerbi"
OUT.mkdir(parents=True, exist_ok=True)

con = get_conn()
cur = con.cursor()

tables = ['fact_bookings','dim_customer','dim_movie','dim_show','dim_date','dim_payment']
for t in tables:
    cur.execute(f"SELECT * FROM {t}")
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    path = OUT / f"{t}.csv"
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            # Convert dates to strings
            nr = []
            for v in r:
                if hasattr(v, 'strftime'):
                    nr.append(v.strftime('%Y-%m-%d %H:%M:%S') if hasattr(v, 'hour') and v.hour else v.strftime('%Y-%m-%d'))
                else:
                    nr.append(v)
            w.writerow(nr)
    print(f"Exported {t}: {len(rows)} rows -> {path}")

con.close()
print("Done")
