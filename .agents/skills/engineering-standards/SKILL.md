---
name: engineering-standards
description: Enforces the architectural guidelines, naming conventions, directory structure, type-safety, and design principles of the HOGC platform and its engines.
---

# HOGC Engineering Standards & Architecture Guidelines

This skill loads the HOGC coding handbook into the context of the AI agent. Use this skill when modifying, creating, or refactoring code in the `platform-crud-engine` repository.

## Instructions

1. When writing, designing, or refactoring code in this repository, always align with the rules and principles in the detailed handbook: [engineering_standards.md](file:///v:/crud_engine/eng_standard/platform-crud-engine/.agents/skills/engineering-standards/references/engineering_standards.md).
2. Specifically ensure compliance with:
   - **Architectural Layers**: concentric outer-to-inner dependency flow.
   - **Folder Standards**: strict directory structure rules.
   - **Naming Conventions**: descriptive, literal names with clear Boolean prefixes (`is_`, `has_`, etc.).
   - **Type Safety**: strict type declarations on all functions; the use of `typing.Any` is strictly forbidden.
   - **DTOs and Services**: stateless orchestration layer design.
