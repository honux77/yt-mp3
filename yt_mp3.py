import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import json
import shutil
import subprocess
import sys
from datetime import datetime
import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TIT2, TRCK, TALB, ID3NoHeaderError
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4


STRINGS = {
    "ko": {
        # YtMp3App
        "window_title": "YouTube 오디오 다운로더",
        "paste": "붙여넣기",
        "url_label": "YouTube URL",
        "save_path_label": "저장 경로",
        "browse": "찾아보기",
        "ffmpeg_path_label": "ffmpeg 경로 (비워두면 시스템 PATH 사용)",
        "ffmpeg_auto": "시스템 PATH에서 자동 설정됨",
        "ffmpeg_missing_win": "ffmpeg 미설치. 설치: winget install Gyan.FFmpeg",
        "ffmpeg_missing_mac": "ffmpeg 미설치. 설치: brew install ffmpeg",
        "ffmpeg_missing_linux": "ffmpeg 미설치. 설치: sudo apt install ffmpeg",
        "audio_format_label": "오디오 포맷",
        "format_opus": "Opus (원본, 변환 없음)",
        "format_mp3": "MP3 (192kbps)",
        "format_aac": "AAC (192kbps)",
        "format_desc_opus": "변환 없이 원본 품질 유지, 파일 크기 최소",
        "format_desc_mp3": "범용 호환, ffmpeg 필요",
        "format_desc_aac": "고품질, Safari 완벽 지원, ffmpeg 필요",
        "download": "다운로드",
        "open_folder": "다운로드 폴더 열기",
        "edit_metadata": "메타 정보 입력",
        "progress_label": "진행률",
        "overall_label": "전체: ({current}/{total})",
        "current_file": "현재 파일:",
        "log_label": "진행 상황",
        "warn_no_url_title": "입력 오류",
        "warn_no_url": "YouTube URL을 입력해 주세요.",
        "warn_no_path_title": "입력 오류",
        "warn_no_path": "저장 경로를 선택해 주세요.",
        "warn_ffmpeg_title": "ffmpeg 필요",
        "warn_ffmpeg": "선택한 포맷은 ffmpeg가 필요합니다.\nffmpeg 경로를 설정하거나 ffmpeg를 설치해 주세요.",
        "fetching_playlist": "재생목록 정보를 가져오는 중...",
        "error_extract": "❌ 정보 추출 오류: {error}",
        "error_title": "오류",
        "playlist_detected": "재생목록 감지: {title} ({count}개)",
        "download_start": "다운로드 시작: {count}개 항목",
        "converting": "변환 중: {filename}",
        "download_done": "✅ 다운로드 완료!",
        "done_title": "완료",
        "done_msg": "다운로드가 완료되었습니다.",
        "error_download": "❌ 오류: {error}",
        "log_saved": "로그 저장: {path}",
        "warn_no_dir_title": "알림",
        "warn_no_dir": "저장 경로가 존재하지 않습니다.",
        "language_label": "언어 / Language",
        "lang_restart_title": "언어 변경",
        "lang_restart_msg": "언어 설정이 변경되었습니다. 앱을 재시작하면 적용됩니다.",
        # MetadataWindow
        "meta_title": "메타 정보 편집",
        "meta_no_files_title": "알림",
        "meta_no_files": "오디오 파일이 없습니다.",
        "meta_file_list": "파일 목록",
        "meta_common": "공통 (전체 적용)",
        "meta_artist": "아티스트:",
        "meta_album": "앨범명:",
        "meta_apply_all": "전체에 적용",
        "meta_per_file": "개별 파일",
        "meta_song_title": "제목:",
        "meta_track": "트랙번호:",
        "meta_auto_fill": "전체 자동 채우기",
        "meta_save": "저장",
        "meta_save_all": "전체 저장",
        "meta_close": "닫기",
        "meta_applied_common": "아티스트/앨범을 전체 적용했습니다.",
        "meta_auto_fill_done": "전체 자동 채우기 완료",
        "meta_saved": "저장 완료: {name}",
        "meta_save_error": "저장 오류: {error}",
        "meta_save_all_done": "전체 저장 완료: {ok}개 성공",
        "meta_save_all_fail": ", {fail}개 실패",
        # PlaylistWindow
        "playlist_title": "재생목록 미리보기",
        "playlist_total": "총 {count}개 영상",
        "playlist_unknown": "알 수 없음",
        "playlist_select_all": "전체 선택",
        "playlist_deselect_all": "전체 해제",
        "playlist_cancel": "취소",
        "playlist_download": "다운로드",
    },
    "en": {
        # YtMp3App
        "window_title": "YouTube Audio Downloader",
        "paste": "Paste",
        "url_label": "YouTube URL",
        "save_path_label": "Save Path",
        "browse": "Browse",
        "ffmpeg_path_label": "ffmpeg Path (leave empty to use system PATH)",
        "ffmpeg_auto": "Auto-detected from system PATH",
        "ffmpeg_missing_win": "ffmpeg not installed. Install: winget install Gyan.FFmpeg",
        "ffmpeg_missing_mac": "ffmpeg not installed. Install: brew install ffmpeg",
        "ffmpeg_missing_linux": "ffmpeg not installed. Install: sudo apt install ffmpeg",
        "audio_format_label": "Audio Format",
        "format_opus": "Opus (original, no conversion)",
        "format_mp3": "MP3 (192kbps)",
        "format_aac": "AAC (192kbps)",
        "format_desc_opus": "Original quality, smallest file size",
        "format_desc_mp3": "Universal compatibility, requires ffmpeg",
        "format_desc_aac": "High quality, Safari compatible, requires ffmpeg",
        "download": "Download",
        "open_folder": "Open Download Folder",
        "edit_metadata": "Edit Metadata",
        "progress_label": "Progress",
        "overall_label": "Overall: ({current}/{total})",
        "current_file": "Current file:",
        "log_label": "Log",
        "warn_no_url_title": "Input Error",
        "warn_no_url": "Please enter a YouTube URL.",
        "warn_no_path_title": "Input Error",
        "warn_no_path": "Please select a save path.",
        "warn_ffmpeg_title": "ffmpeg Required",
        "warn_ffmpeg": "The selected format requires ffmpeg.\nPlease set the ffmpeg path or install ffmpeg.",
        "fetching_playlist": "Fetching playlist info...",
        "error_extract": "❌ Extraction error: {error}",
        "error_title": "Error",
        "playlist_detected": "Playlist detected: {title} ({count} items)",
        "download_start": "Download started: {count} items",
        "converting": "Converting: {filename}",
        "download_done": "✅ Download complete!",
        "done_title": "Done",
        "done_msg": "Download completed successfully.",
        "error_download": "❌ Error: {error}",
        "log_saved": "Log saved: {path}",
        "warn_no_dir_title": "Notice",
        "warn_no_dir": "Save path does not exist.",
        "language_label": "Language",
        "lang_restart_title": "Language Changed",
        "lang_restart_msg": "Language setting has been changed. Restart the app to apply.",
        # MetadataWindow
        "meta_title": "Edit Metadata",
        "meta_no_files_title": "Notice",
        "meta_no_files": "No audio files found.",
        "meta_file_list": "File List",
        "meta_common": "Common (apply to all)",
        "meta_artist": "Artist:",
        "meta_album": "Album:",
        "meta_apply_all": "Apply to All",
        "meta_per_file": "Per File",
        "meta_song_title": "Title:",
        "meta_track": "Track #:",
        "meta_auto_fill": "Auto-fill All",
        "meta_save": "Save",
        "meta_save_all": "Save All",
        "meta_close": "Close",
        "meta_applied_common": "Applied artist/album to all files.",
        "meta_auto_fill_done": "Auto-fill complete",
        "meta_saved": "Saved: {name}",
        "meta_save_error": "Save error: {error}",
        "meta_save_all_done": "Save complete: {ok} succeeded",
        "meta_save_all_fail": ", {fail} failed",
        # PlaylistWindow
        "playlist_title": "Playlist Preview",
        "playlist_total": "{count} videos total",
        "playlist_unknown": "Unknown",
        "playlist_select_all": "Select All",
        "playlist_deselect_all": "Deselect All",
        "playlist_cancel": "Cancel",
        "playlist_download": "Download",
    },
}

