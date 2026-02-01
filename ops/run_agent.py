#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from getpass import getuser

WORKTREE = Path("/srv/claude-agent/worktree")
RULES_FILE = WORKTREE / "ops" / "agent_rules.txt"
LOCKDIR = Path("/tmp/claude_agent.lock")
LOCKINFO = LOCKDIR / "lock.json"
STALE_LOCK_SECS = 90 * 60
CLAUDE_CLI_ENV = "CLAUDE_CLI"
REQUIRED_USER = "claudeagent"
REQUIRED_VENV = "claude-base"

# Fallback paths for claude CLI when not on PATH (headless/cron environments)
CLAUDE_CLI_FALLBACK_PATHS = [
    Path.home() / ".npm-global" / "bin" / "claude",
    Path.home() / ".local" / "bin" / "claude",
    Path("/usr/local/bin/claude"),
    Path("/opt/claude/bin/claude"),
]
RUN_DEADLINE_SECS = 55 * 60
DEFAULT_SH_TIMEOUT_SECS = 10 * 60
DEFAULT_CLAUDE_TIMEOUT_SECS = 20 * 60

PLANNER_MAX_TURNS = 5
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

def sh(cmd, cwd=WORKTREE, check=True, timeout=DEFAULT_SH_TIMEOUT_SECS):
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=check,
        timeout=timeout,
    )

def _pid_is_running(pid: int) -> bool:
    if pid <= 0:
        return False
    return Path(f"/proc/{pid}").exists()

def _is_lock_stale() -> bool:
    try:
        if not LOCKINFO.exists():
            return True
        data = json.loads(LOCKINFO.read_text(encoding="utf-8"))
        pid = int(data.get("pid", 0))
        created = float(data.get("created", 0.0))
        if not _pid_is_running(pid):
            return True
        if time.time() - created > STALE_LOCK_SECS:
            return True
        return False
    except Exception:
        return True

def acquire_lock():
    try:
        os.mkdir(str(LOCKDIR))
    except FileExistsError:
        if _is_lock_stale():
            try:
                release_lock()
                os.mkdir(str(LOCKDIR))
            except Exception:
                return False
        else:
            return False

    lock_payload = {
        "pid": os.getpid(),
        "created": time.time(),
        "user": getuser(),
    }
    LOCKINFO.write_text(json.dumps(lock_payload), encoding="utf-8")
    return True

def release_lock():
    try:
        if LOCKINFO.exists():
            LOCKINFO.unlink()
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

def resolve_claude_cli() -> str:
    """Resolve claude CLI path with fallbacks for headless environments."""
    # 1. Check explicit environment variable
    env_path = os.environ.get(CLAUDE_CLI_ENV, "").strip()
    if env_path and Path(env_path).is_file():
        return env_path

    # 2. Check PATH (works in interactive sessions)
    which_path = shutil.which("claude")
    if which_path:
        return which_path

    # 3. Check common installation paths (for headless/cron)
    for fallback in CLAUDE_CLI_FALLBACK_PATHS:
        if fallback.is_file() and os.access(fallback, os.X_OK):
            return str(fallback)

    return ""

def require_environment():
    current_user = getuser()
    if current_user != REQUIRED_USER:
        raise RuntimeError(f"Must run as user '{REQUIRED_USER}', got '{current_user}'")

    venv_path = os.environ.get("VIRTUAL_ENV", "").strip()
    venv_name = Path(venv_path).name if venv_path else ""
    if venv_name != REQUIRED_VENV:
        raise RuntimeError(
            f"Must run inside venv '{REQUIRED_VENV}', got '{venv_name or 'none'}'"
        )

    cli_path = resolve_claude_cli()
    if not cli_path:
        checked_paths = [str(p) for p in CLAUDE_CLI_FALLBACK_PATHS]
        raise RuntimeError(
            f"claude CLI not found. Set {CLAUDE_CLI_ENV} env var, add 'claude' to PATH, "
            f"or install to one of: {checked_paths}"
        )
    if not Path(cli_path).exists():
        raise RuntimeError(f"claude CLI path does not exist: {cli_path}")
    if not os.access(cli_path, os.X_OK):
        raise RuntimeError(f"claude CLI is not executable: {cli_path}")

    return cli_path

def ensure_time_remaining(start_time: float, step: str):
    elapsed = time.monotonic() - start_time
    if elapsed > RUN_DEADLINE_SECS:
        raise RuntimeError(f"Time budget exceeded before {step} ({elapsed:.0f}s)")

def run_claude(prompt: str, max_turns: int, output_format: str, json_schema=None):
    # Read the rules file content to append as system prompt
    rules_content = ""
    if RULES_FILE.exists():
        rules_content = RULES_FILE.read_text(encoding="utf-8").strip()

    cli_path = resolve_claude_cli()
    if not cli_path:
        raise FileNotFoundError(
            f"claude CLI not found. Set {CLAUDE_CLI_ENV} env var or install claude to a standard location."
        )

    log(f"Using claude CLI: {cli_path}", "debug")

    cmd = [
        cli_path, "-p",
        "--tools", TOOLS,
        "--output-format", output_format,
        "--max-turns", str(max_turns),
    ]

    if rules_content:
        cmd += ["--append-system-prompt", rules_content]

    for rule in ALLOWED:
        cmd += ["--allowedTools", rule]

    if json_schema is not None:
        cmd += ["--json-schema", json.dumps(json_schema)]

    cmd.append(prompt)

    try:
        p = subprocess.run(
            cmd,
            cwd=str(WORKTREE),
            text=True,
            capture_output=True,
            timeout=DEFAULT_CLAUDE_TIMEOUT_SECS,
        )
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Failed to execute claude CLI at '{cli_path}': {e}"
        ) from e

