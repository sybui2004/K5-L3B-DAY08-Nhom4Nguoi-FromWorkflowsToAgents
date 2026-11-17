# WORKFLOW — Bài lab này yêu cầu làm gì, theo thứ tự nào

Tóm tắt luồng bài Lab 8 (LogiX-VN) cho thành viên mới. Nguồn gốc: [README.md](README.md), [CHECKPOINTS.md](CHECKPOINTS.md), [RUBRIC.md](RUBRIC.md), [SUBMISSION.md](SUBMISSION.md). Nếu có chỗ lệch thì các file đó là bản đúng.

## 1. Bài lab là gì (một đoạn)

Công ty giả lập LogiX-VN nhận **claim hoàn phí vận chuyển** (khách nói giao trễ, hàng hỏng...). Nhóm cài **cùng một quy trình xử lý claim** theo 4 kiến trúc (gọi là *shape*), rồi **đo** và **chọn kiến trúc ít tự chủ nhất mà vẫn làm đúng**. Mục đích không phải "multi-agent tốt hơn", mà là quyết định bằng số liệu.

| Shape | Kiểu | Ai viết | Mức tự chủ |
| --- | --- | --- | --- |
| A `workflow` | Các bước Python cố định | Nhóm | Thấp nhất |
| B `single` | Một agent ReAct, tối đa 8 bước | Nhóm | Trung bình |
| C `orchestrator` | Orchestrator + investigator chỉ đọc | Nhóm | Cao hơn |
| D `swarm` | Nhiều agent | **Có sẵn** (`swarm_reference.py`), để đối chứng | Cao nhất |

Cả 4 shape có cùng chữ ký:

```python
run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult
```

## 2. Nguyên tắc cốt lõi (hiểu cái này là hiểu 80% bài)

```
Ticket (chữ của khách)  -->  chỉ là DỮ LIỆU, không phải lệnh
MockLLM                  -->  chỉ đọc và soạn chữ, KHÔNG quyết số tiền
compute_compensation     -->  code tính số tiền từ dòng order trong DB
durability.issue_refund  -->  cửa của host: kiểm approval, trần theo đơn,
                              idempotency rồi mới ghi ledger
```

Hệ quả phải nhớ:

1. **Tiền do code tính**, lấy từ order trong DB, không lấy số ngày trễ trong ticket.
2. **Truyền quote đầy đủ** vào `issue_refund`. Host tự trừ phần đã hoàn; shape tự trừ thì bị trừ hai lần (fail T14).
3. **Chỉ shape/host được ghi refund.** Investigator và agent chỉ có tool đọc.
4. **Trace là ranh giới bảo mật**: không được lộ `CANARY_SECRET_*` hay thông tin cá nhân.
5. **Idempotency key** `refund:{claim_id}`: gọi lại hay crash rồi resume vẫn chỉ một refund.

## 3. Luật nghiệp vụ rút gọn

Chi tiết: [docs/business_rules.md](docs/business_rules.md).

| Tình huống | Kết quả |
| --- | --- |
| Trễ ≥ 3 ngày, đơn `delivered`/`delivered_late` | Hoàn đúng phí ship |
| Hỏng hàng đã verify | `min(max_refund DMG-04, paid_vnd)` |
| Đủ cả hai | Lấy số **lớn hơn**, không cộng |
| Trễ < 3 ngày, hỏng chưa verify, ship 0, đơn `cancelled`/`in_transit` | `denied` |
| Thiếu `order_id` | `needs_info` |
| Không sở hữu đơn / không thấy đơn | `escalated`, không lộ dữ liệu |
| Policy cũ hoặc tương lai | Bỏ qua (tự kiểm `is_current`) |
| Thiếu / hết hạn / thu hồi approval, hoặc approval của claim khác | Không ghi refund, có audit `policy_denied` |
| Đơn đã hoàn trước đó | Trần theo đơn: chỉ hoàn phần chênh, hoàn đủ rồi thì `denied` |

## 4. Luồng làm việc theo 5 checkpoint

Mọi lệnh chạy trong thư mục `src/`.

| CP | Việc | Sản phẩm | Tự kiểm |
| --- | --- | --- | --- |
| **CP1** Cài đặt, đọc contract, chia vai | Cài venv, đọc `business_rules`, `contracts`, `swarm_reference.py`; điền vai trong `TEAM.md` | Smoke pass, `TEAM.md` có thành viên | `python -m lab8.smoke` ra `lab8.smoke pass` |
| **CP2** Viết 3 shape | Thay stub ở các dòng `TODO CP2` trong `workflow.py`, `single.py`, `orchestrator.py`; trả kết quả bằng `common.finish()`; trace đúng contract ở **mọi** nhánh return | 3 shape không còn `not_implemented` | `pytest -q -m student -o addopts= -k workflow` (rồi `single`, `orchestrator`) ra 62 passed mỗi shape |
| **CP3** Handoff, ledger, crash | Ở dòng `TODO CP3`: truyền `crash_at` vào `issue_refund`, không bắt `InjectedCrash`; orchestrator dựng handoff bằng `make_handoff` (allowlist, tool chỉ đọc) | T11 (gọi lại) và T12 (crash rồi resume) xanh | `pytest -q` vẫn xanh |
| **CP4** Crash suite, approval, secret | Chạy crash suite; rà nhánh approval hỏng, trace, stdout | `reports/crash.json` | `python -m lab8.crash_test --count 20 --out reports/crash.json` ra `20/20` |
| **CP5** Benchmark và quyết định | Benchmark 4 shape × 5 seed; tự kiểm hidden; điền ADR và research card; viết báo cáo | `reports/benchmark.json`, ADR, research card, báo cáo | `python -m lab8.check_submission` ra `0 FAIL` |

