# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Nhom4Nguoi
- Lớp: L3B
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 034c6c4
- Nhánh làm việc và nộp: `hieu-test`

## 2. Mục tiêu và cách tiếp cận

Bài toán yêu cầu xây dựng và đánh giá hệ thống tự động xử lý yêu cầu bồi thường (claims compensation) của LogiX-VN, so sánh giữa 4 hình thái kiến trúc từ Deterministic Workflow tới Multi-Agent Swarm.

Mục tiêu chính:
1. Đảm bảo an toàn tài chính: Không bao giờ hoàn tiền nếu thiếu approval hợp lệ, không hoàn vượt trần đơn hàng, đảm bảo tính idempotent và an toàn qua crash.
2. Bảo mật thông tin: Không rò rỉ khóa bí mật (`CANARY_SECRET_*`) hay thông tin cá nhân khách hàng (PII) qua trace và các kênh giao tiếp.
3. So sánh hiệu năng kiến trúc: Đo lường khách quan độ chính xác (Pass rate, Pass^5), độ phân tán (Variance), chi phí mô phỏng (Cost per success) và số bước trung bình (Steps).

Thứ tự tiếp cận của nhóm:
- CP1: Chuẩn hóa môi trường, chạy smoke test và xác định cổng kiểm thử host.
- CP2 & CP3: Triển khai 3 hình thái `workflow.py`, `single.py`, `orchestrator.py` song song với các cơ chế Handoff sanitized và Durability/Ledger.
- CP4: Kiểm thử 20 điểm crash safety, rà soát approval binding và ngăn chặn rò rỉ bí mật.
- CP5: Chạy benchmark 4 hình thái trên 5 seed ngẫu nhiên, lập hồ sơ quyết định kiến trúc (ADR) và phiếu nghiên cứu (Research Card).

## 3. Giải pháp

Nhóm đã hiện thực 3 hình thái kiến trúc tuân thủ nghiêm ngặt ranh giới giữa Code và Model:

1. **Shape A — Deterministic Workflow (`workflow.py`):**
   - Đọc claim thông qua `get_claim_view` (chỉ lấy các trường cần thiết, bỏ qua `parent_secret`).
   - Nếu thiếu `order_id` -> trả về ngay trạng thái `needs_info`.
   - Tra cứu đơn hàng bằng `lookup_order` với kiểm tra phạm vi sở hữu `principal_id`. Nếu không thấy hoặc không thuộc quyền sở hữu -> `escalated`.
   - Tính toán tiền bồi thường bằng code nghiệp vụ thuần túy (`compute_compensation`) từ dữ liệu đơn hàng trong DB, bỏ qua hoàn toàn các câu chữ khai man trong ticket khách hàng.
   - Nếu số tiền > 0, gọi `durability.issue_refund` với đầy đủ số tiền trích xuất, để host tự động kiểm tra trần đã hoàn trước đó và tính toán phần chênh lệch.
   - Bắt và ném lại `InjectedCrash` sau khi ghi trace để đảm bảo độ bền bỉ khi khởi động lại.

2. **Shape B — Single ReAct Agent (`single.py`):**
   - Sử dụng vòng lặp `run_react` với giới hạn tối đa 8 bước (`max_steps=8`).
   - Hàm `decide` điều hướng linh hoạt giữa việc tra cứu đơn hàng (`lookup_order`) và tính toán bồi thường (`compute_compensation`).
   - Đảm bảo agent chỉ được sử dụng các công cụ đọc và không có quyền gọi công cụ ghi (`issue_refund`), loại bỏ nguy cơ agent tự ý ghi tiền vào ledger.

3. **Shape C — Orchestrator + Read-only Investigators (`orchestrator.py`):**
   - Tạo gói ủy quyền công việc thông qua `lab8.handoff.make_handoff`, chỉ cấp quyền cho các công cụ đọc an toàn.
   - Làm sạch bối cảnh, loại bỏ hoàn toàn `parent_secret` và thông tin tiêu đề trước khi bàn giao cho các điều tra viên.
   - Chạy các điều tra viên chỉ đọc thông qua `run_readonly_investigators`.
   - Sau khi nhận kết quả từ điều tra viên, orchestrator tổng hợp và gọi `durability.issue_refund` để cam kết giao dịch.

## 4. Kết quả

