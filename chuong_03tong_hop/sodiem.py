from flask import Flask, request, redirect, url_for, abort, make_response, jsonify
from markupsafe import escape
import math

app = Flask(__name__)
app.json.ensure_ascii = False
app.json.sort_keys = False

STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "lop": "K47A",
        "scores": {
            "PMMNM": 8.5,
            "CSDL": 7.0,
            "MMT": 9.0
        }
    },
    "23T1020002": {
        "name": "Trần Thị Bình",
        "lop": "K47A",
        "scores": {
            "PMMNM": 6.0,
            "CSDL": 5.5,
            "MMT": 7.0
        }
    },
    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "lop": "K47B",
        "scores": {
            "PMMNM": 9.5,
            "CSDL": 9.0
        }
    },
    "23T1020004": {
        "name": "Phạm Minh Dũng",
        "lop": "K47B",
        "scores": {
            "PMMNM": 4.0,
            "CSDL": 3.5,
            "MMT": 5.0
        }
    },
    "23T1020005": {
        "name": "Hoàng Thu Hà",
        "lop": "K47A",
        "scores": {}
    },
    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "lop": "K47C",
        "scores": {
            "PMMNM": 7.5,
            "MMT": 8.0
        }
    }
}


def average(scores):
    """
    Tính điểm trung bình cộng.

    - Nếu scores rỗng -> None
    - Nếu có điểm -> trung bình, làm tròn 2 chữ số
    """
    if not scores:
        return None

    return round(sum(scores.values()) / len(scores), 2)


def rank(avg):
    """
    Xếp loại dựa trên điểm trung bình.
    """
    if avg is None:
        return "Chưa có điểm"

    if avg >= 8.5:
        return "Giỏi"

    if avg >= 7.0:
        return "Khá"

    if avg >= 5.0:
        return "Trung bình"

    return "Yếu"


def student_summary(mssv):
    """
    Tạo dictionary thông tin tổng hợp của một sinh viên.
    """
    student = STUDENTS[mssv]

    avg = average(student["scores"])

    return {
        "mssv": mssv,
        "name": student["name"],
        "lop": student["lop"],
        "scores": student["scores"],
        "average": avg,
        "rank": rank(avg)
    }


def layout(title, body):
    """
    Tạo một trang HTML hoàn chỉnh.

    title được escape() vì title là dữ liệu được chèn vào HTML.

    body được chèn nguyên văn theo yêu cầu đề bài.
    """

    safe_title = escape(title)

    return f"""<!doctype html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>{safe_title} - Sổ điểm</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 30px auto;
            padding: 0 20px;
            line-height: 1.6;
        }}

        nav {{
            margin-bottom: 25px;
            padding: 12px;
            background: #f2f2f2;
        }}

        nav a {{
            margin-right: 20px;
            text-decoration: none;
        }}

        table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
        }}

        th, td {{
            border: 1px solid #ccc;
            padding: 8px;
            text-align: left;
        }}

        th {{
            background: #eee;
        }}

        .filter {{
            margin: 15px 0;
        }}
    </style>
</head>

<body>

<nav>
    <a href="{url_for('home')}">Trang chủ</a>
    <a href="{url_for('student_list')}">Sinh viên</a>
    <a href="{url_for('search')}">Tìm kiếm sinh viên</a>
</nav>

{body}

</body>
</html>"""


@app.route("/")
def home():
    total_students = len(STUDENTS)

    classes = set()
    for student in STUDENTS.values():
        classes.add(student["lop"])

    total_classes = len(classes)

    body = f"""
    <h1>Sổ điểm</h1>

    <p>Tổng số sinh viên: {escape(total_students)}</p>
    <p>Số lớp: {escape(total_classes)}</p>

    <ul>
        <li>
            <a href="{url_for('student_list')}">
                Xem danh sách sinh viên
            </a>
        </li>

        <li>
            <a href="{url_for('student_api_list')}">
                API danh sách sinh viên
            </a>
        </li>
    </ul>
    """

    return layout("Trang chủ", body)


