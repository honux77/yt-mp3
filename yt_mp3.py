import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import shutil
import subprocess
import sys
from datetime import datetime
import yt_dlp


class PlaylistWindow:
    """재생목록 미리보기 및 선택 다운로드 서브 윈도우."""

    def __init__(self, parent, title, entries, callback):
        self.callback = callback
        self.entries = entries

        self.win = tk.Toplevel(parent)
        self.win.title("재생목록 미리보기")
        self.win.geometry("560x460")
        self.win.resizable(False, True)
        self.win.grab_set()
        self.win.transient(parent)

        # 상단: 재생목록 제목 + 영상 수
        header = ttk.Frame(self.win)
        header.pack(fill="x", padx=10, pady=(10, 5))
        ttk.Label(header, text=title, font=("", 11, "bold")).pack(anchor="w")
        ttk.Label(header, text=f"총 {len(entries)}개 영상").pack(anchor="w")

        # 중앙: 스크롤 가능한 체크박스 목록
        list_frame = ttk.Frame(self.win)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(list_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.inner = ttk.Frame(canvas)

        self.inner.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 마우스 휠 스크롤
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.win.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self.vars = []
        for i, entry in enumerate(entries):
            var = tk.BooleanVar(value=True)
            self.vars.append(var)
            dur = PlaylistWindow._fmt_duration(entry.get("duration"))
            label = f"{i + 1}. {entry.get('title', '알 수 없음')}"
            if dur:
                label += f"  ({dur})"
            ttk.Checkbutton(self.inner, text=label, variable=var).pack(
                anchor="w", padx=5, pady=1
            )

        # 하단 버튼
        btn_frame = ttk.Frame(self.win)
        btn_frame.pack(fill="x", padx=10, pady=(5, 10))

        ttk.Button(btn_frame, text="전체 선택", command=self._select_all).pack(
            side="left", padx=(0, 5)
        )
        ttk.Button(btn_frame, text="전체 해제", command=self._deselect_all).pack(
            side="left", padx=(0, 5)
        )
        ttk.Button(btn_frame, text="취소", command=self._on_cancel).pack(
            side="right", padx=(5, 0)
        )
        ttk.Button(btn_frame, text="다운로드", command=self._on_download).pack(
            side="right", padx=(5, 0)
        )

    def _select_all(self):
        for v in self.vars:
            v.set(True)

    def _deselect_all(self):
        for v in self.vars:
            v.set(False)

    def _on_download(self):
        selected = [
            entry.get("url") or entry.get("webpage_url") or entry.get("id")
            for entry, var in zip(self.entries, self.vars)
            if var.get()
        ]
        self.win.grab_release()
        self.win.destroy()
        if selected:
            self.callback(selected)

    def _on_cancel(self):
        self.win.grab_release()
        self.win.destroy()

    @staticmethod
    def _fmt_duration(seconds):
        if not seconds:
            return ""
        seconds = int(seconds)
        if seconds >= 3600:
            h, rem = divmod(seconds, 3600)
            m, s = divmod(rem, 60)
            return f"{h}:{m:02d}:{s:02d}"
        m, s = divmod(seconds, 60)
        return f"{m}:{s:02d}"


class YtMp3App:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube 오디오 다운로더")
        self.root.geometry("620x580")
        self.root.resizable(False, False)

        self.downloading = False
        self._log_lines = []

        self.formats = {
            "Opus (원본, 변환 없음)": {"codec": "opus", "ext": "opus"},
            "MP3 (192kbps)": {"codec": "mp3", "ext": "mp3"},
            "AAC (192kbps)": {"codec": "aac", "ext": "m4a"},
        }

        default_path = os.path.join(os.path.expanduser("~"), "Music", "yt-mp3")
        self.save_path = tk.StringVar(value=default_path)
        self.ffmpeg_path = tk.StringVar(value="")
        self.selected_format = tk.StringVar(value="Opus (원본, 변환 없음)")

        self._build_ui()
        self._check_ffmpeg_on_startup()

    def _check_ffmpeg_on_startup(self):
        ffmpeg_loc = shutil.which("ffmpeg")
        if ffmpeg_loc:
            ffmpeg_dir = os.path.dirname(ffmpeg_loc)
            self.ffmpeg_path.set(ffmpeg_dir)
            self.ffmpeg_status.configure(
                text=f"시스템 PATH에서 자동 설정됨", foreground="green"
            )
        else:
            self.ffmpeg_status.configure(
                text="ffmpeg를 찾을 수 없습니다. MP3/AAC 변환에 필요합니다.", foreground="red"
            )

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

        # --- ffmpeg 경로 ---
        ffmpeg_frame = ttk.LabelFrame(self.root, text="ffmpeg 경로 (비워두면 시스템 PATH 사용)")
        ffmpeg_frame.pack(fill="x", **pad)

        ffmpeg_input = ttk.Frame(ffmpeg_frame)
        ffmpeg_input.pack(fill="x")

        ttk.Entry(ffmpeg_input, textvariable=self.ffmpeg_path).pack(
            side="left", fill="x", expand=True, padx=(10, 5), pady=8
        )

        ttk.Button(ffmpeg_input, text="찾아보기", command=self._browse_ffmpeg).pack(
            side="right", padx=(0, 10), pady=8
        )

        self.ffmpeg_status = ttk.Label(ffmpeg_frame, text="", font=("", 8))
        self.ffmpeg_status.pack(anchor="w", padx=10, pady=(0, 5))

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

    def _browse_ffmpeg(self):
        path = filedialog.askdirectory(initialdir=self.ffmpeg_path.get() or None)
        if path:
            self.ffmpeg_path.set(path)

    def _find_ffmpeg(self):
        """ffmpeg 실행 가능 여부를 확인하고, 찾으면 경로를 반환한다."""
        custom = self.ffmpeg_path.get().strip()
        if custom:
            candidate = os.path.join(custom, "ffmpeg.exe") if sys.platform == "win32" else os.path.join(custom, "ffmpeg")
            if os.path.isfile(candidate):
                return custom
            return None
        if shutil.which("ffmpeg"):
            return ""
        return None

    def _log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log_lines.append(f"[{timestamp}] {msg}")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _set_progress(self, value):
        self.progress["value"] = value

    def _save_log(self, dest):
        if not self._log_lines:
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(dest, f"download_log_{timestamp}.txt")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("\n".join(self._log_lines))
            self.root.after(0, self._log, f"로그 저장: {log_path}")
        except OSError:
            pass

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

        fmt = self.formats[self.selected_format.get()]
        if fmt["codec"] != "opus" and self._find_ffmpeg() is None:
            messagebox.showwarning(
                "ffmpeg 필요",
                "선택한 포맷은 ffmpeg가 필요합니다.\n"
                "ffmpeg 경로를 설정하거나 ffmpeg를 설치해 주세요.",
            )
            return

        self._log_lines.clear()
        self.download_btn.configure(state="disabled")
        self._set_progress(0)
        self.progress.configure(mode="indeterminate")
        self.progress.start(15)
        self._log("재생목록 정보를 가져오는 중...")

        ffmpeg_loc = self._find_ffmpeg()
        thread = threading.Thread(
            target=self._extract_and_route,
            args=(url, dest, fmt, ffmpeg_loc),
            daemon=True,
        )
        thread.start()

    def _extract_and_route(self, url, dest, fmt, ffmpeg_loc):
        """메타데이터를 추출하여 재생목록이면 서브 윈도우, 단일 영상이면 바로 다운로드."""
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            self.root.after(0, self._log, f"❌ 정보 추출 오류: {e}")
            self.root.after(
                0, lambda: messagebox.showerror("오류", str(e))
            )
            self.root.after(0, self._stop_indeterminate)
            return

        entries = info.get("entries")
        if entries is not None:
            entries = [e for e in entries if e is not None]

        if entries:
            # 재생목록 → 서브 윈도우
            playlist_title = info.get("title", "재생목록")

            def show_playlist():
                self._stop_indeterminate()
                self._log(f"재생목록 감지: {playlist_title} ({len(entries)}개)")

                def on_selected(urls):
                    self.downloading = True
                    self.download_btn.configure(state="disabled")
                    self._set_progress(0)
                    thread = threading.Thread(
                        target=self._download,
                        args=(urls, dest, fmt, ffmpeg_loc),
                        daemon=True,
                    )
                    thread.start()

                PlaylistWindow(self.root, playlist_title, entries, on_selected)

            self.root.after(0, show_playlist)
        else:
            # 단일 영상 → 바로 다운로드
            self.root.after(0, self._stop_indeterminate)
            self.downloading = True
            self._download([url], dest, fmt, ffmpeg_loc)

    def _stop_indeterminate(self):
        self.progress.stop()
        self.progress.configure(mode="determinate")
        self._set_progress(0)
        self.download_btn.configure(state="normal")

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

    def _download(self, urls, dest, fmt, ffmpeg_loc):
        metadata_pps = [
            {"key": "FFmpegMetadata"},
            {"key": "EmbedThumbnail"},
        ]

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(dest, "%(title)s.%(ext)s"),
            "progress_hooks": [self._progress_hook],
            "writethumbnail": True,
            "noplaylist": True,
            "ignoreerrors": True,
        }

        if ffmpeg_loc:
            ydl_opts["ffmpeg_location"] = ffmpeg_loc

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
            self.root.after(
                0, self._log, f"다운로드 시작: {len(urls)}개 항목"
            )
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(urls)
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
            self._save_log(dest)
            self.downloading = False
            self.root.after(0, lambda: self.download_btn.configure(state="normal"))


if __name__ == "__main__":
    root = tk.Tk()
    YtMp3App(root)
    root.mainloop()
