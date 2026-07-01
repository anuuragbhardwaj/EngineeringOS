# Scheduler Guide

`ExecutionScheduler` builds plans, spawns workers, tracks dependencies, and supports pause/resume/cancel.

Plans consist of parallel groups with `wait_all` barriers between groups.
