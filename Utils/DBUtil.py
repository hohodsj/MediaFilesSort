import os,sys
import sqlite3 as lite
from datetime import datetime
from Utils.FileUtil import FileUtil

class DBUtil:
    DB_FILE_NAME = "db/mediasort.db"
    TBL_NAME = 'file_info'
    def __init__(self, dest):
        fu = FileUtil()
        try:
            if not fu.is_folder_exists(f'{dest}/db'):
                fu.create_directory_recursive(f'{dest}/db')
            self.db_dest = os.path.join(dest, DBUtil.DB_FILE_NAME)
            self.con = lite.connect(str(self.db_dest))
            self.con.row_factory = lite.Row
            self.cursor = self.con.cursor()
            '''
            src_path + mode + dest_path should be a composite key
            Columns:
            src_path (varchar): where the origin file is
            mode (varchar): copy, move, etc
            dest_path (varchar): where the new location of the file
            status(varchar): initiated, completed, failed
            create_date (datetime)
            update_date (datetime)
            file_create_datetime: when the file is first created
            potential_duplicate(bool): potential duplicate files determined by repeated dest_path
            '''
            create_table_sql = f"""CREATE TABLE IF NOT EXISTS {DBUtil.TBL_NAME}(
                src_path VARCHAR(500), 
                mode VARCHAR(10), 
                dest_path VARCHAR(500), 
                status VARCHAR(50), 
                create_date TIMESTAMP, 
                update_date TIMESTAMP, 
                file_create_datetime TIMESTAMP, 
                potential_duplicate BOOLEAN)"""
            self.cursor.execute(create_table_sql)
            self.con.commit()
        except Exception as e:
            print('Error while creating db: {e}')
    
    def upsert(self,src_path, mode, dest_path, status, file_create_datetime, potential_duplicate):
        res = self.select(src_path=src_path, mode=mode, dest_path=dest_path)
        if len(res): # already record update
            return self.update(src_path=src_path, mode=mode, dest_path=dest_path, status=status, file_create_datetime=file_create_datetime, potential_duplicate=potential_duplicate)
        else: # insert record
            return self.insert(src_path, mode, dest_path, status, file_create_datetime, potential_duplicate)

        
    def select(self, src_path = None, mode = None, dest_path = None, 
               status = None, create_date = None, update_date= None, 
               file_create_datetime = None, potential_duplicate=None):
        sql = f"SELECT src_path, mode, dest_path, status, create_date, update_date, file_create_datetime, potential_duplicate FROM {DBUtil.TBL_NAME}"
        where = []
        params = {}
        if src_path:
            where.append("src_path = :src_path")
            params['src_path'] = src_path
        if mode:
            where.append("mode = :mode")
            params['mode'] = mode
        if dest_path:
            where.append("dest_path = :dest_path")
            params['dest_path'] = dest_path
        if status:
            where.append("status = :status")
            params['status'] = status
        if create_date:
            where.append("create_date = :create_date")
            params['create_date'] = create_date
        if update_date:
            where.append("update_date = :update_date")
            params['update_date'] = update_date
        if file_create_datetime:
            where.append("file_create_datetime = :file_create_datetime")
            params['file_create_datetime'] = file_create_datetime
        if potential_duplicate:
            where.append("potential_duplicate = :potential_duplicate")
            params['potential_duplicate'] = potential_duplicate
        if where:
            sql = '{} WHERE {}'.format(sql, ' AND '.join(where))
        res = self.cursor.execute(sql,params)
        return res.fetchall()

    def update(self, src_path, mode, dest_path, 
               status, file_create_datetime, potential_duplicate):
        sql = f"""UPDATE {DBUtil.TBL_NAME}
               SET status=?, update_date=?, file_create_datetime=?, potential_duplicate=?
               WHERE src_path=? AND mode=? AND dest_path=?"""
        params = (status, datetime.now(), str(file_create_datetime), potential_duplicate, src_path, mode, dest_path)
        res = self.cursor.execute(sql, params)
        self.con.commit()
        return res.rowcount

    def insert(self, src_path, mode, dest_path, 
               status,  file_create_datetime, potential_duplicate):
        sql = f"INSERT INTO {DBUtil.TBL_NAME} VALUES (?,?,?,?,?,?,?,?)"
        params = (src_path, mode, dest_path, status, datetime.now(), datetime.now(), file_create_datetime, potential_duplicate)
        res = self.cursor.execute(sql, params)
        self.con.commit()
        return res.rowcount
    
    def get_last_update_date(self):
        sql = f"SELECT MAX(update_date) FROM {DBUtil.TBL_NAME}"
        res = self.cursor.execute(sql)
        return res.fetchone()

if __name__ == '__main__':
    dest = '/path/to/dest'
    src_path = "src_path"
    mode = "mode"
    dest_path = "dest_path"
    status = "status"
    file_create_datetime = datetime.now()
    potential_duplicate = False
    db = DBUtil(dest)
    ct = db.upsert(src_path, mode, dest_path, status, file_create_datetime, potential_duplicate)
    print(ct)
    res = db.select(src_path=src_path, mode=mode, dest_path=dest_path)
    print(res)
    assert len(res) > 0
    assert res[0]['src_path'] == src_path
    # update
    file_create_datetime = datetime.now()
    status = 'different status'
    potential_duplicate = True
    ct = db.upsert(src_path, mode, dest_path, status, file_create_datetime, potential_duplicate)
    print(ct)

