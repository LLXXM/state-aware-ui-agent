# Computer-Use-Agent

Windows UI agent prototype for controlled ibaPDA test cases using Ollama and
Qwen 3.5. The agent observes screenshots, proposes structured computer actions,
records mouse-target overlays, and can optionally verify targets before clicks.

## Structure

```text
Computer-Use-Agent/
  see_think_act_agent.py       Core see-think-act loop
  config.py                    Runtime and safety defaults
  ui_contexts.py               ibaPDA-specific visual knowledge
  utils/                       Ollama client and action execution
  ui_tests/
    run_test_case.py           Single test-case runner
    test_cases/                Executable test-case definitions
      tf_00.py                 Data Recording start/stop cycle
    support/                   Cleanup and window-management helpers
  tests/                       Automated unit tests
  artifacts/ui_tests/          Generated run screenshots, ignored by Git
```

## Remote Ollama Setup

In the current setup, the Computer-Use-Agent runs in the VM while Ollama runs
on the server laptop at `192.168.21.148`. By default Ollama accepts requests
only from the same machine, so the server must first be exposed to the local
network.

### Server Laptop

On the laptop that runs Ollama, open PowerShell and make the Ollama API listen
on all local network interfaces:

```powershell
setx OLLAMA_HOST "0.0.0.0:11434"
```

Install or confirm the multimodal model intended for the UI agent:

```powershell
ollama pull qwen3.5:9b
ollama list
```

Restart Ollama after setting `OLLAMA_HOST`. When launching the server manually
for a test session, the equivalent temporary configuration is:

```powershell
$env:OLLAMA_HOST = "0.0.0.0:11434"
ollama serve
```

If the VM cannot connect, allow inbound TCP traffic to Ollama through Windows
Firewall. Run this on the server laptop in an Administrator PowerShell:

```powershell
New-NetFirewallRule -DisplayName "Ollama API from VM" `
  -Direction Inbound -Protocol TCP -LocalPort 11434 `
  -Profile Private -Action Allow
```

For a tighter rule, additionally provide the VM IP via
`-RemoteAddress <IP-DER-VM>`.

### VM / Agent Machine

From the VM, first verify that the remote Ollama endpoint is reachable:

```powershell
Invoke-RestMethod http://192.168.21.148:11434/api/tags
```

The returned model list must contain the selected model, for example
`qwen3.5:9b`. Set endpoint and model in the PowerShell session that starts the
agent:

```powershell
$env:OLLAMA_HOST = "http://192.168.21.148:11434"
$env:OLLAMA_MODEL = "qwen3.5:9b"
$env:OLLAMA_NUM_CTX = "32768"
$env:OLLAMA_NUM_PREDICT = "1024"
$env:OLLAMA_THINK = "true"
$env:VERIFY_MOUSE_TARGETS = "false"
```

These variables apply to the current PowerShell session. To persist the VM
configuration for future sessions:

```powershell
setx OLLAMA_HOST "http://192.168.21.148:11434"
setx OLLAMA_MODEL "qwen3.5:9b"
setx OLLAMA_NUM_CTX "32768"
setx OLLAMA_NUM_PREDICT "1024"
setx OLLAMA_THINK "true"
setx VERIFY_MOUSE_TARGETS "false"
```

Open a new PowerShell terminal after using `setx`.

## Run A Test Case

With the remote environment variables configured, run TF-00 from the VM:

```powershell
py -m ui_tests.run_test_case TF-00
```

`TF-00` cleans up an existing ibaPDA Client window if needed, opens ibaPDA,
starts Data Recording, verifies the running state, stops recording, verifies
the stopped state, and closes the client safely.

Without environment variables, the project connects to local Ollama at
`http://127.0.0.1:11434`, uses `qwen3.5`, and requests a context window of
`32768` tokens. The defaults are intentionally tuned for maximum recognition
quality first: `OLLAMA_THINK=true` and `OLLAMA_NUM_PREDICT=1024`. Once a test
case is visually reliable, reduce these values step by step to trade quality
for speed. Values near `4096` may truncate screenshot and tool instructions for
UI test cases.

By default, proposed clicks execute immediately after their overlay is saved,
which makes wrong clicks visible during VM debugging and avoids a second slow
model request. To restore pre-click visual verification for a run:

```powershell
$env:VERIFY_MOUSE_TARGETS = "true"
```

## Add A Test Case

Create a module such as `ui_tests/test_cases/tf_01.py` containing a
`UiTestCase` instance named `CASE`. Each case defines its task text, allowed
actions, optional UI context, limits, and whether ibaPDA cleanup is required.
Tests that do not activate Data Recording use the same runner and simply omit
recording actions from their task.

## Safety

- Move the mouse to the top-left corner to trigger the `pyautogui` failsafe.
- Mouse targets are always saved as overlays. Pre-click visual verification is
  optional through `VERIFY_MOUSE_TARGETS=true`.
- ibaPDA cleanup prevents duplicate client instances and avoids leaving Data
  Recording active after a test case.

## Verify

```powershell
python -m unittest discover -s tests -v
```
