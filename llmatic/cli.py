import click
import json
import sqlite3
from pathlib import Path
from .db import init_db, DB_PATH

init_db()  # Ensure the database is initialized

@click.group()
def main():
    pass

@main.command()
def list():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT project_id FROM trackings')
    projects = cursor.fetchall()
    conn.close()
    if projects:
        for project in projects:
            print(project['project_id'])
    else:
        print("No trackings found.")

@main.command()
@click.argument("project_id")
@click.argument("tracking_id")
def show(project_id, tracking_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM trackings WHERE project_id = ? AND tracking_id = ?
        ORDER BY created_at DESC LIMIT 1
    ''', (project_id, tracking_id))
    tracking = cursor.fetchone()
    conn.close()
    if tracking:
        format_output(tracking)
    else:
        print(f"No tracking found for project: {project_id} with id: {tracking_id}")

@main.command()
@click.argument("project_id")
def remove(project_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM trackings WHERE project_id = ?', (project_id,))
    conn.commit()
    conn.close()
    print(f"Removed all tracking files for project: {project_id}")

@main.command()
@click.argument("project_id")
def summary(project_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM trackings WHERE project_id = ? ORDER BY created_at ASC
    ''', (project_id,))
    trackings = cursor.fetchall()
    conn.close()
    if trackings:
        print(f"Run summary for project: {project_id}")
        print(click.style("-" * 60, fg="yellow"))
        for tracking in trackings:
            tracking_id = tracking['tracking_id']
            model = tracking['model']
            exec_time = tracking['execution_time_ms'] / 1000
            total_cost = tracking['total_cost']
            file_func = tracking['file_func']
            print(f"{tracking_id} - [{model}], {exec_time:.2f}s, ${total_cost:.6f}, {file_func}")
    else:
        print(f"No trackings found for project: {project_id}")

def format_output(tracking):
    exec_time_color = "red" if tracking["execution_time_ms"] > 500 else "green"
    
    prompt_cost = float(tracking["prompt_cost"])
    completion_cost = float(tracking["completion_cost"])
    
    print(click.style(f"LLM Tracking Results for: {tracking['tracking_id']}", fg="cyan"))
    print(click.style("-" * 60, fg="yellow"))
    print(f"Tracking ID: {click.style(tracking['tracking_id'], fg='red')}")
    print(f"Model: {click.style(tracking['model'], fg='yellow')}")
    print(f"File and Function: {click.style(tracking['file_func'], fg='blue')}")
    prompt_text = f"\"{tracking['input']}\""
    print(f"Prompt: {click.style(prompt_text, fg='yellow')} (Cost: ${prompt_cost:.6f})")
    execution_time = tracking["execution_time_ms"]
    print(f"Execution Time: {click.style(f'{execution_time} ms', fg=exec_time_color)}")
    print("Total Cost: ${:.6f}".format(float(tracking["total_cost"])))
    print(f"Tokens: {tracking['total_tokens']} (Prompt: {tracking['prompt_tokens']}, Completion: {tracking['completion_tokens']})")
    print(f"Created At: {click.style(tracking['created_at'], fg='yellow')}")
    print()
    print(click.style("Evaluation Results:", fg="cyan"))
    print(click.style("-" * 60, fg="yellow"))
    eval_results = json.loads(tracking["eval_results"])
    for eval in eval_results:
        description = eval["description"]
        score = eval["score"]
        model = eval["model"]
        print(f"{description} (Model: {model}): {click.style(f'{score:.2f}', fg='green')}")
    print()
    print(click.style("Generated Text:", fg="cyan"))
    print(click.style("-" * 60, fg="yellow"))
    output = json.loads(tracking["output"])
    print(click.style(output["choices"][0]["text"], fg="green") + f" (Cost: ${completion_cost:.6f})")

if __name__ == "__main__":
    main()
