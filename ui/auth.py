import tkinter as tk


def get_credentials_from_tkinter() -> dict[str, str | bool] | None:
    credentials: dict[str, str | bool] = {}

    def submit() -> None:
        credentials["username"] = username_var.get()
        credentials["password"] = password_var.get()
        credentials["auto_click"] = auto_click_var.get()
        root.destroy()

    root = tk.Tk()
    root.title("Council Connect Login")
    root.geometry("350x200")
    root.attributes("-topmost", True)

    tk.Label(root, text="Council ID:").pack(pady=(10, 0))
    username_var = tk.StringVar()
    tk.Entry(root, textvariable=username_var, width=40).pack()

    tk.Label(root, text="Password:").pack(pady=(10, 0))
    password_var = tk.StringVar()
    tk.Entry(root, textvariable=password_var, show="*", width=40).pack()

    auto_click_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Auto-click 'Save'", variable=auto_click_var).pack(pady=10)

    tk.Button(root, text="Start", command=submit, width=15).pack(pady=10)
    root.mainloop()

    return credentials if credentials else None