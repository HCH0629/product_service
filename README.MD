# Product Service API

這是一個使用 FastAPI 建構的產品管理 API，用於處理產品資料的 CRUD (建立、讀取、更新、刪除) 操作。後端使用 Python、FastAPI、SQLAlchemy ORM，並連接到 MySQL 資料庫。

## 功能特性

- 建立新產品
- 根據產品代碼 (code) 讀取特定產品資訊
- 更新現有產品資訊
- 根據產品代碼 (code) 刪除產品

## API 文檔

該 API 服務於容器運行的主機根目錄下提供（例如：`http://127.0.0.1:8000`）。

## 技術棧

- **後端框架**: FastAPI
- **資料庫**: MySQL
- **ORM**: SQLAlchemy
- **資料驗證**: Pydantic
- **環境變數管理**: python-dotenv
- **資料庫驅動**: PyMySQL

## 專案結構

```
your_project_root/
├── api/
│   ├── routers/
│   │   └── product.py  # 產品相關的 API 路由
│   ├── main.py         # FastAPI 應用程式入口點
│   ├── database.py     # 資料庫連線設定和 session 管理
│   └── models.py       # SQLAlchemy 模型和 Pydantic schemas
├── .env                # 環境變數檔案
├── docker-compose.yml  # Docker Compose 檔案，用於啟動 Docker
├── requirements.txt    # Python 依賴套件
└── README.md           # 本檔案
```


## 使用指南：使用 Docker Compose 運行

### 前提條件：

