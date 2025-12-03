# gui.py

import argparse
import threading
import queue
from collections import Counter
from typing import List, Dict
from urllib.parse import urljoin

# Tkinter + matplotlib cho GUI
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from config import (
    DEFAULT_TIMEOUT,
    DEFAULT_MATCH_CODES,
    DEFAULT_MATCH_SIZES,
    DEFAULT_FILTER_CODES,
    DEFAULT_FILTER_SIZES,
    DEFAULT_WORDLIST,
)
from dictionary import load_wordlist
from http_client import HttpClient
from filters import build_filter_config, should_show
from output import print_result, save_report


# ====================== PHẦN SCAN CHUNG (cho CLI) ======================

def scan_sync(
    base_url: str,
    paths: List[str],
    http_client: HttpClient,
    cfg,
    on_result,
) -> List[Dict]:
    """
    Hàm scan đồng bộ, dùng cho CLI.
    """
    results: List[Dict] = []
    base = base_url.rstrip("/") + "/"

    for path in paths:
        full_url = urljoin(base, path.lstrip("/"))
        res = http_client.get(full_url)
        if not res:
            continue

        if should_show(res, cfg):
            results.append(res)
            on_result(res)

    return results


# ====================== PHẦN CLI ======================

def run_cli() -> bool:
    parser = argparse.ArgumentParser(
        description="Simple Web Path Scanner (CLI + GUI)"
    )

    # HTTP OPTIONS
    parser.add_argument(
        "-u",
        help="URL target",
    )
    parser.add_argument(
        "-timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"HTTP request timeout in seconds. (default: {DEFAULT_TIMEOUT})",
    )

    # MATCHER OPTIONS
    parser.add_argument(
        "-mc",
        help=(
            'Match HTTP status codes, or "all" for everything. '
            f'(default: {DEFAULT_MATCH_CODES})'
        ),
    )
    parser.add_argument(
        "-ms",
        help="Match HTTP response size (e.g. 100,200-300)",
    )

    # FILTER OPTIONS
    parser.add_argument(
        "-fc",
        help="Filter HTTP status codes from response. Comma separated list of codes and ranges",
    )
    parser.add_argument(
        "-fs",
        help="Filter HTTP response size. Comma separated list of sizes and ranges",
    )

    # INPUT OPTIONS
    parser.add_argument(
        "-w",
        default=DEFAULT_WORDLIST,
        help=f"Wordlist file path (default: {DEFAULT_WORDLIST})",
    )

    args = parser.parse_args()

    # Nếu không có -u => không chạy CLI, trả về False để mở GUI
    if not args.u:
        return False

    # Chạy CLI
    print(f"[+] Target URL: {args.u}")
    print(f"[+] Wordlist   : {args.w}")
    print(f"[+] Timeout    : {args.timeout}s")

    try:
        paths = load_wordlist(args.w)
    except FileNotFoundError:
        print(f"[!] Wordlist not found: {args.w}")
        return True

    if not paths:
        print("[!] Wordlist is empty.")
        return True

    cfg = build_filter_config(
        mc_str=args.mc,
        ms_str=args.ms or DEFAULT_MATCH_SIZES,
        fc_str=args.fc or DEFAULT_FILTER_CODES,
        fs_str=args.fs or DEFAULT_FILTER_SIZES,
        default_mc_str=DEFAULT_MATCH_CODES,
    )

    client = HttpClient(timeout=args.timeout)

    def on_result(res):
        print_result(res)

    results = scan_sync(
        base_url=args.u,
        paths=paths,
        http_client=client,
        cfg=cfg,
        on_result=on_result,
    )

    print(f"\n[+] Found {len(results)} matching paths.")
    report_file = save_report(results, args.u)
    print(f"[+] Report saved to {report_file}")

    return True  # đã chạy CLI


# ====================== PHẦN GUI TKINTER ======================

class WebPathScanApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Kingsearch - Web Path Scanner")
        self.root.geometry("1100x650")

        self.results: List[Dict] = []
        self.status_counter: Counter = Counter()

        # queue để nhận kết quả từ thread scan
        self.result_queue: "queue.Queue[Dict]" = queue.Queue()
        self.is_scanning = False

        # progress
        self.total_paths = 0
        self.done_paths = 0

        self._build_ui()
        self._setup_chart()

        # loop đọc queue định kỳ
        self.root.after(50, self._process_results_from_queue)

    # ---------- UI ----------

    def _build_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Khung cấu hình
        config_frame = ttk.LabelFrame(main_frame, text="Cấu hình")
        config_frame.pack(fill=tk.X, padx=5, pady=5)

        # Progress string
        self.progress_var = tk.StringVar(value="Progress: [0/0]")

        # URL
        ttk.Label(config_frame, text="URL:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.url_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.url_var, width=50).grid(
            row=0, column=1, padx=5, pady=2, sticky=tk.W
        )

        # Wordlist
        ttk.Label(config_frame, text="Wordlist:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.wordlist_var = tk.StringVar(value=DEFAULT_WORDLIST)
        ttk.Entry(config_frame, textvariable=self.wordlist_var, width=40).grid(
            row=1, column=1, padx=5, pady=2, sticky=tk.W
        )
        ttk.Button(config_frame, text="Chọn...", command=self._browse_wordlist).grid(
            row=1, column=2, padx=5, pady=2
        )

        # Timeout
        ttk.Label(config_frame, text="Timeout (s):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.timeout_var = tk.IntVar(value=DEFAULT_TIMEOUT)
        ttk.Spinbox(
            config_frame,
            from_=1,
            to=60,
            textvariable=self.timeout_var,
            width=5,
        ).grid(row=0, column=3, padx=5, pady=2, sticky=tk.W)

        # Match codes
        ttk.Label(config_frame, text="Match codes (-mc):").grid(
            row=2, column=0, sticky=tk.W, padx=5, pady=2
        )
        self.mc_var = tk.StringVar(value=DEFAULT_MATCH_CODES)
        ttk.Entry(config_frame, textvariable=self.mc_var, width=40).grid(
            row=2, column=1, padx=5, pady=2, sticky=tk.W
        )

        # Filter codes
        ttk.Label(config_frame, text="Filter codes (-fc):").grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=2
        )
        self.fc_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.fc_var, width=40).grid(
            row=3, column=1, padx=5, pady=2, sticky=tk.W
        )

        # Match sizes
        ttk.Label(config_frame, text="Match sizes (-ms):").grid(
            row=2, column=2, sticky=tk.W, padx=5, pady=2
        )
        self.ms_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.ms_var, width=20).grid(
            row=2, column=3, padx=5, pady=2, sticky=tk.W
        )

        # Filter sizes
        ttk.Label(config_frame, text="Filter sizes (-fs):").grid(
            row=3, column=2, sticky=tk.W, padx=5, pady=2
        )
        self.fs_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.fs_var, width=20).grid(
            row=3, column=3, padx=5, pady=2, sticky=tk.W
        )

        # Nút
        self.start_button = ttk.Button(config_frame, text="Bắt đầu scan", command=self.start_scan)
        self.start_button.grid(row=0, column=4, padx=10, pady=2, sticky=tk.E)

        self.save_button = ttk.Button(config_frame, text="Lưu báo cáo", command=self.save_report_gui)
        self.save_button.grid(row=1, column=4, padx=10, pady=2, sticky=tk.E)

        # Progress Label
        ttk.Label(config_frame, textvariable=self.progress_var).grid(
            row=4, column=0, columnspan=5, sticky=tk.W, padx=5, pady=2
        )

        # Khung dưới chia đôi: trái (kết quả), phải (biểu đồ)
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Kết quả
        results_frame = ttk.LabelFrame(bottom_frame, text="Kết quả")
        results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        columns = ("status", "length", "time", "url")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings")
        self.tree.heading("status", text="Status")
        self.tree.heading("length", text="Length (B)")
        self.tree.heading("time", text="Time (ms)")
        self.tree.heading("url", text="URL")

        self.tree.column("status", width=70, anchor=tk.CENTER)
        self.tree.column("length", width=90, anchor=tk.E)
        self.tree.column("time", width=90, anchor=tk.E)
        self.tree.column("url", width=400, anchor=tk.W)

        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Khung biểu đồ
        chart_frame = ttk.LabelFrame(bottom_frame, text="Thống kê status code")
        chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.chart_frame = chart_frame

    def _setup_chart(self):
        self.figure = Figure(figsize=(4, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Số lượng path theo status code")
        self.ax.set_xlabel("Status code")
        self.ax.set_ylabel("Count")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ---------- Hành vi GUI ----------

    def _browse_wordlist(self):
        filename = filedialog.askopenfilename(
            title="Chọn wordlist",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
        )
        if filename:
            self.wordlist_var.set(filename)

    def _update_progress_label(self):
        self.progress_var.set(f"Progress: [{self.done_paths}/{self.total_paths}]")

    def start_scan(self):
        if self.is_scanning:
            return  # đang scan thì bỏ

        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Thiếu URL", "Vui lòng nhập URL mục tiêu.")
            return

        wordlist_path = self.wordlist_var.get().strip()
        try:
            paths = load_wordlist(wordlist_path)
        except FileNotFoundError:
            messagebox.showerror("Lỗi", f"Không tìm thấy wordlist: {wordlist_path}")
            return

        if not paths:
            messagebox.showwarning("Wordlist rỗng", "Wordlist không có đường dẫn nào.")
            return

        # Tạo cấu hình matcher/filter
        cfg = build_filter_config(
            mc_str=self.mc_var.get().strip() or None,
            ms_str=self.ms_var.get().strip() or None,
            fc_str=self.fc_var.get().strip() or None,
            fs_str=self.fs_var.get().strip() or None,
            default_mc_str=DEFAULT_MATCH_CODES,
        )

        client = HttpClient(timeout=self.timeout_var.get())

        # Reset dữ liệu cũ
        self.results.clear()
        self.status_counter.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._update_chart()

        base = url.rstrip("/") + "/"

        # thiết lập progress
        self.total_paths = len(paths)
        self.done_paths = 0
        self._update_progress_label()

        self.is_scanning = True
        self.start_button.config(state=tk.DISABLED)

        def worker():
            for idx, path in enumerate(paths, start=1):
                if not self.is_scanning:
                    break

                self.done_paths = idx  # cập nhật số đã xử lý

                full_url = urljoin(base, path.lstrip("/"))
                res = client.get(full_url)
                if not res:
                    continue

                if not should_show(res, cfg):
                    continue

                self.result_queue.put(res)

            # báo kết thúc
            self.result_queue.put(None)

        threading.Thread(target=worker, daemon=True).start()

    def _process_results_from_queue(self):
        """
        Hàm này chạy trong main thread, lấy kết quả từ queue & update UI.
        Được gọi định kỳ bằng root.after().
        """
        try:
            while True:
                item = self.result_queue.get_nowait()
                if item is None:
                    # scan xong
                    self.is_scanning = False
                    self.start_button.config(state=tk.NORMAL)
                    messagebox.showinfo(
                        "Hoàn thành",
                        f"Scan xong. Tìm được {len(self.results)} kết quả."
                    )
                    break

                res = item
                self.results.append(res)
                status = res["status_code"]
                self.status_counter[status] += 1

                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        status,
                        res["length"],
                        f"{res['elapsed_ms']:.1f}",
                        res["url"],
                    ),
                )
                self._update_chart()

        except queue.Empty:
            pass

        # cập nhật progress mỗi lần tick
        self._update_progress_label()

        # nếu vẫn đang scan thì poll nhanh hơn
        delay = 50 if self.is_scanning else 200
        self.root.after(delay, self._process_results_from_queue)

    def _update_chart(self):
        self.ax.clear()
        self.ax.set_title("Số lượng path theo status code")
        self.ax.set_xlabel("Status code")
        self.ax.set_ylabel("Count")

        if self.status_counter:
            codes = sorted(self.status_counter.keys())
            counts = [self.status_counter[c] for c in codes]
            self.ax.bar([str(c) for c in codes], counts)

        self.canvas.draw_idle()

    def save_report_gui(self):
        if not self.results:
            messagebox.showwarning("Chưa có dữ liệu", "Chưa có kết quả để lưu.")
            return

        url = self.url_var.get().strip() or "unknown"
        filename = save_report(self.results, url)
        messagebox.showinfo("Đã lưu", f"Đã lưu báo cáo: {filename}")


# ====================== MAIN ======================

def main():
    # Thử chạy CLI trước
    ran_cli = run_cli()

    # Nếu CLI không chạy (không có -u) => mở GUI
    if not ran_cli:
        root = tk.Tk()
        app = WebPathScanApp(root)
        root.mainloop()


if __name__ == "__main__":
    main()
