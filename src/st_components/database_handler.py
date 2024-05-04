import pandas as pd
from sqlalchemy import create_engine
import configparser


class DatabaseHandler:
    def __init__(self, config_file="config.ini"):
        # 创建 ConfigParser 对象
        self.config = configparser.ConfigParser()

        # 读取配置文件
        self.config.read(config_file, encoding="utf-8")

        # 从配置文件中获取数据库配置信息
        host = self.config.get("Database", "host")
        port = self.config.getint("Database", "port")
        user = self.config.get("Database", "user")
        password = self.config.get("Database", "password")
        database = self.config.get("Database", "database")

        # 创建 SQLAlchemy 引擎
        self.engine = create_engine(
            f"postgresql://{user}:{password}@{host}:{port}/{database}"
        )

    def query(self, query_string: str):
        return pd.read_sql_query(query_string, self.engine)

    def add_to_database(self, df: pd.DataFrame, name: str):
        df.to_sql(name, self.engine, if_exists="replace", index=False)

    def query_chinese_healing_timeline(self):
        x = r"""SELECT
    en_name AS "name","time","target",duration,"user",kwargs
    FROM
    test_healing_timeline
    LEFT JOIN skill_translate on test_healing_timeline.name = skill_translate.cn_name;"""
        return self.query(x)