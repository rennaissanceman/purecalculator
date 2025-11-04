import warnings
from math import isclose, isfinite
from sys import float_info
from typing import Optional

__all__ = ["Calculator", "NEAR_ZERO_TOL", "ACTIONS", "main"]

# --- 1) Constants / configuration -------------------------------------------------
ACTIONS = {
    "1": ("Addition", "+", "add"),
    "2": ("Subtraction", "-", "subtract"),
    "3": ("Multiplication", "*", "multiply"),
    "4": ("Division", "/", "divide"),
}

NEAR_ZERO_TOL = 1e-12  # default tolerance "close to zero"


# --- 2) Core-helpers (without I/O) -----------------------------------------------
def _finite_or_none(value: float, op_name: str) -> Optional[float]:
    """Return the value only if it is finite; otherwise, return None + warning."""
    if not isfinite(value):
        warnings.warn(f"{op_name} produced a non-finite result (inf/NaN).", stacklevel=2)
        return None
    return value


# --- 3) Logic (core) --------------------------------------------------------------
class Calculator:
    """Pure calculations; without I/O (print/input)."""

    def __init__(self, op1: float, op2: float):
        self._op1 = op1
        self._op2 = op2

    def add(self) -> Optional[float]:
        # can give inf for very large values
        return _finite_or_none(self._op1 + self._op2, "addition")

    def subtract(self) -> Optional[float]:
        return _finite_or_none(self._op1 - self._op2, "subtraction")

    def multiply(self) -> Optional[float]:
        # pre-check overflow: |x| > max / |y|
        x, y = self._op1, self._op2
        if isfinite(x) and isfinite(y):
            ay = abs(y)
            if ay != 0.0 and abs(x) > float_info.max / ay:
                warnings.warn(
                    "multiplication would overflow (|x|*|y| > max_float).",
                    stacklevel=2,
                )
                return None
        return _finite_or_none(x * y, "multiplication")

    def divide(self, tol: float = NEAR_ZERO_TOL) -> Optional[float]:
        x, y = self._op1, self._op2

        # 1) division by zero/near-zero/NaN/Inf
        if not isfinite(y) or isclose(y, 0.0, abs_tol=tol):
            warnings.warn("attempt to divide by (near) zero.", stacklevel=2)
            return None

        # 2) pre-check overflow: |x|/|y| > max_float  ->  |x| > max_float * |y|
        if isfinite(x) and abs(x) > float_info.max * abs(y): # pragma: no cover
            warnings.warn(
                "division would overflow (|x|/|y| > max_float).",
                stacklevel=2,
            )
            return None

        # 3) proper division + verification
        return _finite_or_none(x / y, "division")


# --- 4) CLI (I/O) ---------------------------------------------------------------
def _parse_number(prompt: str) -> float:
    """Load a number (decimal point or comma), discard NaN/Inf."""
    while True:
        s = input(prompt).strip().replace(",", ".")
        try:
            x = float(s)
            if not isfinite(x):
                print("Error: Not a Number or Infinity are not allowed. Try again.")
                continue
            return x
        except ValueError:
            print("Error: enter a correct number (e.g., 3.14).")


def _ask_menu() -> str:
    """Display the menu and return the user's selection (string)."""
    print("\nSelect an action by entering the number:")
    for k in sorted(ACTIONS.keys(), key=int):
        label, symbol, _ = ACTIONS[k]
        print(f"{k}. {label} ({symbol})")
    return input("Your selection (1-4): ").strip()


def _run_action(calc: Calculator, choice: str) -> Optional[float]:
    """Run the selected operation; no if/elif – dispatch by method name."""
    action = ACTIONS.get(choice)
    if not action:
        print("Incorrect selection. Select 1–4.")
        return None
    _label, symbol, method_name = action
    func = getattr(calc, method_name, None)
    if func is None:
        print("Internal error: operation not implemented.")
        return None
    result = func()
    if result is not None:
        print(f"RESULT ({symbol}): {result}")
    return result


def _ask_quit() -> bool:
    """Returns True if the user wants to quit."""
    s = input("\nDo you want to quit (y/n): ").strip().lower()
    return s.startswith("y")


def main() -> None:
    """CLI main loop."""
    print("=== WELCOME TO PURE CALCULATOR ===")
    print("\n--- I'm launching the user interface. ---")
    while True:
        op1 = _parse_number("\nEnter the first number: ")
        op2 = _parse_number("Enter the second number: ")
        calc = Calculator(op1, op2)

        choice = _ask_menu()
        try:
            _run_action(calc, choice)
        except Exception as e:  # noqa: BLE001
            # in a real app: log stack trace
            print(f"An unexpected error has occurred: {e}")

        if _ask_quit():
            print("GOOD BYE! / SEE YOU LATER ALLIGATOR!!!")
            break


# --- 5) Demo (optional) ---------------------------------------------------------
def demo_tests() -> None: # pragma: no cover
    """Simple demonstrations (do not replace testing)."""
    print("\nSample tests for the Calculator class:")
    c1 = Calculator(10, 2)
    print(f"10 + 2 = {c1.add()}")
    print(f"10 - 2 = {c1.subtract()}")
    print(f"10 * 2 = {c1.multiply()}")
    print(f"10 / 2 = {c1.divide()}")

    c2 = Calculator(5, 0)
    print(f"5 / 0 = {c2.divide()}")  # WARNING + None

    c3 = Calculator(5, 1e-308)
    print(f"5 / 1e-308 = {c3.divide()}")  # WARNING overflow + None

    c4 = Calculator(float_info.max, 2.0)
    print(f"max * 2 = {c4.multiply()}")  # WARNING + None


# --- 6) Enter -------------------------------------------------------------------
if __name__ == "__main__": # pragma: no cover
    # Choose what to run:
    # demo_tests()
    main()
