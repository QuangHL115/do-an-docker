VN-NEWS Portal - Hệ Thống Cổng Thông Tin Tin Tức Container Hóa
Dự án triển khai cổng thông tin điện tử VN-NEWS Portal dựa trên kiến trúc microservices container hóa với Docker Compose. Hệ thống áp dụng mô hình phân tách mạng đa tầng (Network Isolation), cơ chế gia cố an toàn tiến trình (Non-root user), proxy bảo mật đầu cuối (Reverse Proxy HTTPS/SSL) và giám sát tập trung toàn diện (Prometheus, Grafana, Loki, Promtail)
1. Ngăn Xếp Công Nghệ (Tech Stack)
- Backend / Ứng dụng cốt lõi: Python (FastAPI), Uvicorn Server.
- Cơ sở dữ liệu: MySQL Server (quản trị trực quan qua phpMyAdmin).
- Cổng điều hướng & Bảo mật: Nginx Reverse Proxy (SSL Termination, HTTP Security Headers).
- Hệ thống giám sát (Metrics): Prometheus & Grafana Dashboard.
- Hệ thống quản lý nhật ký tập trung (Log Management): Loki & Promtail (truy vấn LogQL).
- Nền tảng vận hành: Docker & Docker Compose trên Ubuntu Server.
  
2. Kiến Trúc Mạng & Cơ Chế An Ninh.
- Phân vùng mạng độc lập (Network Isolation).
  + frontend_net (Bridge): Vùng mạng công cộng tiếp nhận kết nối ngoài, chỉ bao gồm container nginx_proxy và news_web.
  + backend_net (Bridge): Vùng mạng cách ly hoàn toàn với bên ngoài, chỉ cho phép container news_web kết nối với cơ sở dữ liệu mysql_db.
  + Cơ sở dữ liệu MySQL không công khai cổng trực tiếp ra Internet (ports: 3306), giảm thiểu nguy cơ tấn công dò quét cổng.
- Gia cố an toàn hệ thống (Security Hardening).
  +Non-root Execution: Ứng dụng FastAPI thực thi dưới quyền người dùng không có đặc quyền hệ thống (appuser).
  +HTTPS/SSL Termination: Mã hóa lưu lượng truy cập bằng giao thức HTTPS/TLS qua cổng 8443.
  +HTTP Security Headers: Nginx được thiết lập các tiêu đề chống tấn công:
     X-Frame-Options: SAMEORIGIN (chống Clickjacking).
     X-Content-Type-Options: nosniff (chống MIME Sniffing).
     X-XSS-Protection: 1; mode=block (ngăn chặn tấn công Cross-Site Scripting).
  
 3. Cấu Trúc Thư Mục Dự Án
   vn-news-portal/
├── docker-compose.yml         # Tệp cấu hình điều phối toàn bộ cụm container
├── .env                       # Biến môi trường hệ thống và cấu hình kết nối DB
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
  
  4. Hướng Dẫn Cài Đặt & Khởi Chạy
  -Điều kiện tiên quyết:
  + Hệ điều hành: Ubuntu Server 20.04/22.04 LTS (hoặc môi trường Linux tương đương).
  + Đã cài đặt Docker Engine và Docker Compose Plugin.
  -Các bước triển khai:
1.Khởi tạo và chạy toàn bộ dịch vụ:
Bash
docker compose up -d --build
2.Kiểm tra trạng thái hoạt động của cụm container:
Bash
docker compose ps
Đảm bảo tất cả các container (nginx_proxy, news_web, mysql_db, prometheus, grafana, loki, promtail) đều ở trạng thái Up.
3.Kiểm tra quyền hạn người dùng ứng dụng (Non-root):
Bash
docker exec -it news_web whoami
# Kết quả mong đợi: appuser
4.Kiểm tra chứng chỉ SSL và Security Headers:
Bash
curl -k -I https://localhost:8443
# Kết quả: HTTP/1.1 200 OK cùng các tiêu đề an ninh X-Frame-Options, nosniff

  5. Danh Mục Cổng Truy Cập Dịch Vụ
     Dịch vụ / Ứng dụng     Giao thức   Cổng truy cập     (Host Port)Địa chỉ mẫu                        Mô tả chức năng
     Cổng tin tức (VN-NEWS)	  HTTPS	       8443	           https://192.168.23.128:8443     Giao diện tin tức người dùng qua Nginx Proxy
     Quản trị phpMyAdmin	    HTTP	       8080	           http://192.168.23.128:8080	     Quản lý cơ sở dữ liệu news_db
     Prometheus Metrics	      HTTP	       9090	           http://192.168.23.128:9090	     Thu thập metrics và kiểm tra Target health
     Grafana Monitoring	      HTTP	       3000	           http://192.168.23.128:3000	     Dashboard giám sát tài nguyên và phân tích log
     Loki Log Engine	        HTTP	       3100            Nội bộ container	               Thu nạp và lưu trữ nhật ký phân tán
  6. Hướng Dẫn Giám Sát Hệ Thống
    - Kiểm tra trạng thái thu thập số liệu (Prometheus)
     +Truy cập: http://<IP_SERVER>:9090/targets
     +Trạng thái các endpoint news_web:8000/metrics và prometheus:9090/metrics phải hiển thị nhãn UP màu xanh lá.
    - Bảng điều khiển Grafana (Dashboards)
     +Truy cập http://<IP_SERVER>:3000 (Tài khoản mặc định: admin / admin).
     +Cấu hình các bảng hiển thị qua Prometheus Data Source:
    . HTTP Request Rate: sum(rate(http_requests_total[1m]))
    . Memory Usage (MB): process_resident_memory_bytes / 1024 / 1024
    . CPU Usage (%): rate(process_cpu_seconds_total[1m]) * 100
    . HTTP Status Codes: sum by (code) (rate(prometheus_http_requests_total[1m]))
   -Truy vấn nhật ký (Loki & LogQL)
     +Truy cập mục Explore trên thanh điều hướng Grafana, chọn Data source loki.
        +Cú pháp truy vấn log container:
     Đoạn mã{container="/news_web"}
       hoặcĐoạn mã{service_name="news_web"}
