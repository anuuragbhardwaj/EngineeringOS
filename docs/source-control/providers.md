# Provider Guide

All Git operations go through `ProviderRegistry`. No package executes Git directly.

| Provider | ID | Implemented |
|----------|-----|-------------|
| Git | `git` | Yes (default) |
| GitHub | `github` | Extension point |
| GitLab | `gitlab` | Extension point |
| Azure DevOps | `azure_devops` | Extension point |
| Bitbucket | `bitbucket` | Extension point |

MCP integration (Context7, future Git MCP) degrades gracefully — reduced confidence when unavailable.
