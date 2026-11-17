# Chia nhánh và commit theo thành viên

Toàn bộ code, test và report đã viết xong và nằm trên nhánh `demo` (commit `1c51d09`). File này chia chúng thành 4 nhánh, mỗi thành viên một nhánh tách từ `main`, theo cách chia vai cho nhóm 4 người trong `TEAM.md`.

**Nhánh tích hợp là nhánh của Bùi Thái Sỹ (TV3), `feature/orchestrator-and-bonus`.** Các thành viên còn lại tự commit trên nhánh của mình, rồi merge vào nhánh của Sỹ. Sỹ sửa tiếp `TEAM.md` và `report/team/group_report.md` trên nhánh đó, rồi mở một PR duy nhất vào `main`. Mỗi nhánh gồm code và ít nhất một test, đúng yêu cầu của bảng đóng góp.

> Mỗi người phải đọc hiểu phần mình commit: người chấm có thể hỏi trực tiếp về ranh giới code / model, vì sao truyền quote đầy đủ, và trace cố ý không ghi field nào ([RULES.md](RULES.md)). Phần "Cần giải thích được" dưới mỗi thành viên liệt kê những điểm đó.

## Trạng thái trên nhánh `demo` (lần chạy gần nhất trong `src/`)

| Kiểm tra | Kết quả |
| --- | --- |
| `python -m pytest -q` (cổng host) | 113 passed (54 test gốc + 59 test mới) |
| `python -m pytest -q -m student -o addopts=` | 248 passed: mỗi shape 62/62, swarm đúng với lần fail dự kiến ở seed 55 |
| Benchmark 4 shape × 5 seed | workflow, single, orchestrator: pass 1.000, pass^5 1.000, variance 0. Swarm: 0.986 / 0.929 |
| `python -m lab8.crash_test --count 20` | `crash_safety` 20/20 |

Sau khi merge cả 4 nhánh, chạy lại các lệnh trên ở `main`. Số phải giống hệt vì MockLLM cố định theo seed.

## Phân công

Thứ tự thành viên theo `showcase/catalog/team_roster.py`. Chỉ có phần của Sỹ là đã chốt; vai TV1, TV2, TV4 là gợi ý, hoán đổi giữa ba người còn lại được.

| TV | Người | Nhánh | File |
| --- | --- | --- | --- |
| 1 | Bùi Phan Thanh Phúc | `feature/workflow-shape` | `src/lab8/shapes/workflow.py`, `src/tests/test_shape_workflow.py`, `WORKFLOW.md` |
| 2 | Hoàng Ngọc Hiệu | `feature/single-agent-shape` | `src/lab8/shapes/single.py`, `src/tests/test_shape_single.py`, `showcase/app.py`, `showcase/requirements-demo.txt`, `showcase/catalog/`, `showcase/services/`, `showcase/ui/`, `showcase/views/` |
| 3 | Bùi Thái Sỹ | `feature/orchestrator-and-bonus` (nhánh tích hợp) | `src/lab8/shapes/orchestrator.py`, `src/tests/test_shape_orchestrator.py`, `src/bonus/__init__.py`, `src/bonus/swarm_verified.py`, `src/bonus/cases.jsonl`, `src/bonus/world.json`, `src/tests/test_bonus_swarm_verified.py`, `TEAM.md`, `report/team/group_report.md` |
| 4 | Đoàn Sỹ Hưng | `feature/evaluation-and-reports` | `src/tests/test_shape_trace_safety.py`, `src/bonus/verifier_stats.py`, `src/reports/*.json`, `report/team/bonus_report.md`, `showcase/slides/`, `DEMO.md`, `RUN_DEMO.md` |

Không nằm trong 4 nhánh: `commit.md` (hướng dẫn nội bộ, không nộp).

`TEAM.md` và `report/team/group_report.md` do Sỹ đảm nhận. Trên `demo` hai file này mới có danh sách thành viên; phần còn lại Sỹ điền sau khi các nhánh đã merge (mục "Sau khi merge").

## Quy trình chung

Mỗi người chạy ở **gốc repo**, trên máy của mình (commit dưới tài khoản git của chính mình, không cần `--author`). Lấy file từ `origin/demo` bằng `git checkout origin/demo -- <file>`, lệnh này tự stage nên không cần `git add`.

```bash
git fetch origin
git checkout -b <tên-nhánh> origin/main
git checkout origin/demo -- <các file của mình>
# chạy test của mình (xem từng thành viên), rồi:
git commit -m "<message>"
git push -u origin <tên-nhánh>
```

Thứ tự tích hợp (nhánh đích là `feature/orchestrator-and-bonus` của Sỹ, **không** phải `main`):

