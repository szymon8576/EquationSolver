from sympy import *
from base64 import b64encode
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from io import BytesIO


def round_expr(expr, num_digits=3):
    return expr.xreplace({n.evalf(): round(n, num_digits) for n in expr.atoms(Number)})


def round_eq(eq):
    return Eq(round_expr(eq.lhs), round_expr(eq.rhs))


def convert_to_int_or_float(num):
    return int(num) if int(num) == num else round(num, 2)


def latex_to_byte64(equations):
    tex = "\n\n".join([f"${e}$" for e in equations])

    fig = plt.figure(figsize=(1, 1))
    plt.text(0.5, 0.5, tex, size=18, ha='center', va='center')
    plt.axis('off')

    buffer = BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0, dpi=100)
    # plt.close(fig)
    plt.close('all')
    return b64encode(buffer.getvalue()).decode('utf-8')


def apply_to_eq(eq, elem, operation):
    lhs, rhs = eq.lhs, eq.rhs
    if operation == "divide":
        result = Eq(lhs / elem, rhs / elem)
    else:
        result = Eq(lhs - elem, rhs - elem)
    return round_eq(result)


def solve_eq(eq):
    instructions, x = [], symbols('x')

    solutions = solveset(eq, x, domain=S.Reals)
    if str(solutions) == "Reals":
        return [None, None], "INDETERMINATE", {"image": latex_to_byte64(["x \in \mathbb{R}"])}
    elif str(solutions) == "EmptySet":
        return [None, None], "CONTRADICTORY", {"image": latex_to_byte64(["x \in \emptyset"])}

    if not eq.lhs.as_poly():
        eq = Eq(eq.rhs, eq.lhs)
        instructions.append(("Firstly, swap equation sides so that all expressions containing x are on left-hand side.", [latex(eq)]))

    # STEP 1: simplify lhs and rhs
    curr_eq, prev_eq = Eq(simplify(eq.lhs), simplify(eq.rhs)), eq
    latex_eqs = [latex(prev_eq), latex(curr_eq)]

    if latex(curr_eq) != latex(prev_eq):
        print(curr_eq, prev_eq)
        instructions.append(("Simplify both sides of the equations by combining like terms.", latex_eqs))

    # STEP 2: subtract {a, LHS} from both sides
    if curr_eq.lhs.as_poly():
        num = curr_eq.lhs.as_poly().all_coeffs()[-1]
        curr_eq, prev_eq = apply_to_eq(curr_eq, num, "subtract"), curr_eq
        latex_eqs = [latex(prev_eq) + r"\quad \mathbf{" + (f" /-{num}" if num >= 0 else f" /-({num})") + "}",
                     latex(curr_eq)]

        if latex(curr_eq) != latex(prev_eq):
            instructions.append((f"Subtract {num} from both sides of the equation.", latex_eqs))

    # STEP 3: subtract {x, RHS} from both sides
    if curr_eq.rhs.as_poly():
        x_coeff = convert_to_int_or_float(curr_eq.rhs.as_poly().all_coeffs()[0])
        curr_eq, prev_eq = apply_to_eq(curr_eq, x_coeff * x, "subtract"), curr_eq
        latex_eqs = [
            latex(prev_eq) + r"\quad \mathbf{" + (f" /-{x_coeff}x" if x_coeff >= 0 else f" /-({x_coeff}x)") + "}",
            latex(curr_eq)]

        if latex(curr_eq) != latex(prev_eq):
            instructions.append((f"Subtract {x_coeff}x from both sides of the equation.", latex_eqs))

    # STEP 4: divide by x coeff
    if curr_eq.lhs.as_poly():
        x_coeff = convert_to_int_or_float(curr_eq.lhs.as_poly().all_coeffs()[0])
        curr_eq, prev_eq = apply_to_eq(curr_eq, x_coeff, "divide"), curr_eq
        latex_eqs = [latex(prev_eq) + r"\quad \mathbf{/:" + str(x_coeff) + r"}", latex(curr_eq)]

        if latex(curr_eq) != latex(prev_eq):
            instructions.append((f"Divide both sides of the equation by {x_coeff}.", latex_eqs))

    instructions.append((f"This is the final result.", [latex(curr_eq)]))

    # convert latex equations to byte64 format
    instructions = [(instr, latex_to_byte64(tex)) for instr, tex in instructions]

    if abs(curr_eq.rhs - list(solutions)[0]) > 0.1:
        raise AssertionError(eq, curr_eq.rhs, list(solutions)[0])

    return instructions, "MARKED", {"image": instructions[-1][1], "string": str(list(solutions)[0])}
