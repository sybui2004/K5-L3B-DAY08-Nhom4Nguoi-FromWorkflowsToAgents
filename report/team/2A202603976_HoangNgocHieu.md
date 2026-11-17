# Báo cáo cá nhân — Hoàng Ngọc Hiệu

## 1. Thông tin thành viên

- Họ tên: Hoàng Ngọc Hiệu
- MSSV: 2A202603976
- Email: hoangngochieu10012000@gmail.com
- GitHub: [hoangngochieu10012000](https://github.com/hoangngochieu10012000)

## 2. Phần việc phụ trách

Thành viên 2 — Single agent (ReAct) và ứng dụng showcase. Các file/thư mục đã sửa:

- `src/lab8/shapes/single.py`
- `src/tests/test_shape_single.py`
- `showcase/app.py`
- `showcase/requirements-demo.txt`
- `showcase/catalog/`
- `showcase/services/`
- `showcase/ui/`
- `showcase/views/`

## 3. Đóng góp cụ thể

- Trong `src/lab8/shapes/single.py`, triển khai agent ReAct tối đa 8 bước. Agent chỉ chọn công cụ đọc; shape giữ trạng thái claim, order và quote giữa các lượt, dừng với `needs_info` nếu thiếu `order_id`, và lấy số tiền từ kết quả `compute_compensation` thay vì câu trả lời của agent hoặc nội dung ticket. Shape gọi `issue_refund` với quote đầy đủ để host kiểm tra, đồng thời ghi trace và xử lý crash được tiêm vào.
- Trong `src/tests/test_shape_single.py`, bổ sung test giới hạn số bước và quyền chỉ đọc, hạch toán số lần gọi model, và kiểm tra claim thiếu `order_id` dừng trước khi tra cứu order.
- Trong `showcase/app.py` và các module ở `showcase/catalog/`, `showcase/services/`, `showcase/ui/`, `showcase/views/`, xây dựng ứng dụng Streamlit để chạy ticket, so sánh các shape, xem thông tin bảo mật và trace, thử crash/retry, và xem benchmark.
- Trong `showcase/requirements-demo.txt`, khai báo các dependency dùng để chạy showcase.

## 4. Bằng chứng

- Nhánh: `feature/single-agent-shape`.
- Commit: `a68db94030d3a51ee0e76da1da8ab5ebb1b28c2d`. Commit này chứa các thay đổi cho `single.py`, test tương ứng và ứng dụng showcase cùng các module/phụ thuộc trong danh sách ở mục 2. Tiêu đề commit trong Git là `feat(single): implement bounded ReAct single-agent shape` (triển khai shape single-agent ReAct có giới hạn bước).
- Test: `src/tests/test_shape_single.py` — **3 passed**.
  - Kiểm tra giới hạn bước và chỉ dùng công cụ đọc.
  - Kiểm tra số lần gọi model được ghi nhận.
  - Kiểm tra claim thiếu order ID dừng sớm, không tra cứu order.

## 5. Công cụ AI đã dùng

Copilot hỗ trợ tổng hợp và diễn đạt báo cáo này. Nội dung được đối chiếu với mã nguồn, test và commit nêu trên; test mục tiêu được chạy bằng `python -m pytest -q tests/test_shape_single.py` từ thư mục `src/`.

## 6. Tự đánh giá

Phần single-agent và showcase đã được triển khai, có test bao phủ các hành vi chính và test mục tiêu hiện đạt. Tôi cần nắm rõ ranh giới giữa agent và host, nguồn xác thực của khoản quote, cùng cách xử lý claim thiếu thông tin để giải thích được các quyết định kỹ thuật khi trình bày.