1. Sỹ push nhánh của mình trước (mục Thành viên 3) để mọi người có nhánh đích.
2. TV1 và TV2 push nhánh của mình, rồi merge vào nhánh của Sỹ. Hai nhánh này không đụng file nhau nên thứ tự nào cũng được.
3. TV4 làm sau cùng, tách từ nhánh của Sỹ sau khi TV1, TV2 đã merge (xem mục Thành viên 4), rồi merge ngược lại.
4. Sỹ sửa tiếp `TEAM.md` và `report/team/group_report.md`, rồi mở PR từ nhánh của mình vào `main`.

Cách merge vào nhánh của Sỹ (mỗi người chạy một lần, sau khi đã push nhánh của mình):

```bash
git fetch origin
git checkout feature/orchestrator-and-bonus
git pull origin feature/orchestrator-and-bonus
git merge --no-ff <nhánh-của-mình>
git push origin feature/orchestrator-and-bonus
```

Có thể thay bằng một PR từ nhánh của mình vào `feature/orchestrator-and-bonus` nếu muốn Sỹ xem trước khi merge.

## Thành viên 1 (Bùi Phan Thanh Phúc): Workflow + integration

```bash
git checkout -b feature/workflow-shape origin/main
git checkout origin/demo -- src/lab8/shapes/workflow.py src/tests/test_shape_workflow.py WORKFLOW.md
cd src && python -m pytest -q tests/test_shape_workflow.py && cd ..
git commit -m "feat(workflow): implement deterministic workflow shape" -m "Fixed Python steps, quote from order row via compute_compensation, full quote to issue_refund, crash_at forwarded. Tests: ticket overstating delay and injected ticket are ignored, unknown claim returns failed."
git push -u origin feature/workflow-shape
```

- **Code:** `src/lab8/shapes/workflow.py`
- **Test:** `src/tests/test_shape_workflow.py`. Có 3 nhóm test: ticket nói trễ 5 ngày nhưng order ghi 2 ngày thì bị từ chối ở cả 5 seed; ticket chứa lệnh "IGNORE POLICY" không tạo refund; claim không tồn tại trả `failed` chứ không ném exception.
- **Cần giải thích được:**
  - Vì sao không đọc số ngày trễ từ ticket.
  - Cách đổi kết quả của host thành status: `ok` → `resolved`, `conflict` → `failed`, còn lại → `denied` với `proposal_amount` là quote đầy đủ.
  - Vì sao ghi trace xong mới `raise` lại `InjectedCrash`.

## Thành viên 2 (Hoàng Ngọc Hiệu): Single agent (ReAct) + showcase

```bash
git checkout -b feature/single-agent-shape origin/main
git checkout origin/demo -- src/lab8/shapes/single.py src/tests/test_shape_single.py showcase/app.py showcase/requirements-demo.txt showcase/catalog showcase/services showcase/ui showcase/views
cd src && python -m pytest -q tests/test_shape_single.py && cd ..
git commit -m "feat(single): implement bounded ReAct single-agent shape" -m "decide() picks read tools only and keeps its own memory; amount comes from compute_compensation result, shape (not agent) calls issue_refund. Tests: step cap and read-only tools, model-call accounting, early needs_info. Adds the showcase demo app."
git push -u origin feature/single-agent-shape
```

- **Code:** `src/lab8/shapes/single.py`, cùng thư mục `showcase/` (app Streamlit demo). Nếu muốn commit nhỏ hơn, tách `showcase/` thành một commit riêng trên cùng nhánh.
- **Test:** `src/tests/test_shape_single.py`. Kiểm số bước không quá 8, agent chỉ gọi tool đọc, mỗi lần `decide` tính đúng một lần gọi model, và claim thiếu `order_id` dừng sớm mà không tra order.
- **Cần giải thích được:**
  - `run_react` chỉ trả lại kết quả của tool gọi gần nhất, nên `_Agent` phải tự nhớ claim, order và quote.
  - Số tiền lấy từ `agent.quote`, không lấy từ `final` của agent.
  - Prompt gửi MockLLM không chứa ticket.

## Thành viên 3 (Bùi Thái Sỹ): Orchestrator + handoff + bonus B3 + TEAM/group_report

`src/bonus/` chưa có trên `main`, nhánh này tạo mới thư mục đó.

