"""Notepad-specific UI context for test cases."""

from ui_tests.contexts.generic import SIMPLE_APP_CONTEXT

NOTEPAD_CONTEXT = SIMPLE_APP_CONTEXT + """

Notepad (Windows 11) specific knowledge:

Window identification:
- Title bar shows the current file name (or "Untitled - Notepad" for new files).
- Main menu bar: File, Edit, Format, View, Help.
- Content area is a single large text editing control.

File operations:
- File -> New: Creates a new empty document (Ctrl+N).
- File -> Open...: Opens file dialog (Ctrl+O).
- File -> Save: Saves current file (Ctrl+S). If untitled, opens Save As dialog.
- File -> Save As...: Opens Save As dialog to choose name/location (Ctrl+Shift+S).
- File -> Exit: Closes Notepad (prompts to save if unsaved changes).

Edit operations:
- Edit -> Undo / Redo (Ctrl+Z / Ctrl+Y).
- Edit -> Cut / Copy / Paste (Ctrl+X / Ctrl+C / Ctrl+V).
- Edit -> Select All (Ctrl+A).
- Edit -> Find... / Replace... (Ctrl+F / Ctrl+H).

Text input:
- Click anywhere in the white content area to set cursor position.
- Type normally; Backspace, Delete, arrow keys work as expected.
- Enter creates new lines.
- Text wraps at window edge (unless Format -> Word Wrap is off).

Save As dialog:
- Standard Windows file dialog with address bar, file list, file name field.
- "Save as type" dropdown defaults to "Text Documents (*.txt)".
- Click "Save" button to confirm; "Cancel" to abort.
- If file exists, confirmation dialog appears: "Replace?" Yes/No.

Confirmation dialogs:
- Unsaved changes on close/New/Open: "Do you want to save changes to <file>?"
  Buttons: Save, Don't Save, Cancel.
- Save As overwrite: "<file> already exists. Replace it?" Yes/No.

Keyboard shortcuts:
- Ctrl+N: New
- Ctrl+O: Open
- Ctrl+S: Save
- Ctrl+Shift+S: Save As
- Ctrl+Z: Undo
- Ctrl+Y: Redo
- Ctrl+X: Cut
- Ctrl+C: Copy
- Ctrl+V: Paste
- Ctrl+A: Select All
- Ctrl+F: Find
- Ctrl+H: Replace
"""