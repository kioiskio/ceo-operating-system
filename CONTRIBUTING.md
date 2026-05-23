# Contributing to CEO Operating System

Thanks for contributing. This project has a clear standard: **every submission must be immediately usable, not just informative.**

## What We Accept

- **Tools:** Runnable scripts or applications that solve a specific founder problem.
- **Frameworks:** Decision trees, playbooks, or structured methodologies with clear inputs and outputs.
- **Templates:** Documents, spreadsheets, or outlines that can be directly copied and used.

## What We Don't Accept

- Link collections or reading lists (there are already dozens of those).
- Abstract advice without a concrete deliverable.
- Content that requires paid subscriptions to be useful.

## Submission Guidelines

### For Tools

- Include a `README.md` explaining what problem it solves, how to run it, and what output to expect.
- Must be self-contained. Minimize external dependencies.
- Python tools: use standard library where possible. If you need a dependency, add it to the root `requirements.txt`.
- Provide example input and expected output in the tool's README.

### For Frameworks

- Use Mermaid diagrams for decision trees where applicable.
- Include: trigger condition → decision criteria → recommended action → next steps.
- Tag the applicable company stage(s).

### For Templates

- Include brief instructions at the top explaining when and how to use it.
- Mark sections that need customization with `[FILL_THIS]` or `{{ placeholder }}`.

## Pull Request Process

1. Fork the repo and create a branch.
2. Add your contribution in the appropriate directory.
3. Ensure your tool runs without errors.
4. Update the root README table of contents if adding a new tool/framework/template.
5. Open a PR with a clear description of what problem your contribution solves.

## Code Style

- Python: PEP 8, type hints preferred.
- Markdown: Use sentence-case headers, keep line length reasonable.
- JavaScript/TypeScript: Prettier defaults.