```bash
git checkout -b feature/orchestrator-and-bonus origin/main
git checkout origin/demo -- src/lab8/shapes/orchestrator.py src/tests/test_shape_orchestrator.py
cd src && python -m pytest -q tests/test_shape_orchestrator.py && cd ..
git commit -m "feat(orchestrator): implement orchestrator with read-only investigators" -m "Handoff built with make_handoff (allowlist, empty facts, read-only tools); investigator re-reads order through principal-scoped tools; orchestrator is the only caller of issue_refund. Tests: handoff allowlist and no secret/ticket, T14 full-quote partial refund."

git checkout origin/demo -- src/bonus/__init__.py src/bonus/swarm_verified.py src/bonus/cases.jsonl src/bonus/world.json src/tests/test_bonus_swarm_verified.py
cd src && python -m pytest -q tests/test_bonus_swarm_verified.py && cd ..
git commit -m "feat(bonus): add swarm_verified with code verifier before write (B3)" -m "Mirrors the swarm flow (weakness kept), re-reads the order and re-quotes on any fact mismatch, one correction round, verifier_override in trace. 8 hand-labelled adversarial claims. Tests: T02 seed 55 fixed, adversarial set x 5 seeds, silent when facts agree, crash/resume, label consistency."
git push -u origin feature/orchestrator-and-bonus
```

Sau đó Sỹ lấy hai file báo cáo của nhóm về nhánh này (đã có danh sách thành viên trên `demo`):

```bash
git checkout origin/demo -- TEAM.md report/team/group_report.md
git commit -m "docs: add team members to TEAM.md and group report"
git push
```

Các phần còn lại của hai file này (tên nhóm, email, GitHub, vai trò, bảng đóng góp, nội dung báo cáo) Sỹ điền sau khi TV1, TV2, TV4 đã merge, vì cần hash commit và số liệu thật.

- **Test:** `src/tests/test_shape_orchestrator.py`. Handoff trong trace chỉ có các field trong allowlist, `facts` rỗng, tool đều là tool đọc, không có secret hay ticket. Với T14, quote 150.000 thì ledger ghi 120.000.
- **Cần giải thích được (orchestrator):**
  - Vì sao để `facts={}`: investigator tự đọc lại order qua tool có kiểm principal, nên không có gì từ context của parent đi qua ranh giới.
  - Vì sao tóm tắt bằng LLM không được tính là redaction.
  - Vì sao investigator không có tool ghi.
- **Cần giải thích được (bonus):**
  - Vì sao verifier đọc lại order bằng `lookup_order` thay vì tin bản investigator đã đọc.
  - Vì sao chỉ cho tối đa 1 vòng sửa, và nếu vẫn lệch thì fail-closed.
  - Nhãn của 8 case được suy ra từ luật nghiệp vụ, không sinh bằng `quote`.
- Bonus chỉ được tính khi shape nhóm chọn qua 3 must-pass, đạt hidden ≥ 0.80, và `pytest` xanh.

## Thành viên 4 (Đoàn Sỹ Hưng): Ledger, trace an toàn, evaluation

Làm sau khi TV1 và TV2 đã merge vào nhánh của Sỹ: benchmark phải chạy trên code của cả 3 shape, và `verifier_stats.py` cần `src/bonus/` của Sỹ. Vì vậy nhánh của TV4 tách từ nhánh tích hợp, không phải từ `main`.

**Bước 1: test trace an toàn** (chạy được ngay, không phụ thuộc thứ tự):

```bash
git checkout -b feature/evaluation-and-reports origin/feature/orchestrator-and-bonus   # sau khi TV1, TV2 đã merge vào đó
git checkout origin/demo -- src/tests/test_shape_trace_safety.py
cd src && python -m pytest -q tests/test_shape_trace_safety.py && cd ..
git commit -m "test: trace contract v1 and leak scan for all group shapes" -m "Every public claim x 3 shapes: trace written this run, run_id matches, no CANARY_SECRET, forbidden substrings or raw ticket text; unknown claim still writes a trace."
```

**Bước 2: chạy lại và sinh report** (không chép tay `src/reports/*.json` từ `demo`):

```bash
cd src
python -m pytest -q
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
python -m lab8.crash_test --count 20 --out reports/crash.json
cd ..
git add src/reports/benchmark.json src/reports/crash.json
git commit -m "chore(reports): add public benchmark and crash suite results"
```

**Bước 3: bonus B3-b**, đo đạc và báo cáo:

```bash
git checkout origin/demo -- src/bonus/verifier_stats.py report/team/bonus_report.md
cd src
python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --seeds 11,22,33,44,55 --out reports/bonus_benchmark_public.json
python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases bonus/cases.jsonl --world bonus/world.json --seeds 11,22,33,44,55 --out reports/bonus_benchmark_adversarial.json
python -m bonus.verifier_stats --out reports/bonus_verifier.json
cd ..
git add src/bonus/verifier_stats.py src/reports/bonus_benchmark_public.json src/reports/bonus_benchmark_adversarial.json src/reports/bonus_verifier.json report/team/bonus_report.md
git commit -m "docs(bonus): B3 benchmark, verifier stats and bonus report"
```

