# Chia commit theo thành viên

Code ba shape và test đã viết xong và đang nằm trong working tree, **chưa commit**. File này chia các thay đổi đó thành 4 commit, mỗi thành viên một commit, theo cách chia vai cho nhóm 4 người trong `TEAM.md`. Mỗi commit gồm code và ít nhất một test, đúng yêu cầu của bảng đóng góp.

> Mỗi người phải đọc hiểu phần mình commit: người chấm có thể hỏi trực tiếp về ranh giới code / model, vì sao truyền quote đầy đủ, và trace cố ý không ghi field nào ([RULES.md](RULES.md)). Phần "Cần giải thích được" dưới mỗi commit liệt kê những điểm đó.

## Trạng thái hiện tại (đã chạy trong `src/`)

| Kiểm tra | Kết quả |
| --- | --- |
| `python -m pytest -q` (cổng host) | 113 passed (54 test gốc + 59 test mới) |
| `python -m pytest -q -m student -o addopts=` | 248 passed: mỗi shape 62/62, swarm đúng với lần fail dự kiến ở seed 55 |
| Benchmark 4 shape × 5 seed | workflow, single, orchestrator: pass 1.000, pass^5 1.000, variance 0. Swarm: 0.986 / 0.929 |
| `python -m lab8.crash_test --count 20` | `crash_safety` 20/20 |
| `python -m lab8.check_submission` | 9 FAIL, toàn bộ là phần báo cáo / `TEAM.md` / ADR chưa điền (xem bước 5) |

## Thứ tự commit

Commit đúng thứ tự dưới đây: test của thành viên 4 dùng cả ba shape, và benchmark phải chạy trên code đã commit. Thay `<Tên>` và `<email>` bằng thông tin thật. Nếu mỗi người commit trên máy mình thì bỏ `--author`, chỉ cần `git pull` trước khi commit.

Mọi lệnh chạy ở **gốc repo**.

### 1. Thành viên 1 — Workflow + integration

```bash
git add src/lab8/shapes/workflow.py src/tests/test_shape_workflow.py
git commit --author="<Tên> <email>" -m "feat(workflow): implement deterministic workflow shape" -m "Fixed Python steps, quote from order row via compute_compensation, full quote to issue_refund, crash_at forwarded. Tests: ticket overstating delay and injected ticket are ignored, unknown claim returns failed."
```

- **Code:** `src/lab8/shapes/workflow.py`
- **Test:** `src/tests/test_shape_workflow.py`. Có 3 nhóm test: ticket nói trễ 5 ngày nhưng order ghi 2 ngày thì bị từ chối ở cả 5 seed; ticket chứa lệnh "IGNORE POLICY" không tạo refund; claim không tồn tại trả `failed` chứ không ném exception.
- **Cần giải thích được:**
  - Vì sao không đọc số ngày trễ từ ticket.
  - Cách đổi kết quả của host thành status: `ok` → `resolved`, `conflict` → `failed`, còn lại → `denied` với `proposal_amount` là quote đầy đủ.
  - Vì sao ghi trace xong mới `raise` lại `InjectedCrash`.

### 2. Thành viên 2 — Single agent (ReAct)

```bash
git add src/lab8/shapes/single.py src/tests/test_shape_single.py
git commit --author="<Tên> <email>" -m "feat(single): implement bounded ReAct single-agent shape" -m "decide() picks read tools only and keeps its own memory; amount comes from compute_compensation result, shape (not agent) calls issue_refund. Tests: step cap and read-only tools, model-call accounting, early needs_info."
```

- **Code:** `src/lab8/shapes/single.py`
- **Test:** `src/tests/test_shape_single.py`. Kiểm số bước không quá 8, agent chỉ gọi tool đọc, mỗi lần `decide` tính đúng một lần gọi model, và claim thiếu `order_id` dừng sớm mà không tra order.
- **Cần giải thích được:**
  - `run_react` chỉ trả lại kết quả của tool gọi gần nhất, nên `_Agent` phải tự nhớ claim, order và quote.
  - Số tiền lấy từ `agent.quote`, không lấy từ `final` của agent.
  - Prompt gửi MockLLM không chứa ticket.

