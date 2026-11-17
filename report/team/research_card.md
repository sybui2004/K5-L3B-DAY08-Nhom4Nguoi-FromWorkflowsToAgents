# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* (loại bằng chứng: benchmark kèm phân tích có người gán nhãn). Bổ trợ cho thành phần verifier: Google Research 2026, *Towards a Science of Scaling Agent Systems*. URL: https://arxiv.org/abs/2503.13657 (MAST); https://arxiv.org/abs/2512.08296 (Google Research) |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lỗi của hệ multi-agent chia thành 3 nhóm: system design, inter-agent misalignment, task verification (14 failure mode, κ = 0,88). |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Taxonomy xây từ trace của các framework MAS với model thật và task khác (không phải claims hoàn tiền). Trên LogiX chỉ có MockLLM, host chặn approval, trần theo đơn và idempotency, và chỉ có một nguồn lỗi. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Lỗi seed 55 của swarm là lỗi **task verification**: không ai kiểm số ngày trễ với DB trước khi ghi. Bật thêm một bước verifier bằng code thì pass rate lên 1.000, pass^5 lên 1.000, variance về 0, và cost/success tăng không quá 20%. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định MockLLM, tool, seed `11,22,33,44,55`, 14 claim public, `config/pricing.yaml`, evaluator `lab8.metrics.trial_pass`, mỗi trial một SQLite mới. Biến duy nhất thay đổi: có hay không bước verifier (`swarm` so với `swarm_verified`). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi: swarm tin delay trong ticket ở seed % 5 == 0 (C-002 seed 55, `status resolved != denied`). Đo bằng pass rate, pass^5, variance theo seed, cost/success và số lần `verifier_override`. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --seeds 11,22,33,44,55 --out reports/bonus_benchmark_public.json` (chạy trong `src/`)
- Run id / file report: `src/reports/bonus_benchmark_public.json`; run id lỗi gốc `R-swarm-C-002-s55`, run id sau sửa `R-swarm_verified-C-002-s55`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng.** Swarm 0.986 / pass^5 0.929 / variance 0.000816 → swarm_verified 1.000 / 1.000 / 0. Cost/success 49.57 → 57.57 (+16,1%, dưới ngưỡng 20%). Verifier can thiệp 1/70 trial public (C-002 seed 55, `delay_days` 5 → 2). Trên bộ 8 claim đối kháng: 0.875 / 0.375 → 1.000 / 1.000, cost 61.71 → 65.74 (+6,5%). Chỉ có một nguồn lỗi nên không suy rộng ra tỉ lệ khuếch đại lỗi của nguồn.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
