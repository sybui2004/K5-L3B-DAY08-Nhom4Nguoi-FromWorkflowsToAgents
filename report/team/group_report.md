# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Nhom4Nguoi (lớp L3B)
- Thành viên (chi tiết xem `TEAM.md`):
  - Bùi Thái Sỹ, 2A202604002 (nhóm trưởng; orchestrator, handoff, bonus B3)
  - Bùi Phan Thanh Phúc, 2A202603981 (workflow)
  - Hoàng Ngọc Hiệu, 2A202603976 (single agent, showcase)
  - Đoàn Sỹ Hưng, 2A202603990 (ledger, evaluation, slide)
- Commit chốt (trùng `report/team/decision_adr.md`): `aa86e18`

## 2. Mục tiêu và cách tiếp cận

LogiX-VN yêu cầu xử lý claim hoàn tiền giao hàng trễ hoặc hỏng hàng. Quyết định phải đúng theo luật nghiệp vụ, không rò secret, không vượt approval, và an toàn khi crash giữa chừng. Lab so sánh bốn shape (workflow, single ReAct, orchestrator, swarm) trên cùng corpus, seed, model (MockLLM), tool và giá, để tách ảnh hưởng của topology khỏi các biến khác.

Nhóm 4 người chia theo thứ tự: workflow và tích hợp (Phúc), single (Hiệu), orchestrator và handoff (Sỹ), ledger và evaluation (Hưng). Workflow làm trước vì là mốc so sánh; orchestrator làm sau single vì cần handoff. Sỹ làm thêm bonus B3 và tích hợp báo cáo.

Nguyên tắc chung: **code giữ tiền, model chỉ soạn văn bản hoặc chọn bước đọc**. Số tiền luôn đến từ `compute_compensation` trên dòng order có cấu trúc, không từ ticket và không từ câu trả lời của model.

## 3. Giải pháp

| Shape | Đọc gì | Quyết định gì | Gọi host thế nào |
| --- | --- | --- | --- |
| workflow | claim view (allowlist), order qua `lookup_order` có kiểm principal | Quote từ order bằng `compute_compensation`; quote 0 thì `denied` | `issue_refund` với quote đầy đủ, host kiểm approval, trần theo đơn, idempotency |
| single (ReAct, tối đa 8 bước) | Agent chọn tool **đọc** nào gọi tiếp và khi nào dừng | Số tiền lấy từ kết quả `compute_compensation`, không lấy từ `final` của agent | Shape (không phải agent) gọi `issue_refund` |
| orchestrator | Claim view, kế hoạch (1 lần gọi MockLLM), investigator đọc order | Orchestrator quote từ order mà investigator đọc | Chỉ orchestrator gọi `issue_refund`, truyền quote đầy đủ để host trừ khoản đã hoàn (T13, T14) |

**Ranh giới code / model** (xem [docs/architecture.md](../../docs/architecture.md)): ticket là dữ liệu người dùng, không bao giờ được parse lấy số, không được làm theo, không ghi vào trace. Model không có tool ghi; `dispatch` từ chối tool ghi. Host là lớp cuối chặn approval hết hạn, vượt trần và refund trùng.

**Handoff được sanitize** (orchestrator): `make_handoff` dùng allowlist field, `facts` luôn rỗng, và chỉ nêu tên các tool đọc. Investigator tự đọc lại order qua tool có kiểm principal, nên không có `parent_secret`, header thô, claim row đầy đủ hay ticket đi qua ranh giới. Tóm tắt bằng LLM không được coi là redaction; allowlist mới là cơ chế chặn.

**Trace** ghi: claim view đã allowlist, từng lần gọi tool, `quote`, số lần gọi model, kết quả host (`refund_committed`, `policy_denied`), trạng thái cuối, và với orchestrator là handoff đã sanitize cùng tóm tắt investigator. Cố ý không ghi nguyên văn ticket (bộ hidden có ticket chèn lệnh và homoglyph), secret/canary, số điện thoại và ghi chú nội bộ.

**Bonus B3** (`src/bonus/swarm_verified.py`): giữ nguyên swarm, thêm verifier bằng code trước khi ghi. Verifier đọc lại order bằng `lookup_order`, đối chiếu các dữ kiện đã dùng để quote, nếu lệch thì quote lại từ dữ liệu có cấu trúc (tối đa 1 vòng, còn lệch thì fail-closed) và ghi `verifier_override`.

## 4. Kết quả

Bộ public: 14 claim × 5 seed (11, 22, 33, 44, 55), nguồn `src/reports/benchmark.json`. Cost là VND mô phỏng, latency là `unavailable`.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success | Mean / p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0 | 28.86 | 4.43 / 5 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0 | 30.60 | 9.21 / 10 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0 | 57.20 | 5.36 / 6 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 |

