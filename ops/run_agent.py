#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKTREE = Path("/srv/claude-agent/worktree")
RULES_FILE = WORKTREE / "ops" / "agent_rules.txt"
LOCKDIR = Path("/tmp/claude_agent.lock")

PLANNER_MAX_TURNS = 3
EXEC_MAX_TURNS = 18

# Keep tools tight. Use --tools to restrict availability,
# and --allowedTools to auto-approve a safe subset. (Docs: CLI reference)
TOOLS = "Bash,Read,Edit,Write,Grep,Glob"

ALLOWED = [
    # Core file operations
    "Read",
    "Write",
    "Edit",
    "Grep",
    "Glob",
    
    # Git operations
    "Bash(git status *)",
    "Bash(git diff *)",
    "Bash(git log *)",
    "Bash(git show *)",
    "Bash(git add *)",
    "Bash(git commit *)",
    "Bash(git checkout *)",
    "Bash(git merge *)",
    "Bash(git fetch *)",
    "Bash(git rev-parse *)",
    "Bash(git branch *)",
    "Bash(git stash *)",
    "Bash(git reset *)",
    
    # File inspection (read-only, safe)
    "Bash(ls *)",
    "Bash(cat *)",
    "Bash(head *)",
    "Bash(tail *)",
    "Bash(wc *)",
    "Bash(find *)",
    "Bash(tree *)",
    "Bash(file *)",
    "Bash(stat *)",
    "Bash(du *)",
    "Bash(pwd)",
    "Bash(which *)",
    "Bash(whoami)",
    "Bash(env)",
    "Bash(echo *)",
    "Bash(date *)",
    
    # Testing frameworks
    "Bash(pytest *)",
    "Bash(python -m pytest *)",
    "Bash(python -m unittest *)",
    "Bash(make *)",
    "Bash(npm test *)",
    "Bash(npm run *)",
    "Bash(npx *)",
    "Bash(go test *)",
    "Bash(cargo test *)",
    "Bash(cargo check *)",
    
    # Python operations
    "Bash(python *)",
    "Bash(python3 *)",
    "Bash(pip list *)",
    "Bash(pip show *)",
    "Bash(pip freeze *)",
    "Bash(pip install *)",
    
    # Directory operations
    "Bash(mkdir *)",
    "Bash(cd *)",
    
    # Text processing (safe, read-only)
    "Bash(grep *)",
    "Bash(awk *)",
    "Bash(sed *)",
    "Bash(sort *)",
    "Bash(uniq *)",
    "Bash(diff *)",
    "Bash(cut *)",
    "Bash(tr *)",
    
    # JSON/data inspection
    "Bash(jq *)",
    "Bash(yq *)",
]

