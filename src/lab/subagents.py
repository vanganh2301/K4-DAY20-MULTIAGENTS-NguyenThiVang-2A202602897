"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Delegate to explorer to inspect workspace files, read README or task instructions, "
                "check data formats, logs, and docstrings before making changes. "
                "Use this to understand the task and report findings without modifying files."
            ),
            "system_prompt": (
                "You are an exploration subagent. Your role is to read and analyze files, docstrings, "
                "data formats, and error traces. Report your factual findings clearly. "
                "Do NOT modify any files."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Delegate to implementer to make file edits, implement fixes or data cleaning logic, "
                "run scripts and tests, and report execution results. "
                "Use this when code changes or script runs are needed."
            ),
            "system_prompt": (
                "You are an implementation subagent. Your role is to edit files, implement solutions, "
                "run tests or scripts via the shell, and report what changes were made and their outcomes."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Delegate to reviewer to independently verify solutions, check edge cases, "
                "run validation tests, and ensure all output formats match requirements. "
                "Use this before finishing a task to verify correctness."
            ),
            "system_prompt": (
                "You are a review and verification subagent. Your role is to inspect results, "
                "run test suites or validation checks, and verify that all task rules and requirements are met."
            ),
        },
    ]
