# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 034c6c4
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000
- Cost per success (mô phỏng, VND): 28.79
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 leak / 0 bypass (vượt qua tất cả test allowlist và PII scan)

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng tập claim công khai (14 claims) và 5 seed thử nghiệm (11, 22, 33, 44, 55), shape **workflow** đạt hiệu năng và độ ổn định tối ưu:
- **Độ tin cậy tuyệt đối:** Pass rate đạt 1.000, pass^5 đạt 1.000 với phương sai variance = 0.000000 (không bị ảnh hưởng bởi seed variance).
- **Chi phí thấp nhất:** Chi phí mô phỏng là 28.79 VND/success, thấp hơn đáng kể so với Single Agent (29.85 VND), Orchestrator (47.36 VND) và Swarm (49.57 VND).
- **Tính xác định cao (Deterministic):** Xử lý luồng bồi hoàn claims dựa hoàn toàn trên luật nghiệp vụ cố định (`compute_compensation`), đọc trực tiếp từ database đã chuẩn hóa, không bị đánh lừa bởi thông tin sai lệch trong ticket của khách hàng (điểm yếu mà Swarm gặp phải ở seed 55 với claim C-002).

## Có đáng đổi lấy multi-agent không

**Không đáng đổi trong bài toán này.** 
Multi-agent (như Swarm) mang lại chi phí cao hơn gần gấp đôi (49.57 VND so với 28.79 VND), số bước trung bình biến động và tiềm ẩn rủi ro hallucination hoặc tin tưởng mù quáng vào text người dùng nếu không có guardrails cứng. Swarm có pass rate giảm xuống 0.986 (pass^5 chỉ đạt 0.929) do fail ở seed 55 trên claim C-002 khi tin số ngày trễ ghi trong ticket thay vì dữ liệu thực tế trong bảng orders.

**Điều kiện làm quyết định đảo lại:**
Quyết định kiến trúc chỉ nên đảo lại (chọn multi-agent hoặc single agent ReAct) khi:
1. Nghiệp vụ mở rộng sang các trường hợp phi cấu trúc phức tạp mà code tĩnh không thể bao phủ (ví dụ: thẩm định bằng chứng ảnh chụp sản phẩm bị hư hỏng, phân tích ngôn ngữ tự nhiên từ hợp đồng đối tác chưa số hóa).
2. Quy trình yêu cầu đàm phán nhiều vòng với khách hàng hoặc phối hợp giữa các bên thứ ba độc lập với API động.

## Trace và bằng chứng

Trace của nhóm được thiết kế tuân thủ nghiêm ngặt **Trace contract v1**:
- **Events được ghi nhận:** Ghi nhận các bước thực thi hợp lệ bao gồm `claim_view` (chỉ chứa claim_id và order_id), `lookup_order` (trạng thái hiển thị và lý do), `quote` (thông tin bồi thường đã tính toán từ DB), `decision` (trạng thái quyết định), `refund_decision` (kết quả ghi nhận từ ledger host) và `crash` (nếu có fault injection).
- **Field cố ý KHÔNG ghi nhận:** Tuyệt đối không ghi `parent_secret`, `raw_headers`, thông tin PII khách hàng (số điện thoại, địa chỉ cụ thể, tên mặt hàng chi tiết, internal notes trong bảng orders). 
- **Bảo mật và chứng minh:** Toàn bộ dữ liệu đi qua tracer đều qua allowlist định sẵn. Nếu trace nằm ngoài chỗ scanner quét được, đội security có thể chứng minh tính an toàn bằng cách đối chiếu mã nguồn kiểm soát luồng (code review), kiểm tra contract allowlist ở tầng runtime/dispatch và chạy bộ test quét PII tự động (`test_trace_contract.py` và `test_handoff_secret.py`).

## Giới hạn

MockLLM không phải model sản xuất thực tế. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.
