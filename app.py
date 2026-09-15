from __future__ import annotations

import hashlib
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_NAME = "ZIP Extractor with Path Fix"
DEFAULT_MAX_PATH = 220
INVALID_WINDOWS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
RESERVED_WINDOWS = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


@dataclass
class ExtractOptions:
    output_root: Path
    max_path: int = DEFAULT_MAX_PATH
    overwrite: bool = False
    preserve_timestamps: bool = True


class Cancelled(Exception):
    pass


def clean_component(name: str, max_component: int = 80) -> str:
    """Return a filesystem-safe component while preserving useful identity."""
    name = INVALID_WINDOWS.sub("_", name).strip().rstrip(". ")
    if not name:
        name = "unnamed"
    stem, suffix = os.path.splitext(name)
    if stem.upper() in RESERVED_WINDOWS:
        stem = "_" + stem
    name = stem + suffix
    if len(name) <= max_component:
        return name
    digest = hashlib.sha1(name.encode("utf-8", "replace")).hexdigest()[:8]
    room = max(8, max_component - len(suffix) - len(digest) - 2)
    return f"{stem[:room]}__{digest}{suffix}"


def safe_member_parts(member_name: str) -> list[str]:
    """Normalize ZIP paths and reject absolute/traversal entries (Zip Slip)."""
    normalized = member_name.replace("\\", "/")
    pure = PurePosixPath(normalized)
    parts = []
    for part in pure.parts:
        if part in ("", ".", "/"):
            continue
        if part == "..":
            raise ValueError("Unsafe parent path '..'")
        if len(part) >= 2 and part[1] == ":":
            raise ValueError("Unsafe drive-qualified path")
        parts.append(clean_component(part))
    return parts