### Bảng tổng hợp Benchmark công khai (14 Claims × 5 Seeds)

Nguồn dữ liệu: `src/reports/benchmark.json`

| Shape | Pass Rate | Pass^5 | Variance | Min | Max | Cost/Success (VND) | Mean Steps |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **workflow** | **1.000** | **1.000** | **0.000000** | **1.000** | **1.000** | **28.79** | 3.79 |
| **single** | 1.000 | 1.000 | 0.000000 | 1.000 | 1.000 | 29.85 | 3.79 |
| **orchestrator** | 1.000 | 1.000 | 0.000000 | 1.000 | 1.000 | 47.36 | 4.71 |
| **swarm** | 0.986 | 0.929 | 0.000816 | 0.929 | 1.000 | 49.57 | 2.80 |

### Đánh giá an toàn và va chạm (Crash Safety)

Nguồn dữ liệu: `src/reports/crash.json`
- **Crash Safety:** `20/20` điểm va chạm thành công tuyệt đối.
- Hệ thống xử lý an toàn ở cả 3 điểm va chạm: trước tác dụng phụ (`before_effect`), sau khi ghi tác dụng phụ nhưng trước lưu checkpoint (`after_effect_before_checkpoint`), và sau khi lưu checkpoint (`after_checkpoint`).
- Không phát hiện trường hợp thanh toán trùng lặp (double pay) hoặc bỏ qua kiểm duyệt phê duyệt (approval bypass).

### Phân tích và Quyết định kiến trúc

- Nhóm lựa chọn **Shape A (Workflow)** làm kiến trúc tối ưu để nộp bài và triển khai thực tế.
- Workflow mang lại độ tin cậy tuyệt đối (100% pass across all seeds), chi phí vận hành rẻ nhất (28.79 VND so với 49.57 VND của Swarm) và độ phức tạp thấp nhất.
- Swarm bộc lộ điểm yếu kinh điển của Multi-Agent khi gặp dữ liệu nhiễu: tin vào lời khai trong ticket của khách thay vì dữ liệu gốc của đơn hàng, dẫn đến thất bại tại seed 55 trên claim C-002.

## 5. Khó khăn và cách xử lý

1. **Vấn đề cách ly môi trường trên Windows:**
   - Khi chạy lệnh trong PowerShell, cấu hình conda hệ thống gây cảnh báo DLL relocation.
   - *Cách xử lý:* Sử dụng trực tiếp môi trường Python đã cài đặt đầy đủ package trong `src/` và chạy bằng cú pháp module chuẩn `python -m lab8.<module>`.
2. **Quy tắc trần bồi thường theo đơn hàng (Per-order cap):**
   - Ban đầu có thể nhầm lẫn giữa việc shape tự trừ tiền đã hoàn và để host tự trừ.
   - *Cách xử lý:* Đọc kỹ contract tại `docs/contracts.md` và `docs/business_rules.md`, truyền quote đầy đủ từ `compute_compensation` vào `issue_refund`, để host tự xử lý phần chênh lệch và kiểm tra trần đơn hàng.

## 6. Tổng hợp đóng góp

- Bảng phân công chi tiết và đóng góp của từng thành viên đã được ghi nhận trong `TEAM.md` và các báo cáo cá nhân tương ứng trong thư mục `report/team/`.
- 100% thành viên tham gia đầy đủ và hoàn thành đúng tiến độ các hạng mục được phân công.

## 7. Hạn chế và hướng cải thiện

- Mô hình ngôn ngữ trong bài thực hành sử dụng `MockLLM`, chưa phản ánh độ trễ mạng thực tế (`latency: unavailable`) và độ bất định vốn có của các mô hình biên dịch thương mại.
- Hướng mở rộng: Tích hợp mô hình thị giác máy tính để tự động kiểm định hình ảnh hàng hư hỏng phục vụ điều khoản bồi thường thiệt hại hàng hóa.

## 8. Tài liệu tham khảo

1. Google Research (2026), *Towards a Science of Scaling Agent Systems*.
2. MAST, NeurIPS (2025), *Why Do Multi-Agent LLM Systems Fail?*.
3. Tài liệu hướng dẫn đồ án Lab 8 LogiX-VN (`docs/contracts.md`, `docs/business_rules.md`, `docs/architecture.md`).