@app.route("/students")
def student_list():
    lop_filter = request.args.get("lop", "")

    students = []

    for mssv, student in STUDENTS.items():
        if lop_filter:
            if student["lop"].lower() != lop_filter.lower():
                continue

        students.append(
            student_summary(mssv)
        )

    classes = sorted(
        {
            student["lop"]
            for student in STUDENTS.values()
        }
    )

    body = """
    <h1>Danh sách sinh viên</h1>

    <div class="filter">
        <strong>Lọc theo lớp:</strong>

        <a href="{}">Tất cả</a>
    """.format(url_for("student_list"))

    for lop in classes:
        body += f"""
        |
        <a href="{url_for('student_list', lop=lop)}">
            {escape(lop)}
        </a>
        """

    body += """
    </div>
    """

    if not students:
        body += "<p>Không có sinh viên phù hợp.</p>"

    else:
        body += """
        <table>
            <thead>
                <tr>
                    <th>MSSV</th>
                    <th>Họ tên</th>
                    <th>Lớp</th>
                    <th>Điểm TB</th>
                    <th>Xếp loại</th>
                </tr>
            </thead>

            <tbody>
        """

        for student in students:
            mssv = student["mssv"]
            name = student["name"]
            lop = student["lop"]
            avg = student["average"]
            rank_name = student["rank"]

            if avg is None:
                avg_display = "—"
            else:
                avg_display = escape(avg)

            body += f"""
                <tr>
                    <td>
                        <a href="{url_for('student_detail', mssv=mssv)}">
                            {escape(mssv)}
                        </a>
                    </td>

                    <td>{escape(name)}</td>
                    <td>{escape(lop)}</td>
                    <td>{avg_display}</td>
                    <td>{escape(rank_name)}</td>
                </tr>
            """

        body += """
            </tbody>
        </table>
        """

    return layout("Danh sách sinh viên", body)


@app.route("/students/<mssv>")
def student_detail(mssv):
    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    student = student_summary(mssv)

    avg = student["average"]

    if avg is None:
        avg_display = "—"
    else:
        avg_display = escape(avg)

    shortcut_url = url_for("student_shortcut", mssv=mssv)

    body = f"""
    <h1>Chi tiết sinh viên</h1>

    <p>
        <strong>Họ tên:</strong>
        {escape(student["name"])}
    </p>

    <p>
        <strong>MSSV:</strong>
        {escape(student["mssv"])}
    </p>

    <p>
        <strong>Lớp:</strong>
        <a href="{url_for('student_list', lop=student["lop"])}">
            {escape(student["lop"])}
        </a>
    </p>

    <p>
        <strong>Điểm trung bình:</strong>
        {avg_display}
    </p>

    <p>
        <strong>Xếp loại:</strong>
        {escape(student["rank"])}
    </p>

    <h2>Bảng điểm</h2>
    """

    if student["scores"]:
        body += """
    <table>
        <thead>
            <tr>
                <th>Học phần</th>
                <th>Điểm</th>
            </tr>
        </thead>

        <tbody>
        """

        for course, score in student["scores"].items():
            body += f"""
            <tr>
                <td>{escape(course)}</td>
                <td>{escape(score)}</td>
            </tr>
            """

        body += """
        </tbody>
    </table>
        """
    else:
        body += "<p>Chưa có điểm học phần nào.</p>"

    body += f"""
    <p>
        <a href="{url_for('export_csv', mssv=mssv)}">
            Tải bảng điểm (CSV)
        </a>
    </p>

    <p>
        Link rút gọn:
        <a href="{shortcut_url}">
            {escape(shortcut_url)}
        </a>
    </p>
    """

    return layout("Chi tiết sinh viên", body)


@app.route("/sv/<mssv>")
def student_shortcut(mssv):
    return redirect(
        url_for("student_detail", mssv=mssv),
        code=301
    )


@app.route("/students/<mssv>/export")
def export_csv(mssv):
    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    lines = [
        "hoc_phan,diem"
    ]

    for course, score in STUDENTS[mssv]["scores"].items():
        lines.append(
            f"{course},{score}"
        )

    csv_content = "\n".join(lines) + "\n"

    response = make_response(csv_content)

    response.headers["Content-Type"] = "text/csv; charset=utf-8"

    response.headers["Content-Disposition"] = (
        f"attachment; filename=diem_{mssv}.csv"
    )

    return response


