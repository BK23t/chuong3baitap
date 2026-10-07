# Sổ điểm lớp học (Flask)

Ứng dụng web và API JSON để xem, tìm kiếm và cập nhật điểm sinh viên.
Dữ liệu mẫu nằm trong biến `STUDENTS` trong file `sodiem.py` (chỉ lưu trong bộ nhớ).

## Cách chạy (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app sodiem run --debug --port 8000
```

Địa chỉ gốc dùng cho các lệnh bên dưới: `http://127.0.0.1:8000`

## 1. Danh sách route

Lệnh `flask --app sodiem routes` cho ra 10 dòng, tính cả `static`:

```text
Endpoint            Methods           Rule
------------------  ----------------  ------------------------------------
export_csv          GET               /students/<mssv>/export
home                GET               /
score_api           DELETE, GET, PUT  /api/students/<mssv>/scores/<course>
search              GET               /search
static              GET               /static/<path:filename>
student_api_detail  GET               /api/students/<mssv>
student_api_list    GET               /api/students
student_detail      GET               /students/<mssv>
student_list        GET               /students
student_shortcut    GET               /sv/<mssv>
```

## 2. Kết quả kiểm thử bằng curl

Server vừa khởi động, chưa có thay đổi dữ liệu. Mỗi lệnh dùng `curl.exe -i`.

| # | Yêu cầu | Mã | Kết quả chính |
|---|---|---|---|
| 1 | `GET /sv/23T1020001` | 301 | `Location: /students/23T1020001` |
| 2 | `GET /students/23T1020001/export` | 200 | `text/csv; charset=utf-8`, tải về `diem_23T1020001.csv` |
| 3 | `GET /api/students?lop=k47a&min_avg=7` | 200 | Chỉ còn sinh viên 23T1020001 (TB 8.17) |
| 4 | `GET /api/students?min_avg=abc` | 400 | JSON báo lỗi |
| 5 | `GET /api/students/999` | 404 | JSON báo lỗi |
| 6 | `PUT /api/students/23T1020005/scores/web?score=9` | 201 | Thêm mới, có `Location` |
| 7 | `PUT .../scores/WEB?score=7.5` | 200 | Sửa điểm đã có |
| 8 | `PUT .../scores/WEB?score=11` | 400 | Điểm ngoài khoảng 0 đến 10 |
| 9 | `DELETE .../scores/WEB` | 204 | Không có body |
| 10 | `POST .../scores/WEB` | 405 | Lỗi dạng JSON |
| 11 | `POST /students` | 405 | Lỗi dạng trang HTML |

Nội dung các phản hồi chính:

**Chuyển hướng (1)**

```text
HTTP/1.1 301 MOVED PERMANENTLY
Location: /students/23T1020001
```

**Tải CSV (2)**

```text
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename=diem_23T1020001.csv

hoc_phan,diem
PMMNM,8.5
CSDL,7.0
MMT,9.0
```

**Lọc theo lớp và điểm trung bình (3)**: `curl.exe -i "http://127.0.0.1:8000/api/students?lop=k47a&min_avg=7"`

```text
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
[{"mssv":"23T1020001","name":"Nguyễn Văn An","lop":"K47A","scores":{"PMMNM":8.5,"CSDL":7.0,"MMT":9.0},"average":8.17,"rank":"Khá"}]
```

**Tham số `min_avg` sai kiểu (4)**

```json
{"error": "Dữ liệu không hợp lệ", "detail": "min_avg phải là một số."}
```

**MSSV không tồn tại (5)**

```json
{"error": "Không tìm thấy", "detail": "Không có sinh viên với MSSV = 999."}
```

**Thêm điểm (6)**: gõ `web`, hệ thống lưu thành `WEB`

```text
HTTP/1.1 201 CREATED
Location: /api/students/23T1020005/scores/WEB
```

```json
{"mssv": "23T1020005", "course": "WEB", "score": 9.0, "average": 9.0}
```

**Sửa điểm (7)**

```json
{"mssv": "23T1020005", "course": "WEB", "score": 7.5, "average": 7.5}
```

**Điểm không hợp lệ (8)**

```json
{"error": "Dữ liệu không hợp lệ", "detail": "score phải nằm trong khoảng từ 0 đến 10."}
```

**Xoá điểm (9)**: `HTTP/1.1 204 NO CONTENT`, body rỗng.

**POST không được hỗ trợ (10, 11)**: cả hai đều trả 405. Đường dẫn bắt đầu bằng `/api/`
trả JSON `{"error": "Phương thức không được hỗ trợ", ...}`, đường dẫn khác trả trang HTML
có mã lỗi, tiêu đề và mô tả.

## 3. Trả lời câu hỏi

**Câu 1: Vì sao Câu 4 dùng 301 còn Câu 8 trả 201 kèm Location?**

`/sv/<mssv>` chỉ là địa chỉ rút gọn của `/students/<mssv>`, tài nguyên thật nằm ở địa chỉ kia.
Server trả 301 để báo đã chuyển vĩnh viễn, và trình duyệt tự đi theo `Location`.

Với `PUT` thêm điểm cho học phần chưa có, server vừa tạo ra một tài nguyên mới nên trả 201.
Header `Location` chỉ cho client biết địa chỉ tài nguyên vừa tạo, client không bị chuyển hướng.

**Câu 2: Thêm điểm cho 23T1020005 rồi khởi động lại server, điểm còn không? Vì sao?**

Không còn. Điểm chỉ được ghi vào dict `STUDENTS` nằm trong bộ nhớ của tiến trình Python.
Khi server khởi động lại, `sodiem.py` được nạp lại từ đầu và dữ liệu mẫu ban đầu được tạo
lại. Ứng dụng chưa lưu thay đổi vào file hay cơ sở dữ liệu nào.

**Vì sao dùng được `request` trong hàm xử lý lỗi dù nó không phải view function?**

`request` là biến toàn cục gắn với request context, không phải với view function. Flask tạo
context này khi bắt đầu xử lý một request và chỉ huỷ khi request đã có phản hồi. Lỗi 400, 404,
405 xảy ra ngay trong lúc request đó đang được xử lý, và Flask gọi hàm xử lý lỗi trước khi
context bị huỷ. Vì vậy `request.path` vẫn đọc được, và hàm có thể dựa vào đó để chọn trả JSON
(đường dẫn bắt đầu bằng `/api/`) hay trang HTML.
