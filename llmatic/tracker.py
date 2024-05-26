import json
import time
import traceback
from pathlib import Path

class Track:
    def __init__(self, id: str):
        self.id = id
        self.start_time = time.time()
        self.input = None
        self.output = None
        self.eval_results = {}
        
        # Get the caller's file and function name from the call stack
        stack = traceback.extract_stack()
        caller = None
        for frame in reversed(stack):
            if "tracker.py" not in frame.filename:
                caller = frame
                break

        if caller:
            # Get the relative path from the project root
            relative_path = Path(caller.filename).relative_to(Path.cwd())
            file_func = f"{relative_path.with_suffix('')}_{caller.name}".replace("/", "_").replace("\\", "_")
        else:
            file_func = "unknown"

        time_str = time.strftime("%Y%m%d-%H%M%S")
        self.save_path = Path.home() / ".llmatic" / self.id / time_str
        self.save_file = self.save_path / f"{file_func}.json"
        self.save_path.mkdir(parents=True, exist_ok=True)
        self.model = None

    def end(self, model: str, prompt: str, response):
        self.end_time = time.time()
        self.execution_time_ms = int((self.end_time - self.start_time) * 1000)
        self.input = prompt
        self.output = response
        self.model = model
        self._save()

    def _save(self):
        data = {
            "id": self.id,
            "execution_time_ms": self.execution_time_ms,
            "input": self.input,
            "output": self.output,
            "eval_results": self.eval_results,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "file_path": str(self.save_file),
            "model": self.model
        }
        with open(self.save_file, "w") as f:
            json.dump(data, f, indent=4)

    def eval(self, description: str, scale: tuple, model: str = None, log_only: bool = False, dev_mode: bool = False):
        if dev_mode:
            return
        self.eval_results[description] = {
            "scale": scale,
            "model": model,
            "log_only": log_only
        }
        self._save()

def get_response(response):
    return response["choices"][0]["text"].strip()