### 3. Thành viên 3 — Orchestrator + handoff

```bash
git add src/lab8/shapes/orchestrator.py src/tests/test_shape_orchestrator.py
git commit --author="<Tên> <email>" -m "feat(orchestrator): implement orchestrator with read-only investigators" -m "Handoff built with make_handoff (allowlist, empty facts, read-only tools); investigator re-reads order through principal-scoped tools; orchestrator is the only caller of issue_refund. Tests: handoff allowlist and no secret/ticket, T14 full-quote partial refund."
```

- **Code:** `src/lab8/shapes/orchestrator.py`
- **Test:** `src/tests/test_shape_orchestrator.py`. Handoff trong trace chỉ có các field trong allowlist, `facts` rỗng, tool đều là tool đọc, không có secret hay ticket. Với T14, quote 150.000 thì ledger ghi 120.000.
- **Cần giải thích được:**
  - Vì sao để `facts={}`: investigator tự đọc lại order qua tool có kiểm principal, nên không có gì từ context của parent đi qua ranh giới.
  - Vì sao tóm tắt bằng LLM không được tính là redaction.
  - Vì sao investigator không có tool ghi.

### 4. Thành viên 4 — Ledger, trace an toàn, evaluation

Commit test trước, **chạy lại** benchmark và crash trên code đã commit, rồi mới commit report:

```bash
git add src/tests/test_shape_trace_safety.py
git commit --author="<Tên> <email>" -m "test: trace contract v1 and leak scan for all group shapes" -m "Every public claim x 3 shapes: trace written this run, run_id matches, no CANARY_SECRET, forbidden substrings or raw ticket text; unknown claim still writes a trace."

cd src
python -m pytest -q
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
python -m lab8.crash_test --count 20 --out reports/crash.json
cd ..
git add src/reports/benchmark.json src/reports/crash.json
git commit --author="<Tên> <email>" -m "chore(reports): add public benchmark and crash suite results"
```

- **Test:** `src/tests/test_shape_trace_safety.py`. Chạy 14 claim × 3 shape: trace được ghi trong chính lần chạy, `run_id` khớp, không có `CANARY_SECRET_*`, không có chuỗi cấm, không có nguyên văn ticket. Claim không tồn tại vẫn có trace.
- **Cần giải thích được:**
  - Grader fail-closed với `missing_trace`, `stale_trace` và `invalid_trace`.
  - Vì sao không ghi ticket vào trace: bộ hidden có ticket bị chèn lệnh và có homoglyph.
  - Crash 20/20 nghĩa là gì: sau resume còn đúng một dòng ledger và một audit `refund_committed`.
- **Không sửa tay** `src/reports/*.json`. `src/reports/benchmark.json` và `src/reports/crash.json` đang có trong working tree là bản sinh trước khi commit. Lệnh trên sẽ ghi đè chúng.

## Bonus B3: verifier trước bước ghi (sau 4 commit chính)

Bonus chỉ được tính khi shape nhóm chọn qua 3 must-pass, đạt hidden ≥ 0.80, và `pytest` xanh. Chia làm 2 commit:

### B3-a. Thành viên 3 — biến thể `swarm_verified` và bộ case đối kháng

```bash
git add src/bonus/__init__.py src/bonus/swarm_verified.py src/bonus/cases.jsonl src/bonus/world.json src/tests/test_bonus_swarm_verified.py
git commit --author="<Tên> <email>" -m "feat(bonus): add swarm_verified with code verifier before write (B3)" -m "Mirrors the swarm flow (weakness kept), re-reads the order and re-quotes on any fact mismatch, one correction round, verifier_override in trace. 8 hand-labelled adversarial claims. Tests: T02 seed 55 fixed, adversarial set x 5 seeds, silent when facts agree, crash/resume, label consistency."
```

