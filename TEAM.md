# Team

## Thông tin nhóm

- Tên nhóm: Nhom4Nguoi
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-Nhom4Nguoi-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/sybui2004/K5-L3B-DAY08-Nhom4Nguoi-FromWorkflowsToAgents , main , `aa86e18`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Bùi Thái Sỹ | 2A202604002 | | https://github.com/sybui2004 | Nhóm trưởng; orchestrator + handoff; bonus B3; tích hợp và báo cáo nhóm |
|   2 | Bùi Phan Thanh Phúc | 2A202603981 |  | https://github.com/Jancaster1234 | Workflow + integration |
|   3 | Hoàng Ngọc Hiệu | 2A202603976 |  | https://github.com/hoangngochieu10012000 | Single agent (ReAct) + showcase |
|   4 | Đoàn Sỹ Hưng | 2A202603990 | | https://github.com/hgmdz1210 | Ledger + evaluation + slide/demo |

- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Bùi Phan Thanh Phúc | Workflow + integration | `c839ece`, `8c1974e` | `src/tests/test_shape_workflow.py` |
| Hoàng Ngọc Hiệu | Single agent + showcase | `a68db94` | `src/tests/test_shape_single.py` |
| Bùi Thái Sỹ | Orchestrator + handoff + bonus B3 | `9547e34`, `ba21183` | `src/tests/test_shape_orchestrator.py`, `src/tests/test_bonus_swarm_verified.py` |
| Đoàn Sỹ Hưng | Ledger + evaluation | `291725c`, `b824ba1`, `b2550dc` | `src/tests/test_shape_trace_safety.py` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202604002_BuiThaiSy

### Phần việc phụ trách

- Shape orchestrator và handoff (`src/lab8/shapes/orchestrator.py`).
- Bonus B3: swarm có verifier bằng code (`src/bonus/`).
- Tích hợp nhánh, điền `TEAM.md`, `group_report.md`, `decision_adr.md`, `research_card.md`.

### Đóng góp cụ thể

- Orchestrator: handoff qua `make_handoff` với `facts` rỗng, investigator chỉ có tool đọc, chỉ orchestrator gọi `issue_refund` với quote đầy đủ.
- B3: verifier đọc lại order, ghi `verifier_override`, tối đa 1 vòng sửa rồi fail-closed; 8 claim đối kháng có nhãn tay.

### Bằng chứng

- `src/tests/test_shape_orchestrator.py`, `src/tests/test_bonus_swarm_verified.py` (51 passed).
- Báo cáo cá nhân: `report/team/202604002_BuiThaiSy.md`.

## 2A202603981_BuiPhanThanhPhuc

### Phần việc phụ trách

- Shape workflow (`src/lab8/shapes/workflow.py`), shape nhóm chọn để chấm hidden.
- Test workflow (`src/tests/test_shape_workflow.py`) và tài liệu luồng bài lab `WORKFLOW.md`.
- Tích hợp nhánh `feature/workflow-shape` vào `main` (PR #2, PR #4).

### Đóng góp cụ thể

- Workflow: các bước Python cố định, quote từ order row qua `compute_compensation`, bỏ qua số ngày trong ticket, truyền quote đầy đủ vào `issue_refund`, chuyển `crash_at` và không bắt `InjectedCrash`; model chỉ soạn lời trả khách.
- Test bổ sung: quote đầy đủ tới host (T14), host từ chối có audit `policy_denied`, crash ở 3 điểm rồi resume chỉ một refund, đúng 1 model call mỗi claim, `escalated` không lộ PII.

### Bằng chứng

- Commit `c839ece` (workflow), `8c1974e` (test).
- `src/tests/test_shape_workflow.py` (31 passed).
- Báo cáo cá nhân: `report/team/2A202603981_BuiPhanThanhPhuc.md`.

## 2A202603976_HoangNgocHieu

### Phần việc phụ trách

- Shape single agent ReAct (`src/lab8/shapes/single.py`).
- Test single agent (`src/tests/test_shape_single.py`).
- Ứng dụng showcase Streamlit (`showcase/app.py`, `showcase/catalog/`, `showcase/services/`, `showcase/ui/`, `showcase/views/`).
- Tích hợp nhánh `feature/single-agent-shape` vào `main` (PR #6).

### Đóng góp cụ thể

- Single agent: ReAct tối đa 8 bước, agent chỉ chọn tool đọc; shape giữ trạng thái claim, order, quote giữa các lượt, dừng `needs_info` nếu thiếu `order_id`, lấy số tiền từ `compute_compensation` thay vì lời agent hoặc nội dung ticket, rồi gọi `issue_refund` với quote đầy đủ để host kiểm tra; ghi trace và chuyển tiếp crash được tiêm.
- Test bổ sung: giới hạn số bước và quyền chỉ đọc, hạch toán số lần gọi model, claim thiếu `order_id` dừng trước khi tra cứu order.
- Showcase: chạy ticket, so sánh các shape, xem bảo mật và trace, thử crash/retry, xem benchmark.

### Bằng chứng

- Commit `a68db94` (single agent + showcase).
- `src/tests/test_shape_single.py` (3 passed).
- Báo cáo cá nhân: `report/team/2A202603976_HoangNgocHieu.md`.

## 2A202603990_DoanSyHung

### Phần việc phụ trách

- Test an toàn trace cho các shape của nhóm (`src/tests/test_shape_trace_safety.py`).
- Chạy benchmark công khai và crash suite, sinh `src/reports/benchmark.json`, `src/reports/crash.json`.
- Đo đạc bonus B3 (`src/bonus/verifier_stats.py`, `src/reports/bonus_*.json`, `report/team/bonus_report.md`).
- Slide và tài liệu demo (`showcase/slides/`, `DEMO.md`, `RUN_DEMO.md`).
- Tích hợp nhánh `feature/evaluation-and-reports` vào `main` (PR #5).

### Đóng góp cụ thể

- Test trace: với mỗi claim public và mỗi shape (workflow, single, orchestrator), trace phải thuộc đúng lần chạy (`run_id` khớp), không chứa `CANARY_SECRET_*`, chuỗi cấm hay nguyên văn ticket; claim không tồn tại vẫn có trace; trace thiếu, cũ hoặc sai định dạng bị fail-closed.
- Báo cáo sinh bằng lệnh: benchmark 4 shape × 5 seed, crash suite, thống kê verifier và benchmark B3 (swarm so với swarm_verified so với workflow).
- Slide và hướng dẫn chạy demo.

### Bằng chứng

- Commit `01ca29e` (slide, demo), `291725c` (test trace), `b824ba1` (benchmark, crash), `b2550dc` (bonus B3).
- `src/tests/test_shape_trace_safety.py` (45 passed).
- Báo cáo cá nhân: `report/team/2A202603990_DoanSyHung.md`.
