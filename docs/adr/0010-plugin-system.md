# ADR-0010: Plugin System

**Status:** Accepted | **Date:** 2026-07-01

## Decision

Dual plugin tiers: Kernel plugins (`IPlugin` / runtime events) and Framework plugins (`IFrameworkPlugin` / company lifecycle events). Plugins extend; never modify core source.

Categories: Memory, Metrics, Dashboard, GitHub, Cloud, Notifications, Marketplace, AI Providers (via adapter), Security, Analytics.

## References

- [plugin-architecture.md](../framework/plugin-architecture.md)
