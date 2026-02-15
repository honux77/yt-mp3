import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import subprocess
import sys
import yt_dlp


class YtMp3App:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube 오디오 다운로더")
        self.root.geometry("620x520")
        self.root.resizable(False, False)

        self.downloading = False

        self.formats = {
            "Opus (원본, 변환 없음)": {"codec": "opus", "ext": "opus"},
            "MP3 (192kbps)": {"codec": "mp3", "ext": "mp3"},
            "AAC (192kbps)": {"codec": "aac", "ext": "m4a"},
        }

        default_path = os.path.join(os.path.expanduser("~"), "Music", "yt-mp3")
        self.save_path = tk.StringVar(value=default_path)
        self.selected_format = tk.StringVar(value="Opus (원본, 변환 없음)")

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        # --- URL 입력 ---
        url_frame = ttk.LabelFrame(self.root, text="YouTube URL")
        url_frame.pack(fill="x", **pad)

        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=8)

        ttk.Button(url_frame, text="붙여넣기", command=self._paste_url).pack(
            side="right", padx=(0, 10), pady=8
        )

        # --- 저장 경로 ---
        path_frame = ttk.LabelFrame(self.root, text="저장 경로")
        path_frame.pack(fill="x", **pad)

        ttk.Entry(path_frame, textvariable=self.save_path).pack(
            side="left", fill="x", expand=True, padx=(10, 5), pady=8
        )

        ttk.Button(path_frame, text="찾아보기", command=self._browse_path).pack(
            side="right", padx=(0, 10), pady=8
        )

        # --- 오디오 포맷 ---
        fmt_frame = ttk.LabelFrame(self.root, text="오디오 포맷")
        fmt_frame.pack(fill="x", **pad)

        fmt_combo = ttk.Combobox(
            fmt_frame,
            textvariable=self.selected_format,
            values=list(self.formats.keys()),
            state="readonly",
            width=30,
        )
        fmt_combo.pack(side="left", padx=10, pady=8)

        self.fmt_desc = ttk.Label(fmt_frame, text="변환 없이 원본 품질 유지, 파일 크기 최소")
        self.fmt_desc.pack(side="left", padx=5, pady=8)
        fmt_combo.bind("<<ComboboxSelected>>", self._on_format_change)

        # --- 버튼 영역 ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", **pad)

        self.download_btn = ttk.Button(
            btn_frame, text="다운로드", command=self._start_download
        )
        self.download_btn.pack(side="left", expand=True)

        ttk.Button(
            btn_frame, text="다운로드 폴더 열기", command=self._open_folder
        ).pack(side="left", expand=True)

        # --- 프로그레스 바 ---
        self.progress = ttk.Progressbar(self.root, mode="determinate")
        self.progress.pack(fill="x", **pad)

        # --- 로그 ---
        log_frame = ttk.LabelFrame(self.root, text="진행 상황")
        log_frame.pack(fill="both", expand=True, **pad)

        self.log_text = tk.Text(log_frame, height=12, state="disabled", wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    # ---- helpers ----

    def _on_format_change(self, _event=None):
        descs = {
            "Opus (원본, 변환 없음)": "변환 없이 원본 품질 유지, 파일 크기 최소",
            "MP3 (192kbps)": "범용 호환, ffmpeg 필요",
            "AAC (192kbps)": "고품질, Safari 완벽 지원, ffmpeg 필요",
        }
        self.fmt_desc.configure(text=descs.get(self.selected_format.get(), ""))

    def _paste_url(self):
        try:
            text = self.root.clipboard_get()
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, text.strip())
        except tk.TclError:
            pass

    def _open_folder(self):
        path = self.save_path.get().strip()
        os.makedirs(path, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def _browse_path(self):
        path = filedialog.askdirectory(initialdir=self.save_path.get())
        if path:
            self.save_path.set(path)

    def _log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _set_progress(self, value):
        self.progress["value"] = value

    # ---- download ----

    def _start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("입력 오류", "YouTube URL을 입력해 주세요.")
            return

        dest = self.save_path.get().strip()
        if not dest:
            messagebox.showwarning("입력 오류", "저장 경로를 선택해 주세요.")
            return

        os.makedirs(dest, exist_ok=True)

        self.downloading = True
        self.download_btn.configure(state="disabled")
        self._set_progress(0)

        fmt = self.formats[self.selected_format.get()]
        thread = threading.Thread(target=self._download, args=(url, dest, fmt), daemon=True)
        thread.start()

    def _progress_hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            if total > 0:
                pct = downloaded / total * 100
                self.root.after(0, self._set_progress, pct)
            info = d.get("_default_template", d.get("_percent_str", ""))
            if info:
                self.root.after(0, self._log, f"  {info.strip()}")
        elif d["status"] == "finished":
            self.root.after(0, self._set_progress, 100)
            filename = os.path.basename(d.get("filename", ""))
            self.root.after(0, self._log, f"변환 중: {filename}")

    def _download(self, url, dest, fmt):
        metadata_pps = [
            {"key": "FFmpegMetadata"},
            {"key": "EmbedThumbnail"},
        ]

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(dest, "%(title)s.%(ext)s"),
            "progress_hooks": [self._progress_hook],
            "writethumbnail": True,
            "noplaylist": False,
            "ignoreerrors": True,
        }

        if fmt["codec"] == "opus":
            ydl_opts["format"] = "bestaudio[acodec=opus]/bestaudio/best"
            ydl_opts["postprocessors"] = metadata_pps
        else:
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": fmt["codec"],
                    "preferredquality": "192",
                },
                *metadata_pps,
            ]

        try:
            self.root.after(0, self._log, f"다운로드 시작: {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.root.after(0, self._log, "✅ 다운로드 완료!")
            self.root.after(
                0,
                lambda: messagebox.showinfo("완료", "다운로드가 완료되었습니다."),
            )
        except Exception as e:
            self.root.after(0, self._log, f"❌ 오류: {e}")
            self.root.after(
                0,
                lambda: messagebox.showerror("오류", str(e)),
            )
        finally:
            self.downloading = False
            self.root.after(0, lambda: self.download_btn.configure(state="normal"))


if __name__ == "__main__":
    root = tk.Tk()
    YtMp3App(root)
    root.mainloop()
