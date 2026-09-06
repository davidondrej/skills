#!/usr/bin/env python3
"""Discover and invoke Corral Design 1 safely from outside Herdr."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tomllib
from typing import Any


PLUGIN_ID = "corral.design1"
SUPPORTED_AGENTS = ("claude", "codex", "cursor", "pi", "hermes")
RUNTIME_ENV_KEYS = (
    "HERDR_BIN_PATH",
    "HERDR_SESSION",
    "HERDR_SOCKET_PATH",
    "HERDR_PLUGIN_ROOT",
    "HERDR_PLUGIN_CONFIG_DIR",
    "HERDR_PLUGIN_STATE_DIR",
    "CORRAL_CONFIG_DIR",
    "CORRAL_STATE_DIR",
    "CORRAL_STORE_PATH",
)


class ToolError(RuntimeError):
    pass


@dataclass(frozen=True)
class Runtime:
    session: str
    herdr_bin: Path
    corral_bin: Path
    plugin_root: Path
    config_dir: Path
    state_dir: Path
    socket_path: Path
    store_path: Path | None


@dataclass(frozen=True)
class LaunchSpec:
    repo: str
    task: str
    preset: str | None = None
    agent: str | None = None
    priority: int | None = None
    base: str | None = None
    prompt: str = ""
    prompt_file: str | None = None
    worktree_path: str | None = None
    allow_dirty: bool = False
    focus: bool = False
    no_focus: bool = False
    json_output: bool = False
    mock_state: str | None = None


def expanded_path(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def first_value(*values: str | None) -> str | None:
    return next((value for value in values if value), None)


def run_capture(command: list[str | Path], *, timeout: float = 10) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(item) for item in command],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def config_root() -> Path:
    configured = os.environ.get("HERDR_CONFIG_PATH")
    if configured:
        return expanded_path(configured).parent
    return expanded_path(Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "herdr")


def state_root() -> Path:
    return expanded_path(Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "herdr")


def find_herdr(override: str | None) -> Path:
    value = first_value(
        override,
        os.environ.get("HERDR_BIN_PATH"),
        os.environ.get("HERDR_BIN"),
        shutil.which("herdr"),
    )
    if not value:
        raise ToolError("herdr is not installed or discoverable; pass --herdr-bin")
    path = expanded_path(value)
    if not path.is_file():
        raise ToolError(f"Herdr binary does not exist: {path}")
    return path


def read_plugin_registry() -> list[dict[str, Any]]:
    path = config_root() / "plugins.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def find_plugin_root(override: str | None, explicit_corral_bin: str | None) -> Path:
    value = first_value(override, os.environ.get("HERDR_PLUGIN_ROOT"))
    if value:
        return expanded_path(value)
    if explicit_corral_bin:
        binary = expanded_path(explicit_corral_bin)
        if binary.parent.name == "bin":
            return binary.parent.parent

    for plugin in read_plugin_registry():
        if plugin.get("plugin_id") == PLUGIN_ID and plugin.get("enabled", True):
            root = plugin.get("plugin_root")
            if isinstance(root, str) and root:
                return expanded_path(root)

    candidates: list[Path] = []
    for parent in (Path.cwd(), *Path.cwd().parents):
        candidates.extend((parent / "Design1/plugin", parent / "plugin"))
    candidates.append(Path.home() / "code/corral/Design1/plugin")
    for candidate in candidates:
        if (candidate / "bin/corral").is_file():
            return candidate.resolve()
    raise ToolError(
        "cannot find the Corral Design 1 plugin; pass --plugin-root or --corral-bin, "
        "or link corral.design1 with Herdr"
    )


def read_sessions(herdr_bin: Path) -> list[dict[str, Any]]:
    for command in (
        [herdr_bin, "session", "list", "--json"],
        [herdr_bin, "--session", "default", "session", "list", "--json"],
    ):
        try:
            result = run_capture(command)
            payload = json.loads(result.stdout)
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
            continue
        sessions = payload.get("sessions") if isinstance(payload, dict) else None
        if isinstance(sessions, list):
            return [item for item in sessions if isinstance(item, dict)]
    return []


def session_from_socket(path: str | None) -> str | None:
    if not path:
        return None
    parent = expanded_path(path).parent
    return parent.name if parent.parent.name == "sessions" else "default"


def choose_session(override: str | None, herdr_bin: Path) -> str:
    explicit = first_value(
        override,
        os.environ.get("CORRAL_SESSION"),
        os.environ.get("HERDR_SESSION"),
        session_from_socket(os.environ.get("HERDR_SOCKET_PATH")),
    )
    if explicit:
        return explicit
    sessions = read_sessions(herdr_bin)
    named_corral = next((item for item in sessions if item.get("name") == "corral"), None)
    if named_corral:
        return "corral"
    running = [item for item in sessions if item.get("running")]
    if len(running) == 1 and isinstance(running[0].get("name"), str):
        return str(running[0]["name"])
    default = next((item for item in sessions if item.get("default")), None)
    if default and isinstance(default.get("name"), str):
        return str(default["name"])
    return "corral"


def discover_config_dir(override: str | None, herdr_bin: Path, session: str) -> Path:
    value = first_value(
        override,
        os.environ.get("CORRAL_CONFIG_DIR"),
        os.environ.get("HERDR_PLUGIN_CONFIG_DIR"),
    )
    if value:
        return expanded_path(value)
    try:
        result = run_capture(
            [herdr_bin, "--session", session, "plugin", "config-dir", PLUGIN_ID]
        )
        if result.returncode == 0 and result.stdout.strip():
            return expanded_path(result.stdout.strip().splitlines()[-1])
    except (OSError, subprocess.SubprocessError):
        pass
    return config_root() / "plugins/config" / PLUGIN_ID


def discover_socket(override: str | None, herdr_bin: Path, session: str) -> Path:
    value = first_value(override, os.environ.get("HERDR_SOCKET_PATH"))
    if value:
        return expanded_path(value)
    for item in read_sessions(herdr_bin):
        if item.get("name") == session and isinstance(item.get("socket_path"), str):
            return expanded_path(str(item["socket_path"]))
    root = config_root()
    return root / "herdr.sock" if session == "default" else root / "sessions" / session / "herdr.sock"


def resolve_runtime(args: argparse.Namespace) -> Runtime:
    herdr_bin = find_herdr(args.herdr_bin)
    session = choose_session(args.session, herdr_bin)
    explicit_corral_bin = first_value(args.corral_bin, os.environ.get("CORRAL_BIN"))
    plugin_root = find_plugin_root(args.plugin_root, explicit_corral_bin)
    corral_bin = (
        expanded_path(explicit_corral_bin)
        if explicit_corral_bin
        else (plugin_root / "bin/corral").resolve()
    )
    if not corral_bin.is_file():
        raise ToolError(f"Corral launcher does not exist: {corral_bin}")
    config_dir = discover_config_dir(args.config_dir, herdr_bin, session)
    state_value = first_value(
        args.state_dir,
        os.environ.get("CORRAL_STATE_DIR"),
        os.environ.get("HERDR_PLUGIN_STATE_DIR"),
    )
    state_dir = expanded_path(state_value) if state_value else state_root() / "plugins" / PLUGIN_ID
    socket_path = discover_socket(args.socket_path, herdr_bin, session)
    store_value = first_value(args.store_path, os.environ.get("CORRAL_STORE_PATH"))
    return Runtime(
        session=session,
        herdr_bin=herdr_bin,
        corral_bin=corral_bin,
        plugin_root=plugin_root,
        config_dir=config_dir,
        state_dir=state_dir,
        socket_path=socket_path,
        store_path=expanded_path(store_value) if store_value else None,
    )


def runtime_environment(runtime: Runtime) -> dict[str, str]:
    values = os.environ.copy()
    values.update(
        {
            "HERDR_BIN_PATH": str(runtime.herdr_bin),
            "HERDR_SESSION": runtime.session,
            "HERDR_SOCKET_PATH": str(runtime.socket_path),
            "HERDR_PLUGIN_ROOT": str(runtime.plugin_root),
            "HERDR_PLUGIN_CONFIG_DIR": str(runtime.config_dir),
            "HERDR_PLUGIN_STATE_DIR": str(runtime.state_dir),
            "CORRAL_CONFIG_DIR": str(runtime.config_dir),
            "CORRAL_STATE_DIR": str(runtime.state_dir),
        }
    )
    if runtime.store_path:
        values["CORRAL_STORE_PATH"] = str(runtime.store_path)
    else:
        values.pop("CORRAL_STORE_PATH", None)
    return values


def server_check(runtime: Runtime) -> tuple[bool, str]:
    try:
        result = run_capture(
            [runtime.herdr_bin, "--session", runtime.session, "api", "snapshot"],
            timeout=8,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return False, str(error)
    if result.returncode == 0 and '"snapshot"' in result.stdout:
        return True, "running"
    return False, (result.stderr or result.stdout).strip() or "server is not responding"


def require_server(runtime: Runtime) -> None:
    running, detail = server_check(runtime)
    if not running:
        raise ToolError(
            f"Herdr session '{runtime.session}' is not running: {detail}\n"
            f"Start or attach it explicitly with: herdr --session {shlex.quote(runtime.session)}"
        )


def load_presets(runtime: Runtime) -> dict[str, dict[str, Any]]:
    path = runtime.config_dir / "presets.toml"
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ToolError(f"Corral preset file is missing: {path}") from error
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ToolError(f"cannot read Corral presets: {error}") from error
    presets = data.get("presets")
    if not isinstance(presets, dict) or not presets:
        raise ToolError(f"{path} contains no [presets.NAME] tables")
    return {str(name): value for name, value in presets.items() if isinstance(value, dict)}


def select_preset(
    presets: dict[str, dict[str, Any]], requested: str | None, agent: str | None
) -> tuple[str, dict[str, Any]]:
    if requested:
        if requested not in presets:
            raise ToolError(f"unknown Corral preset: {requested}")
        selected = presets[requested]
        if agent and selected.get("agent") != agent:
            raise ToolError(
                f"preset '{requested}' launches {selected.get('agent')!r}, not {agent!r}"
            )
        return requested, selected
    desired = agent or "pi"
    matches = [(name, value) for name, value in presets.items() if value.get("agent") == desired]
    if not matches:
        raise ToolError(f"no Corral preset launches agent kind '{desired}'")
    if len(matches) > 1:
        names = ", ".join(name for name, _ in matches)
        raise ToolError(f"multiple {desired} presets exist ({names}); pass --preset")
    return matches[0]


def read_prompt(spec: LaunchSpec, *, base_dir: Path | None = None) -> str:
    if spec.prompt and spec.prompt_file:
        raise ToolError("use either prompt or prompt_file, not both")
    if not spec.prompt_file:
        return spec.prompt
    path = Path(spec.prompt_file).expanduser()
    if not path.is_absolute() and base_dir:
        path = base_dir / path
    try:
        return path.resolve().read_text(encoding="utf-8")
    except OSError as error:
        raise ToolError(f"cannot read prompt file {path}: {error}") from error


def build_launch_command(
    runtime: Runtime,
    presets: dict[str, dict[str, Any]],
    spec: LaunchSpec,
    *,
    base_dir: Path | None = None,
) -> tuple[list[str], str]:
    title = " ".join(spec.task.split())
    if not title or len(title) > 80:
        raise ToolError("task title must contain 1 to 80 characters")
    if spec.priority is not None and spec.priority not in range(1, 5):
        raise ToolError("priority must be 1, 2, 3, or 4")
    if spec.focus and spec.no_focus:
        raise ToolError("--focus and --no-focus cannot be combined")
    repository = expanded_path(spec.repo)
    if not repository.is_dir():
        raise ToolError(f"repository path is not a directory: {repository}")
    preset_name, _ = select_preset(presets, spec.preset, spec.agent)
    prompt = read_prompt(spec, base_dir=base_dir).strip()
    command = [
        str(runtime.corral_bin),
        "launch",
        "--repo",
        str(repository),
        "--task",
        title,
        "--preset",
        preset_name,
    ]
    if spec.priority is not None:
        command.extend(("--priority", str(spec.priority)))
    if spec.base:
        command.extend(("--base", spec.base))
    if prompt:
        command.extend(("--prompt", prompt))
    if spec.worktree_path:
        command.extend(("--worktree-path", str(expanded_path(spec.worktree_path))))
    if spec.allow_dirty:
        command.append("--allow-dirty")
    command.append("--focus" if spec.focus else "--no-focus")
    if spec.mock_state:
        command.extend(("--mock-state", spec.mock_state))
    if spec.json_output:
        command.append("--json")
    return command, preset_name


def git_read(repository: Path, arguments: list[str]) -> str:
    result = run_capture(["git", "-C", repository, *arguments])
    if result.returncode != 0:
        raise ToolError((result.stderr or result.stdout).strip())
    return result.stdout.strip()


def primary_checkout(repository: Path) -> Path:
    root = expanded_path(git_read(repository, ["rev-parse", "--show-toplevel"]))
    worktrees = git_read(root, ["worktree", "list", "--porcelain"])
    for line in worktrees.splitlines():
        if line.startswith("worktree "):
            return expanded_path(line.removeprefix("worktree "))
    return root


def launch_plan(
    runtime: Runtime,
    presets: dict[str, dict[str, Any]],
    spec: LaunchSpec,
    command: list[str],
    *,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    preset_name, preset = select_preset(presets, spec.preset, spec.agent)
    repository = primary_checkout(expanded_path(spec.repo))
    base = spec.base or str(preset.get("base", "HEAD"))
    base_sha = git_read(repository, ["rev-parse", f"{base}^{{commit}}"])
    dirty = git_read(repository, ["status", "--porcelain=v1"]).splitlines()
    preset_prompt = preset.get("initial_prompt")
    preset_prompt = preset_prompt.strip() if isinstance(preset_prompt, str) else ""
    user_prompt = read_prompt(spec, base_dir=base_dir).strip()
    combined_prompt = "\n\n".join(part for part in (preset_prompt, user_prompt) if part)
    priority = spec.priority if spec.priority is not None else preset.get("default_priority", 3)
    setup = preset.get("setup") if isinstance(preset.get("setup"), list) else []
    copy_files = (
        preset.get("copy_files") if isinstance(preset.get("copy_files"), list) else []
    )
    environment = preset.get("env") if isinstance(preset.get("env"), dict) else {}
    return {
        "session": runtime.session,
        "socket_path": str(runtime.socket_path),
        "config_dir": str(runtime.config_dir),
        "state_dir": str(runtime.state_dir),
        "repository": str(repository),
        "task": " ".join(spec.task.split()),
        "preset": preset_name,
        "agent": preset.get("agent"),
        "priority": priority,
        "base": base,
        "base_sha": base_sha,
        "worktree_path": (
            str(expanded_path(spec.worktree_path))
            if spec.worktree_path
            else "<Herdr-managed automatic path>"
        ),
        "focus": spec.focus,
        "allow_dirty": spec.allow_dirty,
        "dirty_changes": len(dirty),
        "would_refuse_dirty": bool(dirty and not spec.allow_dirty),
        "prompt_chars": len(combined_prompt),
        "preset_prompt_chars": len(preset_prompt),
        "task_prompt_chars": len(user_prompt),
        "setup_commands": len(setup),
        "copy_files": [str(item) for item in copy_files],
        "environment_keys": sorted(str(key) for key in environment),
        "command": redacted_command(command),
    }


def redacted_command(command: list[str]) -> str:
    rendered = list(command)
    for option in ("--prompt", "--api-key"):
        while option in rendered:
            index = rendered.index(option)
            if index + 1 < len(rendered):
                value = rendered[index + 1]
                rendered[index + 1] = f"<{option.removeprefix('--')}:{len(value)} chars>"
            rendered[index] = f"__seen_{option}"
        rendered = [option if item == f"__seen_{option}" else item for item in rendered]
    return shlex.join(rendered)


def launch_spec_from_args(args: argparse.Namespace) -> LaunchSpec:
    return LaunchSpec(
        repo=args.repo,
        task=args.task,
        preset=args.preset,
        agent=args.agent,
        priority=args.priority,
        base=args.base,
        prompt=args.prompt,
        prompt_file=args.prompt_file,
        worktree_path=args.worktree_path,
        allow_dirty=args.allow_dirty,
        focus=args.focus,
        no_focus=args.no_focus,
        json_output=args.json,
        mock_state=args.mock_state,
    )


def command_doctor(args: argparse.Namespace) -> int:
    runtime = resolve_runtime(args)
    checks: list[dict[str, Any]] = []

    def add(level: str, name: str, detail: str) -> None:
        checks.append({"level": level, "name": name, "detail": detail})

    version = run_capture([runtime.herdr_bin, "--session", runtime.session, "--version"])
    if version.returncode == 0:
        add("ok", "herdr", version.stdout.strip())
    else:
        add("error", "herdr", (version.stderr or version.stdout).strip())
    add("ok" if runtime.corral_bin.is_file() else "error", "corral", str(runtime.corral_bin))
    add(
        "ok" if runtime.config_dir.is_dir() else "error",
        "plugin config",
        str(runtime.config_dir),
    )
    add(
        "ok" if (runtime.config_dir / "presets.toml").is_file() else "error",
        "presets",
        str(runtime.config_dir / "presets.toml"),
    )
    add(
        "ok" if runtime.state_dir.is_dir() else "warn",
        "plugin state",
        str(runtime.state_dir),
    )
    running, detail = server_check(runtime)
    add("ok" if running else "error", f"session {runtime.session}", detail)
    add("ok" if runtime.socket_path.exists() else "error", "socket", str(runtime.socket_path))

    pi_binary = shutil.which("pi")
    if pi_binary:
        pi_version = run_capture([pi_binary, "--version"])
        detail = pi_version.stdout.strip() or pi_version.stderr.strip() or pi_binary
        add("ok" if pi_version.returncode == 0 else "warn", "pi", detail)
    else:
        add("error", "pi", "pi is not on PATH")

    try:
        presets = load_presets(runtime)
        pi_presets = [name for name, value in presets.items() if value.get("agent") == "pi"]
        add(
            "ok" if pi_presets else "error",
            "Pi presets",
            ", ".join(pi_presets) if pi_presets else "none",
        )
    except ToolError as error:
        add("error", "Pi presets", str(error))

    payload = {
        "session": runtime.session,
        "runtime": {
            "herdr_bin": str(runtime.herdr_bin),
            "corral_bin": str(runtime.corral_bin),
            "plugin_root": str(runtime.plugin_root),
            "config_dir": str(runtime.config_dir),
            "state_dir": str(runtime.state_dir),
            "socket_path": str(runtime.socket_path),
            "store_path": str(runtime.store_path) if runtime.store_path else None,
        },
        "checks": checks,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"Corral session: {runtime.session}")
        for item in checks:
            print(f"[{item['level']}] {item['name']}: {item['detail']}")
    return 1 if any(item["level"] == "error" for item in checks) else 0


def sanitized_preset(name: str, value: dict[str, Any]) -> dict[str, Any]:
    command = value.get("command") if isinstance(value.get("command"), list) else []
    safe_command = [str(item) for item in command]
    for index, item in enumerate(safe_command[:-1]):
        if item == "--api-key":
            safe_command[index + 1] = "<redacted>"
    safe_command = [
        "--api-key=<redacted>" if item.startswith("--api-key=") else item
        for item in safe_command
    ]
    environment = value.get("env") if isinstance(value.get("env"), dict) else {}
    setup = value.get("setup") if isinstance(value.get("setup"), list) else []
    copy_files = value.get("copy_files") if isinstance(value.get("copy_files"), list) else []
    prompt = value.get("initial_prompt") if isinstance(value.get("initial_prompt"), str) else ""
    return {
        "name": name,
        "agent": value.get("agent"),
        "command": safe_command,
        "default_priority": value.get("default_priority", 3),
        "base": value.get("base", "HEAD"),
        "setup_commands": len(setup),
        "copy_files": copy_files,
        "initial_prompt_chars": len(prompt),
        "environment_keys": sorted(str(key) for key in environment),
    }


def command_list_presets(args: argparse.Namespace) -> int:
    runtime = resolve_runtime(args)
    values = [
        sanitized_preset(name, value)
        for name, value in load_presets(runtime).items()
        if not args.agent or value.get("agent") == args.agent
    ]
    if args.json:
        print(json.dumps(values, indent=2, sort_keys=True))
    else:
        for item in values:
            command = shlex.join(item["command"])
            print(
                f"{item['name']}: agent={item['agent']} priority=P{item['default_priority']} "
                f"base={item['base']} command={command}"
            )
    return 0


def command_launch(args: argparse.Namespace) -> int:
    runtime = resolve_runtime(args)
    presets = load_presets(runtime)
    spec = launch_spec_from_args(args)
    command, _ = build_launch_command(runtime, presets, spec)
    if args.dry_run:
        plan = launch_plan(runtime, presets, spec, command)
        if args.json:
            print(json.dumps(plan, indent=2, sort_keys=True))
        else:
            for key in (
                "session",
                "repository",
                "task",
                "preset",
                "agent",
                "priority",
                "base",
                "base_sha",
                "worktree_path",
                "focus",
                "allow_dirty",
                "dirty_changes",
                "would_refuse_dirty",
                "prompt_chars",
                "setup_commands",
                "copy_files",
                "environment_keys",
            ):
                print(f"{key}={plan[key]}")
            print(plan["command"])
        return 0
    require_server(runtime)
    result = subprocess.run(command, env=runtime_environment(runtime))
    return result.returncode


def summary_task(task: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "task_id",
        "title",
        "status",
        "error",
        "agent",
        "agent_name",
        "agent_session",
        "preset",
        "priority",
        "repository_path",
        "worktree_path",
        "branch",
        "base",
        "base_sha",
        "workspace_id",
        "pane_id",
        "created_at",
        "archived_at",
        "cleaned_at",
    )
    return {key: task.get(key) for key in keys}


def command_status(args: argparse.Namespace) -> int:
    runtime = resolve_runtime(args)
    result = subprocess.run(
        [str(runtime.corral_bin), "state", "--json"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=runtime_environment(runtime),
    )
    if result.returncode != 0:
        raise ToolError((result.stderr or result.stdout).strip())
    try:
        state = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ToolError("Corral returned invalid state JSON") from error
    tasks = state.get("tasks", []) if isinstance(state, dict) else []
    if args.task:
        tasks = [
            task
            for task in tasks
            if task.get("task_id") == args.task or task.get("title") == args.task
        ]
        if len(tasks) != 1:
            raise ToolError(f"task target is not unique: {args.task}")
    selected = tasks if args.full else [summary_task(task) for task in tasks]
    live: dict[str, Any] = {}
    if args.live:
        for task in selected:
            pane_id = task.get("pane_id")
            task_id = str(task.get("task_id"))
            if not isinstance(pane_id, str):
                live[task_id] = {"error": "task has no pane_id"}
                continue
            response = run_capture(
                [runtime.herdr_bin, "--session", runtime.session, "agent", "get", pane_id]
            )
            if response.returncode == 0:
                try:
                    live[task_id] = json.loads(response.stdout)
                except json.JSONDecodeError:
                    live[task_id] = {"raw": response.stdout.strip()}
            else:
                live[task_id] = {"error": (response.stderr or response.stdout).strip()}
    payload = {"session": runtime.session, "tasks": selected, "live": live}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for task in selected:
            print(
                f"P{task.get('priority')} {task.get('title')} [{task.get('status')}] "
                f"preset={task.get('preset')} pane={task.get('pane_id')}"
            )
            print(f"  worktree: {task.get('worktree_path')}")
            if task.get("error"):
                print(f"  error: {task.get('error')}")
            task_live = live.get(str(task.get("task_id")))
            if task_live is not None:
                print(f"  live: {json.dumps(task_live, sort_keys=True)}")
    return 0


BATCH_KEYS = {
    "repo",
    "task",
    "preset",
    "agent",
    "priority",
    "base",
    "prompt",
    "prompt_file",
    "worktree_path",
    "allow_dirty",
    "focus",
    "no_focus",
    "json",
    "mock_state",
}


def batch_specs(args: argparse.Namespace) -> tuple[list[LaunchSpec], Path]:
    if args.file == "-":
        source = sys.stdin.read()
        base_dir = Path.cwd()
    else:
        path = expanded_path(args.file)
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as error:
            raise ToolError(f"cannot read batch file: {error}") from error
        base_dir = path.parent
    try:
        payload = json.loads(source)
    except json.JSONDecodeError as error:
        raise ToolError(f"invalid batch JSON: {error}") from error
    if not isinstance(payload, list) or not payload:
        raise ToolError("batch file must contain a non-empty JSON array")
    specs: list[LaunchSpec] = []
    for index, item in enumerate(payload, 1):
        if not isinstance(item, dict):
            raise ToolError(f"batch item {index} must be an object")
        unknown = set(item) - BATCH_KEYS
        if unknown:
            raise ToolError(f"batch item {index} has unknown fields: {', '.join(sorted(unknown))}")
        if not isinstance(item.get("repo"), str) or not isinstance(item.get("task"), str):
            raise ToolError(f"batch item {index} requires string fields repo and task")
        priority = item.get("priority", args.priority)
        if priority is not None and (not isinstance(priority, int) or isinstance(priority, bool)):
            raise ToolError(f"batch item {index} priority must be an integer")
        for key in ("allow_dirty", "focus", "no_focus", "json"):
            if key in item and not isinstance(item[key], bool):
                raise ToolError(f"batch item {index} field {key} must be boolean")
        specs.append(
            LaunchSpec(
                repo=item["repo"],
                task=item["task"],
                preset=item.get("preset", args.preset),
                agent=item.get("agent", args.agent),
                priority=priority,
                base=item.get("base", args.base),
                prompt=item.get("prompt", ""),
                prompt_file=item.get("prompt_file"),
                worktree_path=item.get("worktree_path"),
                allow_dirty=item.get("allow_dirty", args.allow_dirty),
                focus=item.get("focus", args.focus),
                no_focus=item.get("no_focus", args.no_focus),
                json_output=item.get("json", args.json),
                mock_state=item.get("mock_state"),
            )
        )
    return specs, base_dir


def command_batch(args: argparse.Namespace) -> int:
    runtime = resolve_runtime(args)
    presets = load_presets(runtime)
    specs, base_dir = batch_specs(args)
    commands: list[tuple[int, LaunchSpec, list[str], str, dict[str, Any]]] = []
    for index, spec in enumerate(specs, 1):
        command, preset = build_launch_command(
            runtime, presets, spec, base_dir=base_dir
        )
        plan = launch_plan(
            runtime, presets, spec, command, base_dir=base_dir
        )
        commands.append((index, spec, command, preset, plan))
    if args.dry_run:
        print(f"session={runtime.session} parallel={args.parallel}")
        for index, spec, command, preset, plan in commands:
            print(
                f"[{index}] task={spec.task!r} preset={preset} priority=P{plan['priority']} "
                f"base={plan['base']} dirty={plan['dirty_changes']} "
                f"would_refuse_dirty={plan['would_refuse_dirty']} prompt_chars={plan['prompt_chars']}"
            )
            print(f"    {redacted_command(command)}")
        return 0

    require_server(runtime)
    environment = runtime_environment(runtime)

    def worker(command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
        )

    outcomes: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=args.parallel) as executor:
        pending = {
            executor.submit(worker, command): (index, spec, preset)
            for index, spec, command, preset, _plan in commands
        }
        for future in as_completed(pending):
            index, spec, preset = pending[future]
            result = future.result()
            outcome = {
                "index": index,
                "task": spec.task,
                "preset": preset,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
            outcomes.append(outcome)
            print(f"[{index}] {spec.task}: {'ok' if result.returncode == 0 else 'failed'}")
            if result.stdout.strip():
                print(result.stdout.rstrip())
            if result.stderr.strip():
                print(result.stderr.rstrip(), file=sys.stderr)
    outcomes.sort(key=lambda item: item["index"])
    if args.summary_json:
        safe = [
            {
                "index": item["index"],
                "task": item["task"],
                "preset": item["preset"],
                "returncode": item["returncode"],
            }
            for item in outcomes
        ]
        print(json.dumps(safe, indent=2, sort_keys=True))
    return 1 if any(item["returncode"] != 0 for item in outcomes) else 0


def add_runtime_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--session", help="named Herdr session; auto-discovers when omitted")
    parser.add_argument("--herdr-bin", help="exact Herdr binary to use")
    parser.add_argument("--corral-bin", help="exact Design 1 plugin/bin/corral path")
    parser.add_argument("--plugin-root", help="exact Design 1 plugin directory")
    parser.add_argument("--config-dir", help="Corral plugin config directory")
    parser.add_argument("--state-dir", help="Corral plugin state directory")
    parser.add_argument("--store-path", help="override Corral SQLite database path")
    parser.add_argument("--socket-path", help="Herdr session socket path")


def add_launch_options(parser: argparse.ArgumentParser, *, require_target: bool) -> None:
    parser.add_argument("--repo", required=require_target, help="repository checkout path")
    parser.add_argument("--task", required=require_target, help="Corral task title")
    parser.add_argument("--preset", help="Corral preset name; auto-selects one Pi preset")
    parser.add_argument("--agent", choices=SUPPORTED_AGENTS, help="agent kind used to select a preset")
    parser.add_argument("--priority", type=int, choices=range(1, 5), help="P1 through P4")
    parser.add_argument("--base", help="Git base ref; otherwise use the preset base")
    parser.add_argument("--prompt", default="", help="task prompt sent after agent readiness")
    parser.add_argument("--prompt-file", help="UTF-8 file containing the task prompt")
    parser.add_argument("--worktree-path", help="exact destination for the new worktree")
    parser.add_argument("--allow-dirty", action="store_true", help="proceed without dirty primary changes")
    focus = parser.add_mutually_exclusive_group()
    focus.add_argument("--focus", action="store_true", help="focus the new workspace")
    focus.add_argument("--no-focus", action="store_true", help="do not steal focus")
    parser.add_argument("--json", action="store_true", help="request native Corral JSON output")
    parser.add_argument(
        "--mock-state",
        choices=("idle", "working", "blocked", "unknown"),
        help="Corral smoke-test only; never use for real agents",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="corral_agents.py",
        description="Launch and inspect Corral Design 1 agents from outside Herdr.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    doctor = commands.add_parser("doctor", help="check Corral, Herdr, Pi, paths, and session")
    add_runtime_options(doctor)
    doctor.add_argument("--json", action="store_true")

    presets = commands.add_parser("list-presets", help="list available Corral presets safely")
    add_runtime_options(presets)
    presets.add_argument("--agent", choices=SUPPORTED_AGENTS)
    presets.add_argument("--json", action="store_true")

    launch = commands.add_parser("launch", help="launch one new Corral task")
    add_runtime_options(launch)
    add_launch_options(launch, require_target=True)
    launch.add_argument("--dry-run", action="store_true", help="resolve and print without launching")

    status = commands.add_parser("status", help="read persisted Corral task state")
    add_runtime_options(status)
    status.add_argument("--task", help="exact task title or ID")
    status.add_argument("--live", action="store_true", help="also query Herdr's live agent state")
    status.add_argument("--full", action="store_true", help="include full stored task records")
    status.add_argument("--json", action="store_true")

    batch = commands.add_parser("batch", help="launch a JSON array of Corral tasks")
    add_runtime_options(batch)
    batch.add_argument("--file", required=True, help="JSON file, or - for stdin")
    batch.add_argument("--preset", help="default preset for entries")
    batch.add_argument("--agent", choices=SUPPORTED_AGENTS, help="default agent kind")
    batch.add_argument("--priority", type=int, choices=range(1, 5), help="default priority")
    batch.add_argument("--base", help="default Git base")
    batch.add_argument("--allow-dirty", action="store_true", help="default dirty policy")
    focus = batch.add_mutually_exclusive_group()
    focus.add_argument("--focus", action="store_true", help="focus new workspaces by default")
    focus.add_argument("--no-focus", action="store_true", help="do not focus new workspaces")
    batch.add_argument("--json", action="store_true", help="request native JSON per launch")
    batch.add_argument("--parallel", type=int, default=3, choices=range(1, 33))
    batch.add_argument("--dry-run", action="store_true")
    batch.add_argument("--summary-json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handlers = {
        "doctor": command_doctor,
        "list-presets": command_list_presets,
        "launch": command_launch,
        "status": command_status,
        "batch": command_batch,
    }
    try:
        return handlers[args.command](args)
    except (ToolError, OSError, subprocess.SubprocessError) as error:
        print(f"corral-launch-agents: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
