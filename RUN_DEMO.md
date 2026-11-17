# RUN_DEMO — Hướng dẫn chạy demo từ đầu

File này chỉ lo phần **cài đặt và chạy**. Kịch bản nói, kết quả đúng của từng bước và câu hỏi người chấm nằm ở [DEMO.md](DEMO.md).

Không cần API key hay internet. Mọi thứ chạy bằng MockLLM.

## 1. Yêu cầu

- Python 3.11 – 3.13
- Trình duyệt (Chrome hoặc Edge) cho UI và slide

## 2. Cài đặt (làm một lần, ở gốc repo)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r showcase/requirements-demo.txt
```

`showcase/requirements-demo.txt` đã gồm `src/requirements.txt` (pytest, PyYAML) cộng thêm Streamlit, nên một lệnh là đủ.

macOS / Linux: thay dòng activate bằng `source .venv/bin/activate`.

Nếu PowerShell chặn script activate, chạy một lần: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## 3. Kiểm tra nhanh (1 phút)

```powershell
cd src
python -m lab8.smoke
python -m pytest -q
cd ..
```

Đúng: `lab8.smoke pass` và `184 passed`. Nếu hai lệnh này xanh thì demo chạy được.

## 4. Chạy demo

Có ba cách, chọn theo nhu cầu. Có thể mở cả ba cùng lúc.

### A. UI Streamlit (nên dùng khi trình bày)

Chạy ở **gốc repo**, không phải trong `src/`:

```powershell
streamlit run showcase/app.py --theme.base light
```

Trình duyệt tự mở `http://localhost:8501`. Menu bên trái theo thứ tự bài nói:

1. Xử lý một ticket
2. So sánh 4 shape
3. Cổng bảo mật
4. Crash và retry
5. Bảng benchmark

Mỗi lần chạy dùng SQLite mới, không ghi đè `src/reports/`. Sửa code trong `showcase/` thì tắt (Ctrl+C) rồi chạy lại.

### B. Slide

Mở `showcase/slides/index.html` bằng trình duyệt.

- `F`: toàn màn hình
- Mũi tên trái / phải: chuyển slide
- Ô vàng "Demo" trên slide là lúc chuyển sang trang tương ứng trong app

### C. Dòng lệnh (chạy trong `src/`)

```powershell
cd src
python -m lab8.run --shape workflow --claim-id C-001 --seed 11 --db data/demo_a.sqlite
```

Đúng: JSON có `status: resolved`, `proposal_amount: 35000`.

Các lệnh còn lại (so sánh swarm, crash, benchmark, bonus) xem [DEMO.md](DEMO.md) bước 2 – 7.

## 5. Lỗi thường gặp

| Triệu chứng | Cách xử lý |
| --- | --- |
| `streamlit` không nhận lệnh | Chưa activate venv, hoặc chưa cài `requirements-demo.txt` |
| `ModuleNotFoundError: lab8` | Đang đứng sai thư mục. Lệnh `python -m lab8...` phải chạy trong `src/` |
| Cổng 8501 bị chiếm | `streamlit run showcase/app.py --server.port 8502` |
| Chạy lại cùng `--db` ra kết quả khác lạ | `run.py` dùng lại DB cũ. Đổi tên `--db` hoặc xóa file `.sqlite` |
| UI không cập nhật sau khi sửa code | Tắt app và chạy lại |

## 6. Dọn sau khi demo

```powershell
Remove-Item src\data\demo_*.sqlite -ErrorAction SilentlyContinue
Remove-Item src\reports\demo_*.json -ErrorAction SilentlyContinue
```

**Đừng** chạy benchmark hoặc crash test với `--out reports/benchmark.json` / `reports/crash.json` khi demo, vì hai file đó là bằng chứng nộp bài. Dùng tên `demo_*.json` như trong [DEMO.md](DEMO.md).
