# Team

## Thông tin nhóm

- Tên nhóm: Nhom4Nguoi
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-Nhom4Nguoi-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/VinUni-AI20k/K5-L3B-DAY08-Nhom4Nguoi-FromWorkflowsToAgents, hieu-test, 034c6c4

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Hoàng Ngọc Hiếu | 20240001 | hoangngochieutin92018@gmail.com | hoangngochieu | Workflow + Integration (Team Lead) |
|   2 | Trần Đức Minh | 20240002 | minhtd@vinuni.edu.vn | minhtd | Single Agent |
|   3 | Lê Thị Mai | 20240003 | mailt@vinuni.edu.vn | mailt | Orchestrator + Handoff |
|   4 | Phạm Quốc Bảo | 20240004 | baopq@vinuni.edu.vn | baopq | Ledger + Evaluation |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Hoàng Ngọc Hiếu | Workflow + Integration | 034c6c4 | tests/test_public_matrix.py (workflow) |
| Trần Đức Minh | Single Agent | 034c6c4 | tests/test_public_matrix.py (single) |
| Lê Thị Mai | Orchestrator + Handoff | 034c6c4 | tests/test_public_matrix.py (orchestrator) |
| Phạm Quốc Bảo | Ledger + Evaluation | 034c6c4 | tests/test_crash_suite.py |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 20240001_HoangNgocHieu

### Phần việc phụ trách

- Trưởng nhóm, phụ trách tích hợp toàn bộ luồng chấm điểm, cài đặt môi trường, điều phối CP1-CP5.
- Triển khai Shape A (Deterministic Workflow) tại `src/lab8/shapes/workflow.py`.

### Đóng góp cụ thể

- Thiết kế kiến trúc workflow xác định, đảm bảo tuân thủ hợp đồng bảo mật không rò rỉ secret/PII.
- Vượt qua 62/62 student test cases cho Shape A và chạy toàn diện ma trận kiểm thử 248 test cases.

### Bằng chứng

- Commit 034c6c4, `tests/test_public_matrix.py` (workflow pass 62/62), `reports/benchmark.json`.

## 20240002_TranDucMinh

### Phần việc phụ trách

- Triển khai Shape B (Single Agent ReAct) tại `src/lab8/shapes/single.py`.

### Đóng góp cụ thể

- Cài đặt vòng lặp ReAct có chặn chặn step cap (max_steps=8), logic `decide` gọi các công cụ đọc `lookup_order` và `compute_compensation`.
- Đảm bảo agent không gọi công cụ ghi và vượt qua 62/62 test cases.

### Bằng chứng

- Commit 034c6c4, `tests/test_public_matrix.py` (single pass 62/62).

## 20240003_LeThiMai

### Phần việc phụ trách

- Triển khai Shape C (Orchestrator + Readonly Investigators) tại `src/lab8/shapes/orchestrator.py`.

### Đóng góp cụ thể

- Dựng handoff chuẩn hóa qua `make_handoff`, sanitize context, không truyền `parent_secret` sang điều tra viên.
- Vượt qua 62/62 test cases cho orchestrator.

### Bằng chứng

- Commit 034c6c4, `tests/test_handoff_secret.py`, `tests/test_public_matrix.py` (orchestrator pass 62/62).

## 20240004_PhamQuocBao

### Phần việc phụ trách

- Phụ trách Ledger, Durability, Crash safety và bộ môn Benchmark / Evaluation.

### Đóng góp cụ thể

- Thực hiện kiểm thử 20 điểm crash safety qua `lab8.crash_test` đạt 20/20.
- Vận hành benchmark đa hình thái, lập báo cáo phân tích kiến trúc ADR và Research Card.

### Bằng chứng

- `reports/crash.json` (20/20), `reports/benchmark.json`, `report/team/decision_adr.md`.
