import json
import os


class ProgressManager:
    def __init__(self, data_dir: str = "data"):
        self._data_dir = data_dir
        self._filepath = os.path.join(data_dir, "progress.json")
        self._progress: dict[str, bool] = {}
        self._load()

    def _load(self) -> None:
        if not os.path.isfile(self._filepath):
            self._progress = {}
            return
        try:
            with open(self._filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self._progress = data
            else:
                self._progress = {}
        except (json.JSONDecodeError, OSError):
            self._progress = {}

    def _save(self) -> None:
        os.makedirs(self._data_dir, exist_ok=True)
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(self._progress, f, indent=2, ensure_ascii=False)

    def mark_complete(self, lesson_name: str) -> None:
        self._progress[lesson_name] = True
        self._save()

    def is_complete(self, lesson_name: str) -> bool:
        return self._progress.get(lesson_name, False)

    def get_all_progress(self) -> dict[str, bool]:
        return dict(self._progress)

    def reset_progress(self) -> None:
        self._progress = {}
        self._save()

    def get_stats(self) -> dict:
        total = len(self._progress)
        done = sum(1 for v in self._progress.values() if v)
        percent = round((done / total * 100) if total > 0 else 0)
        return {"total": total, "done": done, "percent": percent}