# Maps old Korean format keys to internal keys for config compatibility
_LEGACY_FORMAT_MAP = {
    "Opus (원본, 변환 없음)": "opus",
    "MP3 (192kbps)": "mp3",
    "AAC (192kbps)": "aac",
}

_LANG_NAMES = {"ko": "한국어", "en": "English"}


class MetadataWindow:
    """다운로드된 오디오 파일의 메타데이터를 편집하는 서브 윈도우."""

    AUDIO_EXTS = (".opus", ".mp3", ".m4a")

    def __init__(self, parent, scan_dir, lang="ko"):
        self.parent = parent
        self.scan_dir = scan_dir
        self.lang = lang
        # {filepath: {"artist": str, "title": str, "track": str}}
        self.file_meta = {}
        self.files = []
        self.current_index = None

        self.win = tk.Toplevel(parent)
        self.win.title(self._t("meta_title"))
        self.win.geometry("640x420")
        self.win.resizable(True, True)
        self.win.grab_set()
        self.win.transient(parent)

        self._scan_files()
        if not self.files:
            messagebox.showinfo(
                self._t("meta_no_files_title"),
                self._t("meta_no_files"),
                parent=self.win,
            )
            self.win.destroy()
            return

        self._build_ui()
        self._select_file(0)

    def _t(self, key, **kwargs):
        s = STRINGS[self.lang][key]
        return s.format(**kwargs) if kwargs else s

    def _scan_files(self):
        """저장 경로에서 오디오 파일을 스캔하고 기존 태그를 로드한다."""
        try:
            entries = sorted(os.listdir(self.scan_dir))
        except OSError:
            return
        for name in entries:
            if not name.lower().endswith(self.AUDIO_EXTS):
                continue
            path = os.path.join(self.scan_dir, name)
            if not os.path.isfile(path):
                continue
            self.files.append(path)
            self.file_meta[path] = self._read_tags(path)

    @staticmethod
    def _read_tags(path):
        """파일에서 기존 메타데이터를 읽는다."""
        meta = {"artist": "", "album": "", "title": "", "track": ""}
        ext = os.path.splitext(path)[1].lower()
        try:
            if ext == ".mp3":
                try:
                    tags = ID3(path)
                except ID3NoHeaderError:
                    return meta
                meta["artist"] = str(tags.get("TPE1", ""))
                meta["album"] = str(tags.get("TALB", ""))
                meta["title"] = str(tags.get("TIT2", ""))
                meta["track"] = str(tags.get("TRCK", ""))
            elif ext == ".opus":
                audio = OggOpus(path)
                meta["artist"] = audio.get("artist", [""])[0]
                meta["album"] = audio.get("album", [""])[0]
                meta["title"] = audio.get("title", [""])[0]
                meta["track"] = audio.get("tracknumber", [""])[0]
            elif ext == ".m4a":
                audio = MP4(path)
                meta["artist"] = (audio.tags or {}).get("\xa9ART", [""])[0]
                meta["album"] = (audio.tags or {}).get("\xa9alb", [""])[0]
                meta["title"] = (audio.tags or {}).get("\xa9nam", [""])[0]
                trkn = (audio.tags or {}).get("trkn")
                if trkn:
                    meta["track"] = str(trkn[0][0])
        except Exception:
            pass
        return meta

    def _build_ui(self):
        # 좌측: 파일 목록
        left = ttk.Frame(self.win)
        left.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)

        ttk.Label(left, text=self._t("meta_file_list"), font=("", 10, "bold")).pack(
            anchor="w"
        )

        list_frame = ttk.Frame(left)
        list_frame.pack(fill="both", expand=True, pady=(5, 0))

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self.file_listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set, activestyle="dotbox"
        )
        scrollbar.configure(command=self.file_listbox.yview)
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for path in self.files:
            self.file_listbox.insert("end", os.path.basename(path))

        self.file_listbox.bind("<<ListboxSelect>>", self._on_listbox_select)

        # 우측: 편집 패널
        right = ttk.Frame(self.win, width=260)
        right.pack(side="right", fill="y", padx=(5, 10), pady=10)
        right.pack_propagate(False)

        # --- 공통 필드 (아티스트 / 앨범) — 전체 파일에 동일 적용 ---
        common_lf = ttk.LabelFrame(right, text=self._t("meta_common"))
        common_lf.pack(fill="x")

        ttk.Label(common_lf, text=self._t("meta_artist")).pack(anchor="w", padx=5)
        self.artist_var = tk.StringVar()
        ttk.Entry(common_lf, textvariable=self.artist_var).pack(
            fill="x", padx=5, pady=(0, 6)
        )

        ttk.Label(common_lf, text=self._t("meta_album")).pack(anchor="w", padx=5)
        self.album_var = tk.StringVar()
        ttk.Entry(common_lf, textvariable=self.album_var).pack(
            fill="x", padx=5, pady=(0, 6)
        )

        ttk.Button(
            common_lf, text=self._t("meta_apply_all"), command=self._apply_common
        ).pack(fill="x", padx=5, pady=(0, 8))

        # --- 개별 파일 필드 (제목 / 트랙번호) ---
        per_file_lf = ttk.LabelFrame(right, text=self._t("meta_per_file"))
        per_file_lf.pack(fill="x", pady=(8, 0))

        ttk.Label(per_file_lf, text=self._t("meta_song_title")).pack(
            anchor="w", padx=5
        )
        self.title_var = tk.StringVar()
        ttk.Entry(per_file_lf, textvariable=self.title_var).pack(
            fill="x", padx=5, pady=(0, 6)
        )

        ttk.Label(per_file_lf, text=self._t("meta_track")).pack(anchor="w", padx=5)
        self.track_var = tk.StringVar()
        ttk.Entry(per_file_lf, textvariable=self.track_var).pack(
            fill="x", padx=5, pady=(0, 8)
        )

        # --- 버튼 ---
        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(
            btn_frame, text=self._t("meta_auto_fill"), command=self._auto_fill_all
        ).pack(fill="x", pady=2)
        ttk.Button(
            btn_frame, text=self._t("meta_save"), command=self._save_current
        ).pack(fill="x", pady=2)
        ttk.Button(
            btn_frame, text=self._t("meta_save_all"), command=self._save_all
        ).pack(fill="x", pady=2)
        ttk.Button(
            btn_frame, text=self._t("meta_close"), command=self._close
        ).pack(fill="x", pady=2)

        # 상태 표시
        self.status_label = ttk.Label(right, text="", foreground="green", wraplength=240)
        self.status_label.pack(anchor="w", pady=(10, 0))

    def _select_file(self, index):
        """파일 목록에서 특정 인덱스를 선택하고 편집 패널을 갱신한다."""
        if index < 0 or index >= len(self.files):
            return
        self._flush_current()
        self.current_index = index
        self.file_listbox.selection_clear(0, "end")
        self.file_listbox.selection_set(index)
        self.file_listbox.see(index)
        path = self.files[index]
        meta = self.file_meta[path]
        # 공통 필드: 첫 파일 선택 시에만 초기화 (이후에는 사용자 입력 유지)
        if self.artist_var.get() == "" and meta["artist"]:
            self.artist_var.set(meta["artist"])
        if self.album_var.get() == "" and meta["album"]:
            self.album_var.set(meta["album"])
        self.title_var.set(meta["title"])
        self.track_var.set(meta["track"])

    def _on_listbox_select(self, _event):
        sel = self.file_listbox.curselection()
        if sel:
            self._select_file(sel[0])

    def _flush_current(self):
        """현재 편집 중인 파일의 변경사항을 메모리에 반영한다."""
        if self.current_index is not None:
            path = self.files[self.current_index]
            self.file_meta[path] = {
                "artist": self.artist_var.get(),
                "album": self.album_var.get(),
                "title": self.title_var.get(),
                "track": self.track_var.get(),
            }

    @staticmethod
    def _parse_filename(path):
        """파일명에서 아티스트와 제목을 유추한다."""
        name = os.path.splitext(os.path.basename(path))[0]
        if " - " in name:
            artist, title = name.split(" - ", 1)
            return artist.strip(), title.strip()
        return "", name.strip()

    def _apply_common(self):
        """공통 필드(아티스트, 앨범)를 모든 파일에 일괄 적용."""
        artist = self.artist_var.get()
        album = self.album_var.get()
        for path in self.files:
            self.file_meta[path]["artist"] = artist
            self.file_meta[path]["album"] = album
        self.status_label.configure(
            text=self._t("meta_applied_common"), foreground="green"
        )

    def _auto_fill_all(self):
        """모든 파일에 파일명 유추 + 트랙번호 자동 부여."""
        self._flush_current()
        artist_common = self.artist_var.get()
        album_common = self.album_var.get()
        for i, path in enumerate(self.files):
            artist, title = self._parse_filename(path)
            # 공통 필드에 값이 있으면 그것을 우선 사용
            self.file_meta[path] = {
                "artist": artist_common if artist_common else artist,
                "album": album_common,
                "title": title,
                "track": str(i + 1),
            }
        # 현재 선택 파일 갱신
        if self.current_index is not None:
            self._select_file(self.current_index)
        self.status_label.configure(
            text=self._t("meta_auto_fill_done"), foreground="green"
        )

    def _save_tags(self, path, meta):
        """mutagen으로 메타데이터를 파일에 쓴다."""
        ext = os.path.splitext(path)[1].lower()
        if ext == ".mp3":
            audio = MP3(path)
            if audio.tags is None:
                audio.add_tags()
            audio.tags["TPE1"] = TPE1(encoding=3, text=meta["artist"])
            audio.tags["TALB"] = TALB(encoding=3, text=meta["album"])
            audio.tags["TIT2"] = TIT2(encoding=3, text=meta["title"])
            audio.tags["TRCK"] = TRCK(encoding=3, text=meta["track"])
            audio.save()
        elif ext == ".opus":
            audio = OggOpus(path)
            audio["artist"] = meta["artist"]
            audio["album"] = meta["album"]
            audio["title"] = meta["title"]
            audio["tracknumber"] = meta["track"]
            audio.save()
        elif ext == ".m4a":
            audio = MP4(path)
            if audio.tags is None:
                audio.add_tags()
            audio.tags["\xa9ART"] = [meta["artist"]]
            audio.tags["\xa9alb"] = [meta["album"]]
            audio.tags["\xa9nam"] = [meta["title"]]
            track_num = int(meta["track"]) if meta["track"].isdigit() else 0
            audio.tags["trkn"] = [(track_num, 0)]
            audio.save()

    def _save_current(self):
        """현재 선택된 파일의 메타데이터를 저장한다."""
        if self.current_index is None:
            return
        self._flush_current()
        path = self.files[self.current_index]
        meta = self.file_meta[path]
        try:
            self._save_tags(path, meta)
            name = os.path.basename(path)
            self.status_label.configure(
                text=self._t("meta_saved", name=name), foreground="green"
            )
        except Exception as e:
            self.status_label.configure(
                text=self._t("meta_save_error", error=e), foreground="red"
            )

    def _save_all(self):
        """모든 파일의 메타데이터를 저장한다."""
        self._flush_current()
        ok, fail = 0, 0
        for path in self.files:
            meta = self.file_meta[path]
            try:
                self._save_tags(path, meta)
                ok += 1
            except Exception:
                fail += 1
        msg = self._t("meta_save_all_done", ok=ok)
        color = "green"
        if fail:
            msg += self._t("meta_save_all_fail", fail=fail)
            color = "orange"
        self.status_label.configure(text=msg, foreground=color)

    def _close(self):
        self.win.grab_release()
        self.win.destroy()


