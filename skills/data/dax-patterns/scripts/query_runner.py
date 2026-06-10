#!/usr/bin/env python3
"""
Kings Pastry — Azure SQL Query Runner
=====================================
Reusable script for running SQL queries against DataWarehousePBI.
Uses AAD token authentication via ODBC Driver 18.

Usage:
    python3 query_runner.py                          # Show table inventory
    python3 query_runner.py --validate               # Run D02 validation queries
    python3 query_runner.py --table bc.SalesLine     # Describe table schema
    python3 query_runner.py -q "SELECT ..."          # Custom query

Requirements: azure-cli, pyodbc, ODBC Driver 18 (brew install msodbcsql18)
"""

import subprocess, sys, argparse, pyodbc, struct

SERVER = "kingsbi-sqlsrv-prod.database.windows.net"
DATABASE = "DataWarehousePBI"

def get_token():
    result = subprocess.run(
        ["az", "account", "get-access-token", "--resource", "https://database.windows.net/",
         "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, timeout=15
    )
    token = result.stdout.strip()
    if not token:
        print("ERROR: Could not get AAD token. Run 'az login' first.")
        sys.exit(1)
    return token

def get_conn(token):
    token_bytes = token.encode("utf-16-le")
    token_struct = struct.pack("<I", len(token_bytes)) + token_bytes
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={SERVER};DATABASE={DATABASE};"
        "Encrypt=yes;TrustServerCertificate=no;"
    )
    return pyodbc.connect(conn_str, attrs_before={1256: token_struct}, timeout=30)

def run_query(cursor, query, label=None):
    if label:
        print(f"\n{'='*70}\n  {label}\n{'='*70}")
    try:
        cursor.execute(query.strip())
        if cursor.description:
            cols = [desc[0] for desc in cursor.description]
            print(f"  {' | '.join(cols)}\n  {'-'*80}")
            rows = cursor.fetchall()
            for row in rows:
                print(f"  {' | '.join(str(v) if v is not None else 'NULL' for v in row)}")
            print(f"  ({len(rows)} rows)")
        else:
            print("  (no result set)")
    except Exception as e:
        print(f"  ERROR: {e}")

def describe_table(cursor, table_name):
    schema = table_name.split(".")[0] if "." in table_name else "dbo"
    table = table_name.split(".")[1] if "." in table_name else table_name
    run_query(cursor, f"""
        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA='{schema}' AND TABLE_NAME='{table}'
        ORDER BY ORDINAL_POSITION;
    """, f"Schema: {table_name}")

def main():
    parser = argparse.ArgumentParser(description="Query Kings Pastry Azure SQL")
    parser.add_argument("-q", "--query", help="Custom SQL query")
    parser.add_argument("--table", help="Describe table (e.g., bc.SalesHeader)")
    parser.add_argument("--validate", action="store_true", help="Run D02 validation queries")
    args = parser.parse_args()

    token = get_token()
    conn = get_conn(token)
    cursor = conn.cursor()
    print(f"Connected to {SERVER}/{DATABASE}")

    if args.query:
        run_query(cursor, args.query, "Custom Query")
    elif args.table:
        describe_table(cursor, args.table)
    elif args.validate:
        for label, query in {
            "Row Counts": "SELECT 'SalesHeader' as tbl, COUNT(*) as rows FROM bc.SalesHeader UNION ALL SELECT 'SalesLine', COUNT(*) FROM bc.SalesLine UNION ALL SELECT 'SalesHeaderArchive', COUNT(*) FROM bc.SalesHeaderArchive UNION ALL SELECT 'SalesLineArchive', COUNT(*) FROM bc.SalesLineArchive UNION ALL SELECT 'Item', COUNT(*) FROM bc.Item UNION ALL SELECT 'DailyInventorySnapshot', COUNT(*) FROM pbi.DailyInventorySnapshot UNION ALL SELECT 'KPIConfig', COUNT(*) FROM pbi.KPIConfig;",
            "Date Ranges": "SELECT 'SalesHeader' as tbl, MIN(PostingDate), MAX(PostingDate) FROM bc.SalesHeader UNION ALL SELECT 'SalesHeaderArchive', MIN(PostingDate), MAX(PostingDate) FROM bc.SalesHeaderArchive UNION ALL SELECT 'DailyInventorySnapshot', MIN(SnapshotDate), MAX(SnapshotDate) FROM pbi.DailyInventorySnapshot;",
            "Ship Dates": "SELECT 'SalesLine' as tbl, COUNT(*) as total, COUNT(ShipmentDate) as has_ship FROM bc.SalesLine UNION ALL SELECT 'SalesLineArchive', COUNT(*), COUNT(ShipmentDate) FROM bc.SalesLineArchive;",
            "KPIConfig": "SELECT * FROM pbi.KPIConfig;",
        }.items():
            run_query(cursor, query, label)
    else:
        run_query(cursor, "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' ORDER BY TABLE_SCHEMA, TABLE_NAME;", "Table Inventory")

    cursor.close(); conn.close()
    print(f"\n{'='*70}\n  DONE\n{'='*70}")

if __name__ == "__main__":
    main()
