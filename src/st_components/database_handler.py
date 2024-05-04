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

    # @st.cache_data
    def query(self, query_string: str):
        return pd.read_sql_query(query_string, self.engine)