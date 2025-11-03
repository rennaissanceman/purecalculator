from math import isfinite, isclose
from sys import float_info
from typing import Optional

# --- Operation configuration (single source of truth) ---
ACTIONS = {
    '1': ("Addition",      "+", "sum"),
    '2': ("Subtraction",   "-", "subtract"),
    '3': ("Multiplication","*", "multiply"),
    '4': ("Division",      "/", "divide"),
}

NEAR_ZERO_TOL = 1e-12  # default tolerance “close to zero”

def _finite_or_none(value: float, op_name: str) -> Optional[float]:
    """Return the result, but only if it is finite (not inf/NaN)."""
    if not isfinite(value):
        print(f"WARNING: {op_name} produced a non-finite result (inf/NaN).")
        return None
    return value


class Calculator:
    def __init__(self, op1: float, op2: float):
        self._op1 = op1
        self._op2 = op2

    def sum(self) -> Optional[float]:
        # May go into inf at extremely large numbers
        return _finite_or_none(self._op1 + self._op2, "addition")

    def subtract(self) -> Optional[float]:
        # as above, check just in case
        return _finite_or_none(self._op1 - self._op2, "subtraction")

    def multiply(self) -> Optional[float]:
        # Pre-check: if |op1| > max_float / |op2|, then multiplication overflows
        x, y = self._op1, self._op2
        if isfinite(x) and isfinite(y):
            ay = abs(y)
            if ay != 0.0 and abs(x) > float_info.max / ay:
                print("WARNING: multiplication would overflow (|x|*|y| > max_float).")
                return None
        # Count and verify
        return _finite_or_none(self._op1 * self._op2, "multiplication")

    def divide(self, tol: float = NEAR_ZERO_TOL) -> Optional[float]:
        x, y = self._op1, self._op2

        # 1) Check the divisor: NaN/inf/zero/close to zero
        if not isfinite(y) or isclose(y, 0.0, abs_tol=tol):
            print("WARNING: attempt to divide by (near) zero.")
            return None

        # 2) Pre-check for overflow: |x|/|y| > max_float  => the result would be inf
        #    (note: also works for very small |y|)
        if isfinite(x) and abs(x) > float_info.max * abs(y):
            print("WARNING: division would overflow (|x|/|y| > max_float).")
            return None

        # 3) Count and verify (catch inf/NaN)
        return _finite_or_none(x / y, "division")


def _parse_number(prompt: str) -> float:
    """Reads a number, supports decimal points, and rejects NaN/Inf."""
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
    print("\nSelect an action by entering the number:")
    for k in sorted(ACTIONS.keys(), key=int):
        label, symbol, _ = ACTIONS[k]
        print(f"{k}. {label} ({symbol})")
    return input("Your selection (1-4): ").strip()


def _run_action(calc: Calculator, choice: str) -> Optional[float]:
    """Runs the selected operation without if/elif, returns the result or None."""
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


def main():
    print("=== WELCOME TO PURE CALCULATOR ===")
    try:
        while True:
            op1 = _parse_number("\nEnter the first number: ")
            op2 = _parse_number("Enter the second number: ")
            calc = Calculator(op1, op2)

            choice = _ask_menu()
            try:
                _run_action(calc, choice)
            except Exception as e:
                print(f"An unexpected error has occurred: {e}")

            if _ask_quit():
                print("GOOD BYE! / SEE You Later ALIGATOR!!!")
                break

    except (KeyboardInterrupt, EOFError):
        print("\nExiting gracefully. Bye!")


def demo_tests():
    print("\nSample tests for the Calculator class:")
    c1 = Calculator(10, 2)
    print(f"10 + 2 = {c1.sum()}")
    print(f"10 - 2 = {c1.subtract()}")
    print(f"10 * 2 = {c1.multiply()}")
    print(f"10 / 2 = {c1.divide()}")

    # Division by zero
    c2 = Calculator(5, 0)
    print(f"5 / 0 = {c2.divide()}")  # WARNING + None

    # Division by a tiny number (close to the minimum normal ~2.22e-308)
    c3 = Calculator(5, 1e-308)
    print(f"5 / 1e-308 = {c3.divide()}")  # WARNING overflow + None

    # Multiplication that would overflow
    c4 = Calculator(float_info.max, 2.0)
    print(f"max * 2 = {c4.multiply()}")  # WARNING + None


if __name__ == "__main__":
    demo_tests()
    print("\n--- I'm launching the user interface. ---")
    main()
 #gfgfg