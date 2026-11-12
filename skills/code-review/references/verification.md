# Choose checks for the project

Use this table to find checks for the affected platform and workflow.
The rows are examples, not required commands or an exhaustive list of platforms.
Find the actual commands, SDK versions, targets, and required checks in the
project. Do not run every row.

| Project or change | Where to find checks | What to verify when relevant |
| --- | --- | --- |
| JS/TS, HTML/CSS, web | Manifests, lockfiles, CI, build/test configuration; simple pages may have no build | Logic, resource loading, DOM, styles, forms, keyboard use, viewport, and affected browser workflows. Do not introduce npm just to review a static page. |
| Browser extension | Manifest, scripts, loading instructions, tests | Target browser/version, permissions, CSP, required extension contexts. Reload content/background/manifest changes as the project requires. An ordinary web page does not replace a loaded extension. |
| Backend or full stack, including Laravel/Nuxt | Manifests, CI, routes, schemas, test environment | Client/server contracts, permissions, validation, writes and reads. Run migrations only in an authorized test environment. |
| Game engine, including Godot | Engine project files, scenes/resources, engine version, CI/export/test scripts | Resource loading, input, lifecycle, saves, physics, and frame behavior affected by the diff. Headless runs do not verify visuals; browsers apply only to web targets. |
| C#/.NET or native desktop | Solution/project files, SDK configuration, CI, test runner, target frameworks | Project build, analysis, and tests; run the app for UI changes. A Windows build does not establish behavior on other targets. |
| Flutter/Dart | Manifest, SDK constraints, CI, tests, selected target | Project analysis, unit/widget/integration checks, and app behavior on the target platform or emulator. Widget tests do not verify platform plugins. |
| Python, scripts, CLI | Manifests, lockfiles, CI, wrappers, test configuration | Interpreter/environment, inputs, outputs, exit codes, paths, encodings, errors, side effects. An executable on PATH does not establish a working interpreter. |
| Playwright or other automated tests | Configuration, projects, fixtures, setup, CI scripts | Whether assertions detect the real defect; waits, isolation, cleanup, flakiness; correct browser/project. A regression test must fail on the defective version for the intended reason. |
| Other toolchain | Project instructions, manifests, build/test scripts, CI | Trace input → behavior → observable result. Do not substitute commands from a familiar stack. |

For each run, record:

- Purpose, code version, executed copy, and cwd.
- Available tools, services, target runtime, and actual versions.
- Command or actions, expected result, completion, exit code or observation,
  and key output.
- Data and artifacts changed by the command; how user data is protected.
- Checks you could not perform and the specific obstacle. Do not count skips as passes.

PowerShell, cmd, and Bash differ in quoting, variables, redirection, and error
handling. Use the actual shell's syntax. Check WSL paths and runtimes separately;
a Windows installation does not establish WSL availability, or vice versa.

State separately what static analysis, compilation, unit tests, integration
checks, and interactive runs verified. Choose checks that cover the change.
Do not claim outcomes those checks did not establish.
