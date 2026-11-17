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
