# Docker Desktop startup on this Windows machine

**Resolved on 2026-09-18:** Docker Desktop 4.91.0 now reports a working Docker Engine 29.8.0 Linux/amd64 server. Image build, Linux tests, live OpenAI HTTP requests, and Compose startup have passed. No further Windows feature changes are needed on this machine. See [verification evidence](VERIFICATION.md).

The following instructions document the earlier failure and are retained for troubleshooting another installation. The earlier backend reported:

```text
engine linux/wsl failed to start: checking preconditions: Virtual Machine Platform not enabled
```

If this specific error occurs, Windows feature activation and the required restart need a local administrator; the application code cannot fix this prerequisite. No registry credentials or API key are needed for that step.

1. Save your work. Open **PowerShell as Administrator**.
2. Enable the feature identified by Docker:

   ```powershell
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   wsl --install --no-distribution --web-download
   ```

3. Restart Windows when installation finishes. No restart has been triggered automatically.
4. Open Docker Desktop, allow it to finish starting, and verify:

   ```powershell
   wsl --version
   docker version
   ```

   Docker documents WSL 2.1.5 or newer as its minimum. `docker version` must show a working **Server**, not just the CLI client.
5. Return to the project and run the Docker build/run checks in the README. Once the engine is working, the remaining image verification can be automated.

If startup still reports virtualization unavailable after enabling the feature and restarting, check firmware virtualization or nested-virtualization support with the machine administrator. The disabled Windows feature is the error observed here; firmware configuration has not been changed.

Sources: [Microsoft WSL installation](https://learn.microsoft.com/en-us/windows/wsl/install), [WSL command options](https://learn.microsoft.com/en-us/windows/wsl/basic-commands), [Docker WSL backend requirements](https://docs.docker.com/desktop/features/wsl/).
