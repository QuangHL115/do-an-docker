# VN-NEWS Portal - Hệ Thống Cổng Thông Tin 

Dự án triển khai cổng thông tin điện tử **VN-NEWS Portal** dựa trên kiến trúc microservices container hóa với **Docker Compose**. Hệ thống áp dụng mô hình phân tách mạng đa tầng (Network Isolation), cơ chế gia cố an toàn tiến trình (Non-root user), proxy bảo mật đầu cuối (Reverse Proxy HTTPS/SSL) và giám sát tập trung toàn diện (Prometheus, Grafana, Loki, Promtail).

---

## 1. Ngăn Xếp Công Nghệ (Tech Stack)

* **Backend / Ứng dụng cốt lõi:** Python (FastAPI), Uvicorn Server
* **Cơ sở dữ liệu:** MySQL Server (quản trị trực quan qua phpMyAdmin)
* **Cổng điều hướng & Bảo mật:** Nginx Reverse Proxy (SSL Termination, HTTP Security Headers)
* **Hệ thống giám sát (Metrics):** Prometheus & Grafana Dashboard
* **Hệ thống quản lý nhật ký tập trung (Log Management):** Loki & Promtail (truy vấn LogQL)
* **Nền tảng vận hành:** Docker & Docker Compose trên Ubuntu Server

---

## 2. Kiến Trúc Mạng & Cơ Chế An Ninh

### Phân vùng mạng độc lập (Network Isolation)
* **`frontend_net` (Bridge):** Vùng mạng công cộng tiếp nhận kết nối ngoài, chỉ bao gồm container `nginx_proxy` và `news_web`.
* **`backend_net` (Bridge):** Vùng mạng cách ly hoàn toàn với bên ngoài, chỉ cho phép container `news_web` kết nối với cơ sở dữ liệu `mysql_db`.
* Cơ sở dữ liệu MySQL không công khai cổng trực tiếp ra Internet (`ports: 3306`), giảm thiểu nguy cơ tấn công dò quét cổng.

### Gia cố an toàn hệ thống (Security Hardening)
* **Non-root Execution:** Ứng dụng FastAPI thực thi dưới quyền người dùng không có đặc quyền hệ thống (`appuser`).
* **HTTPS/SSL Termination:** Mã hóa lưu lượng truy cập bằng giao thức HTTPS/TLS qua cổng `8443`.
* **HTTP Security Headers:** Nginx được thiết lập các tiêu đề chống tấn công:
  * `X-Frame-Options: SAMEORIGIN` (chống Clickjacking).
  * `X-Content-Type-Options: nosniff` (chống MIME Sniffing).
  * `X-XSS-Protection: 1; mode=block` (ngăn chặn tấn công Cross-Site Scripting).

---

## 3. Cấu Trúc Thư Mục Dự Án

```text
vn-news-portal/
├── docker-compose.yml         # Tệp cấu hình điều phối toàn bộ cụm container
├── .env                       # Biến môi trường hệ thống và cấu hình kết nối DB
├── .env.example               # Tệp biến môi trường mẫu phục vụ triển khai
├── README.md                  # Tài liệu hướng dẫn cài đặt và vận hành hệ thống
├── nginx/
│   ├── nginx.conf             # Cấu hình Reverse Proxy, SSL và Security Headers
│   └── certs/                 # Thư mục lưu trữ khóa riêng và chứng chỉ SSL
│       ├── server.crt
│       └── server.key
├── web/
│   ├── Dockerfile             # Quy trình đóng gói image FastAPI chạy quyền appuser
│   ├── requirements.txt       # Danh sách thư viện Python phụ thuộc
│   ├── main.py                # Mã nguồn khởi tạo backend và định tuyến API
│   └── templates/             # Giao diện hiển thị cổng tin tức (HTML/CSS)
├── prometheus/
│   └── prometheus.yml         # Cấu hình endpoints thu thập số liệu (Targets)
├── loki/
│   └── loki-config.yml        # Cấu hình lưu trữ và nén log
└── promtail/
    └── promtail-config.yml    # Cấu hình thu thập log container và đẩy về Loki
```

---

## 4. Hướng Dẫn Cấu Hình Biến Môi Trường (`.env`)

Trước khi khởi động cụm container, hệ thống cần được thiết lập các biến môi trường cấu hình cơ sở dữ liệu, cổng ứng dụng và thông tin quản trị Grafana.

### 4.1. Khởi tạo tệp `.env` từ tệp mẫu
Tại thư mục gốc của dự án, tạo tệp `.env`:
```bash
cp .env.example .env
```
*(Nếu chưa có tệp `.env.example`, bạn có thể tạo mới tệp `.env` bằng lệnh `nano .env`)*.

### 4.2. Mẫu nội dung tệp `.env` hoàn chỉnh

```dotenv
# ==============================================================================
# CẤU HÌNH CƠ SỞ DỮ LIỆU MYSQL
# ==============================================================================
MYSQL_ROOT_PASSWORD=RootSecretPassword2026!
MYSQL_DATABASE=news_db
MYSQL_USER=news_user
MYSQL_PASSWORD=NewsSecureUserPassword2026!
MYSQL_HOST=mysql_db
MYSQL_PORT=3306

# ==============================================================================
# CẤU HÌNH BACKEND ỨNG DỤNG WEB (FASTAPI)
# ==============================================================================
APP_ENV=production
APP_DEBUG=False
APP_PORT=8000
DATABASE_URL=mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DATABASE}

# ==============================================================================
# CẤU HÌNH NGINX REVERSE PROXY
# ==============================================================================
NGINX_HTTPS_PORT=8443
NGINX_HTTP_PORT=80

# ==============================================================================
# CẤU HÌNH QUẢN TRỊ GRAFANA
# ==============================================================================
GRAFANA_PORT=3000
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=AdminGrafanaSecure2026!
GF_USERS_ALLOW_SIGN_UP=false

# ==============================================================================
# CẤU HÌNH GIÁM SÁT PROMETHEUS & LOKI
# ==============================================================================
PROMETHEUS_PORT=9090
LOKI_PORT=3100
```

