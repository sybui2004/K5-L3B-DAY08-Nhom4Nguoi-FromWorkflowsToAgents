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
| CÂU | R1 / R2 / R3 / R4 | R2 · Failure taxonomy |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST, NeurIPS 2025, https://arxiv.org/abs/2503.13654, benchmark |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Hệ thống Multi-Agent thường fail do lỗi kiểm chứng (verification failure) và tin tưởng không căn cứ vào input phi cấu trúc của người dùng (input hallucination). |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Giới hạn trong môi trường MockLLM/LLM agent xử lý claims với ticket chứa thông tin mâu thuẫn so với cơ sở dữ liệu orders đã lưu trữ. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Nếu đổi từ Swarm (Shape D) sang Workflow (Shape A), pass rate tăng từ 0.986 lên 1.000, pass^5 tăng từ 0.929 lên 1.000, variance giảm từ 0.000816 về 0.000000, và cost/success giảm từ 49.57 VND xuống 28.79 VND. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định model (MockLLM), toolset, 5 seeds (11, 22, 33, 44, 55), 14 claims public, bảng giá pricing.yaml. Biến duy nhất thay đổi: topology xử lý (Deterministic Workflow vs Swarm). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: Swarm chấp nhận refund sai trên claim C-002 ở seed 55 do tin số ngày trễ ghi trong ticket; đo bằng pass rate, pass^5, seed variance, và cost/success. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `reports/benchmark.json`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu:
  - **Đúng hoàn toàn.**
  - **Workflow:** pass rate 1.000, pass^5 1.000, seed min-max 1.000–1.000, variance 0.000000, cost/success 28.79 VND, mean steps 3.79.
  - **Swarm:** pass rate 0.986, pass^5 0.929, seed min-max 0.929–1.000, variance 0.000816, cost/success 49.57 VND, mean steps 2.80.
  - Thất bại của Swarm xảy ra chính xác tại claim C-002 với seed 55 (`status resolved != denied x1`), chứng minh giả thuyết về lỗi kiểm chứng dữ liệu người dùng trong hệ thống multi-agent.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.
