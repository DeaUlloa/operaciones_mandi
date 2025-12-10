
import os
import math
import random
import streamlit as st

st.set_page_config(page_title="Aritmética Interactiva", page_icon="🧮", layout="wide")
st.title("🧮 Aritmética Interactiva")
st.caption("Multiplicación (1×1, 2×1, 3×1) • División exacta (1–3 cifras ÷ 1 cifra) • Sumas/Restas hasta 4 cifras")

def rand_with_digits(d: int) -> int:
    if d == 1:
        return random.randint(1, 9)
    lo = 10 ** (d - 1)
    hi = 10 ** d - 1
    return random.randint(lo, hi)

def grade_rows(rows):
    correct = 0
    for r in rows:
        txt = str(r.get("answer", "")).strip().replace(",", ".").replace(" ", "")
        ok = False
        if txt == str(r["correct"]):
            ok = True
        else:
            try:
                ok = float(txt) == float(r["correct"])
            except Exception:
                ok = False
        r["feedback"] = "✅ Correcto" if ok else "❌ Incorrecto"
        if ok:
            correct += 1
    return correct

def show_solutions(rows, prefix="Solución"):
    for i, r in enumerate(rows, start=1):
        st.write(f"👀 {prefix} {i}: **{r['correct']}**")

def gen_addition(n=10, d_left=4, d_right=4):
    rows = []
    for _ in range(n):
        a = random.randint(0, 10**d_left - 1)
        b = random.randint(0, 10**d_right - 1)
        rows.append({"prompt": f"{a} + {b} =", "correct": a + b, "answer": "", "feedback": ""})
    return rows

def gen_subtraction(n=10, d_left=4, d_right=4):
    rows = []
    for _ in range(n):
        a = random.randint(0, 10**d_left - 1)
        b = random.randint(0, 10**d_right - 1)
        if b > a:
            a, b = b, a
        rows.append({"prompt": f"{a} - {b} =", "correct": a - b, "answer": "", "feedback": ""})
    return rows

def gen_multiplication(n=10, left_digits=1, missing_ratio=0.3):
    rows = []
    for _ in range(n):
        a = rand_with_digits(left_digits)
        b = rand_with_digits(1)
        product = a * b
        if random.random() < missing_ratio:
            if random.random() < 0.5:
                prompt = f"__ × {b} = {product}"
                correct = a
            else:
                prompt = f"{a} × __ = {product}"
                correct = b
        else:
            prompt = f"{a} × {b} ="
            correct = product
        rows.append({"prompt": prompt, "correct": correct, "answer": "", "feedback": ""})
    return rows

def pick_quotient_for_dividend_digits(divisor, dividend_digits):
    lo = 10**(dividend_digits-1)
    hi = 10**dividend_digits - 1
    qmin = math.ceil(lo / divisor)
    qmax = hi // divisor
    if qmin > qmax:
        return None
    return random.randint(qmin, qmax)

def gen_division(n=10, dividend_digits=3, missing_ratio=0.3):
    rows = []
    for _ in range(n):
        while True:
            divisor = random.randint(1, 9)
            q = pick_quotient_for_dividend_digits(divisor, dividend_digits)
            if q is not None and q >= 1:
                quotient = q
                dividend = divisor * quotient
                break
        if random.random() < missing_ratio:
            choice = random.choice(["dividend", "divisor", "quotient"])
            if choice == "dividend":
                prompt = f"__ ÷ {divisor} = {quotient}"
                correct = dividend
            elif choice == "divisor":
                prompt = f"{dividend} ÷ __ = {quotient}"
                correct = divisor
            else:
                prompt = f"{dividend} ÷ {divisor} = __"
                correct = quotient
        else:
            prompt = f"{dividend} ÷ {divisor} ="
            correct = quotient
        rows.append({"prompt": prompt, "correct": correct, "answer": "", "feedback": ""})
    return rows

def init_state_key(key, default):
    if key not in st.session_state:
        st.session_state[key] = default

init_state_key("mul_rows", [])
init_state_key("div_rows", [])
init_state_key("add_rows", [])
init_state_key("sub_rows", [])

# ------------ RENDER EN GRILLA 2 COLUMNAS ------------
def render_rows_grid(rows, prefix_key):
    num_cols = 2
    for start in range(0, len(rows), num_cols):
        cols = st.columns(num_cols)
        for idx, col in enumerate(cols):
            i = start + idx
            if i >= len(rows):
                break
            r = rows[i]
            with col:
                st.markdown(f"**{r['prompt']}**")
                r["answer"] = st.text_input(
                    "",
                    value=r.get("answer", ""),
                    key=f"{prefix_key}_ans_{i}",
                )
                if r.get("feedback", ""):
                    st.write(r["feedback"])

# ------------ TABS ------------
tab_mul, tab_div, tab_add, tab_sub = st.tabs(
    ["✖️ Multiplicación", "➗ División", "➕ Suma", "➖ Resta"]
)

