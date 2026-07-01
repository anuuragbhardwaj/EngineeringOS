"""Framework API implementations."""

from company_core.api.company import CompanyAPI
from company_core.api.framework import FrameworkAPI
from company_core.api.manifest import ManifestAPI
from company_core.api.mcp import McpAPI
from company_core.api.project import ProjectAPI
from company_core.api.context import ContextAPI
from company_core.api.workspace import WorkspaceAPI
from company_core.api.knowledge import KnowledgeAPI
from company_core.api.autonomous_company import AutonomousCompanyAPI
from company_core.api.parallel_execution import ParallelExecutionAPI
from company_core.api.source_control import RepositoryAPI, SourceControlAPI
from company_core.api.stubs import EmployeeAPI, IntegrationAPI

__all__ = [
    "AutonomousCompanyAPI",
    "CompanyAPI",
    "ContextAPI",
    "EmployeeAPI",
    "FrameworkAPI",
    "IntegrationAPI",
    "KnowledgeAPI",
    "ManifestAPI",
    "McpAPI",
    "ParallelExecutionAPI",
    "ProjectAPI",
    "RepositoryAPI",
    "SourceControlAPI",
    "WorkspaceAPI",
]
