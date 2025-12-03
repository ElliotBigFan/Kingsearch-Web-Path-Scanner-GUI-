# WebPathScan (KingSearch Web Path Scanner)

WebPathScan là một công cụ **quét đường dẫn (path) web** đơn giản, mô phỏng cách hoạt động của các tool như `dirsearch`.  
Đồ án được xây dựng bằng **Python**, có **giao diện đồ họa (GUI)** với **Tkinter + Matplotlib** và hỗ trợ **chế độ dòng lệnh (CLI)**.

---

## 1. Chức năng chính

### 🔍 Quét đường dẫn (Web Path Scanning)
- Nhập **URL mục tiêu** (vd: `https://example.com/`).
- Sử dụng **wordlist** (mỗi dòng là một đường dẫn, vd: `/admin`, `/login`, `/robots.txt`).
- Gửi lần lượt các HTTP request đến từng path và ghi nhận:
  - Status code (200, 301, 403, 404, …)
  - Kích thước response (bytes)
  - Thời gian phản hồi (ms)
  - Header `Location` (nếu có redirect).

### 🎛 Bộ lọc kết quả (Matcher & Filter)
Thông qua các tuỳ chọn tương tự `dirsearch`:

- **Match codes (`-mc`)**  
  Chỉ hiển thị các status code mong muốn.  
  Mặc định: `200-299,301,302,307,401,403,405,500`  
  Hỗ trợ:
  - Khoảng: `200-299`
  - Nhiều giá trị: `200,301,302,403`

- **Filter codes (`-fc`)**  
  Loại bỏ các mã trạng thái không muốn xem (vd: bỏ hết 404,…).

- **Match size (`-ms`)** & **Filter size (`-fs`)**  
  Lọc theo kích thước nội dung phản hồi (byte).

### 📊 Giao diện đồ họa (GUI)
File chính: `gui.py`

- Form nhập:
  - URL mục tiêu
  - Đường dẫn wordlist
  - Timeout
  - Tham số `-mc`, `-fc`, `-ms`, `-fs`

- Bảng kết quả (Treeview):
  - Cột: Status, Length (B), Time (ms), URL.

- **Biểu đồ Matplotlib**:
  - Biểu đồ cột thống kê số lượng path theo từng status code.

- **Thanh tiến trình dạng text**:
  - Hiển thị dạng: `Progress: [7205/90823]` để biết chương trình đang chạy tới đâu.

- Nút **Lưu báo cáo**:
  - Tự sinh file report trong thư mục `reports/`.

### 🧾 Lưu báo cáo
- Module `output.py` hỗ trợ lưu kết quả ra file `.txt` trong thư mục:
  - `reports/report_<target>_<timestamp>.txt`
- Mỗi dòng ghi: `[status] lengthB timems URL`

### 🧱 Cấu trúc thư mục

```text
webpathscan/ (kingsearch-WebPathScan)
├─ gui.py               # Chạy GUI + hỗ trợ CLI
├─ config.py            # Cấu hình mặc định (timeout, match codes, ...)
├─ dictionary.py        # Xử lý wordlist
├─ http_client.py       # Gửi HTTP request bằng requests
├─ filters.py           # Matcher & filter kết quả
├─ output.py            # In & lưu báo cáo
├─ requirements.txt     # Danh sách thư viện Python cần cài
├─ kingsearch.bat       # Script chạy nhanh trên Windows
├─ kingsearch.sh        # Script chạy nhanh trên Linux/WSL
├─ wordlists/
│   └─ common.txt       # Wordlist mẫu
└─ reports/
    └─ ...              # Thư mục chứa report được sinh ra
```

---

## 2. Yêu cầu hệ thống

- Python **3.13** (hoặc tương đương, đã map với lệnh `python` / `python3`).
- Đã cài được internet & pip hoạt động bình thường.

Các thư viện Python (sẽ tự cài từ `requirements.txt`):
- `requests`
- `matplotlib`

> Trên Linux/WSL có thể cần cài thêm Tkinter:
> ```bash
> sudo apt install python3-tk
> ```

---

## 3. Cách chạy trên Windows

### 3.1. Chạy nhanh bằng script `kingsearch.bat` (khuyến nghị)

1. Mở **Command Prompt** hoặc **PowerShell**.
2. Di chuyển vào thư mục project, ví dụ:

   ```powershell
   cd E:\VKU\Project\kingsearch-WebPathScan
   ```

3. Chạy:

   ```powershell
   kingsearch.bat
   ```

Script sẽ tự động:
1. Cài các thư viện trong `requirements.txt` (ẩn output của pip).
2. Chạy `python gui.py` để mở giao diện.

> Bạn cũng có thể **double-click `kingsearch.bat`** trong Explorer để chạy.

---

### 3.2. Tự chạy bằng tay (không dùng .bat)

1. Cài thư viện (chỉ cần làm lần đầu):

   ```powershell
   cd E:\VKU\Project\kingsearch-WebPathScan
   python -m pip install --user -r requirements.txt
   ```

2. Chạy GUI:

   ```powershell
   python gui.py
   ```

3. Chạy ở chế độ CLI (dòng lệnh), ví dụ:

   ```powershell
   python gui.py -u https://example.com -w wordlists/common.txt -timeout 10 -mc 200-299,301,302
   ```

Trong đó:
- `-u` : URL mục tiêu
- `-w` : đường dẫn wordlist
- `-timeout` : timeout cho mỗi request (giây)
- `-mc`, `-ms`, `-fc`, `-fs` : các tuỳ chọn matcher/filter (tùy chọn, có thể bỏ trống để dùng mặc định).

---

## 4. Cách chạy trên Linux / WSL

### 4.1. Chạy nhanh bằng script `kingsearch.sh`

1. Mở terminal.
2. Di chuyển đến thư mục project:

   ```bash
   cd /mnt/e/VKU/Project/kingsearch-WebPathScan
   ```

3. Cấp quyền thực thi (chỉ cần làm lần đầu):

   ```bash
   chmod +x kingsearch.sh
   ```

4. Chạy script:

   ```bash
   ./kingsearch.sh
   ```

Script sẽ:
1. Cài các thư viện trong `requirements.txt` (ẩn log pip bằng `&> /dev/null`).
2. Chạy `python3 gui.py` (hoặc `python` tuỳ máy).

---

### 4.2. Tự chạy bằng tay

1. Cài thư viện (lần đầu):

   ```bash
   cd /mnt/e/VKU/Project/kingsearch-WebPathScan
   python3 -m pip install --user -r requirements.txt
   ```

2. Chạy GUI:

   ```bash
   python3 gui.py
   ```

3. CLI mode (tương tự Windows):

   ```bash
   python3 gui.py -u https://example.com -w wordlists/common.txt -timeout 10 -mc 200-299,301,302
   ```

---

## 5. Lưu ý khi sử dụng

- **Chỉ nên quét các website mà bạn có quyền kiểm thử**  
  (site của bạn, lab, hoặc được chủ sở hữu cho phép).  
  Việc quét bừa bãi hệ thống người khác có thể vi phạm pháp luật / chính sách sử dụng mạng.

- Wordlist càng lớn → thời gian quét càng lâu.  
  GUI có hiển thị `Progress: [x/y]` để theo dõi tiến độ.

- Timeout nên đặt hợp lý (vd 5–15 giây). Timeout quá nhỏ có thể làm nhiều request bị lỗi do mạng chậm.