- Crash safety: **20/20** (`src/reports/crash.json`). Sau resume còn đúng một dòng ledger và một audit `refund_committed`.
- Secret leak / approval bypass: 0 / 0 (mọi trial `ok` theo `lab8.metrics.trial_pass`).
- Lần fail duy nhất: `R-swarm-C-002-s55` (`status resolved != denied`), do swarm tin số ngày trễ trong ticket ở seed chia hết cho 5.
- Tự kiểm `student_drop/` (3 shape × 40 claim × 5 seed, `src/reports/hidden_selfcheck.json`): 600 trial, 0 `leak_suspect_trials`, 0 lỗi chạy. File này không có nhãn nên không có pass rate; kết luận chọn shape vẫn dựa trên bộ public.
- Test (chạy trong `src/` trên commit `aa86e18`): `python -m pytest -q` 184 passed; `python -m pytest -q -m student -o addopts=` 248 passed; `python -m lab8.check_submission` 0 FAIL. Chạy lại benchmark và crash suite cho số liệu trùng file nộp (`crash_safety` 20/20).

**Bonus B3** (`reports/bonus_benchmark_*.json`): verifier đưa swarm từ 0.986 / 0.929 lên 1.000 / 1.000 trên public, và từ 0.875 / 0.375 lên 1.000 / 1.000 trên 8 claim đối kháng. Cost/success tăng 16,1% (49.57 → 57.57) và 6,5% (61.71 → 65.74), nhưng vẫn gấp khoảng 2 lần workflow (28.86).

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md` (chọn **workflow**). Phiếu nghiên cứu và ablation: xem `report/team/research_card.md` (R2, bật/tắt verifier trên swarm; giả thuyết đúng).

## 5. Khó khăn và cách xử lý

- **Quote đầy đủ so với phần còn lại.** Với T14 (hoàn nhiều lần trên cùng đơn), nếu orchestrator trừ khoản đã hoàn ở phía mình thì host sẽ trừ lần hai. Xử lý: luôn truyền quote đầy đủ (150.000), host tự trừ nên ledger ghi 120.000. Có test riêng.
- **Handoff có thể rò context.** Tóm tắt bằng LLM không đảm bảo sạch. Xử lý: allowlist của `make_handoff`, `facts` rỗng, investigator đọc lại order qua tool có kiểm principal; test kiểm handoff trong trace không chứa secret hay ticket.
- **Swarm tin số ngày trong ticket (seed 55).** Xác định theo seed, không phải nhiễu. Xử lý ở bonus: verifier đọc lại order thay vì tin bản investigator đã đọc.
- **`run_react` chỉ trả lại kết quả tool gần nhất**, nên agent của shape single phải tự nhớ claim, order và quote.
- **Nhãn của claim đối kháng.** Viết tay theo luật nghiệp vụ ([docs/business_rules.md](../../docs/business_rules.md)), không sinh bằng `quote`, để tránh tự kiểm chính mình.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md` của từng người (của Sỹ: `report/team/202604002_BuiThaiSy.md`).

## 7. Hạn chế và hướng cải thiện

- MockLLM không phải model sản xuất; latency là `unavailable`, cost là mô phỏng.
- Bộ public chỉ có 14 claim và ba shape đều đạt 1.000, nên chưa đủ để nói khác biệt giữa chúng có ý nghĩa thống kê. Cần bootstrap CI và kiểm định cặp (B4) nếu muốn kết luận chặt hơn.
- LogiX chỉ có một nguồn lỗi và host chặn lỗi lan giữa agent, nên không đo được tỉ lệ khuếch đại lỗi như paper.
- Kết luận chọn workflow đảo lại khi: task song song được thật và latency là chi phí chính, dữ kiện quyết định không còn nằm hết trong DB có cấu trúc, hoặc bộ hidden cho thấy workflow fail ở nhóm claim mà shape khác xử lý được.
- Verifier có thể áp đặt dữ liệu cũ hoặc sai một cách nhất quán, và sẽ từ chối claim hợp lệ mà DB chưa kịp cập nhật (ví dụ hỏng hàng chưa verify).

## 8. Tài liệu tham khảo

- Google Research, 2026, *Towards a Science of Scaling Agent Systems* (error amplification, evaluator–optimizer).
- MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?*.
- Tài liệu lab: [docs/architecture.md](../../docs/architecture.md), [docs/business_rules.md](../../docs/business_rules.md), [docs/bonus_topics.md](../../docs/bonus_topics.md), [RULES.md](../../RULES.md).