# ANSI color codes for verbose output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(msg: str, level: str = "info"):
    """Print verbose status messages to CLI."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix_map = {
        "info": f"{Colors.CYAN}[INFO]{Colors.ENDC}",
        "step": f"{Colors.BOLD}{Colors.BLUE}[STEP]{Colors.ENDC}",
        "ok": f"{Colors.GREEN}[ OK ]{Colors.ENDC}",
        "warn": f"{Colors.YELLOW}[WARN]{Colors.ENDC}",
        "error": f"{Colors.RED}[FAIL]{Colors.ENDC}",
        "debug": f"{Colors.HEADER}[DBUG]{Colors.ENDC}",
    }
    prefix = prefix_map.get(level, prefix_map["info"])
    print(f"{Colors.BOLD}{timestamp}{Colors.ENDC} {prefix} {msg}", flush=True)

def log_step(step_num: int, total: int, description: str):
    """Print a major step indicator."""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    log(f"Step {step_num}/{total}: {description}", "step")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n", flush=True)

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def sh(cmd, cwd=WORKTREE, check=True):
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, check=check)

def acquire_lock():
    try:
        os.mkdir(str(LOCKDIR))
        return True
    except FileExistsError:
        return False

def release_lock():
    try:
        os.rmdir(str(LOCKDIR))
    except Exception:
        pass

def append_runlog(text: str):
    p = WORKTREE / "RUNLOG.md"
    with p.open("a", encoding="utf-8") as f:
        f.write("\n" + text.strip() + "\n")

def git_dirty():
    return sh(["git", "status", "--porcelain"], check=True).stdout.strip() != ""

def commit_if_needed(message: str):
    if not git_dirty():
        return None
    sh(["git", "add", "-A"], check=True)
    sh(["git", "commit", "-m", message], check=True)
    return sh(["git", "rev-parse", "HEAD"], check=True).stdout.strip()

def run_claude(prompt: str, max_turns: int, output_format: str, json_schema=None):
    cmd = [
        "claude", "-p",
        "--append-system-prompt-file", str(RULES_FILE),
        "--tools", TOOLS,
        "--output-format", output_format,
        "--max-turns", str(max_turns),
    ]
    for rule in ALLOWED:
        cmd += ["--allowedTools", rule]

    if json_schema is not None:
        cmd += ["--json-schema", json.dumps(json_schema)]

    cmd.append(prompt)

    p = subprocess.run(cmd, cwd=str(WORKTREE), text=True, capture_output=True)
    return p.returncode, p.stdout, p.stderr

def main():
    TOTAL_STEPS = 5
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}  CLAUDE AGENT RUN - {now()}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    # Step 1: Acquire lock
    log_step(1, TOTAL_STEPS, "Acquiring execution lock")
    if not acquire_lock():
        log("Another agent instance is running, exiting gracefully", "warn")
        sys.exit(0)
    log(f"Lock acquired: {LOCKDIR}", "ok")

    try:
        # Validate worktree
        log(f"Validating worktree: {WORKTREE}", "info")
        if not WORKTREE.exists():
            log(f"Missing worktree: {WORKTREE}", "error")
            raise RuntimeError(f"Missing worktree: {WORKTREE}")
        log("Worktree exists", "ok")

        # Step 2: Git setup
        log_step(2, TOTAL_STEPS, "Preparing git branch")
        try:
            log("Fetching from origin...", "info")
            sh(["git", "fetch", "origin"], check=True)
            log("Fetch complete", "ok")
            
            log("Checking out agent/auto branch...", "info")
            sh(["git", "checkout", "agent/auto"], check=True)
            log("Checkout complete", "ok")
            
            log("Attempting fast-forward merge from origin/main...", "info")
            sh(["git", "merge", "--ff-only", "origin/main"], check=True)
            log("Branch is up-to-date with origin/main", "ok")
        except subprocess.CalledProcessError as e:
            log(f"Git precheck failed: {e.stderr.strip()}", "error")
            append_runlog(f"- {now()} | PRECHECK FAILED\n  - stderr: {e.stderr.strip()}\n")
            sys.exit(2)

        # Step 3: Run planner
        log_step(3, TOTAL_STEPS, "Running planner agent")
        log(f"Max turns: {PLANNER_MAX_TURNS}", "info")
        
        planner_schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "loop_todo": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 5},
                "definition_of_done": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 5},
                "commands_expected": {"type": "array", "items": {"type": "string"}, "maxItems": 12},
                "risks": {"type": "array", "items": {"type": "string"}, "maxItems": 12},
            },
            "required": ["loop_todo", "definition_of_done"],
        }

        planner_prompt = (
            "Read STATE.md and GOALS.md. Create a small plan for THIS RUN ONLY.\n"
            "Return JSON matching the provided schema.\n"
        )

        log("Invoking Claude planner...", "info")
        rc, out, err = run_claude(planner_prompt, PLANNER_MAX_TURNS, "json", planner_schema)
        
        if rc != 0:
            log(f"Planner failed with exit code {rc}", "error")
            if err:
                log(f"stderr: {err.strip()[:200]}", "debug")
            append_runlog(f"- {now()} | PLANNER FAILED (rc={rc})\n  - stderr: {err.strip()[:1200]}\n")
            sys.exit(1)
        log("Planner completed successfully", "ok")

        try:
            plan = json.loads(out)
            log("Parsed planner JSON output", "ok")
        except json.JSONDecodeError:
            log("Failed to parse planner output as JSON", "error")
            log(f"Raw output: {out.strip()[:200]}", "debug")
            append_runlog(f"- {now()} | PLANNER OUTPUT NOT JSON\n  - raw: {out.strip()[:1200]}\n")
            sys.exit(1)

        # Display the plan
        todo_items = plan.get("loop_todo", [])
        log(f"Plan contains {len(todo_items)} TODO items:", "info")
        for i, item in enumerate(todo_items, 1):
            print(f"    {Colors.CYAN}{i}.{Colors.ENDC} {item}")
        
        if plan.get("definition_of_done"):
            log("Definition of done:", "info")
            for item in plan.get("definition_of_done", []):
                print(f"    {Colors.GREEN}✓{Colors.ENDC} {item}")

        # Step 4: Run executor
        log_step(4, TOTAL_STEPS, "Running executor agent")
        log(f"Max turns: {EXEC_MAX_TURNS}", "info")
        
        todo_lines = "\n".join([f"- {x}" for x in todo_items])

        executor_prompt = (
            "Implement this run-scoped TODO list:\n"
            f"{todo_lines}\n\n"
            "Rules:\n"
            "- Do at most 2 commits.\n"
            "- Run appropriate tests or checks if possible.\n"
            "- Update STATE.md and GOALS.md to reflect actual work completed.\n"
            "- Append a RUNLOG.md entry with timestamp, summary, tests, and commit hashes.\n"
            "- If you are capped or cannot continue, stop and write a clear handoff in STATE.md.\n"
        )

        log("Invoking Claude executor...", "info")
        rc2, out2, err2 = run_claude(executor_prompt, EXEC_MAX_TURNS, "text", None)
        
        if rc2 == 0:
            log("Executor completed successfully", "ok")
        else:
            log(f"Executor finished with exit code {rc2}", "warn")

        # Step 5: Finalize
        log_step(5, TOTAL_STEPS, "Finalizing run")
        
        log("Checking for uncommitted changes...", "info")
        checkpoint = commit_if_needed(f"agent: checkpoint {now()}")
        
        if checkpoint:
            log(f"Created checkpoint commit: {checkpoint[:8]}", "ok")
        else:
            log("No uncommitted changes to checkpoint", "info")

        log("Appending to RUNLOG.md...", "info")
        append_runlog(
            f"- {now()} | EXECUTOR rc={rc2}\n"
            f"  - checkpoint: {checkpoint or 'none'}\n"
            f"  - stdout: {(out2.strip()[:800] if out2 else '')}\n"
            f"  - stderr: {(err2.strip()[:800] if err2 else '')}\n"
        )
        log("Runlog updated", "ok")

        # Final summary
        print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
        if rc2 == 0:
            log("Agent run completed successfully!", "ok")
        else:
            log(f"Agent run finished with issues (exit code: {rc2})", "warn")
        print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

        sys.exit(0 if rc2 == 0 else 3)

    finally:
        log("Releasing execution lock...", "info")
        release_lock()
        log("Lock released", "ok")

if __name__ == "__main__":
    main()
