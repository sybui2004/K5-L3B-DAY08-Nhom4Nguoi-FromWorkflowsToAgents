# Báo cáo cá nhân — 20240004_PhamQuocBao

## 1. Thông tin thành viên

- Họ tên: Phạm Quốc Bảo
- MSSV: 20240004
- Email: baopq@vinuni.edu.vn
- GitHub: baopq

## 2. Phần việc phụ trách

- Phụ trách độ bền bỉ (Durability), quản lý Ledger, kiểm thử va chạm (Crash Test 20/20) và đánh giá Benchmark đa hình thái (Evaluation).

## 3. Đóng góp cụ thể

- Phân tích cơ chế idempotency key `refund:{claim_id}`, trần hoàn tiền theo đơn `order_refunded_vnd` và kiểm tra approval binding.
- Chạy và xác thực toàn bộ bộ kiểm thử va chạm 20 điểm đạt tỷ lệ tuyệt đối 20/20.
- Thực hiện chạy `lab8.benchmark` trên 4 hình thái x 5 seed, tổng hợp số liệu vào `reports/benchmark.json`.

## 4. Bằng chứng

- Commit hash: 034c6c4
- Báo cáo: `reports/crash.json` (20/20), `reports/benchmark.json`.
- Test: `tests/test_crash_suite.py`, `tests/test_refund_idempotency.py`.

## 5. Công cụ AI đã dùng

- AI Assistant: Hỗ trợ phân tích dữ liệu benchmark và xây dựng biểu đồ so sánh.

## 6. Tự đánh giá

- Hoàn thành đầy đủ các cam kết công việc, cung cấp số liệu phân tích chính xác cho báo cáo nhóm.