**Bước 4: slide và tài liệu demo:**

```bash
git checkout origin/demo -- showcase/slides DEMO.md RUN_DEMO.md
git commit -m "docs: add demo slides and run instructions"
git push -u origin feature/evaluation-and-reports
```

Sau đó TV4 merge nhánh này vào nhánh của Sỹ theo cách ở mục "Quy trình chung".

`src/reports/hidden_selfcheck.json` có trên `demo` nhưng không do lệnh nào ở trên sinh ra. Nếu muốn giữ, `git checkout origin/demo -- src/reports/hidden_selfcheck.json` rồi thêm vào commit report.

- **Test:** `src/tests/test_shape_trace_safety.py`. Chạy 14 claim × 3 shape: trace được ghi trong chính lần chạy, `run_id` khớp, không có `CANARY_SECRET_*`, không có chuỗi cấm, không có nguyên văn ticket. Claim không tồn tại vẫn có trace.
- **Cần giải thích được:**
  - Grader fail-closed với `missing_trace`, `stale_trace` và `invalid_trace`.
  - Vì sao không ghi ticket vào trace: bộ hidden có ticket bị chèn lệnh và có homoglyph.
  - Crash 20/20 nghĩa là gì: sau resume còn đúng một dòng ledger và một audit `refund_committed`.
  - Verifier đưa swarm về mức workflow và tốn thêm bao nhiêu cost; khi verifier đã thay toàn bộ phần quyết định thì swarm còn giữ lại giá trị gì; điều kiện nào làm kết luận đảo ngược.
- Số liệu trong `report/team/bonus_report.md` lấy từ lần chạy trên `demo`. Sau khi chạy lại, đối chiếu với file JSON mới: nếu số lệch thì sửa báo cáo theo JSON, không sửa ngược.

## Sau khi merge: Sỹ điền báo cáo, cả nhóm góp số liệu

1. Chạy `git log --oneline` trên nhánh của Sỹ để lấy hash commit của từng người. Merge bằng `--no-ff` giữ nguyên commit gốc nên hash không đổi.
2. Điền `report/team/decision_adr.md`, lấy số từ `src/reports/benchmark.json` sau khi chạy lại:
   - `- Shape chọn: workflow`. Đây là shape ít tự chủ nhất mà vẫn đạt pass 1.0 và pass^5 1.0, với cost/success thấp nhất (≈ 28.86 VND mô phỏng, so với single ≈ 30.60, orchestrator ≈ 57.20, swarm ≈ 49.57).
   - `- Run id dẫn chứng:` lấy `run_id` của một trial workflow trong `trials` của `benchmark.json`, ví dụ trial C-014 seed 11.
   - `- Crash safety: 20/20 (src/reports/crash.json)`
   - `- Secret leak / approval bypass: 0 / 0`
3. Điền `report/team/research_card.md`: chọn một câu trong R1–R4 và một ablation.
4. Sỹ điền `report/team/group_report.md` và `TEAM.md` (thông tin nhóm và bảng đóng góp). Mỗi người tự copy `report/team/MSSV_HoTen.md` thành file của mình, commit trên nhánh của mình rồi merge vào nhánh của Sỹ.
5. Sỹ chạy `cd src && python -m lab8.check_submission` cho ra `0 FAIL`, push nhánh `feature/orchestrator-and-bonus` và mở PR vào `main`.

## Bảng đóng góp gợi ý cho `TEAM.md`

| Người | Vai | Nhánh | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- | --- |
| Bùi Phan Thanh Phúc | Workflow + integration | `feature/workflow-shape` | `<hash commit 1>` | `src/tests/test_shape_workflow.py` |
| Hoàng Ngọc Hiệu | Single agent + showcase | `feature/single-agent-shape` | `<hash commit 2>` | `src/tests/test_shape_single.py` |
| Bùi Thái Sỹ | Orchestrator + handoff + bonus B3 | `feature/orchestrator-and-bonus` | `<hash commit 3>` | `src/tests/test_shape_orchestrator.py`, `src/tests/test_bonus_swarm_verified.py` |
| Đoàn Sỹ Hưng | Ledger + evaluation | `feature/evaluation-and-reports` | `<hash commit 4>` | `src/tests/test_shape_trace_safety.py` |

`commit.md` chỉ là hướng dẫn nội bộ. Không đưa file này vào nhánh nào trong 4 nhánh trên. Sau khi chia xong, xóa nó khỏi `demo`.
