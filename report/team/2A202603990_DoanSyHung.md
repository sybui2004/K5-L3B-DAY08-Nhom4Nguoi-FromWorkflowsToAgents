# Báo cáo cá nhân — 2A202603990_DoanSyHung

## 1. Thông tin thành viên

- Họ tên: Đoàn Sỹ Hưng
- MSSV: 2A202603990
- Email: 
- GitHub: https://github.com/hgmdz1210

## 2. Phần việc phụ trách

Thành viên 4 (Nhom4Nguoi). Phụ trách phần đo đạc và bằng chứng của nhóm:

- Test an toàn trace cho ba shape của nhóm (`src/tests/test_shape_trace_safety.py`).
- Chạy benchmark công khai và crash suite, sinh `src/reports/benchmark.json` và `src/reports/crash.json`.
- Bonus **B3** phần đo đạc: `src/bonus/verifier_stats.py`, ba file `src/reports/bonus_*.json` và `report/team/bonus_report.md`.
- Slide và tài liệu demo: `showcase/slides/`, `DEMO.md`, `RUN_DEMO.md`.

## 3. Đóng góp cụ thể

Commit trên nhánh `feature/evaluation-and-reports` (PR #5):

- `01ca29e` docs: add demo slides and run instructions
- `291725c` test: trace contract v1 and leak scan for all group shapes
- `b824ba1` chore(reports): add public benchmark and crash suite results
- `b2550dc` docs(bonus): B3 benchmark, verifier stats and bonus report

**Test trace an toàn.** Với mỗi claim public và mỗi shape của nhóm (workflow, single, orchestrator), test kiểm trace được ghi trong chính lần chạy đó, `run_id` khớp, không chứa `CANARY_SECRET_*`, không chứa chuỗi cấm của claim và không chứa nguyên văn ticket. Claim không tồn tại vẫn phải có trace. Grader đọc trace nên trace thiếu, cũ hoặc sai định dạng bị fail-closed (`missing_trace`, `stale_trace`, `invalid_trace`).

**Báo cáo sinh bằng lệnh.** Các file trong `src/reports/` do tôi chạy lại bằng lệnh trên nhánh của mình, không chép tay. Đối chiếu với bản đã có trên nhánh `demo` thì số giống hệt, chỉ lệch sai số làm tròn số thực.

Quyết định kỹ thuật:

- Không ghi ticket vào trace, vì bộ hidden có ticket bị chèn lệnh và có homoglyph.
- Báo cáo bonus lấy số từ file JSON do `lab8.benchmark` sinh, nếu số lệch thì sửa báo cáo theo JSON chứ không sửa ngược.
- Cost chỉ là số mô phỏng của MockLLM, nên chỉ dùng để so sánh tương đối giữa các shape.

## 4. Bằng chứng

Chạy trong `src/` trên nhánh `feature/evaluation-and-reports`:

```text
python -m lab8.smoke                      -> lab8.smoke pass
python -m pytest -q                       -> 160 passed
python -m pytest -q -m student -o addopts= -> 248 passed
python -m lab8.crash_test --count 20      -> crash_safety 20/20
python -m pytest -q tests/test_bonus_swarm_verified.py -> 47 passed
```

Benchmark công khai (4 shape × 5 seed, `src/reports/benchmark.json`):

| Shape | Pass rate | Pass^5 | Variance | Cost/success (VND mô phỏng) |
| --- | ---: | ---: | ---: | ---: |
| workflow | 1.000 | 1.000 | 0.000000 | 28.86 |
| single | 1.000 | 1.000 | 0.000000 | 30.60 |
| orchestrator | 1.000 | 1.000 | 0.000000 | 57.20 |
| swarm | 0.986 | 0.929 | 0.000816 | 49.57 |

Bonus B3 (`src/reports/bonus_benchmark_*.json`):

| Bộ claim | swarm | swarm_verified | workflow |
| --- | --- | --- | --- |
| Public | 0.986 / 0.929 | 1.000 / 1.000 | 1.000 / 1.000 |
| 8 claim tự viết | 0.875 / 0.375 | 1.000 / 1.000 | 1.000 / 1.000 |

Cost/success của `swarm_verified` là 57.57 trên bộ public, so với 28.86 của workflow.

## 5. Công cụ AI đã dùng

- Claude Code: giúp đọc repo và `commit.md`, tạo nhánh, lấy file từ nhánh `demo`, chạy lệnh kiểm tra, sinh lại báo cáo, chia commit và soạn mô tả PR.
- Cách tự kiểm tra: kết quả `pytest`, crash suite và benchmark ở mục 4 là đầu ra của các lệnh chạy trên nhánh này. Tôi đối chiếu số benchmark với `commit.md` và với bản trên `demo`. Tôi đọc lại cách `issue_refund` ghi ledger và audit trong một transaction để giải thích được vì sao crash rồi retry vẫn chỉ có một dòng tiền.

## 6. Tự đánh giá

- Làm tốt: số liệu trong báo cáo tái lập được bằng lệnh, có kiểm trace sạch cho cả ba shape, có crash suite 20/20.
- Hạn chế: test trace chỉ chạy trên ba shape của nhóm, không chạy trên swarm. MockLLM chỉ có một nguồn lỗi nên không đo được tỉ lệ khuếch đại lỗi như paper, và latency là `unavailable`.
- Cần làm thêm: điền Email, và chạy `python -m lab8.check_submission` sau khi các PR đã merge.
