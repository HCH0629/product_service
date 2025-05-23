import os
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException, status

# --- 載入環境變數 ---
load_dotenv()


# --- 建立 MySQL 資料庫連線 URL 為了測試方便所以暫時寫在這邊，理論上會在 K8s 的 secret，或是 .env 裡面 ---
# 使用環境變數或預設值設定 MySQL 連線參數
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'test')
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'product')


DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
# print(f"資料庫連線 URL: {DATABASE_URL}")


class MySQLManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine: Engine = None
        self.SessionLocal = None

    def create_engine(self):
        """建立 SQLAlchemy 引擎"""
        try:
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,  # 先執行簡單的 SQL 查詢，檢查連線是否有效
                pool_size=10,  # 池中的連線數量
                max_overflow=20,  # 當池已滿時，最多能夠打開多少額外的連線
                pool_timeout=30,  # 每次請求連線的超時時間
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            print("資料庫引擎建立成功")
        except Exception as e:
            print(f"建立資料庫引擎時發生錯誤: {e}")
            raise RuntimeError("無法建立資料庫引擎") from e


    
    def test_connection(self):
        """測試資料庫連線"""
        try:
            with self.engine.connect() as conn:
                print("連線成功")
                sql_query = text("SELECT 1")
                result = conn.execute(sql_query)
                print(f"測試查詢結果: {result.scalar_one()}")
        except Exception as e:
            print(f"測試連線失敗: {e}")

db_manager = MySQLManager(DATABASE_URL)

try:
    db_manager.create_engine() # 載入 class 建立引擎和 SessionLocal
except RuntimeError as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"無法在啟動時建立資料庫引擎: {e}")


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依賴項，直接從 db_manager 取得 SessionLocal 並管理 Session"""
    db: Session | None = None
    try:
        db = db_manager.SessionLocal()
        yield db # 給 api 使用
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DB Session Error: {e}")
    
    finally:
        try:
            db.close()
        except Exception as e_close:
            # 在關閉資料庫連線時發生的錯誤被記錄下來
            print(f"CRITICAL: Error while closing DB session: {e_close}")


# 使用方式
if __name__ == "__main__":
    db_manager_main = MySQLManager(DATABASE_URL) # 避免與全域 db_manager 混淆
    db_manager_main.create_engine()  # 建立引擎
    db_manager_main.test_connection()  # 測試連線
