"""Calculator-specific UI context for test cases."""

from ui_tests.contexts.generic import SIMPLE_APP_CONTEXT

CALCULATOR_CONTEXT = SIMPLE_APP_CONTEXT + """

Calculator (Windows 11) specific knowledge:

Window identification:
- Title bar shows "Calculator".
- Main area has a display at the top showing the current value/expression.
- Below the display: a grid of buttons for digits, operators, and functions.

Modes (via hamburger menu top-left):
- Standard: Basic arithmetic (+, -, *, /, %, sqrt, x^2, 1/x).
- Scientific: Adds trig, log, exp, constants, etc.
- Programmer: Hex/Dec/Oct/Bin, bitwise ops.
- Date Calculation: Date difference, add/subtract days.
- Converter: Volume, length, weight, temperature, etc.
Default is Standard mode.

Standard mode layout (approximate):
Row 1: MC, MR, M+, M-, MS, M (memory)
Row 2: %, sqrt, x^2, 1/x
Row 3: CE, C, Backspace, /
Row 4: 7, 8, 9, *
Row 5: 4, 5, 6, -
Row 6: 1, 2, 3, +
Row 7: +/-, 0, ., =

Display:
- Shows current entry or full expression (e.g., "2 + 3").
- After "=", shows result.
- Can be copied via right-click -> Copy or Ctrl+C.

Button interaction:
- Click a digit/button to append to expression.
- Operators (+, -, *, /) set pending operation.
- "=" evaluates and shows result.
- "C" clears all; "CE" clears current entry only.
- Backspace deletes last digit/char from current entry.
- Memory buttons: MC (clear), MR (recall), M+ (add), M- (subtract), MS (store).

Keyboard support:
- Number keys, numpad: enter digits.
- +, -, *, /: operators.
- Enter or =: evaluate.
- Escape: clear (C).
- Backspace: delete last digit.
- Ctrl+C: copy display value.
- Ctrl+V: paste into display (if valid number).

Scientific mode additions (when switched):
- Trig: sin, cos, tan, sinh, cosh, tanh
- Inverse: sin^-1, cos^-1, tan^-1
- Log/exp: log, ln, e^x, 10^x
- Powers: x^y, x^2, x^3, 10^x
- Constants: pi, e
- Deg/Rad/Grad toggle

Mode switching:
- Click hamburger menu (top-left) -> select mode.
- Mode change preserves current value in Standard/Scientific.

History (Standard/Scientific):
- Click history button (top-right) to show past calculations.
- Click a history item to load it.
- Clear history via trash icon.
"""