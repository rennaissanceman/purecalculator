import builtins
import math
import re
from sys import float_info

import pytest

from src.calculator import (
    Calculator,
    _finite_or_none,
    _parse_number,
    _ask_menu,
    _run_action,
    _ask_quit,
    main,
    NEAR_ZERO_TOL,
    ACTIONS,
)


# --- 1) _finite_or_none ---------------------------------------------------------

def test_finite_or_none_returns_value_for_finite():
    assert _finite_or_none(3.14, "test") == 3.14


def test_finite_or_none_returns_none_and_warns_on_inf():
    with pytest.warns(UserWarning, match="non-finite"):
        assert _finite_or_none(float("inf"), "add") is None


def test_finite_or_none_returns_none_and_warns_on_nan():
    with pytest.warns(UserWarning, match="non-finite"):
        val = _finite_or_none(float("nan"), "mul")
        assert val is None


# --- 2) Calculator.add / subtract -----------------------------------------------

@pytest.mark.parametrize("x,y,expected", [
    (2.0, 3.0, 5.0),
    (-1.0, 1.0, 0.0),
    (1e-9, -1e-9, 0.0),
])
def test_add_normal(x, y, expected):
    c = Calculator(x, y)
    assert c.add() == expected


@pytest.mark.parametrize("x,y,expected", [
    (2.0, 3.0, -1.0),
    (-1.0, 1.0, -2.0),
    (1e-9, 1e-9, 0.0),
])
def test_subtract_normal(x, y, expected):
    c = Calculator(x, y)
    assert c.subtract() == expected


def test_add_overflow_goes_to_warning_and_none():
    c = Calculator(float_info.max, float_info.max)
    with pytest.warns(UserWarning, match="non-finite"):
        assert c.add() is None


# --- 3) Calculator.multiply ------------------------------------------------------

def test_multiply_normal():
    c = Calculator(6.0, 7.0)
    assert c.multiply() == 42.0


def test_multiply_precheck_overflow_warns_and_returns_none():
    y = 2.0
    x = float_info.max / abs(y) * 1.1
    c = Calculator(x, y)
    with pytest.warns(UserWarning, match="overflow"):
        assert c.multiply() is None


def test_multiply_with_infinite_operand_warns_nonfinite():
    c = Calculator(float("inf"), 2.0)
    with pytest.warns(UserWarning, match="non-finite"):
        assert c.multiply() is None


# --- 4) Calculator.divide --------------------------------------------------------

def test_divide_normal():
    c = Calculator(10.0, 2.0)
    assert c.divide() == 5.0


def test_divide_by_zero_warns_and_returns_none():
    c = Calculator(10.0, 0.0)
    with pytest.warns(UserWarning, match="near"):
        assert c.divide() is None


def test_divide_by_near_zero_warns_and_returns_none():
    c = Calculator(5.0, 1e-13)
    with pytest.warns(UserWarning, match="near"):
        assert c.divide() is None


def test_divide_by_nan_or_inf_warns_and_returns_none():
    for denom in (float("nan"), float("inf"), -float("inf")):
        c = Calculator(1.0, denom)
        with pytest.warns(UserWarning, match="near"):
            assert c.divide() is None


def test_divide_nonfinite_result_warns_and_none():
    c = Calculator(float_info.max, 1.0)
    assert math.isfinite(c.divide())


# --- 5) Constants / contracts ----------------------------------------------------

def test_actions_contract_has_expected_ops_and_methods_present():
    expected = {"1", "2", "3", "4"}
    assert set(ACTIONS.keys()) == expected
    for k, (_label, _sym, method) in ACTIONS.items():
        assert hasattr(Calculator, method), f"Missing method {method} for ACTION {k}"


def test_near_zero_tol_positive_and_small():
    assert NEAR_ZERO_TOL > 0
    assert NEAR_ZERO_TOL < 1e-6


# --- 6) CLI: _parse_number -------------------------------------------------------

def test_parse_number_accepts_dot_and_comma(monkeypatch):
    inputs = iter(["abc", "NaN", "3,14"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    val = _parse_number("Enter: ")
    assert val == 3.14


def test_parse_number_rejects_inf(monkeypatch, capsys):
    inputs = iter(["inf", "2.5"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    val = _parse_number("Enter: ")
    captured = capsys.readouterr().out
    assert "Not a Number or Infinity" in captured
    assert val == 2.5


# --- 7) CLI: _ask_menu -----------------------------------------------------------

def test_ask_menu_returns_stripped_choice(monkeypatch, capsys):
    monkeypatch.setattr(builtins, "input", lambda _: " 2 ")
    choice = _ask_menu()
    out = capsys.readouterr().out
    assert "Select an action" in out
    assert choice == "2"


# --- 8) CLI: _run_action ---------------------------------------------------------

def test_run_action_valid_addition_prints_result(capsys):
    calc = Calculator(10, 5)
    res = _run_action(calc, "1")
    out = capsys.readouterr().out
    assert res == 15
    assert "RESULT (+): 15" in out


def test_run_action_invalid_choice_prints_message(capsys):
    calc = Calculator(1, 2)
    res = _run_action(calc, "9")
    out = capsys.readouterr().out
    assert res is None
    assert "Incorrect selection" in out


def test_run_action_missing_method_is_handled(monkeypatch, capsys):
    monkeypatch.setitem(ACTIONS, "9", ("Weird", "?", "not_implemented"))
    calc = Calculator(1, 2)
    res = _run_action(calc, "9")
    out = capsys.readouterr().out
    assert res is None
    assert "not implemented" in out


# --- 9) CLI: _ask_quit -----------------------------------------------------------

@pytest.mark.parametrize("answer,expected", [
    ("y", True), ("Y", True), ("yes", True),
    ("n", False), ("no", False), ("", False),
])
def test_ask_quit_variants(monkeypatch, answer, expected):
    monkeypatch.setattr(builtins, "input", lambda _: answer)
    assert _ask_quit() is expected


# --- 10) E2E: main() one full loop -----------------------------------------------

def test_main_one_round_addition_and_quit(monkeypatch, capsys):
    inputs = iter(["3.5", "2.5", "1", "y"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    main()
    out = capsys.readouterr().out
    assert "WELCOME TO PURE CALCULATOR" in out
    assert "1. Addition (+)" in out
    assert re.search(r"RESULT \(\+\): 6\.0\b", out)
    assert "GOOD BYE" in out

def test_main_handles_unexpected_exception(monkeypatch, capsys):
    import builtins
    from src.calculator import Calculator, main

    # inputs: op1, op2, menu ‘1’ (add), then ‘y’ (quit)
    inputs = iter(["3", "1", "1", "y"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))

    # cause an unexpected exception during an operation
    def boom(self):
        raise RuntimeError("boom")

    monkeypatch.setattr(Calculator, "add", boom)

    main()
    out = capsys.readouterr().out.lower()
    assert "unexpected error" in out  # message from the except block
