# UI Contexts

Application-specific prompt context for UI test cases.

## Modules

- `ibapda.py`: Visual and workflow knowledge for ibaPDA Client, including
  shared controls, proprietary trees, Data Recording behavior, and TF-specific
  contexts.

The test-case scripts import context constants from this package through
`additional_system_prompt`. Keep concrete ibaPDA UI descriptions here rather
than in generic agent or utility modules.
