"""Shared local-only demo credentials for the seed command and login page."""

DEMO_PASSWORD = "NoiNgheDemo2026!"
DEMO_ADMIN_EMAIL = "admin@noinghe.local"


def get_demo_login_accounts():
    accounts = [{"label": "Quản trị viên", "email": DEMO_ADMIN_EMAIL}]
    accounts.extend(
        {
            "label": f"Sinh viên {number:02d}",
            "email": f"sinhvien{number:02d}@example.com",
        }
        for number in range(1, 11)
    )
    accounts.extend(
        {
            "label": f"Nhà tuyển dụng {number:02d}",
            "email": f"nhatuyendung{number:02d}@example.com",
        }
        for number in range(1, 11)
    )
    return accounts
