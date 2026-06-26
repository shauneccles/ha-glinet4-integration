# Development

This repo uses the standard Home Assistant custom-integration workflow — the
[`ludeeus/integration_blueprint`](https://github.com/ludeeus/integration_blueprint)
pattern (VS Code devcontainer + `scripts/develop`), adapted to this project's
[`uv`](https://docs.astral.sh/uv/) tooling. Home Assistant runs from the project
virtualenv with `custom_components/glinet` loaded live; edit, restart, repeat.

> **Which OS?** Home Assistant is developed on Unix-like systems. The
> devcontainer below is a Linux container, so it works identically on Windows,
> macOS and Linux — everything (including `scripts/develop`) runs inside the
> container, and your host OS doesn't matter. **On Windows, use the devcontainer
> or a [WSL2](https://learn.microsoft.com/windows/wsl/) shell** — don't run the
> scripts from PowerShell.

## Quick start (devcontainer — recommended)

1. Open the repo in VS Code with the **Dev Containers** extension and _Reopen in
   Container_ (or run it in a GitHub Codespace). The image
   ([`.devcontainer/Dockerfile`](.devcontainer/Dockerfile)) bakes in `uv` and the
   system libs; on create it just runs `uv sync` to install Home Assistant + the
   integration.
2. In the integrated terminal:

   ```bash
   scripts/develop
   ```

   Home Assistant starts in debug mode; VS Code forwards **port 8123**. Open
   <http://localhost:8123>.

3. Complete the onboarding wizard **once** (create any account). State is written
   to `config/` (gitignored) and persists across restarts.
4. **Settings → Devices & Services → Add Integration → GL-iNet**, enter your
   router's LAN address (GL-iNet default `192.168.8.1`) and admin password. The
   container reaches your router over the LAN through Docker's outbound NAT, so
   use the same address you'd use from the host. The GL-iNet device should then
   appear with its sensors, switches and device-trackers populated from live
   router data — you're now running against real hardware.

## Quick start (local, without the devcontainer)

Use a Unix-like shell (Linux, macOS, or WSL2 on Windows) with
[`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed. Then:

```bash
uv sync            # install Home Assistant + dev tools + this integration (editable)
scripts/develop    # start HA on http://localhost:8123
```

`uv sync` installs the integration **editable**, so Home Assistant discovers
`custom_components/glinet` automatically — no symlink, no `PYTHONPATH` tricks.
(On Debian/Ubuntu, some optional HA integrations also want `ffmpeg libturbojpeg0
libpcap-dev`; the devcontainer image includes them.)

## The dev loop

- Edit files under `custom_components/glinet/`.
- Stop HA with **Ctrl-C** and re-run `scripts/develop` to load the changes
  (integration Python is not hot-reloaded; a reload of just the config entry from
  the UI only re-runs `async_setup_entry`).
- `scripts/develop` runs HA with `--debug`, so full tracebacks print straight to
  the terminal; the committed `logger:` config (below) adds the integration's
  debug logs.

### Debug logging

The committed [`config/configuration.yaml`](config/configuration.yaml) turns on
debug logging for the integration and its `gli4py` API client by default:

```yaml
logger:
  default: info
  logs:
    custom_components.glinet: debug
    gli4py: debug
```

Edit that file to tune levels (e.g. `default: warning` to quiet the rest of Home
Assistant) — it's the source of truth for the dev instance's logging.

### Resetting

Home Assistant's runtime state (database, `.storage`, onboarding) lives in
`config/` alongside the committed `configuration.yaml`, and is gitignored. Wipe it
for a clean slate — keeping your dev config — and you'll re-onboard and re-add the
integration:

```bash
git clean -dfx config && scripts/develop
```

## Testing a change against the live router

The point of the container is to exercise the integration against a **real
GL-iNet device**, not just unit tests. Once it's added (step 4 above), the device
and its live entity values confirm Home Assistant is talking to your router. To
validate a change end to end:

1. Make your change under `custom_components/glinet/`, then reload (**Ctrl-C** and
   re-run `scripts/develop`).
2. **Verify on the real hardware** — debug logging is already on (above), so the
   integration's calls to the router print straight to the terminal:
   - _read paths_ — the affected sensors/attributes show the right values, and
     the debug log shows the expected API calls succeeding;
   - _write paths_ — toggle the relevant entity (a WiFi network or VPN switch, the
     reboot button) and confirm the **router actually changes**, then that the new
     state is reflected on the next poll.

Your router credentials and config entry persist in `config/`, so you add the
integration only once; every restart reconnects to the router automatically.

> Tip: keep `docker logs -f` / the dev terminal visible while you toggle things —
> the `gli4py: debug` logs show the exact request/response against the router,
> which is the quickest way to see a change working (or failing) live.

## Networking

The container reaches your router over your LAN through Docker's default **bridge
network**: outbound traffic is NAT'd through the host, and your host is already on
the router's network, so its LAN address (e.g. `192.168.8.1`) is reachable. This
behaves the same on **Docker Engine (Linux), Docker Desktop (macOS/Windows) and
WSL2** — no host-specific configuration. Two choices keep it portable:

- You **type the router's IP** when adding the integration, so it never depends on
  mDNS/SSDP discovery (which doesn't cross the container NAT).
- The devcontainer uses the **default bridge**, deliberately not `--network host`
  — host networking behaves differently on Docker Desktop (its "host" is a VM, not
  your machine) and wouldn't see your LAN.

The only requirement is that **the machine running the container can reach the
router's IP**. If you can't connect, confirm the host itself can (ping it or open
its web UI), then rule out a VPN, firewall, or the router sitting on a different
subnet — the container inherits the host's path to the router.

> **Windows + WSL2:** default WSL2 networking reaches a router on your LAN fine
> (the container NATs out through Windows). If a VPN or firewall blocks the path,
> WSL2's [mirrored networking mode](https://learn.microsoft.com/windows/wsl/networking#mirrored-mode-networking)
> (`networkingMode=mirrored` in `.wslconfig`, Windows 11) puts WSL2 directly on
> your LAN and clears it up — it isn't required otherwise.

**Port:** Home Assistant serves on **8123** and the devcontainer forwards it. If
8123 is already taken (e.g. a production Home Assistant on the same machine), VS
Code forwards to the next free local port and notifies you — check the
notification or the **Ports** view for the URL.

## Code quality

CI runs the full pre-commit suite (ruff, mypy, pylint and file checks) with
`uvx`, so `pre-commit` doesn't need to be a project dependency. Run the same
checks locally:

```bash
uvx pre-commit run --all-files       # everything CI enforces
uvx pre-commit install               # optional: run them on every git commit
```

Or invoke a single tool directly through the project environment:

```bash
uv run ruff format . && uv run ruff check . --fix
uv run mypy
uv run pylint custom_components/glinet
```

## Tests

There's no test suite yet (see the TODO in the [README](README.md)). The standard
tool for custom integrations is
[`pytest-homeassistant-custom-component`](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component);
adding it under the `dev` dependency group and a `tests/` directory (mocking the
`gli4py` API) is the recommended next step.

## Notes

- **Python / HA version** come from `requires-python` and the `homeassistant`
  pin in [`pyproject.toml`](pyproject.toml) (the devcontainer's Python is the
  [`Dockerfile`](.devcontainer/Dockerfile) base image); `uv` reproduces the exact
  dependency set from [`uv.lock`](uv.lock).
- **In the devcontainer** the virtualenv lives at `/home/vscode/.venv` (not in
  the workspace), so the host's `.venv` is never reused inside the container, and
  uv's download cache is kept in a named volume for fast rebuilds. Locally, the
  venv is the usual `.venv/` in the project root.
- The default config (`default_config:`) pulls in optional integrations like
  `bluetooth`. If a transitive dependency in the lockfile is skewed from the
  running HA version you may see a non-fatal `Setup failed for 'bluetooth'` at
  startup — it's unrelated to this integration and safe to ignore (or trim
  `default_config` in `config/configuration.yaml` while developing).
