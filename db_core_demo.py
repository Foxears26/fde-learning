from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg2://postgres:devpassword@localhost:5432/alertsdb")

with engine.connect() as conn:
    # Insert
    conn.execute(text("INSERT INTO alerts (title, level) VALUES ('磁盘告警', 'warning')"))
    conn.commit()
    # Select
    result = conn.execute(text("SELECT id, title, level FROM alerts"))
    for row in result:
        print(row)
    # Update
    conn.execute(text("UPDATE alerts SET level='critical' WHERE title='磁盘告警'"))
    conn.commit()
    # Delete
    conn.execute(text("DELETE FROM alerts WHERE title='磁盘告警'"))
    conn.commit()
