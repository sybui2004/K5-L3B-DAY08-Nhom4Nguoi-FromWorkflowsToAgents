# Báo cáo cá nhân — 2A202603981_BuiPhanThanhPhuc

## 1. Thông tin thành viên

- Họ tên: Bùi Phan Thanh Phúc
- MSSV: 2A202603981
- Email: thanhphuccrkh@gmail.com
- GitHub: https://github.com/Jancaster1234

## 2. Phần việc phụ trách

Thành viên 1 (TV1), vai **Workflow + integration**:

- Shape A **workflow** (`src/lab8/shapes/workflow.py`). Đây là shape nhóm chọn trong `report/team/decision_adr.md` để chấm hidden.
- Test của shape: `src/tests/test_shape_workflow.py`.
- Tài liệu tóm tắt luồng bài lab cho cả nhóm: `WORKFLOW.md`.
- Tích hợp phần của mình vào `main`: nhánh `feature/workflow-shape`, merge `main` mới vào nhánh rồi mở PR #2.

## 3. Đóng góp cụ thể

Commit: `c839ece` (`feat(workflow): implement deterministic workflow shape`) trên nhánh `feature/workflow-shape`, vào `main` qua PR #2.

**Workflow.** Các bước Python cố định, model không quyết định gì:

1. Đọc claim qua `get_claim_view` (chỉ các cột trong allowlist). Claim không tồn tại thì trả `failed`, không ném exception.
2. Thiếu `order_id` thì trả `needs_info`, không lấy mã đơn từ câu chữ trong ticket.
3. `lookup_order` theo principal. Không thấy đơn hoặc sai chủ đơn thì trả `escalated`, trace chỉ ghi `reason`.
4. Quote bằng `compute_compensation` từ order row. Số ngày trễ ghi trong ticket bị bỏ qua.
5. Quote bằng 0 thì trả `denied` và không gọi host.
6. Quote > 0 thì gọi `durability.issue_refund` với **quote đầy đủ** và chuyển tiếp `crash_at`. Kết quả host đổi thành status: `ok` → `resolved`, `conflict` → `failed`, còn lại → `denied`, `proposal_amount` giữ quote đầy đủ để host ghi `policy_denied`.
7. MockLLM chỉ được gọi một lần để soạn lời trả khách.

Quyết định kỹ thuật cần giải thích được:

- **Không đọc số ngày từ ticket:** ticket là dữ liệu người dùng, có thể nói dối hoặc chứa lệnh. Nguồn sự thật là order row và policy hiện hành. Đây là chỗ swarm sai ở C-002 seed 55.
- **Truyền quote đầy đủ:** host tự trừ phần đơn đã được hoàn. Shape trừ trước thì bị trừ hai lần và T14 fail.
- **Ghi trace rồi mới `raise` lại `InjectedCrash`:** grader vẫn có trace hợp lệ cho lần chạy bị crash, và T12 thấy crash thật sự xảy ra. Khi resume, host tra ledger theo khóa `refund:{claim_id}` nên không trả lần hai.

**Cách làm.** Tôi tự viết shape workflow theo luồng 7 bước ở trên, kèm bản của single và orchestrator, rồi chạy bộ test: cổng host xanh, bộ student 248/248 passed, crash suite 20/20, benchmark 4 shape × 5 seed cho workflow pass 1.000 với cost/success thấp nhất. Bản này đã đủ để nộp, nhưng tôi chưa push vì nhóm muốn một bạn làm lại toàn bộ luồng từ đầu đến cuối để demo và cả nhóm cùng hiểu luồng. Sau buổi demo, nhóm chia phần đã demo ra theo từng thành viên để commit cho nhanh; bản workflow được commit là bản dùng trong demo, cùng luồng và cùng kết quả test với bản tôi đã viết. Tôi kiểm thử lại và commit phần workflow lên nhánh `feature/workflow-shape`.

**Tích hợp.** Kiểm tra `main` sau PR #1 thì thấy `workflow.py` vẫn là stub trong khi ADR chọn workflow. Tôi merge `main` mới vào `feature/workflow-shape`, chạy lại toàn bộ test, rồi cập nhật PR #2 (không xung đột).

## 4. Bằng chứng

Test (chạy trong `src/`):

```text
python -m pytest -q tests/test_shape_workflow.py
7 passed
python -m pytest -q -m student -o addopts= -k workflow
62 passed
```

- `src/tests/test_shape_workflow.py`: ticket C-002 nói trễ 5 ngày nhưng order ghi 2 ngày thì bị từ chối ở cả 5 seed; ticket chứa "IGNORE POLICY" không tạo dòng ledger nào; claim không tồn tại trả `failed` với `error_reason = unknown_claim`.
- Sau khi merge `main` vào nhánh: cổng host 112 passed; student cho workflow, orchestrator, swarm 186 passed.
- Số liệu workflow trên bộ public (`src/reports/benchmark.json`): pass 1.000, pass^5 1.000, variance 0.
- Chấm local trên bộ hidden bằng nhãn do lab coach cung cấp (40 claim × 5 seed): workflow pass 1.000, pass^5 1.000, 0 trial lộ secret/PII, 0 trial ghi tiền khi approval không hợp lệ. Điểm chính thức do grader của giảng viên chấm.

## 5. Công cụ AI đã dùng

- Claude Code: giải thích đề và luật nghiệp vụ, hỗ trợ viết bản workflow, single, orchestrator đầu tiên, chạy test và benchmark, kiểm tra các nhánh của nhóm, hỗ trợ tách commit, merge `main` và mở PR.
- Cách tự kiểm tra: tự chạy lại `pytest` (cổng host, bộ student, test riêng của workflow), đối chiếu benchmark chạy lại với file JSON đã commit, và đọc lại từng bước trong `workflow.py` để tự trả lời được ba câu ở mục 3.

## 6. Tự đánh giá

- Làm tốt: hiểu và giải thích được ranh giới code / model trong workflow; phát hiện `main` còn stub workflow sau PR #1 và sửa qua PR #2.
- Hạn chế: để thống nhất với bản demo của nhóm, bản workflow tôi tự viết không được push nguyên trạng; lịch sử git chỉ có bản đã thống nhất.
- Cần làm thêm: hỗ trợ nhóm đưa `single` và các report vào `main` để `python -m lab8.check_submission` ra `0 FAIL`.