* 您的系統已經安裝 Docker 和 Docker Compose。如果尚未安裝，可以參考 [Docker 安裝指南](https://docs.docker.com/get-docker/) 和 [Docker Compose 安裝指南](https://docs.docker.com/compose/install/)。

### 步驟：

1. **下載專案並進入專案目錄**：
    ```bash
    git clone https://github.com/HCH0629/product_service
    cd product_service
    ```

2. **啟動 Docker Compose**：
    使用 Docker Compose 來啟動所有必要的服務，包括應用程式和資料庫。
    ```bash
    docker-compose up -d
    ```
    * **說明**：
        * `docker-compose up -d`：在背景模式下啟動所有服務。
        * `-d`：讓容器在後台運行。

3. **檢查容器狀態**：
    確保所有服務運行正常。
    ```bash
    docker-compose ps
    ```

4. **訪問服務**：
    * 服務將在 `http://127.0.0.1:8000` 提供。
    * 您可以在瀏覽器中進行 API 測試，或者使用 `curl` 或 Postman 進行交互。

    # 範例：使用 curl 建立一個新產品
    ```bash
    curl -X POST 'http://127.0.0.1:8000/products/' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
        "name": "Cool Gadget",
        "code": "CG-001",
        "category": "Electronics",
        "unit_price": 99.99,
        "inventory": 150,
        "size": "M",
        "color": "Black"
    }'
    ```
    # 預期成功回應 (201 Created):
    # {"name":"Cool Gadget","code":"CG-001","category":"Electronics","unit_price":99.99,"inventory":150,"size":"M","color":"Black"}


---

### 1. 建立新產品

建立一個新的產品記錄。

*   **URL**：`/products/`
*   **方法**：`POST`
*   **請求主體**：JSON
    ```json
    {
        "name": "Star",
        "code": "A-001",
        "category": "cloth",
        "unit_price": 200.00,
        "inventory": 20,
        "size": "S",
        "color": "Red"
    }
    ```
    *   `name`（字串，必需）：產品名稱。
    *   `code`（字串，必需）：產品的唯一代碼。
    *   `category`（字串，可選）：產品類別。
    *   `unit_price`（浮點數，必需）：產品單價，必須大於 0。
    *   `inventory`（整數，必需）：產品庫存數量，必須大於等於 0。
    *   `size`（字串，可選）：產品尺寸。
    *   `color`（字串，可選）：產品顏色。


*   **成功響應 (201 Created)**：
    ```json
    {
        "name": "Star",
        "code": "A-001",
        "category": "cloth",
        "unit_price": 200.00,
        "inventory": 20,
        "size": "S",
        "color": "Red"
    }
    ```
    *   `code`：新建立產品的唯一識別碼。
    *   其他欄位與請求中的對應。


*   **錯誤響應**：
    *   `409 Conflict`：產品代碼已存在。
        ```json
        {
            "detail": "Product with code A-001 already exists"
        }
        ```
    *   `422 Unprocessable Entity`：輸入資料無效（例如，欄位缺失、類型錯誤、值不符合 Pydantic 模型中定義的約束）。
        ```json
        {
            "detail": [
                {
                    "loc": [
                        "body",
                        "unit_price"
                    ],
                    "msg": "Input should be a valid number, unable to parse string as a number",
                    "type": "float_parsing"
                }
            ]
        }
        ```
    *   `500 Internal Server Error`：建立產品過程中發生未預期的伺服器端錯誤。
        ```json
        {
            "detail": "An error occurred: <具體的錯誤訊息>"
        }
        ```

---

### 2. 根據產品代碼讀取產品資訊

根據產品的唯一代碼獲取特定產品的詳細資訊。

*   **URL**：`/products/{code}`
*   **方法**：`GET`
*   **路徑參數**：
    *   `code`（字串，必需）：要查詢的產品代碼。

*   **成功響應 (200 OK)**：
    ```json
    {
        "name": "Star",
        "code": "A-001",
        "category": "cloth",
        "unit_price": 200.00,
        "inventory": 20,
        "size": "S",
        "color": "Red"
    }
    ```

*   **錯誤響應**：
    *   `404 Not Found`：找不到具有指定代碼的產品。
        ```json
        {
            "detail": "Product not found"
        }
        ```
    *   `422 Unprocessable Entity`：如果路徑參數 `code` 的類型不正確 (雖然 FastAPI 通常會處理)。
    *   `500 Internal Server Error`：查詢過程中發生未預期的伺服器端錯誤。

---

### 3. 根據產品代碼更新產品資訊

根據產品的唯一代碼更新現有產品的資訊。只會更新請求主體中提供的欄位。

*   **URL**：`/products/{code}`
*   **方法**：`PUT`
*   **路徑參數**：
    *   `code`（字串，必需）：要更新的產品代碼。
*   **請求主體**：JSON (包含要更新的欄位)
    ```json
    {
        "name": "Star Updated",
        "inventory": 25,
        "unit_price": 210.50
    }
    ```
    *   所有欄位都是可選的。

*   **成功響應 (200 OK)**：
    ```json
    {
        "name": "Star Updated",
        "code": "A-001",
        "category": "cloth",
        "unit_price": 210.50,
        "inventory": 25,
        "size": "S",
        "color": "Red"
    }
    ```
    *   返回更新後的完整產品資訊。

*   **錯誤響應**：
    *   `404 Not Found`：找不到具有指定代碼的產品。
        ```json
        {
            "detail": "Product not found"
        }
        ```
    *   `409 Conflict`：如果嘗試將 `code` 更新為一個已存在的產品代碼。
        ```json
        {
            "detail": "Product with code <new_code> already exists"
        }
        ```
    *   `422 Unprocessable Entity`：輸入資料無效。
    *   `500 Internal Server Error`：更新過程中發生未預期的伺服器端錯誤。

---

### 4. 根據產品代碼刪除產品

根據產品的唯一代碼刪除一個產品。

*   **URL**：`/products/{code}`
*   **方法**：`DELETE`
*   **路徑參數**：
    *   `code`（字串，必需）：要刪除的產品代碼。

*   **成功響應 (204 No Content)**：
    *   回應主體為空。

*   **錯誤響應**：
    *   `404 Not Found`：找不到具有指定代碼的產品。
        ```json
        {
            "detail": "Product not found"
        }
        ```
    *   `500 Internal Server Error`：刪除過程中發生未預期的伺服器端錯誤。

---