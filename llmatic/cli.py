import click
import json
from pathlib import Path
import shutil
import os

@click.group()
def main():
    pass

@main.command()
def list():
    output_dir = Path.home() / ".llmatic"
    if output_dir.exists():
        for item in output_dir.iterdir():
            if item.is_dir():
                print(item.name)
    else:
        print("No trackings found.")

@main.command()
@click.argument("id")
def show(id):
    output_dir = Path.home() / ".llmatic" / id
    if not output_dir.exists():
        print(f"No tracking found for id: {id}")
        return
    
    # Get the latest directory by datetime
    subdirs = [d for d in output_dir.iterdir() if d.is_dir()]
    if not subdirs:
        print(f"No tracking found for id: {id}")
        return

    # Get the latest subdirectory based on modification time
    latest_subdir = max(subdirs, key=lambda d: d.stat().st_mtime)
    
    # Debug print
    print(f"Latest subdir: {latest_subdir}")

    # Find the first JSON file in the latest subdir
    json_file = next(latest_subdir.glob("*.json"), None)
    if json_file:
        with json_file.open() as f:
            tracking_data = json.load(f)
            format_output(tracking_data, json_file)
    else:
        print(f"No tracking found for id: {id}")

@main.command()
@click.argument("id")
def remove(id):
    output_dir = Path.home() / ".llmatic" / id
    if not output_dir.exists():
        print(f"No tracking found for id: {id}")
        return
    
    # Remove the entire directory for the given id
    shutil.rmtree(output_dir)
    print(f"Removed all tracking files for id: {id}")

def format_output(data, file_path):
    exec_time_color = "red" if data["execution_time_ms"] > 500 else "green"
    
    print(click.style(f"LLM Tracking Results for: {data['id']}", fg="cyan"))
    print(click.style("-" * 60, fg="yellow"))
    print(f"Tracking ID: {click.style(data['id'], fg='red')}")
    print(f"Model: {click.style(data.get('model', 'N/A'), fg='yellow')}")
    prompt_text = f"\"{data['input']}\""
    print(f"Prompt: {click.style(prompt_text, fg='yellow')}")
    execution_time = data['execution_time_ms']
    print(f"Execution Time: {click.style(f'{execution_time} ms', fg=exec_time_color)}")
    print("Total Cost: N/A")
    print(f"Tracking File Path: {click.style(str(file_path), fg='yellow')}")
    print()
    print(click.style("Evaluation Results:", fg="cyan"))
    print(click.style("-" * 60, fg="yellow"))
    for eval_name, eval_result in data.get('eval_results', {}).items():
        scale_basis = eval_result['scale'][0]
        scale = eval_result['scale'][1]
        print(f"{eval_name}: {click.style(f'{scale_basis} / {scale}', fg='green')} (N/A)")
    print()
    print(click.style("Generated Text:", fg="cyan"))
    print(click.style("-" * 60, fg="yellow"))
    print(click.style(data["output"]["choices"][0]["text"], fg="green"))

if __name__ == "__main__":
    main()
