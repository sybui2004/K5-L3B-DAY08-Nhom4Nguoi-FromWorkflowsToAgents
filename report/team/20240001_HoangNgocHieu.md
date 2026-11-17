# Báo cáo cá nhân — 20240001_HoangNgocHieu

## 1. Thông tin thành viên

- Họ tên: Hoàng Ngọc Hiếu
- MSSV: 20240001
- Email: hoangngochieutin92018@gmail.com
- GitHub: hoangngochieu

## 2. Phần việc phụ trách

- Trưởng nhóm, phụ trách tích hợp và kiến trúc hệ thống (Integration & Architecture).
- Lập trình hình thái Shape A (Deterministic Workflow) tại `src/lab8/shapes/workflow.py`.
- Thiết lập môi trường, kiểm thử suite và hoàn thiện các mốc Checkpoint CP1 -> CP5.

## 3. Đóng góp cụ thể

- Triển khai Shape A tuân thủ đúng hợp đồng Output Contract và Trace Contract v1.
- Không để model tự đưa ra quyết định tiền bạc hoặc commit trực tiếp vào ledger mà ủy thác cho `compute_compensation` và `durability.issue_refund`.
- Vượt qua toàn bộ 62/62 test student cho Shape A, giữ vững toàn bộ 54 host tests pass và crash safety 20/20.

## 4. Bằng chứng

- Commit hash: 034c6c4
- Test: `tests/test_public_matrix.py` (workflow pass 62/62), `tests/test_trace_contract.py`.
- Run ID dẫn chứng: `R-workflow-C-001-s11`.
- Kết quả benchmark: Pass rate 1.000, Pass^5 1.000, Variance 0.000000, Chi phí 28.79 VND.

## 5. Công cụ AI đã dùng

- Antigravity AI Assistant: Hỗ trợ rà soát hợp đồng contract, phân tích lỗi pytest và sinh template báo cáo tuân thủ chuẩn rubric của môn học. Tự tay kiểm tra và xác thực mọi lệnh chạy trong môi trường cục bộ.

## 6. Tự đánh giá

- Hoàn thành xuất sắc 100% nhiệm vụ được giao, hỗ trợ đồng đội hoàn thành các shape và bài nộp đúng hạn.
