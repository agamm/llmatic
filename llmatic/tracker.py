import json
import time
import traceback
import sqlite3
from decimal import Decimal
from pathlib import Path
from tokencost import calculate_prompt_cost, calculate_completion_cost, count_string_tokens
from .db import init_db, DB_PATH

init_db()  # Ensure the database is initialized

class Track:
    def __init__(self, project_id: str, id: str):
        self.project_id = project_id
        self.id = id
        self.start_time = time.time()
        self.input = None
        self.output = None
        self.eval_results = []
        self.model = None
        self.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
        
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
            self.file_func = f"{relative_path.with_suffix('')}_{caller.name}".replace("/", "_").replace("\\", "_")
        else:
            self.file_func = "unknown"

    def end(self, model: str, prompt: str, response):
        self.end_time = time.time()
        self.execution_time_ms = int((self.end_time - self.start_time) * 1000)
        self.input = prompt
        self.output = response
        self.model = model

        # Calculate token costs and count
        prompt_cost = calculate_prompt_cost(prompt, model)
        completion_cost = calculate_completion_cost(response["choices"][0]["text"], model)
        prompt_tokens = count_string_tokens(prompt, model)
        completion_tokens = count_string_tokens(response["choices"][0]["text"], model)

        self.cost = {
            "prompt_cost": float(prompt_cost),
            "completion_cost": float(completion_cost),
            "total_cost": float(prompt_cost + completion_cost),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }

        self._save_initial()

    def _save_initial(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trackings (
                project_id, tracking_id, execution_time_ms, input, output, eval_results, created_at, model,
                prompt_cost, completion_cost, total_cost, prompt_tokens, completion_tokens, total_tokens, file_func
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.project_id, self.id, self.execution_time_ms, self.input, json.dumps(self.output), json.dumps(self.eval_results),
            self.created_at, self.model,
            self.cost["prompt_cost"], self.cost["completion_cost"], self.cost["total_cost"],
            self.cost["prompt_tokens"], self.cost["completion_tokens"], self.cost["total_tokens"], self.file_func
        ))
        conn.commit()
        conn.close()

    def _save_eval(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE trackings SET
                eval_results = ?
            WHERE project_id = ? AND tracking_id = ? AND created_at = ?
        ''', (
            json.dumps(self.eval_results), self.project_id, self.id, self.created_at
        ))
        conn.commit()
        conn.close()

    def eval(self, description: str, scale: tuple, model: str = None, eval_function=None, log_only: bool = False, dev_mode: bool = False):
        if dev_mode:
            return
        
        score = 0
        if eval_function:
            score = eval_function(self.output)
        else:
            # Mock LLM evaluation (use actual LLM call here in the future)
            score = self.mock_llm_evaluation(description, self.output, model)

        scaled_score = (score / scale[1]) * 10  # Scale the score to be out of 10

        self.eval_results.append({
            "description": description,
            "score": scaled_score,
            "scale": scale,
            "log_only": log_only,
            "model": model
        })
        self._save_eval()

    def mock_llm_evaluation(self, description, response, model):
        # Mock evaluation logic based on the model
        # Here you can add logic to return different scores based on the model if needed
        return 7  # Mock score

def get_response(response):
    return response["choices"][0]["text"].strip()
