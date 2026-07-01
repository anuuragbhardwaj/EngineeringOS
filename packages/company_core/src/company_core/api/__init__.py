"""Framework API implementations."""

from company_core.api.company import CompanyAPI
from company_core.api.framework import FrameworkAPI
from company_core.api.manifest import ManifestAPI
from company_core.api.mcp import McpAPI
from company_core.api.project import ProjectAPI
from company_core.api.stubs import EmployeeAPI, IntegrationAPI, WorkspaceAPI

__all__ = [
    "CompanyAPI",
    "EmployeeAPI",
    "FrameworkAPI",
    "IntegrationAPI",
    "ManifestAPI",
    "McpAPI",
    "ProjectAPI",
    "WorkspaceAPI",
]
