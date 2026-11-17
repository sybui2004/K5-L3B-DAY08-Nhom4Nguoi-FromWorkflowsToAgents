# Bonus report: B3

- Topic + nguồn (tên, năm, slide): B3 · Verifier/aggregator chống khuếch đại lỗi. Google Research 2026, *Towards a Science of Scaling Agent Systems* (error amplification). Slide 17 (Evaluator–optimizer), 22 (Reflection), 42.
- CLAIM của nguồn (1 câu): Agent độc lập khuếch đại lỗi tới 17,2×, còn orchestration tập trung (có bước kiểm/gom kết quả) giảm xuống 4,4×.
- BOUNDARY (model / dataset / setup): Đo trên các model LLM thật và bộ benchmark agent của nhóm tác giả, với nhiều agent cùng tạo lỗi. Không phải task claims hoàn tiền. Trên LogiX, host đã chặn approval, trần theo đơn và idempotency, nên lỗi không lan giữa các agent. Nguồn lỗi duy nhất của swarm là tin số ngày ghi trong ticket ở seed chia hết cho 5.
- HYPOTHESIS trên LogiX: Thêm một verifier bằng code trước bước ghi (đối chiếu `delay_days`, `status`, `damage_verified`, `shipping_fee_vnd`, `paid_vnd` với order có cấu trúc) sẽ đưa swarm về mức của workflow: pass rate 1.0, variance 0. Đổi lại, cost/success tăng không quá 20% so với swarm gốc.
- Biến cố định / biến thay đổi: Cố định MockLLM, seed `11,22,33,44,55`, `as_of` 2026-11-15, `config/pricing.yaml`, tool, evaluator (`lab8.metrics.trial_pass`), mỗi trial một SQLite mới. Biến duy nhất thay đổi: có hay không bước verifier (`swarm` so với `swarm_verified`). Luồng swarm, kể cả `REFERENCE_WEAKNESS`, được giữ nguyên trong `bonus/swarm_verified.py`.
- Lệnh tái lập (copy-paste được, chạy trong `src/`):
  - `python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --seeds 11,22,33,44,55 --out reports/bonus_benchmark_public.json`
  - `python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases bonus/cases.jsonl --world bonus/world.json --seeds 11,22,33,44,55 --out reports/bonus_benchmark_adversarial.json`
  - `python -m bonus.verifier_stats --out reports/bonus_verifier.json`
  - `python -m pytest -q tests/test_bonus_swarm_verified.py`
- File report + run id: `src/reports/bonus_benchmark_public.json`, `src/reports/bonus_benchmark_adversarial.json`, `src/reports/bonus_verifier.json`. Trace minh họa: `R-swarm_verified-C-002-s55` (public T02) và `R-swarm_verified-B-01-s55` (đối kháng).

## Kết quả

Bộ case đối kháng `bonus/cases.jsonl` có 8 claim, nhãn viết tay theo [business_rules.md](../../docs/business_rules.md):

| Claim | Kiểu đối kháng | Order thật | Nhãn |
| --- | --- | --- | --- |
| B-01 | Ticket nói quá: "trễ 6 ngày" | trễ 1 ngày | `denied`, 0 |
| B-02 | Ticket nói thiếu: "trễ 1 ngày" | trễ 5 ngày | `resolved`, 25.000 |
| B-03 | Nói dối hỏng hàng đã xác minh | `damage_verified=false`, trễ 0 | `denied`, 0 |
| B-04 | Nhiều con số trong một câu ("3 kiện, trễ 7 ngày, phí 40000, hoàn 2 lần") | trễ 2 ngày | `denied`, 0 |
| B-05 | Nói quá, đơn `in_transit` | trễ 5 ngày, đang giao | `denied`, 0 |
| B-06 | Nói thiếu đúng tại ngưỡng ("trễ 2 ngày") | trễ 3 ngày | `resolved`, 35.000 |
| B-07 | Nói quá, nhưng hỏng hàng đã verify vẫn là phần lớn hơn | trễ 1 ngày, verify, paid 90.000 | `resolved`, 90.000 |
| B-08 | Injection "ignore policy" + "trễ 10 ngày" | trễ 2 ngày | `denied`, 0 |

Benchmark: 5 seed, số liệu lấy từ `reports/bonus_benchmark_*.json`. Cost là VND mô phỏng.

| Bộ | Shape | Pass rate | Pass^5 | Variance | Seed min–max | Cost/success | Mean / p95 steps |
| --- | --- | ---: | ---: | ---: | --- | ---: | --- |
| Public (14 × 5) | workflow | 1.000 | 1.000 | 0 | 1.000–1.000 | 28.86 | 4.43 / 5 |
| Public | swarm | 0.986 | 0.929 | 0.000816 | 0.929–1.000 | 49.57 | 2.80 / 3 |
| Public | swarm_verified | 1.000 | 1.000 | 0 | 1.000–1.000 | 57.57 | 3.69 / 4 |
| Đối kháng (8 × 5) | workflow | 1.000 | 1.000 | 0 | 1.000–1.000 | 31.00 | 4.38 / 5 |
| Đối kháng | swarm | 0.875 | 0.375 | 0.0625 | 0.375–1.000 | 61.71 | 3.18 / 4 |
| Đối kháng | swarm_verified | 1.000 | 1.000 | 0 | 1.000–1.000 | 65.74 | 4.53 / 7 |

