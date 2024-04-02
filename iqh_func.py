# coding: utf8
import os
import sqlite3
from pathlib import Path


__all__ = ["iqh_init", "iqh_create_conn", "iqh_close_conn",
           "iqh_create_table", "iqh_select_id2group",
           "iqh_select_group2id", "iqh_insert_data"]


def iqh_init() -> Path:
    base_path = Path(os.path.expandvars("%appdata%"), "JnPrograms", "IdQuery")
    if not base_path.exists():
        base_path.mkdir(parents=True, exist_ok=True)

    return base_path


def iqh_create_conn(base_path: Path, db_name: str) -> sqlite3.Connection:
    db_path = Path(base_path, db_name)
    conn = sqlite3.connect(db_path)
    return conn


def iqh_close_conn(conn: sqlite3.Connection):
    conn.close()


def iqh_create_table(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS idrepo (
        id_index INTEGER PRIMARY KEY NOT NULL,
        id_num INTEGER NOT NULL,
        group_name TEXT
    )""")
    cursor.close()


def iqh_select_id2group(conn: sqlite3.Connection, id_list: list[int]) -> list[tuple[int, str]]:
    cursor = conn.cursor()
    ids = ",".join(map(str, id_list))
    cursor.execute(f"SELECT id_num, group_name FROM idrepo WHERE id_num IN ({ids})")
    result = cursor.fetchall()
    cursor.close()
    return result


def iqh_select_group2id(conn: sqlite3.Connection, group_name: str) -> list[tuple[int, str]]:
    cursor = conn.cursor()
    cursor.execute(f"SELECT id_num, group_name FROM idrepo WHERE group_name = '{group_name}'")
    result = cursor.fetchall()
    cursor.close()
    return result


def iqh_insert_data(conn: sqlite3.Connection, data: list[tuple[int, str]]):
    cursor = conn.cursor()
    values = ",".join(map(str, data))
    cursor.execute(f"INSERT INTO idrepo (id_num, group_name) VALUES {values}")
    conn.commit()
    cursor.close()