def main():
    start_time = time.monotonic()
    TOTAL_STEPS = 5
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}  CLAUDE AGENT RUN - {now()}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    # Step 1: Acquire lock
    log_step(1, TOTAL_STEPS, "Acquiring execution lock")
    try:
        cli_path = require_environment()
        log(f"Claude CLI resolved: {cli_path}", "ok")
    except RuntimeError as e:
        log(f"Preflight failed: {e}", "error")
        return 5

    if not acquire_lock():
        log("Another agent instance is running, exiting", "warn")
        return 6
    log(f"Lock acquired: {LOCKDIR}", "ok")

    try:
        ensure_time_remaining(start_time, "worktree validation")
        # Validate worktree
        log(f"Validating worktree: {WORKTREE}", "info")
        if not WORKTREE.exists():
            log(f"Missing worktree: {WORKTREE}", "error")
            raise RuntimeError(f"Missing worktree: {WORKTREE}")
        log("Worktree exists", "ok")

        # Step 2: Git setup
        log_step(2, TOTAL_STEPS, "Preparing git branch")
        try:
            ensure_time_remaining(start_time, "git setup")
            log("Fetching from origin...", "info")
            sh(["git", "fetch", "origin"], check=True)
            log("Fetch complete", "ok")
            
            log("Checking out agent/auto branch...", "info")
            sh(["git", "checkout", "agent/auto"], check=True)
            log("Checkout complete", "ok")
            
            log("Attempting fast-forward merge from origin/main...", "info")
            sh(["git", "merge", "--ff-only", "origin/main"], check=True)
            log("Branch is up-to-date with origin/main", "ok")
        except subprocess.TimeoutExpired as e:
            log(f"Git precheck timed out: {str(e).strip()}", "error")
            append_runlog(f"- {now()} | PRECHECK TIMEOUT\n  - error: {str(e).strip()}\n")
            return 2
        except subprocess.CalledProcessError as e:
            log(f"Git precheck failed: {e.stderr.strip()}", "error")
            append_runlog(f"- {now()} | PRECHECK FAILED\n  - stderr: {e.stderr.strip()}\n")
            return 2

        # Check for CLAUDE.md existence
        claude_md_path = WORKTREE / "CLAUDE.md"
        needs_init = not claude_md_path.exists()
        if needs_init:
            log("CLAUDE.md not found - will request /init", "warn")
        else:
            log("CLAUDE.md found", "ok")

        # Step 3: Run planner
        log_step(3, TOTAL_STEPS, "Running planner agent")
        log(f"Max turns: {PLANNER_MAX_TURNS}", "info")
        ensure_time_remaining(start_time, "planner start")
        
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
            f"{'Start by running /init to set up the workspace. ' if needs_init else ''}"
            "Return JSON matching the provided schema.\n"
        )

        log("Invoking Claude planner...", "info")
        try:
            rc, out, err = run_claude(planner_prompt, PLANNER_MAX_TURNS, "json", planner_schema)
        except subprocess.TimeoutExpired as e:
            log(f"Planner timed out: {str(e).strip()}", "error")
            append_runlog(f"- {now()} | PLANNER TIMEOUT\n  - error: {str(e).strip()}\n")
            return 1
        
        if rc != 0:
            log(f"Planner failed with exit code {rc}", "error")
            if err:
                log(f"stderr: {err.strip()[:200]}", "debug")
            append_runlog(f"- {now()} | PLANNER FAILED (rc={rc})\n  - stderr: {err.strip()[:1200]}\n")
            return 1
        log("Planner completed successfully", "ok")

        try:
            plan = json.loads(out)
            log("Parsed planner JSON output", "ok")
        except json.JSONDecodeError:
            log("Failed to parse planner output as JSON", "error")
            log(f"Raw output: {out.strip()[:200]}", "debug")
            append_runlog(f"- {now()} | PLANNER OUTPUT NOT JSON\n  - raw: {out.strip()[:1200]}\n")
            return 1

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
        ensure_time_remaining(start_time, "executor start")
        
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
        try:
            rc2, out2, err2 = run_claude(executor_prompt, EXEC_MAX_TURNS, "text", None)
        except subprocess.TimeoutExpired as e:
            log(f"Executor timed out: {str(e).strip()}", "error")
            append_runlog(f"- {now()} | EXECUTOR TIMEOUT\n  - error: {str(e).strip()}\n")
            return 3
        
        if rc2 == 0:
            log("Executor completed successfully", "ok")
        else:
            log(f"Executor finished with exit code {rc2}", "warn")

        # Step 5: Finalize
        log_step(5, TOTAL_STEPS, "Finalizing run")
        ensure_time_remaining(start_time, "finalize")
        
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

        return 0 if rc2 == 0 else 3

    except Exception as e:
        log(f"Unexpected error: {e}", "error")
        append_runlog(f"- {now()} | UNEXPECTED ERROR\n  - {str(e)[:500]}\n")
        return 4

    finally:
        log("Releasing execution lock...", "info")
        release_lock()
        log("Lock released", "ok")

if __name__ == "__main__":
    sys.exit(main())