# ------------ MULTIPLICACIÓN ------------
with tab_mul:
    st.subheader("✖️ Multiplicaciones (1×1, 2×1, 3×1 cifras)")
    c1, c2, c3 = st.columns([1, 1, 2])
    n_mul = c1.number_input("Ejercicios", 1, 100, 10, key="n_mul")
    left_digits = c2.selectbox("Cifras A", [1, 2, 3], 0, key="mul_left_digits")
    miss_ratio = c3.slider("Faltantes", 0.0, 1.0, 0.3, 0.1, key="mul_missing")
    new_mul = st.button("🧩 Generar ejercicios", key="mul_new")
    grade_mul = st.button("✅ Corregir", key="mul_grade")
    show_mul = st.button("👀 Mostrar soluciones", key="mul_show")
    st.markdown("---")

    if new_mul:
        st.session_state.mul_rows = gen_multiplication(n_mul, left_digits, miss_ratio)

    if grade_mul and st.session_state.mul_rows:
        score = grade_rows(st.session_state.mul_rows)
        st.success(f"Puntaje: {score}/{len(st.session_state.mul_rows)}")

    render_rows_grid(st.session_state.mul_rows, "mul")

    if show_mul and st.session_state.mul_rows:
        show_solutions(st.session_state.mul_rows, prefix="Solución")

# ------------ DIVISIÓN ------------
with tab_div:
    st.subheader("➗ Divisiones exactas (1–3 cifras ÷ 1 cifra)")
    c1, c2, c3 = st.columns([1, 1, 2])
    n_div = c1.number_input("Ejercicios", 1, 100, 10, key="n_div")
    dividend_digits = c2.selectbox("Cifras dividendo", [1, 2, 3], 2, key="div_digits")
    miss_ratio_d = c3.slider("Faltantes", 0.0, 1.0, 0.3, 0.1, key="div_missing")
    new_div = st.button("🧩 Generar ejercicios", key="div_new")
    grade_div = st.button("✅ Corregir", key="div_grade")
    show_div = st.button("👀 Mostrar soluciones", key="div_show")
    st.markdown("---")

    if new_div:
        st.session_state.div_rows = gen_division(n_div, dividend_digits, miss_ratio_d)

    if grade_div and st.session_state.div_rows:
        score = grade_rows(st.session_state.div_rows)
        st.success(f"Puntaje: {score}/{len(st.session_state.div_rows)}")

    render_rows_grid(st.session_state.div_rows, "div")

    if show_div and st.session_state.div_rows:
        show_solutions(st.session_state.div_rows, prefix="Solución")

# ------------ SUMA ------------
with tab_add:
    st.subheader("➕ Sumas (hasta 4 cifras)")
    c1, c2, c3 = st.columns(3)
    n_add = c1.number_input("Ejercicios", 1, 100, 10, key="n_add")
    d_left_a = c2.selectbox("Cifras A", [1, 2, 3, 4], 3, key="add_left_d")
    d_right_a = c3.selectbox("Cifras B", [1, 2, 3, 4], 3, key="add_right_d")
    new_add = st.button("🧩 Generar ejercicios", key="add_new")
    grade_add = st.button("✅ Corregir", key="add_grade")
    show_add = st.button("👀 Mostrar soluciones", key="add_show")
    st.markdown("---")

    if new_add:
        st.session_state.add_rows = gen_addition(n_add, d_left_a, d_right_a)

    if grade_add and st.session_state.add_rows:
        score = grade_rows(st.session_state.add_rows)
        st.success(f"Puntaje: {score}/{len(st.session_state.add_rows)}")

    render_rows_grid(st.session_state.add_rows, "add")

    if show_add and st.session_state.add_rows:
        show_solutions(st.session_state.add_rows, prefix="Solución")

# ------------ RESTA ------------
with tab_sub:
    st.subheader("➖ Restas (hasta 4 cifras)")
    c1, c2, c3 = st.columns(3)
    n_sub = c1.number_input("Ejercicios", 1, 100, 10, key="n_sub")
    d_left_s = c2.selectbox("Cifras A", [1, 2, 3, 4], 3, key="sub_left_d")
    d_right_s = c3.selectbox("Cifras B", [1, 2, 3, 4], 3, key="sub_right_d")
    new_sub = st.button("🧩 Generar ejercicios", key="sub_new")
    grade_sub = st.button("✅ Corregir", key="sub_grade")
    show_sub = st.button("👀 Mostrar soluciones", key="sub_show")
    st.markdown("---")

    if new_sub:
        st.session_state.sub_rows = gen_subtraction(n_sub, d_left_s, d_right_s)

    if grade_sub and st.session_state.sub_rows:
        score = grade_rows(st.session_state.sub_rows)
        st.success(f"Puntaje: {score}/{len(st.session_state.sub_rows)}")

    render_rows_grid(st.session_state.sub_rows, "sub")

    if show_sub and st.session_state.sub_rows:
        show_solutions(st.session_state.sub_rows, prefix="Solución")