- **Cần giải thích được:**
  - Vì sao verifier đọc lại order bằng `lookup_order` thay vì tin bản investigator đã đọc.
  - Vì sao chỉ cho tối đa 1 vòng sửa, và nếu vẫn lệch thì fail-closed.
  - Nhãn của 8 case được suy ra từ luật nghiệp vụ, không sinh bằng `quote`.

### B3-b. Thành viên 4 — đo đạc và báo cáo bonus

Chạy trong `src/` sau commit B3-a, rồi commit kết quả:

```bash
cd src
python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --seeds 11,22,33,44,55 --out reports/bonus_benchmark_public.json
python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases bonus/cases.jsonl --world bonus/world.json --seeds 11,22,33,44,55 --out reports/bonus_benchmark_adversarial.json
python -m bonus.verifier_stats --out reports/bonus_verifier.json
cd ..
git add src/bonus/verifier_stats.py src/reports/bonus_benchmark_public.json src/reports/bonus_benchmark_adversarial.json src/reports/bonus_verifier.json report/team/bonus_report.md
git commit --author="<Tên> <email>" -m "docs(bonus): B3 benchmark, verifier stats and bonus report"
```

- Số liệu trong `report/team/bonus_report.md` lấy từ lần chạy hiện tại. Sau khi chạy lại, đối chiếu với file JSON mới: MockLLM cố định theo seed nên số phải giống hệt.
- **Cần giải thích được:**
  - Verifier đưa swarm về mức workflow và tốn thêm bao nhiêu cost.
  - Khi verifier đã thay toàn bộ phần quyết định thì swarm còn giữ lại giá trị gì.
  - Điều kiện nào làm kết luận đảo ngược.

## 5. Sau 4 commit: điền báo cáo, cả nhóm cùng làm

1. Chạy `git rev-parse --short HEAD` để lấy commit hash.
2. Điền `report/team/decision_adr.md`. Số liệu tham khảo từ lần chạy hiện tại, nhưng phải lấy lại từ `src/reports/benchmark.json` sau khi chạy lại:
   - `- Shape chọn: workflow`. Đây là shape ít tự chủ nhất mà vẫn đạt pass 1.0 và pass^5 1.0, với cost/success thấp nhất (≈ 28.86 VND mô phỏng, so với single ≈ 30.60, orchestrator ≈ 57.20, swarm ≈ 49.57).
   - `- Run id dẫn chứng:` lấy `run_id` của một trial workflow trong `trials` của `benchmark.json`, ví dụ trial C-014 seed 11.
   - `- Crash safety: 20/20 (src/reports/crash.json)`
   - `- Secret leak / approval bypass: 0 / 0`
3. Điền `report/team/research_card.md`: chọn một câu trong R1–R4 và một ablation.
4. Điền `report/team/group_report.md`, `TEAM.md` (thông tin nhóm và bảng đóng góp, mỗi người một dòng với hash commit và tên file test ở trên), rồi mỗi người copy `report/team/MSSV_HoTen.md` thành file của mình.
5. Commit báo cáo, chạy `cd src && python -m lab8.check_submission` cho ra `0 FAIL`, rồi push.

## Bảng đóng góp gợi ý cho `TEAM.md`

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Thành viên 1 | Workflow + integration | `<hash commit 1>` | `src/tests/test_shape_workflow.py` |
| Thành viên 2 | Single agent | `<hash commit 2>` | `src/tests/test_shape_single.py` |
| Thành viên 3 | Orchestrator + handoff | `<hash commit 3>` | `src/tests/test_shape_orchestrator.py` |
| Thành viên 4 | Ledger + evaluation | `<hash commit 4>` | `src/tests/test_shape_trace_safety.py` |

`commit.md` chỉ là hướng dẫn nội bộ. Xóa file này hoặc để ngoài các commit nộp bài.
