def problem(status, title, detail, problem_type="about:blank"):
    return {
        "type": problem_type,
        "title": title,
        "status": status,
        "detail": detail
    }