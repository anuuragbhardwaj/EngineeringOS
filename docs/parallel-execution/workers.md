# Worker Guide

Workers are provider-independent execution units carrying employee, context, knowledge, and artifacts.

Workers execute via `ThreadPoolExecutor` with artifact locks for safe concurrent access.