### 4.3. Giải thích chi tiết các biến

| Tên biến | Giá trị mẫu | Mô tả chức năng |
| :--- | :--- | :--- |
| `MYSQL_ROOT_PASSWORD` | `RootSecretPassword2026!` | Mật khẩu tài khoản `root` của MySQL container |
| `MYSQL_DATABASE` | `news_db` | Tên cơ sở dữ liệu chính được tạo tự động khi khởi chạy |
| `MYSQL_USER` / `MYSQL_PASSWORD` | `news_user` / `...` | Tài khoản dành riêng cho ứng dụng FastAPI truy cập DB |
| `MYSQL_HOST` | `mysql_db` | Tên hostname nội bộ của MySQL bên trong `backend_net` |
| `DATABASE_URL` | Chuỗi kết nối SQLAlchemy | Đường dẫn kết nối CSDL chuẩn của FastAPI |
| `NGINX_HTTPS_PORT` | `8443` | Cổng Public HTTPS được map ra máy host |
| `GF_SECURITY_ADMIN_USER` | `admin` | Tài khoản quản trị viên tối cao trên Grafana |
| `GF_SECURITY_ADMIN_PASSWORD` | `AdminGrafanaSecure2026!` | Mật khẩu truy cập hệ thống Grafana |
| `GF_USERS_ALLOW_SIGN_UP` | `false` | Khóa chức năng tự đăng ký tài khoản tự do trên Grafana |

> **Lưu ý bảo mật:**  
> - Tuyệt đối không commit tệp `.env` lên các kho mã nguồn công khai (GitHub, GitLab). Hãy thêm `.env` vào file `.gitignore`.
> - Thay đổi toàn bộ mật khẩu mẫu trước khi triển khai trên môi trường thật.

---

## 5. Hướng Dẫn Cài Đặt & Khởi Chạy

### Điều kiện tiên quyết
* Hệ điều hành: Ubuntu Server 20.04/22.04 LTS (hoặc môi trường Linux tương đương).
* Đã cài đặt Docker Engine và Docker Compose Plugin.
* Đã cấu hình tệp `.env` đầy đủ theo Mục 4.

### Các bước triển khai

1. **Khởi tạo và chạy toàn bộ dịch vụ:**
   ```bash
   docker compose up -d --build
   ```

2. **Kiểm tra trạng thái hoạt động của cụm container:**
   ```bash
   docker compose ps
   ```
   *Đảm bảo tất cả các container (`nginx_proxy`, `news_web`, `mysql_db`, `prometheus`, `grafana`, `loki`, `promtail`) đều ở trạng thái `Up`.*

3. **Kiểm tra quyền hạn người dùng ứng dụng (Non-root):**
   ```bash
   docker exec -it news_web whoami
   # Kết quả mong đợi: appuser
   ```

4. **Kiểm tra chứng chỉ SSL và Security Headers:**
   ```bash
   curl -k -I https://localhost:8443
   # Kết quả: HTTP/1.1 200 OK cùng các tiêu đề an ninh X-Frame-Options, nosniff
   ```

---

## 6. Danh Mục Cổng Truy Cập Dịch Vụ

| Dịch vụ / Ứng dụng | Giao thức | Cổng truy cập (Host Port) | Địa chỉ mẫu | Mô tả chức năng |
| :--- | :--- | :--- | :--- | :--- |
| **Cổng tin tức (VN-NEWS)** | HTTPS | `8443` | `https://192.168.23.128:8443` | Giao diện tin tức người dùng qua Nginx Proxy |
| **Quản trị phpMyAdmin** | HTTP | `8080` | `http://192.168.23.128:8080` | Quản lý cơ sở dữ liệu `news_db` |
| **Prometheus Metrics** | HTTP | `9090` | `http://192.168.23.128:9090` | Thu thập metrics và kiểm tra Target health |
| **Grafana Monitoring** | HTTP | `3000` | `http://192.168.23.128:3000` | Dashboard giám sát tài nguyên và phân tích log |
| **Loki Log Engine** | HTTP | `3100` | Nội bộ container | Thu nạp và lưu trữ nhật ký phân tán |

---

## 7. Hướng Dẫn Giám Sát Hệ Thống

### Kiểm tra trạng thái thu thập số liệu (Prometheus)
* Truy cập: `http://<IP_SERVER>:9090/targets`
* Trạng thái các endpoint `news_web:8000/metrics` và `prometheus:9090/metrics` phải hiển thị nhãn **`UP`** màu xanh lá.

### Bảng điều khiển Grafana (Dashboards)
* Truy cập `http://<IP_SERVER>:3000` (Đăng nhập theo tài khoản cấu hình trong `.env`).
* Cấu hình các bảng hiển thị qua Prometheus Data Source:
  * **HTTP Request Rate:** `sum(rate(http_requests_total[1m]))`
  * **Memory Usage (MB):** `process_resident_memory_bytes / 1024 / 1024`
  * **CPU Usage (%):** `rate(process_cpu_seconds_total[1m]) * 100`
  * **HTTP Status Codes:** `sum by (code) (rate(prometheus_http_requests_total[1m]))`

### Truy vấn nhật ký (Loki & LogQL)
* Truy cập mục **Explore** trên thanh điều hướng Grafana, chọn Data source **`loki`**.
* Cú pháp truy vấn log container:
  ```logql
  {container="/news_web"}
  ```
  hoặc
  ```logql
  {service_name="news_web"}
  ```
