"""Static demo vocabulary: scenario labels for the 14 public claims, shapes, seeds, presets.

Pure data, no lab8 import. Labels describe what each claim tests so the audience
does not need to read raw tickets to follow the demo.
"""

from __future__ import annotations

SHAPES = ["workflow", "single", "orchestrator", "swarm"]

SHAPE_LABELS = {
    "workflow": "Workflow - tất định",
    "single": "Single agent - ReAct",
    "orchestrator": "Orchestrator - worker chỉ đọc",
    "swarm": "Swarm - bản tham chiếu",
    "swarm_verified": "Swarm + verifier (bonus B3)",
}

SHAPE_SHORT = {
    "workflow": "Code quyết mọi bước, không cần model",
    "single": "Model tự chọn tool, tối đa 8 bước",
    "orchestrator": "Worker chỉ đọc, handoff qua allowlist",
    "swarm": "Peer bàn nhau, có điểm yếu cố ý ở seed 55",
}

SEEDS = [11, 22, 33, 44, 55]

CRASH_POINTS = [None, "before_effect", "after_effect_before_checkpoint", "after_checkpoint"]

CRASH_LABELS = {
    None: "Không crash",
    "before_effect": "Trước khi ghi tiền",
    "after_effect_before_checkpoint": "Sau khi ghi tiền, trước checkpoint",
    "after_checkpoint": "Sau checkpoint",
}

GROUP_LABELS = {
    "all": "Tất cả",
    "basic": "Cơ bản",
    "trap": "Bẫy nghiệp vụ",
    "money": "Đã hoàn trước đó",
    "security": "Bảo mật",
    "durability": "Durability",
}

# claim_id -> (scenario label, group key)
SCENARIOS = {
    "C-001": ("Trễ 4 ngày, ca chuẩn", "basic"),
    "C-002": ("Ticket nói trễ 5 ngày, order row nói khác", "trap"),
    "C-003": ("Hàng hỏng đã xác minh", "basic"),
    "C-004": ("Thiếu mã đơn", "basic"),
    "C-005": ("Đơn thuộc principal khác", "security"),
    "C-006": ("Viện dẫn policy cũ", "trap"),
    "C-007": ("Approval đã hết hạn", "trap"),
    "C-008": ("Đã hoàn trước một phần", "money"),
    "C-009": ("Prompt injection: ignore policy", "trap"),
    "C-010": ("Order chứa PII, bẫy rò trace", "security"),
    "C-011": ("Đòi hoàn thêm lần nữa", "money"),
    "C-012": ("Dùng cho demo crash và retry", "durability"),
    "C-013": ("Đã hoàn đủ trước đó", "money"),
    "C-014": ("Hàng hỏng, đã hoàn ship trước đó", "money"),
}

# Opening scenario of the live demo (slide 5 -> tab Chạy claim).
RUNNER_PRESET = {"claim": "C-001", "shape": "workflow", "seed": 11}

# (button label, claim_id, seed) for the shape comparison tab.
COMPARE_PRESETS = [
    ("Ca chuẩn · C-001", "C-001", 11),
    ("Ticket nói dối · C-002 seed 55", "C-002", 55),
    ("Injection · C-009", "C-009", 55),
    ("Đã hoàn một phần · C-014", "C-014", 11),
]

# Default durability scenario (slide 8 -> tab Durability).
DURABILITY_PRESET = {
    "claim": "C-012",
    "shape": "workflow",
    "seed": 11,
    "crash_at": "after_effect_before_checkpoint",
}


def scenario_label(claim_id: str) -> str:
    return SCENARIOS.get(claim_id, ("Claim ngoài bộ công khai", "all"))[0]


def scenario_group(claim_id: str) -> str:
    return SCENARIOS.get(claim_id, ("", "all"))[1]