@app.route("/search")
def search():
    keyword = request.args.get("q", "")

    keyword_lower = keyword.strip().lower()

    results = []

    if keyword_lower:
        for mssv, student in STUDENTS.items():
            if (
                keyword_lower in student["name"].lower()
                or keyword_lower in mssv.lower()
            ):
                results.append(
                    student_summary(mssv)
                )

    body = f"""
    <h1>Tìm kiếm sinh viên</h1>

    <form method="get" action="{url_for('search')}">
        <input
            type="text"
            name="q"
            value="{escape(keyword)}"
            placeholder="Nhập họ tên hoặc MSSV"
        >

        <button type="submit">
            Tìm kiếm
        </button>
    </form>
    """

    if keyword_lower:
        body += f"""
    <p>
        Tìm thấy {escape(len(results))} kết quả cho
        “{escape(keyword)}”
    </p>
    """

    if results:
        body += "<ul>"

        for student in results:
            body += f"""
            <li>
                <a href="{url_for(
                    'student_detail',
                    mssv=student['mssv']
                )}">
                    {escape(student["mssv"])}
                    -
                    {escape(student["name"])}
                </a>
            </li>
            """

        body += "</ul>"

    return layout("Tìm kiếm sinh viên", body)


@app.route("/api/students")
def student_api_list():
    lop_filter = request.args.get("lop")

    min_avg_raw = request.args.get("min_avg")

    min_avg = None
    if min_avg_raw is not None:
        try:
            min_avg = float(min_avg_raw)
        except ValueError:
            abort(
                400,
                description="min_avg phải là một số."
            )

        if not math.isfinite(min_avg):
            abort(
                400,
                description="min_avg phải là một số hợp lệ."
            )

    results = []

    for mssv, student in STUDENTS.items():

        if lop_filter:
            if student["lop"].lower() != lop_filter.lower():
                continue

        summary = student_summary(mssv)

        if min_avg is not None:
            if summary["average"] is None:
                continue

            if summary["average"] < min_avg:
                continue

        results.append(summary)

    return jsonify(results)


@app.route("/api/students/<mssv>")
def student_api_detail(mssv):
    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    return jsonify(
        student_summary(mssv)
    )


@app.route(
    "/api/students/<mssv>/scores/<course>",
    methods=["GET", "PUT", "DELETE"]
)
def score_api(mssv, course):

    if mssv not in STUDENTS:
        abort(
            404,
            description=f"Không có sinh viên với MSSV = {mssv}."
        )

    course = course.upper()

    scores = STUDENTS[mssv]["scores"]

    if request.method == "GET":

        if course not in scores:
            abort(
                404,
                description=(
                    f"Sinh viên {mssv} chưa có điểm "
                    f"học phần {course}."
                )
            )

        return jsonify({
            "mssv": mssv,
            "course": course,
            "score": scores[course]
        })

    if request.method == "PUT":

        score_raw = request.args.get("score")

        if score_raw is None:
            abort(
                400,
                description="Thiếu tham số score."
            )

        try:
            score = float(score_raw)
        except ValueError:
            abort(
                400,
                description="score phải là một số."
            )

        if not math.isfinite(score):
            abort(
                400,
                description="score phải là một số hợp lệ."
            )

        if score < 0 or score > 10:
            abort(
                400,
                description="score phải nằm trong khoảng từ 0 đến 10."
            )

        # Kiểm tra thêm hay sửa
        is_new = course not in scores

        scores[course] = score

        summary = student_summary(mssv)

        body = {
            "mssv": mssv,
            "course": course,
            "score": score,
            "average": summary["average"]
        }

        if is_new:
            response = make_response(
                jsonify(body),
                201
            )

            response.headers["Location"] = url_for(
                "score_api",
                mssv=mssv,
                course=course
            )

            return response

        return jsonify(body), 200

    if request.method == "DELETE":

        if course not in scores:
            abort(
                404,
                description=(
                    f"Sinh viên {mssv} chưa có điểm "
                    f"học phần {course}."
                )
            )

        del scores[course]

        return "", 204

    abort(405)


# ============================================================
# CÂU 9 - XỬ LÝ LỖI CHUNG
# ============================================================

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):

    status_code = error.code

    titles = {
        400: "Dữ liệu không hợp lệ",
        404: "Không tìm thấy",
        405: "Phương thức không được hỗ trợ"
    }

    title = titles.get(
        status_code,
        "Lỗi"
    )

    detail = error.description

    # Nếu URL bắt đầu bằng /api/ -> trả JSON
    if request.path.startswith("/api/"):

        response = jsonify({
            "error": title,
            "detail": detail
        })

        response.status_code = status_code

        return response

    # Các URL thông thường -> trả HTML
    body = f"""
    <h1>{escape(status_code)} - {escape(title)}</h1>

    <p>{escape(detail)}</p>
    """

    return layout(
        title,
        body
    ), status_code


if __name__ == "__main__":
    app.run(debug=True, port=8000)