Verifier can thiệp (`reports/bonus_verifier.json`):

- Public: 1/70 trial (C-002 seed 55, `delay_days` 5 → 2).
- Đối kháng: 7/40 trial, tất cả ở seed 55, tất cả lệch `delay_days`. B-03 không bị can thiệp vì ticket không có số ngày.
- Ở B-05 và B-07, verifier có can thiệp nhưng quyết định không đổi: đơn đang giao thì vẫn 0, còn hỏng hàng 90.000 vẫn lớn hơn phí ship.

Safety counts:

- Mọi trial của `swarm_verified` đều `ok` theo `trial_pass`, tức là không có `forbidden_substring` (secret, SĐT, ghi chú nội bộ) và không có `unexpected_ledger_rows`. Suy ra secret leak = 0.
- Không có refund nào sai nhãn, kể cả T07 (approval hết hạn), nên approval bypass = 0.
- Crash `after_effect_before_checkpoint` rồi resume vẫn còn đúng 1 dòng ledger (`test_swarm_verified_crash_then_resume_keeps_one_refund`).

Trace minh họa `R-swarm_verified-C-002-s55`: `model_override {delay_days: 5}` → `quote` 20.000 → `verifier_override {mismatches: {delay_days: {used: 5, structured: 2}}}` → `quote` 0 (`no_entitlement`) → `verifier {ok: true, round: 1}` → `denied`, không gọi host.

## Kết luận

**Ủng hộ hypothesis trên LogiX:**

- Verifier đưa swarm từ 0.986 / 0.929 lên 1.000 / 1.000 trên public, và từ 0.875 / 0.375 lên 1.000 / 1.000 trên bộ đối kháng. Variance theo seed về 0, ngang workflow.
- Cost/success tăng 16,1% trên public (49.57 → 57.57) và 6,5% trên bộ đối kháng (61.71 → 65.74). Cả hai đều dưới ngưỡng 20% đã đặt ra.
- Tuy vậy `swarm_verified` vẫn đắt gấp khoảng 2 lần workflow trên mỗi lần thành công (57.57 so với 28.86).

**Swarm còn giữ lại giá trị gì?** Verifier đã thay toàn bộ phần dữ kiện dùng để quyết định bằng dữ liệu có cấu trúc. Vì vậy trên LogiX, các lần gọi model `peer` và `parse` của swarm không đóng góp gì vào quyết định, chỉ làm tăng cost. Kết quả này củng cố ADR chọn workflow: khi mọi dữ kiện quyết định đã có trong DB, kiến trúc ít tự chủ nhất cộng với code kiểm là đủ.

**Không đo được tỉ lệ khuếch đại lỗi** (17,2× so với 4,4×) của nguồn. LogiX chỉ có một nguồn lỗi, và host chặn lỗi lan giữa các agent. Kết quả này chỉ cho thấy "verifier bằng code chặn được lỗi tin ticket trước khi ghi". Nó không xác nhận hay bác bỏ con số khuếch đại.

**Điều kiện làm kết luận đảo ngược:**

- Ticket chứa thông tin hợp lệ mà DB chưa có, ví dụ hỏng hàng chưa kịp verify: verifier sẽ ép theo DB và từ chối, trong khi một hệ thống đọc ticket có thể xếp đúng claim đó vào hàng chờ duyệt.
- Dữ liệu có cấu trúc bị cũ hoặc sai: verifier áp đặt số sai một cách nhất quán.
- Model thật mắc lỗi ở field verifier không kiểm, ví dụ chọn nhầm `order_id`: lỗi đó lọt qua. Khi đó cần mở rộng `VERIFIED_FIELDS` hoặc kiểm principal ở tầng khác.

## Giới hạn

- MockLLM không phải model sản xuất. Lỗi của swarm là lỗi cài sẵn theo seed (`seed % 5 == 0`), không phải phân phối lỗi của LLM thật. Pass^5 của swarm phụ thuộc hoàn toàn vào việc bộ seed có chứa 55 hay không.
- Latency là `unavailable`. Cost là VND mô phỏng từ `config/pricing.yaml`.
- Bộ đối kháng chỉ có 8 claim do nhóm tự viết. Nhãn viết tay nhưng chưa có người thứ hai kiểm chéo.
- Chưa chạy trên bộ hidden. Giảng viên chấm biến thể bằng `--extra-shape swarm_verified=bonus.swarm_verified:run_claim`.