def fit_path(root: Path, parts: list[str], max_path: int) -> Path:
    """Shorten only as much as needed, adding hashes to avoid collisions."""
    candidate = root.joinpath(*parts)
    if len(str(candidate)) <= max_path:
        return candidate
    adjusted = list(parts)
    # Repeatedly shorten the longest component.
    while len(str(root.joinpath(*adjusted))) > max_path:
        indices = [i for i, value in enumerate(adjusted) if len(value) > 16]
        if not indices:
            break
        i = max(indices, key=lambda n: len(adjusted[n]))
        current = adjusted[i]
        stem, suffix = os.path.splitext(current)
        digest = hashlib.sha1(current.encode("utf-8", "replace")).hexdigest()[:8]
        reduce_by = max(8, len(str(root.joinpath(*adjusted))) - max_path + 4)
        target = max(12, len(current) - reduce_by)
        room = max(3, target - len(suffix) - len(digest) - 2)
        adjusted[i] = f"{stem[:room]}__{digest}{suffix}"
    result = root.joinpath(*adjusted)
    if len(str(result)) > max_path:
        raise OSError(f"Cannot fit path under {max_path} characters: {result}")
    return result


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    for i in range(1, 10000):
        candidate = path.with_name(f"{stem} ({i}){suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(f"Too many name collisions for {path.name}")


def open_in_file_manager(path: Path) -> None:
    path = path.resolve()
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


def extract_one(zip_path: Path, options: ExtractOptions, emit, progress, cancelled) -> tuple[int, int, int]:
    dest_name = clean_component(zip_path.stem)
    destination = options.output_root / dest_name
    if destination.exists() and not options.overwrite:
        destination = unique_path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    extracted = renamed = skipped = 0
    with zipfile.ZipFile(zip_path, "r") as archive:
        members = archive.infolist()
        for index, info in enumerate(members, 1):
            if cancelled():
                raise Cancelled()
            try:
                parts = safe_member_parts(info.filename)
                if not parts:
                    progress(index, len(members))
                    continue
                target = fit_path(destination, parts, options.max_path)
                original_target = destination.joinpath(*parts)
                if target != original_target:
                    renamed += 1
                    emit(f"RENAMED: {info.filename} -> {target.relative_to(destination)}")
                if info.is_dir() or info.filename.endswith("/"):
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if target.exists() and not options.overwrite:
                        target = unique_path(target)
                        renamed += 1
                    with archive.open(info, "r") as source, open(target, "wb") as output:
                        shutil.copyfileobj(source, output, length=1024 * 1024)
                    if options.preserve_timestamps:
                        try:
                            stamp = time.mktime((*info.date_time, 0, 0, -1))
                            os.utime(target, (stamp, stamp))
                        except (OSError, ValueError, OverflowError):
                            pass
                    extracted += 1
            except (OSError, ValueError, RuntimeError, zipfile.BadZipFile) as exc:
                skipped += 1
                emit(f"SKIPPED: {info.filename} | {exc}")
            progress(index, max(1, len(members)))
    return extracted, renamed, skipped


class ZipExtractorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("900x680")
        self.minsize(760, 560)
        self.files: list[Path] = []
        self.events: queue.Queue = queue.Queue()
        self.cancel_event = threading.Event()
        self.worker: threading.Thread | None = None
        self._build_style()
        self._build_ui()
        self.after(100, self._drain_events)

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("vista" if sys.platform.startswith("win") else "clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Sub.TLabel", foreground="#52606d")
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        outer = ttk.Frame(self, padding=18)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text=APP_NAME, style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="Batch extract ZIP files safely, fixing long and invalid paths along the way.", style="Sub.TLabel").pack(anchor="w", pady=(2, 14))

        source = ttk.LabelFrame(outer, text="1. ZIP files", padding=10)
        source.pack(fill="both", expand=False)
        toolbar = ttk.Frame(source)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Button(toolbar, text="Add ZIP files", command=self.add_files).pack(side="left")
        ttk.Button(toolbar, text="Add folder", command=self.add_folder).pack(side="left", padx=6)
        ttk.Button(toolbar, text="Remove selected", command=self.remove_selected).pack(side="left")
        ttk.Button(toolbar, text="Clear", command=self.clear_files).pack(side="left", padx=6)
        self.file_list = tk.Listbox(source, height=7, selectmode="extended", font=("Segoe UI", 9))
        self.file_list.pack(fill="both", expand=True)

        settings = ttk.LabelFrame(outer, text="2. Destination and settings", padding=10)
        settings.pack(fill="x", pady=12)
        self.output_var = tk.StringVar(value=str(Path.home() / "Extracted ZIPs"))
        ttk.Label(settings, text="Output folder").grid(row=0, column=0, sticky="w")
        ttk.Entry(settings, textvariable=self.output_var).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(settings, text="Browse", command=self.choose_output).grid(row=0, column=2)
        self.max_path_var = tk.IntVar(value=DEFAULT_MAX_PATH)
        ttk.Label(settings, text="Maximum path length").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Spinbox(settings, from_=80, to=1000, textvariable=self.max_path_var, width=8).grid(row=1, column=1, sticky="w", padx=8, pady=(10, 0))
        self.overwrite_var = tk.BooleanVar(value=False)
        self.timestamps_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings, text="Overwrite existing files", variable=self.overwrite_var).grid(row=2, column=1, sticky="w", padx=8, pady=(8, 0))
        ttk.Checkbutton(settings, text="Preserve file timestamps", variable=self.timestamps_var).grid(row=3, column=1, sticky="w", padx=8)
        settings.columnconfigure(1, weight=1)

        actions = ttk.Frame(outer)
        actions.pack(fill="x")
        self.extract_btn = ttk.Button(actions, text="Extract all", style="Accent.TButton", command=self.start)
        self.extract_btn.pack(side="left")
        self.cancel_btn = ttk.Button(actions, text="Cancel", command=self.cancel, state="disabled")
        self.cancel_btn.pack(side="left", padx=6)
        ttk.Button(actions, text="Open output folder", command=self.open_output).pack(side="left")
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(actions, textvariable=self.status_var).pack(side="right")
        self.progress = ttk.Progressbar(outer, mode="determinate")
        self.progress.pack(fill="x", pady=(10, 8))

        log_frame = ttk.LabelFrame(outer, text="Activity log", padding=8)
        log_frame.pack(fill="both", expand=True)
        self.log = tk.Text(log_frame, height=10, wrap="word", state="disabled", font=("Consolas", 9))
        scroll = ttk.Scrollbar(log_frame, command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        self.log.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def add_files(self):
        names = filedialog.askopenfilenames(title="Select ZIP files", filetypes=[("ZIP archives", "*.zip"), ("All files", "*.*")])
        self._add_paths(Path(n) for n in names)

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select folder containing ZIP files")
        if folder:
            self._add_paths(sorted(Path(folder).glob("*.zip")))

    def _add_paths(self, paths):
        known = {p.resolve() for p in self.files}
        for path in paths:
            if path.is_file() and path.suffix.lower() == ".zip" and path.resolve() not in known:
                self.files.append(path)
                known.add(path.resolve())
        self._refresh_list()

    def _refresh_list(self):
        self.file_list.delete(0, "end")
        for path in self.files:
            self.file_list.insert("end", str(path))
        self.status_var.set(f"{len(self.files)} archive(s) selected")

    def remove_selected(self):
        selected = set(self.file_list.curselection())
        self.files = [p for i, p in enumerate(self.files) if i not in selected]
        self._refresh_list()

    def clear_files(self):
        self.files.clear()
        self._refresh_list()

    def choose_output(self):
        folder = filedialog.askdirectory(title="Choose output folder")
        if folder:
            self.output_var.set(folder)

    def open_output(self):
        path = Path(self.output_var.get()).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        try:
            open_in_file_manager(path)
        except OSError as exc:
            messagebox.showerror(APP_NAME, str(exc))

    def start(self):
        if not self.files:
            messagebox.showwarning(APP_NAME, "Add at least one ZIP file first.")
            return
        try:
            max_path = int(self.max_path_var.get())
            if max_path < 80:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showerror(APP_NAME, "Maximum path length must be a number of at least 80.")
            return
        output = Path(self.output_var.get()).expanduser()
        try:
            output.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror(APP_NAME, f"Cannot create output folder:\n{exc}")
            return
        options = ExtractOptions(output, max_path, self.overwrite_var.get(), self.timestamps_var.get())
        self.cancel_event.clear()
        self.extract_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.progress["value"] = 0
        self._write_log("Starting extraction...")
        self.worker = threading.Thread(target=self._run_worker, args=(list(self.files), options), daemon=True)
        self.worker.start()

    def cancel(self):
        self.cancel_event.set()
        self.status_var.set("Cancelling...")

    def _run_worker(self, files: list[Path], options: ExtractOptions):
        totals = [0, 0, 0]
        try:
            for file_index, archive in enumerate(files, 1):
                if self.cancel_event.is_set():
                    raise Cancelled()
                self.events.put(("log", f"\n[{file_index}/{len(files)}] {archive.name}"))
                self.events.put(("status", f"Extracting {archive.name}"))
                def progress(member_index, member_total):
                    overall = ((file_index - 1) + member_index / member_total) / len(files) * 100
                    self.events.put(("progress", overall))
                result = extract_one(archive, options, lambda text: self.events.put(("log", text)), progress, self.cancel_event.is_set)
                totals = [a + b for a, b in zip(totals, result)]
                self.events.put(("log", f"DONE: {result[0]} extracted, {result[1]} renamed, {result[2]} skipped"))
            self.events.put(("complete", tuple(totals)))
        except Cancelled:
            self.events.put(("cancelled", None))
        except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile) as exc:
            self.events.put(("error", str(exc)))

    def _drain_events(self):
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "log": self._write_log(payload)
                elif kind == "status": self.status_var.set(payload)
                elif kind == "progress": self.progress["value"] = payload
                elif kind == "complete":
                    self._set_idle()
                    e, r, s = payload
                    self.progress["value"] = 100
                    self.status_var.set(f"Complete: {e} extracted, {r} renamed, {s} skipped")
                    self._write_log(f"\nCOMPLETE: {e} extracted, {r} renamed, {s} skipped")
                    messagebox.showinfo(APP_NAME, f"Extraction complete.\n\nExtracted: {e}\nRenamed: {r}\nSkipped: {s}")
                elif kind == "cancelled":
                    self._set_idle(); self.status_var.set("Cancelled"); self._write_log("\nCANCELLED by user")
                elif kind == "error":
                    self._set_idle(); self.status_var.set("Error"); self._write_log(f"ERROR: {payload}"); messagebox.showerror(APP_NAME, payload)
        except queue.Empty:
            pass
        self.after(100, self._drain_events)

    def _set_idle(self):
        self.extract_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")

    def _write_log(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")


if __name__ == "__main__":
    ZipExtractorApp().mainloop()
