from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from runtime.ui.app_shell import DNAFilmApp


def main() -> None:
    root = tk.Tk()
    ttk.Style().theme_use('clam')
    DNAFilmApp(root)
    root.minsize(1200, 760)
    root.mainloop()


if __name__ == '__main__':
    main()
