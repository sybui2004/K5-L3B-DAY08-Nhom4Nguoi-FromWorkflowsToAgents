# Báo cáo cá nhân — 20240002_TranDucMinh

## 1. Thông tin thành viên

- Họ tên: Trần Đức Minh
- MSSV: 20240002
- Email: minhtd@vinuni.edu.vn
- GitHub: minhtd

## 2. Phần việc phụ trách

- Chịu trách nhiệm phát triển hình thái Shape B (Single ReAct Agent) tại `src/lab8/shapes/single.py`.

## 3. Đóng góp cụ thể

- Hiện thực hóa vòng lặp `run_react` với hàm `decide` có giới hạn 8 bước (`max_steps=8`).
- Điều phối các công cụ chỉ đọc `lookup_order` và `compute_compensation`, đảm bảo không gọi công cụ ghi từ phía agent.
- Đảm bảo agent vượt qua 62/62 bài kiểm thử student, đạt độ chính xác 100%.

## 4. Bằng chứng

- Commit hash: 034c6c4
- Test: `tests/test_public_matrix.py` (single pass 62/62).
- File: `src/lab8/shapes/single.py`.

## 5. Công cụ AI đã dùng

- AI Assistant: Tham khảo cấu trúc định tuyến ReAct và chuẩn hóa gọi dispatch.

## 6. Tự đánh giá

- Hoàn thành đầy đủ chức năng và chỉ tiêu kiểm thử, đóng góp tích cực vào tiến độ chung.