class PlaylistWindow:
    """재생목록 미리보기 및 선택 다운로드 서브 윈도우."""

    def __init__(self, parent, title, entries, callback, lang="ko"):
        self.callback = callback
        self.entries = entries
        self.lang = lang

        self.win = tk.Toplevel(parent)
        self.win.title(self._t("playlist_title"))
        self.win.geometry("560x460")
        self.win.resizable(False, True)
        self.win.grab_set()
        self.win.transient(parent)

        # 상단: 재생목록 제목 + 영상 수
        header = ttk.Frame(self.win)
        header.pack(fill="x", padx=10, pady=(10, 5))
        ttk.Label(header, text=title, font=("", 11, "bold")).pack(anchor="w")
        ttk.Label(
            header, text=self._t("playlist_total", count=len(entries))
        ).pack(anchor="w")

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
            label = f"{i + 1}. {entry.get('title', self._t('playlist_unknown'))}"
            if dur:
                label += f"  ({dur})"
            ttk.Checkbutton(self.inner, text=label, variable=var).pack(
                anchor="w", padx=5, pady=1
            )

        # 하단 버튼
        btn_frame = ttk.Frame(self.win)
        btn_frame.pack(fill="x", padx=10, pady=(5, 10))

        ttk.Button(
            btn_frame, text=self._t("playlist_select_all"), command=self._select_all
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            btn_frame,
            text=self._t("playlist_deselect_all"),
            command=self._deselect_all,
        ).pack(side="left", padx=(0, 5))
        ttk.Button(
            btn_frame, text=self._t("playlist_cancel"), command=self._on_cancel
        ).pack(side="right", padx=(5, 0))
        ttk.Button(
            btn_frame, text=self._t("playlist_download"), command=self._on_download
        ).pack(side="right", padx=(5, 0))

    def _t(self, key, **kwargs):
        s = STRINGS[self.lang][key]
        return s.format(**kwargs) if kwargs else s

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
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".yt-mp3")
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

    def __init__(self, root):
        self.root = root

        self.downloading = False
        self._log_lines = []

        self.formats = {
            "opus": {"codec": "opus", "ext": "opus"},
            "mp3":  {"codec": "mp3",  "ext": "mp3"},
            "aac":  {"codec": "aac",  "ext": "m4a"},
        }

        config = self._load_config()

        # Language
        self.lang = config.get("language", "ko")
        if self.lang not in STRINGS:
            self.lang = "ko"

        self.root.title(self._t("window_title"))
        self.root.geometry("620x640")
        self.root.resizable(False, False)

        default_path = os.path.join(os.path.expanduser("~"), "Music", "yt-mp3")
        self.save_path = tk.StringVar(value=config.get("save_path", default_path))
        self.ffmpeg_path = tk.StringVar(value=config.get("ffmpeg_path", ""))

        # Migrate legacy Korean format key to internal key
        saved_format = config.get("audio_format", "opus")
        if saved_format in _LEGACY_FORMAT_MAP:
            saved_format = _LEGACY_FORMAT_MAP[saved_format]
        if saved_format not in self.formats:
            saved_format = "opus"
        self.selected_format = tk.StringVar(value=saved_format)

        self._build_ui()
        self._check_ffmpeg_on_startup()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _t(self, key, **kwargs):
        s = STRINGS[self.lang][key]
        return s.format(**kwargs) if kwargs else s

    def _load_config(self):
        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def _save_config(self):
        config = {
            "save_path": self.save_path.get(),
            "ffmpeg_path": self.ffmpeg_path.get(),
            "audio_format": self.selected_format.get(),
            "language": self.lang,
        }
        os.makedirs(self.CONFIG_DIR, exist_ok=True)
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def _on_close(self):
        self._save_config()
        self.root.destroy()

    def _check_ffmpeg_on_startup(self):
        ffmpeg_loc = shutil.which("ffmpeg")
        if ffmpeg_loc:
            ffmpeg_dir = os.path.dirname(ffmpeg_loc)
            if not self.ffmpeg_path.get():
                self.ffmpeg_path.set(ffmpeg_dir)
            self.ffmpeg_status.configure(
                text=self._t("ffmpeg_auto"), foreground="green"
            )
        else:
            if sys.platform == "win32":
                hint = self._t("ffmpeg_missing_win")
            elif sys.platform == "darwin":
                hint = self._t("ffmpeg_missing_mac")
            else:
                hint = self._t("ffmpeg_missing_linux")
            self.ffmpeg_status.configure(text=hint, foreground="red")

    def _format_display_names(self):
        """Return ordered list of (internal_key, display_name) pairs."""
        return [
            ("opus", self._t("format_opus")),
            ("mp3", self._t("format_mp3")),
            ("aac", self._t("format_aac")),
        ]

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        # --- 언어 선택 ---
        lang_frame = ttk.LabelFrame(self.root, text=self._t("language_label"))
        lang_frame.pack(fill="x", **pad)

        lang_names = [_LANG_NAMES[k] for k in ("ko", "en")]
        self.lang_var = tk.StringVar(value=_LANG_NAMES[self.lang])
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=lang_names,
            state="readonly",
            width=15,
        )
        lang_combo.pack(side="left", padx=10, pady=8)
        lang_combo.bind("<<ComboboxSelected>>", self._on_language_change)

        # --- URL 입력 ---
        url_frame = ttk.LabelFrame(self.root, text=self._t("url_label"))
        url_frame.pack(fill="x", **pad)

        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=8)

        ttk.Button(url_frame, text=self._t("paste"), command=self._paste_url).pack(
            side="right", padx=(0, 10), pady=8
        )

        # --- 저장 경로 ---
        path_frame = ttk.LabelFrame(self.root, text=self._t("save_path_label"))
        path_frame.pack(fill="x", **pad)

        ttk.Entry(path_frame, textvariable=self.save_path).pack(
            side="left", fill="x", expand=True, padx=(10, 5), pady=8
        )

        ttk.Button(path_frame, text=self._t("browse"), command=self._browse_path).pack(
            side="right", padx=(0, 10), pady=8
        )

        # --- ffmpeg 경로 ---
        ffmpeg_frame = ttk.LabelFrame(
            self.root, text=self._t("ffmpeg_path_label")
        )
        ffmpeg_frame.pack(fill="x", **pad)

        ffmpeg_input = ttk.Frame(ffmpeg_frame)
        ffmpeg_input.pack(fill="x")

        ttk.Entry(ffmpeg_input, textvariable=self.ffmpeg_path).pack(
            side="left", fill="x", expand=True, padx=(10, 5), pady=8
        )

        ttk.Button(
            ffmpeg_input, text=self._t("browse"), command=self._browse_ffmpeg
        ).pack(side="right", padx=(0, 10), pady=8)

        self.ffmpeg_status = ttk.Label(ffmpeg_frame, text="", font=("", 8))
        self.ffmpeg_status.pack(anchor="w", padx=10, pady=(0, 5))

        # --- 오디오 포맷 ---
        fmt_frame = ttk.LabelFrame(self.root, text=self._t("audio_format_label"))
        fmt_frame.pack(fill="x", **pad)

        self._fmt_pairs = self._format_display_names()
        fmt_display = [name for _, name in self._fmt_pairs]
        # Find display name for current selection
        current_display = fmt_display[0]
        for key, name in self._fmt_pairs:
            if key == self.selected_format.get():
                current_display = name
                break
        self._fmt_display_var = tk.StringVar(value=current_display)

        fmt_combo = ttk.Combobox(
            fmt_frame,
            textvariable=self._fmt_display_var,
            values=fmt_display,
            state="readonly",
            width=30,
        )
        fmt_combo.pack(side="left", padx=10, pady=8)

        self.fmt_desc = ttk.Label(
            fmt_frame, text=self._t("format_desc_opus")
        )
        self.fmt_desc.pack(side="left", padx=5, pady=8)
        fmt_combo.bind("<<ComboboxSelected>>", self._on_format_change)
        # Set initial description
        self._on_format_change()

        # --- 버튼 영역 ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", **pad)

        self.download_btn = ttk.Button(
            btn_frame, text=self._t("download"), command=self._start_download
        )
        self.download_btn.pack(side="left", expand=True)

        ttk.Button(
            btn_frame, text=self._t("open_folder"), command=self._open_folder
        ).pack(side="left", expand=True)

        ttk.Button(
            btn_frame, text=self._t("edit_metadata"), command=self._open_metadata_window
        ).pack(side="left", expand=True)

        # --- 프로그레스 바 ---
        prog_frame = ttk.LabelFrame(self.root, text=self._t("progress_label"))
        prog_frame.pack(fill="x", **pad)

        # 전체 진행 (여러 곡일 때만 표시, 초기에는 숨김)
        self.overall_frame = ttk.Frame(prog_frame)
        # pack 하지 않음 — _show_overall(True) 시 표시

        self.overall_label = ttk.Label(
            self.overall_frame, text=self._t("overall_label", current=0, total=0)
        )
        self.overall_label.pack(side="left", padx=(10, 5))
        self.overall_progress = ttk.Progressbar(
            self.overall_frame, mode="determinate"
        )
        self.overall_progress.pack(
            side="left", fill="x", expand=True, padx=(0, 10), pady=4
        )

        # 개별 파일 진행
        self.file_frame = ttk.Frame(prog_frame)
        self.file_frame.pack(fill="x", pady=(0, 4))

        self.file_label = ttk.Label(self.file_frame, text=self._t("current_file"))
        self.file_label.pack(side="left", padx=(10, 5))
        self.progress = ttk.Progressbar(self.file_frame, mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=4)

        # --- 로그 ---
        log_frame = ttk.LabelFrame(self.root, text=self._t("log_label"))
        log_frame.pack(fill="both", expand=True, **pad)

        self.log_text = tk.Text(log_frame, height=12, state="disabled", wrap="word")
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    # ---- helpers ----

    def _on_language_change(self, _event=None):
        name_to_code = {v: k for k, v in _LANG_NAMES.items()}
        new_lang = name_to_code.get(self.lang_var.get(), "ko")
        if new_lang != self.lang:
            self.lang = new_lang
            self._save_config()
            messagebox.showinfo(
                self._t("lang_restart_title"),
                self._t("lang_restart_msg"),
            )

    def _on_format_change(self, _event=None):
        # Map display name back to internal key
        display = self._fmt_display_var.get()
        for key, name in self._fmt_pairs:
            if name == display:
                self.selected_format.set(key)
                break
        desc_keys = {
            "opus": "format_desc_opus",
            "mp3": "format_desc_mp3",
            "aac": "format_desc_aac",
        }
        desc_key = desc_keys.get(self.selected_format.get(), "format_desc_opus")
        self.fmt_desc.configure(text=self._t(desc_key))

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

    def _open_metadata_window(self):
        scan_dir = self.save_path.get().strip()
        if not scan_dir or not os.path.isdir(scan_dir):
            messagebox.showwarning(
                self._t("warn_no_dir_title"), self._t("warn_no_dir")
            )
            return
        MetadataWindow(self.root, scan_dir, lang=self.lang)

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
            self.root.after(0, self._log, self._t("log_saved", path=log_path))
        except OSError:
            pass

    # ---- download ----

    def _start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning(
                self._t("warn_no_url_title"), self._t("warn_no_url")
            )
            return

        dest = self.save_path.get().strip()
        if not dest:
            messagebox.showwarning(
                self._t("warn_no_path_title"), self._t("warn_no_path")
            )
            return

        os.makedirs(dest, exist_ok=True)

        fmt = self.formats[self.selected_format.get()]
        if fmt["codec"] != "opus" and self._find_ffmpeg() is None:
            messagebox.showwarning(
                self._t("warn_ffmpeg_title"),
                self._t("warn_ffmpeg"),
            )
            return

        self._log_lines.clear()
        self.download_btn.configure(state="disabled")
        self._set_progress(0)
        self.progress.configure(mode="indeterminate")
        self.progress.start(15)
        self._log(self._t("fetching_playlist"))

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
            self.root.after(
                0, self._log, self._t("error_extract", error=e)
            )
            self.root.after(
                0,
                lambda: messagebox.showerror(self._t("error_title"), str(e)),
            )
            self.root.after(0, self._stop_indeterminate)
            return

        entries = info.get("entries")
        if entries is not None:
            entries = [e for e in entries if e is not None]

        if entries:
            # 재생목록 → 서브 윈도우
            playlist_title = info.get("title", self._t("playlist_title"))

            def show_playlist():
                self._stop_indeterminate()
                self._log(
                    self._t(
                        "playlist_detected",
                        title=playlist_title,
                        count=len(entries),
                    )
                )

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

                PlaylistWindow(
                    self.root, playlist_title, entries, on_selected, lang=self.lang
                )

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
            self.root.after(
                0, self._log, self._t("converting", filename=filename)
            )

    def _show_overall(self, show):
        if show:
            self.overall_frame.pack(fill="x", pady=(4, 0), before=self.file_frame)
        else:
            self.overall_frame.pack_forget()

    def _update_overall(self, current, total):
        self.overall_label.configure(
            text=self._t("overall_label", current=current, total=total)
        )
        self.overall_progress["value"] = current / total * 100 if total else 0

    def _download(self, urls, dest, fmt, ffmpeg_loc):
        metadata_pps = [
            {"key": "FFmpegThumbnailsConvertor", "format": "png"},
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

        total = len(urls)
        is_multi = total > 1

        if is_multi:
            self.root.after(0, self._show_overall, True)
            self.root.after(0, self._update_overall, 0, total)

        try:
            self.root.after(
                0, self._log, self._t("download_start", count=total)
            )
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for i, url in enumerate(urls):
                    self.root.after(0, self._set_progress, 0)
                    if is_multi:
                        self.root.after(
                            0, self._log, f"--- ({i + 1}/{total}) ---"
                        )
                    ydl.download([url])
                    if is_multi:
                        self.root.after(
                            0, self._update_overall, i + 1, total
                        )
            self.root.after(0, self._log, self._t("download_done"))
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    self._t("done_title"), self._t("done_msg")
                ),
            )
        except Exception as e:
            self.root.after(
                0, self._log, self._t("error_download", error=e)
            )
            self.root.after(
                0,
                lambda: messagebox.showerror(self._t("error_title"), str(e)),
            )
        finally:
            self._save_log(dest)
            self.downloading = False
            self.root.after(0, lambda: self.download_btn.configure(state="normal"))
            if is_multi:
                self.root.after(0, self._show_overall, False)


if __name__ == "__main__":
    root = tk.Tk()
    YtMp3App(root)
    root.mainloop()
