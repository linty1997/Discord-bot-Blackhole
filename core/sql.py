import pymysql

host = ""
database = ""
user = ""
password = ""


class SQL:
    # 初始
    def __init__(self, host=host, user=user, password=password, database=database):
        self.host = host
        self.user = user
        self.passwd = password
        self.database = database
        self.db = None
        self.cursor = None

    # 連結
    def connet(self):
        try:
            self.db = pymysql.connect(
                host=self.host, user=self.user, password=self.passwd, db=self.database, use_unicode=True, charset='utf8mb4')
            self.cursor = self.db.cursor()
        except Exception as e:
            return e

    # 關閉
    def close(self):
        try:
            self.cursor.close()
            self.db.close()
        except Exception as e:
            return e

    # 查詢單一
    def get_one(self, sql):
        try:
            self.connet()
            self.cursor.execute(sql)
            res = self.cursor.fetchone()
            self.close()
        except Exception as e:
            res = None
        return res

    # 查詢多條
    def get_all(self, sql):
        try:
            self.connet()
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
            self.close()
        except Exception:
            res = ()
        return res

    # 查詢對象
    def get_all_obj(self, sql, tableName, *args):
        resList = []
        fieldsList = []
        try:
            if (len(args) > 0):
                for item in args:
                    fieldsList.append(item)
            else:
                fieldsSql = "select COLUMN_NAME from information_schema.COLUMNS where table_name = '%s' and table_schema = '%s'" % (
                    tableName, self.dbName)
                fields = self.get_all(fieldsSql)
                for item in fields:
                    fieldsList.append(item[0])

            # 執行查詢SQL
            res = self.get_all(sql)
            for item in res:
                obj = {}
                count = 0
                for x in item:
                    obj[fieldsList[count]] = x
                    count += 1
                resList.append(obj)
            return resList
        except Exception as e:
            return e

    # 資料庫插入, 更新, 刪除
    def insert(self, sql, val=None):
        return self.__edit(sql, val)

    def update(self, sql, val=None):
        return self.__edit(sql, val)

    def delete(self, sql, val=None):
        return self.__edit(sql, val)

    def __edit(self, sql, val=None):
        try:
            self.connet()
            count = self.cursor.execute(sql, val)
            self.db.commit()
            self.close()
        except Exception as e:
            self.db.rollback()
            count = e  # 0
        return count
