# Inventory scope

The inventory lists common development tools; they are not all required.
Run checks with the same OS, shell, PATH, and Python environment as the task.

| Tool | Typical use |
| --- | --- |
| Python | Scripts; its interpreter determines which Python distributions are visible |
| Node.js | JavaScript tooling |
| Git | Repository operations |
| curl | HTTP transfers |
| jq | JSON processing |
| gh | GitHub operations; a version check does not verify account access |
| rg | Text search |
| fd / fdfind | File search; names vary by distribution |
| ffmpeg | Media conversion |
| bat / batcat | File viewing; names vary by distribution |
| uv | Python environment and package management |

Optional Python distributions: `requests` for HTTP, `Pillow` for images, `pandas`
for tabular data, `openpyxl` for Excel, `python-docx` for Word, `pypdf` for PDFs.
The helper reads `importlib.metadata` without importing these packages.
Finding metadata does not establish that imports or native extensions work.

The helper prints the exact interpreter used for checks and suggested commands.
It does not require pip. To check packages in another Python environment, select
that environment's interpreter explicitly.

Windows suggestions use `winget install --id ID --exact` for each known missing
tool. Before an authorized install, verify WinGet availability, sources, package
IDs, and versions. Do not assume a fixed executable location.

Follow the project's environment and dependency rules. If it has no Python
environment, these commands illustrate creating one and installing a package:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install package-name
```

```powershell
python -m venv .venv
& '.venv/Scripts/python.exe' -m pip install package-name
```

Do not run these examples as part of the inventory. Do not bypass protections
on externally managed Python, change execution policies, or run downloaded shell
code to check the environment.

References:

- [Python distribution metadata](https://docs.python.org/3/library/importlib.metadata.html)
- [Python virtual environments](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/)
- [WinGet install command](https://learn.microsoft.com/en-us/windows/package-manager/winget/install)