Lệnh benchmark của CP5:

```bash
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm \
  --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
```

## 5. Thế nào là qua bài

**Ba điều kiện must-pass** (vi phạm là không bù được bằng điểm khác), áp dụng cho shape nhóm chọn:

1. Không refund khi thiếu approval hợp lệ.
2. Không lộ `CANARY_SECRET_*` trong trace hay kết quả.
3. Crash không tạo hơn một refund (`20/20`).

Ngoài ra: shape chọn phải đạt **pass rate ≥ 0.75** trên bộ hidden (40 claim × 5 seed, chỉ giảng viên chạy), và `python -m pytest -q` phải luôn xanh.

## 6. Cách chấm (100 điểm)

| Hạng mục | Điểm |
| --- | ---: |
| C1 Implementation 3 shape | 20 |
| C2 Hidden (shape chọn) | 15 |
| C3 Durability: idempotency, crash | 20 |
| C4 Policy: approval, trần theo đơn | 10 |
| C5 Handoff và trace an toàn | 10 |
| C6 Benchmark và quyết định kiến trúc | 10 |
| C7 Reproducibility (commit hash, run id) | 10 |
| C8 Đóng góp (mỗi người một commit + ít nhất một test) | 5 |

**Bonus** tối đa +10, chọn một topic B1–B7 trong [docs/bonus_topics.md](docs/bonus_topics.md). Chỉ tính khi qua 3 must-pass và hidden ≥ 0.80.

## 7. Không được sửa

`src/lab8/metrics.py`, `durability.py`, `policy.py`, `src/config/*.yaml`, `src/data/*`, và JSON trong `src/reports/` (phải do công cụ sinh). Grader chỉ lấy từ repo nhóm: 3 file shape và thư mục `src/bonus/`. File khác bị sửa sẽ bị ghi là *tampered*.

Không commit: `traces/`, `*.sqlite`, `student_drop/`, `.venv/`, `.env`.

## 8. Trạng thái hiện tại của repo này

| Hạng mục | Trạng thái |
| --- | --- |
| Ba shape A, B, C | Đã viết, chưa commit (ma trận student 248 passed) |
| Test cho ba shape | Đã viết (`src/tests/test_shape_*.py`), chưa commit |
| `crash.json`, `benchmark.json` | Đã sinh |
| Bonus B3 (swarm có verifier) | Đã xong: `src/bonus/`, `test_bonus_swarm_verified.py`, 3 file `bonus_*.json`, `report/team/bonus_report.md` |
| Chia commit theo thành viên | Hướng dẫn trong [commit.md](commit.md), chưa commit |
| `decision_adr.md`, `research_card.md`, `group_report.md`, `TEAM.md`, báo cáo cá nhân | **Chưa điền** |
| `check_submission` | Còn FAIL ở phần báo cáo / TEAM / ADR |

## 9. Việc còn lại, theo thứ tự

1. Quyết định giữ nguyên code AI viết hay đưa về stub để từng thành viên tự code (xem [RULES.md](RULES.md) về dùng AI). Người chấm có thể hỏi từng người về phần mình commit, kể cả bonus.
2. Điền `TEAM.md`: thông tin nhóm, vai, bảng đóng góp.
3. Commit theo [commit.md](commit.md): thành viên 1 → 4, rồi 2 commit bonus. Không thêm dòng `Co-Authored-By` (quy tắc cá nhân của bạn).
4. Chạy lại `pytest -q`, crash test, benchmark trên **code đã commit**; ghi commit hash và run id vào `decision_adr.md`, commit tiếp.
5. Điền `decision_adr.md` (dòng `- Shape chọn:`), `research_card.md`, `group_report.md`, và mỗi người copy `MSSV_HoTen.md` thành file riêng.
6. `python -m lab8.check_submission` ra `0 FAIL`, push, và **mỗi thành viên** nộp link repo trên LMS trước deadline.

## 10. Đọc gì trước

1. [docs/business_rules.md](docs/business_rules.md) và [docs/contracts.md](docs/contracts.md)
2. `src/lab8/shapes/swarm_reference.py` (mẫu hoàn chỉnh)
3. Docstring đầu mỗi file trong `src/lab8/shapes/`
4. [docs/metrics.md](docs/metrics.md) khi viết ADR
