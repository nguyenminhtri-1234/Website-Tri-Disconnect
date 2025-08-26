# Website Tri Disconnect
Website bán phần mềm
## 🛠️ Cài đặt
Hướng dẫn cách cài đặt dự án:
Cài MySQL 8.* , Python 3.10
Tạo Database TDC Collation utf8mb4_unicode_ci
```bash
git clone https://github.com/nguyenminhtri-1234/Website-Tri-Disconnect.git
cd Website-Tri-Disconnect
```

```bash
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
```
Thay Password MySQL với secret_key trong __init__.py

```bash
python3 -m TDC.models
```
