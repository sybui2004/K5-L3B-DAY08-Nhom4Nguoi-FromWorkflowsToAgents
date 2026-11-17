"""Team shown in the sidebar. Keep in sync with TEAM.md and slides/index.html.

A member with mssv=None is a slot still to be filled; the sidebar prints it as pending.
"""

from __future__ import annotations

TEAM_NAME = "Nhóm L3B"

MEMBERS: list[dict[str, str | None]] = [
    {"name": "Bùi Thái Sỹ", "mssv": "2A202604002"},
    {"name": "Bùi Phan Thanh Phúc", "mssv": "2A202603981"},
    {"name": "Hoàng Ngọc Hiệu", "mssv": "2A202603976"},
    {"name": "Đoàn Sỹ Hưng", "mssv": "2A202603990"},
]
