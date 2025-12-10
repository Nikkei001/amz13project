from sqlalchemy import create_engine
from sqlalchemy import text
from data.dbconfig import DB_CONFIG

def export_to_postgres(df, table_name):
   
    # Create connection string
    conn_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    
    # Create SQLAlchemy engine
    engine = create_engine(conn_string)
    
    try:
        # Export DataFrame to PostgreSQL with schema specified
        with engine.connect() as conn:
            result = conn.execute(
                text(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :tablename)"),
                {"tablename": table_name}
            )
            if result.scalar():
                conn.execute(text(f'DELETE FROM "{DB_CONFIG['schema']}"."{table_name}"'))
                conn.commit()
        df.to_sql(table_name, engine, if_exists='append', index=False, schema=DB_CONFIG['schema'])
        print(f"Data successfully exported to table '{table_name}' in schema '{DB_CONFIG['schema']}' in database '{DB_CONFIG['database']}'")
    except Exception as e:
        print(f"Error exporting data to PostgreSQL: {e}")
    finally:
        engine.dispose()

def main():
    print("hola")

if __name__ == "__main__":
    main()