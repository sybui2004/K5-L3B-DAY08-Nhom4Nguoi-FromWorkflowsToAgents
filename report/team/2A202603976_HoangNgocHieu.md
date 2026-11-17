# Báo cáo cá nhân — Hoàng Ngọc Hiệu

## 1. Thông tin thành viên

- Họ tên: Hoàng Ngọc Hiệu
- MSSV: 2A202603976
- Email: hoangngochieu10012000@gmail.com
- GitHub: [hoangngochieu10012000](https://github.com/hoangngochieu10012000)

## 2. Phần việc phụ trách

Thành viên 2 — Single agent (ReAct) và ứng dụng showcase:

- Shape single-agent tại `src/lab8/shapes/single.py`.
- Test tại `src/tests/test_shape_single.py`.
- Ứng dụng demo Streamlit và các module liên quan trong `showcase/`.

## 3. Đóng góp cụ thể

- Xây dựng vòng ReAct có giới hạn tối đa 8 bước; agent chỉ chọn công cụ đọc và không trực tiếp gọi `issue_refund`.
- Lưu trạng thái claim, order và quote trong agent vì mỗi lượt chỉ nhận kết quả công cụ gần nhất.
- Dừng sớm với `needs_info` khi claim thiếu `order_id`; tính khoản đề xuất từ kết quả `compute_compensation`, không lấy số tiền từ câu trả lời cuối của agent hay nội dung ticket.
- Để shape gọi `issue_refund` với quote đầy đủ để host kiểm tra chính sách và độ bền; ghi trace và xử lý trường hợp crash được tiêm vào.
- Xây dựng showcase để chạy ticket, so sánh các shape, xem cổng bảo mật, thử crash/retry và theo dõi benchmark.

## 4. Bằng chứng

- Nhánh: `feature/single-agent-shape`.
- Commit chính: `a68db94030d3a51ee0e76da1da8ab5ebb1b28c2d` — `feat(single): implement bounded ReAct single-agent shape`.
- Test: `src/tests/test_shape_single.py` — **3 passed**.
  - Kiểm tra giới hạn bước và chỉ dùng công cụ đọc.
  - Kiểm tra số lần gọi model được ghi nhận.
  - Kiểm tra claim thiếu order ID dừng sớm, không tra cứu order.

## 5. Công cụ AI đã dùng

Copilot hỗ trợ tổng hợp và diễn đạt báo cáo này. Nội dung được đối chiếu với mã nguồn, test và commit nêu trên; test mục tiêu được chạy bằng `python -m pytest -q tests/test_shape_single.py` từ thư mục `src/`.

## 6. Tự đánh giá

Phần single-agent và showcase đã được triển khai, có test bao phủ các hành vi chính và test mục tiêu hiện đạt. Tôi cần nắm rõ ranh giới giữa agent và host, nguồn xác thực của khoản quote, cùng cách xử lý claim thiếu thông tin để giải thích được các quyết định kỹ thuật khi trình bày.
