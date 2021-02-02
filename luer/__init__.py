import sqlite3


class ImageData:
    def __init__(self, db_path):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    async def _get_random_image(self, table):
        try:
            r = (
                self._connect()
                .execute(f"SELECT LINK FROM {table}IMAGELINK ORDER BY RANDOM() limit 1")
                .fetchone()
            )
            if r:
                return r[0]
            else:
                return None
        except:
            raise Exception(f"获取{self.db_path}发生错误")
