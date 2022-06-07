# Copyright 2022 Google
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import pytest

import cirq

import unitary.alpha as alpha
import unitary.examples.tictactoe as tictactoe


@pytest.mark.parametrize(
    "mark, swap_state1, swap_state2",
    [(tictactoe.TicTacSquare.X, 0, 1), (tictactoe.TicTacSquare.O, 0, 2)],
)
def test_tic_tac_split_gate(
    mark: tictactoe.TicTacSquare, swap_state1: int, swap_state2: int
):
    q0 = cirq.NamedQid("a", dimension=3)
    q1 = cirq.NamedQid("b", dimension=3)

    sim = cirq.Simulator()
    for a in range(3):
        for b in range(3):
            c = cirq.Circuit()
            if a > 0:
                c.append(alpha.qudit_gates.QuditXGate(3, 0, a)(q0))
            if b > 0:
                c.append(alpha.qudit_gates.QuditXGate(3, 0, b)(q1))
            c.append(tictactoe.tic_tac_split.QuditSplitGate(mark)(q0, q1))
            c.append(tictactoe.tic_tac_split.QuditSplitGate(mark)(q0, q1))
            c.append(cirq.measure(q0, key="a"))
            c.append(cirq.measure(q1, key="b"))
            results = sim.run(c, repetitions=10)
            if (a == swap_state1 and b == swap_state2) or (
                a == swap_state2 and b == swap_state1
            ):
                # Swap the two states
                assert all(result == b for result in results.measurements["a"])
                assert all(result == a for result in results.measurements["b"])
            else:
                # Leave them alone
                assert all(result == a for result in results.measurements["a"])
                assert all(result == b for result in results.measurements["b"])


def test_invalid_mark_for_gate():
    with pytest.raises(ValueError, match="Not a valid square"):
        _ = tictactoe.tic_tac_split.QuditSplitGate(True)
    with pytest.raises(ValueError, match="Not a valid square"):
        _ = tictactoe.tic_tac_split.QuditSplitGate(0)


def test_diagram():
    q0 = cirq.NamedQid("a", dimension=3)
    q1 = cirq.NamedQid("b", dimension=3)
    c = cirq.Circuit(
        tictactoe.tic_tac_split.QuditSplitGate(tictactoe.TicTacSquare.X)(q0, q1)
    )
    assert (
        str(c)
        == """
a (d=3): ───×X───
            │
b (d=3): ───×X───
""".strip()
    )


@pytest.mark.parametrize("mark", [tictactoe.TicTacSquare.X, tictactoe.TicTacSquare.O])
def test_tic_tac_split(mark: tictactoe.TicTacSquare):
    a = alpha.QuantumObject("a", tictactoe.TicTacSquare.EMPTY)
    b = alpha.QuantumObject("b", tictactoe.TicTacSquare.EMPTY)
    board = alpha.QuantumWorld([a, b])
    tictactoe.TicTacSplit(mark)(a, b)
    results = board.peek(count=1000)
    on_a = [mark, tictactoe.TicTacSquare.EMPTY]
    on_b = [tictactoe.TicTacSquare.EMPTY, mark]
    assert any(r == on_a for r in results)
    assert any(r == on_b for r in results)
    assert all(r == on_a or r == on_b for r in results)


def test_tic_tac_split_entangled():
    a = alpha.QuantumObject("a", tictactoe.TicTacSquare.EMPTY)
    b = alpha.QuantumObject("b", tictactoe.TicTacSquare.EMPTY)
    c = alpha.QuantumObject("c", tictactoe.TicTacSquare.EMPTY)
    board = alpha.QuantumWorld([a, b, c])
    tictactoe.TicTacSplit(tictactoe.TicTacSquare.X)(a, b)
    tictactoe.TicTacSplit(tictactoe.TicTacSquare.O)(b, c)
    results = board.peek(count=1000)
    on_ab = [
        tictactoe.TicTacSquare.X,
        tictactoe.TicTacSquare.O,
        tictactoe.TicTacSquare.EMPTY,
    ]
    on_ac = [
        tictactoe.TicTacSquare.X,
        tictactoe.TicTacSquare.EMPTY,
        tictactoe.TicTacSquare.O,
    ]
    on_b = [
        tictactoe.TicTacSquare.EMPTY,
        tictactoe.TicTacSquare.X,
        tictactoe.TicTacSquare.EMPTY,
    ]
    assert any(r == on_ab for r in results)
    assert any(r == on_ac for r in results)
    assert any(r == on_b for r in results)
    assert all(r == on_ab or r == on_ac or r == on_b for r in results)
