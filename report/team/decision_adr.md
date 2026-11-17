# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: <điền bằng `git rev-parse --short HEAD` sau commit cuối>
- Run id dẫn chứng: R-workflow-C-001-s11 (src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0 (src/reports/benchmark.json)
- Cost per success (mô phỏng, VND): 28.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Cùng corpus (14 claim public), cùng 5 seed (11, 22, 33, 44, 55), cùng MockLLM, tool và giá, 4 shape cho kết quả như sau:

| Shape | Pass rate | Pass^5 | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps |
| --- | ---: | ---: | ---: | ---: | --- |
| workflow | 1.000 | 1.000 | 0 | 28.86 | 4.43 / 5 |
| single | 1.000 | 1.000 | 0 | 30.60 | 9.21 / 10 |
| orchestrator | 1.000 | 1.000 | 0 | 57.20 | 5.36 / 6 |
| swarm | 0.986 | 0.929 | 0.000816 | 49.57 | 2.80 / 3 |

Ba shape của nhóm đều đạt 1.000 trên bộ public, nên pass rate không phân biệt được chúng. Nhóm chọn **workflow** vì nó là shape ít tự chủ nhất mà vẫn đạt pass 1.0 và pass^5 1.0, với cost/success thấp nhất. Mọi dữ kiện quyết định (ngày trễ, trạng thái, hỏng hàng, phí) đã có trong DB có cấu trúc, nên không có bước nào cần model suy luận. Tiền luôn đến từ `compute_compensation`, và host chặn approval, trần theo đơn và idempotency. Khác biệt duy nhất về chất lượng nằm ở swarm: lần fail duy nhất là C-002 seed 55, khi swarm tin số ngày trễ ghi trong ticket (`R-swarm-C-002-s55`, `status resolved != denied`).

## Có đáng đổi lấy multi-agent không

Nhóm giữ workflow. Trên bộ public, multi-agent không cho pass nhỉnh hơn: orchestrator bằng workflow (1.000) nhưng đắt gấp khoảng 2 lần (57.20 so với 28.86), còn swarm vừa thấp hơn vừa có variance. Bonus B3 cho thấy ngay cả khi thêm verifier bằng code đưa swarm lên 1.000 / 1.000, cost/success vẫn là 57.57, tức gấp khoảng 2 lần workflow (`report/team/bonus_report.md`).

Quyết định đảo lại khi: (1) task có phần đọc độc lập thật sự song song được và latency là chi phí chính, vì orchestrator có thể rút critical path; (2) dữ kiện quyết định không còn nằm hết trong DB có cấu trúc, ví dụ phải đọc văn bản tự do hoặc nhiều nguồn ngoài, khi đó cần investigator/model suy luận; (3) bộ hidden cho thấy workflow fail ở nhóm claim mà shape khác xử lý được. Hiện chưa có bằng chứng nào trong ba điều này.

## Trace và bằng chứng

Trace ghi: claim view đã allowlist, từng lần gọi tool (tên và kết quả đã `safe_dump`), `quote`, lần gọi model (số lần và token để tính cost), kết quả host (`refund_committed`, `policy_denied`) và trạng thái cuối. Với orchestrator còn có handoff đã sanitize và tóm tắt kết quả investigator; với bonus còn có `verifier_override`.

Cố ý **không** ghi: nguyên văn ticket (bộ hidden có ticket chèn lệnh và homoglyph, ghi vào trace là đưa dữ liệu không tin cậy vào bằng chứng), `parent_secret` và `CANARY_SECRET_*`, header thô, số điện thoại, ghi chú nội bộ.

Bằng chứng không lộ: mọi trial trong benchmark đều `ok` theo `lab8.metrics.trial_pass`, nghĩa là không có `forbidden_substring` và không có `unexpected_ledger_rows`. Trace nằm trong `traces/` và được scanner của grader quét; test `test_shape_orchestrator.py` kiểm handoff và trace của orchestrator trên claim public, `test_shape_trace_safety.py` (TV4) kiểm cả ba shape. Grader fail-closed với `missing_trace`, `stale_trace`, `invalid_trace`.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.

Bộ public chỉ có 14 claim và ba shape đều đạt 1.000, nên chưa đủ để kết luận khác biệt thống kê giữa chúng. Lần fail duy nhất của swarm là xác định theo seed (chia hết cho 5), không phải nhiễu ngẫu nhiên. Số liệu trên lấy từ `src/reports/benchmark.json` do `lab8.benchmark` sinh, không sửa tay.
