"""
Laboratorio interactivo: Materiales utilizados en baterías y almacenamiento de energía
Ingeniería de Materiales · Grupo 05 · Semestre 2027-1

Ejecutar con:
    pip install -r requirements.txt
    streamlit run Interactivo.py 
"""

import re

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Laboratorio de Baterías",
    page_icon="🔋",
    layout="wide",
)

F = 96485  # C/mol

# --------------------------------------------------------------------------
# Datos (tomados del documento; los valores marcados como "aprox." son
# órdenes de magnitud típicos de la literatura, con fines didácticos)
# --------------------------------------------------------------------------
CATODOS = {
    "LiCoO2 (LCO)": dict(formula="LiCoO2", estructura="Laminar, R-3m", difusion="2D (planos)",
                         q_teo=274, q_prac=148, v=3.8, color="#2563eb",
                         ventajas="Alta densidad de energía, buena conductividad",
                         limitaciones="Cobalto caro; inestable si se extrae mucho litio",
                         energia=4, potencia=3, vida=3, seguridad=2, costo=1),
    "NMC 811": dict(formula="LiNi0.8Mn0.1Co0.1O2", estructura="Laminar, R-3m", difusion="2D (planos)",
                    q_teo=275, q_prac=200, v=3.7, color="#7c3aed",
                    ventajas="Alta energía; menos cobalto",
                    limitaciones="Mezcla catiónica; menor estabilidad con alto Ni",
                    energia=5, potencia=3, vida=3, seguridad=2, costo=2),
    "NCA": dict(formula="LiNi0.8Co0.15Al0.05O2", estructura="Laminar, R-3m", difusion="2D (planos)",
                q_teo=279, q_prac=199, v=3.7, color="#db2777",
                ventajas="Muy alta energía",
                limitaciones="Estabilidad térmica limitada",
                energia=5, potencia=3, vida=3, seguridad=2, costo=2),
    "LiMn2O4 (LMO)": dict(formula="LiMn2O4", estructura="Espinela, Fd-3m", difusion="3D (red)",
                          q_teo=148, q_prac=120, v=4.1, color="#ea580c",
                          ventajas="Barato, alta potencia (difusión 3D)",
                          limitaciones="Disolución de Mn; vida corta a alta temperatura",
                          energia=2, potencia=5, vida=2, seguridad=4, costo=4),
    "LiFePO4 (LFP)": dict(formula="LiFePO4", estructura="Olivino, Pnma", difusion="1D (canales)",
                          q_teo=170, q_prac=165, v=3.4, color="#16a34a",
                          ventajas="Seguro, barato, larga vida, sin Co ni Ni",
                          limitaciones="Menor voltaje y energía; baja conductividad",
                          energia=3, potencia=3, vida=5, seguridad=5, costo=5),
}

ANODOS = {
    "Grafito (LiC6)": dict(formula="C6", q_teo=372, v=0.1, expansion=10, color="#374151",
                           nota="Ánodo dominante; forma SEI en los primeros ciclos."),
    "Titanato Li4Ti5O12 (LTO)": dict(formula="Li4Ti5O12", q_teo=175, v=1.55, expansion=0.2, color="#0891b2",
                                     nota="'Deformación cero', sin SEI, vida y seguridad excepcionales."),
    "Silicio (Li15Si4)": dict(formula="Si", q_teo=3579, v=0.4, expansion=280, color="#b45309",
                              nota="Casi 10× el grafito, pero se expande ~280 %."),
    "Litio metálico": dict(formula="Li", q_teo=3860, v=0.0, expansion=None, color="#9ca3af",
                           nota="Meta de las baterías de estado sólido; riesgo de dendritas."),
}

MASAS = {
    "H": 1.008, "Li": 6.94, "C": 12.011, "N": 14.007, "O": 15.999, "F": 18.998, "Na": 22.990,
    "Mg": 24.305, "Al": 26.982, "Si": 28.085, "P": 30.974, "S": 32.06, "Cl": 35.45, "K": 39.098,
    "Ti": 47.867, "V": 50.942, "Cr": 51.996, "Mn": 54.938, "Fe": 55.845, "Co": 58.933,
    "Ni": 58.693, "Cu": 63.546, "Zn": 65.38, "Ge": 72.63, "Zr": 91.224, "Nb": 92.906,
    "Mo": 95.95, "La": 138.905, "Pb": 207.2,
}


def masa_molar(formula: str) -> float:
    """Masa molar de una fórmula sencilla (admite subíndices decimales y paréntesis)."""
    tokens = re.findall(r"([A-Z][a-z]?|\(|\)|\d+\.?\d*)", formula.replace(" ", ""))
    pila = [{}]
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t == "(":
            pila.append({})
        elif t == ")":
            grupo = pila.pop()
            mult = 1.0
            if i + 1 < len(tokens) and re.match(r"\d", tokens[i + 1]):
                mult = float(tokens[i + 1])
                i += 1
            for el, n in grupo.items():
                pila[-1][el] = pila[-1].get(el, 0) + n * mult
        elif re.match(r"[A-Z]", t):
            if t not in MASAS:
                raise ValueError(f"Elemento desconocido: {t}")
            n = 1.0
            if i + 1 < len(tokens) and re.match(r"\d", tokens[i + 1]):
                n = float(tokens[i + 1])
                i += 1
            pila[-1][t] = pila[-1].get(t, 0) + n
        else:
            raise ValueError(f"No entendí '{t}'")
        i += 1
    return sum(MASAS[el] * n for el, n in pila[0].items())


def curva_catodo(nombre: str, x: np.ndarray) -> np.ndarray:
    """Curvas de descarga esquemáticas (potencial vs. Li/Li+) para cada cátodo."""
    caida = 0.35 * np.exp(-(1 - x) * 25)      # caída al final de la descarga
    arranque = 0.25 * np.exp(-x * 25)          # pico al inicio
    if "LFP" in nombre:
        return 3.42 - 0.04 * x + arranque - 2.2 * caida
    if "LMO" in nombre:
        return 4.15 - 0.15 / (1 + np.exp(-(x - 0.5) * 30)) - 0.1 * x + arranque - 2.5 * caida
    if "LCO" in nombre:
        return 4.2 - 0.35 * x - 0.15 * x ** 4 + arranque * 0.2 - 2.0 * caida
    return 4.2 - 0.75 * x - 0.15 * x ** 6 - 1.4 * caida  # NMC / NCA: pendiente


# --------------------------------------------------------------------------
# Barra lateral
# --------------------------------------------------------------------------
st.sidebar.title("🔋 Laboratorio de Baterías")
st.sidebar.caption("Ingeniería de Materiales · Grupo 05 · 2027-1")

SECCIONES = [
    "🏠 Inicio",
    "⚡ Funcionamiento de la celda",
    "🧮 Calculadora de capacidad (Faraday)",
    "📈 Mapa voltaje vs. capacidad",
    "🧊 Estructuras cristalinas y difusión",
    "🪫 Ánodos y expansión de volumen",
    "🔬 Simulador de celda",
    "🎯 ¿Qué material para qué aplicación?",
    "🏭 Procesamiento",
    "⛏️ Cómo llegar al material",
    "📝 Quiz",
]
seccion = st.sidebar.radio("Secciones", SECCIONES, label_visibility="collapsed")

st.sidebar.divider()
st.sidebar.markdown(
    "**Equipo**  \n"
    "Valadez Colin Sebastián  \n"
    "Silvestre Morales Gael Octavio  \n"
    "Silva Martínez Alexis  \n"
    "Mendoza López Aaron  \n\n"
    "**Profesor:** David Eduardo Abad Contreras"
)

# --------------------------------------------------------------------------
# Inicio
# --------------------------------------------------------------------------
if seccion == SECCIONES[0]:
    st.title("Materiales utilizados en baterías y almacenamiento de energía")
    st.markdown(
        "> El desempeño de una batería —**energía, potencia, vida útil, seguridad y costo**— "
        "depende casi por completo de los materiales que la forman: su **composición**, su "
        "**estructura cristalina**, su **microestructura** y la forma en que se **procesan**."
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Baterías para VE (2025)", "1.2 TWh", "+30 % vs 2024")
    c2.metric("LFP vs NMC (costo, 2025)", "> 40 % más barato")
    c3.metric("Eficiencia ion-litio", "> 90 %")
    c4.metric("Si vs grafito (capacidad)", "≈ 10×")

    st.subheader("Línea de tiempo")
    hitos = pd.DataFrame([
        (1800, "Pila de Volta (Zn/Cu y salmuera)"),
        (1859, "Planté: plomo-ácido, primera recargable"),
        (1976, "Whittingham: intercalación TiS2 / Li metálico"),
        (1980, "Goodenough: cátodo LiCoO2"),
        (1983, "Thackeray y Goodenough: espinela LiMn2O4"),
        (1985, "Yoshino: ánodo de carbono, primer prototipo ion-Li"),
        (1991, "Sony comercializa la batería de ion-litio"),
        (1997, "Padhi y Goodenough: olivino LiFePO4"),
        (2011, "Li10GeP2S12: electrolito sólido de 12 mS/cm"),
        (2019, "Nobel de Química: Whittingham, Goodenough, Yoshino"),
        (2026, "Ion-sodio a escala industrial"),
        (2027, "Estado sólido: producción en masa prevista"),
    ], columns=["Año", "Hito"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hitos["Año"], y=[1 if i % 2 else -1 for i in range(len(hitos))],
        mode="markers+text", text=hitos["Hito"],
        textposition=["top center" if i % 2 else "bottom center" for i in range(len(hitos))],
        marker=dict(size=14, color="#2563eb"), hovertemplate="%{x}: %{text}<extra></extra>",
    ))
    fig.add_hline(y=0, line_color="#9ca3af")
    for _, r in hitos.iterrows():
        fig.add_annotation(x=r["Año"], y=0, text=str(r["Año"]), showarrow=False, yshift=-12,
                           font=dict(size=10, color="#6b7280"))
    fig.update_layout(height=420, yaxis=dict(visible=False, range=[-2.5, 2.5]),
                      xaxis=dict(visible=False, range=[1790, 2035]),
                      margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    st.plotly_chart(fig, width="stretch")
    st.info("Usa el menú de la izquierda para recorrer el laboratorio. Cada sección tiene controles que puedes mover.")

# --------------------------------------------------------------------------
# Funcionamiento
# --------------------------------------------------------------------------
elif seccion == SECCIONES[1]:
    st.title("⚡ Funcionamiento de una celda de ion-litio")
    st.markdown(
        "Dos electrodos (ánodo y cátodo) separados por un **electrolito** que transporta iones pero no "
        "electrones. El litio va y viene entre dos estructuras anfitrionas (*mecedora*)."
    )
    modo = st.radio("Modo", ["Descarga (usa la batería)", "Carga (conectada al cargador)"], horizontal=True)
    soc = st.slider("Estado de carga (%)", 0, 100, 60)
    descarga = modo.startswith("Descarga")

    rng = np.random.default_rng(1)
    n_total = 40
    n_anodo = int(round(n_total * soc / 100))
    xa = rng.uniform(0.3, 2.7, n_anodo)
    ya = rng.uniform(0.3, 3.7, n_anodo)
    xc = rng.uniform(5.3, 7.7, n_total - n_anodo)
    yc = rng.uniform(0.3, 3.7, n_total - n_anodo)

    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=3, y1=4, fillcolor="#d1d5db", line_color="#374151")
    fig.add_shape(type="rect", x0=5, y0=0, x1=8, y1=4, fillcolor="#bfdbfe", line_color="#1e40af")
    fig.add_shape(type="rect", x0=3.95, y0=0, x1=4.05, y1=4, fillcolor="#fde68a", line_width=0)
    fig.add_shape(type="rect", x0=3, y0=0, x1=5, y1=4, fillcolor="rgba(253,230,138,0.25)", line_width=0)
    fig.add_annotation(x=1.5, y=4.3, text="<b>Ánodo (–)</b><br>Grafito", showarrow=False)
    fig.add_annotation(x=6.5, y=4.3, text="<b>Cátodo (+)</b><br>Óxido / fosfato", showarrow=False)
    fig.add_annotation(x=4, y=-0.35, text="Electrolito + separador", showarrow=False)
    fig.add_trace(go.Scatter(x=np.r_[xa, xc], y=np.r_[ya, yc], mode="markers",
                             marker=dict(size=11, color="#16a34a", line=dict(width=1, color="white")),
                             name="Li+", hoverinfo="skip"))
    # flechas de iones y electrones
    sx, ex = (2.8, 5.2) if descarga else (5.2, 2.8)
    fig.add_annotation(x=ex, y=2, ax=sx, ay=2, xref="x", yref="y", axref="x", ayref="y",
                       arrowhead=3, arrowsize=1.5, arrowwidth=3, arrowcolor="#16a34a", text="")
    fig.add_annotation(x=4, y=2.3, text="Li⁺", showarrow=False, font=dict(color="#16a34a", size=16))
    fig.add_shape(type="path", path="M 1.5 4.8 L 1.5 5.6 L 6.5 5.6 L 6.5 4.8", line=dict(color="#111827", width=3))
    ex2, sx2 = (6.0, 2.0) if descarga else (2.0, 6.0)
    fig.add_annotation(x=ex2, y=5.6, ax=sx2, ay=5.6, xref="x", yref="y", axref="x", ayref="y",
                       arrowhead=3, arrowsize=1.5, arrowwidth=2, arrowcolor="#dc2626", text="")
    fig.add_annotation(x=4, y=5.95, text=("e⁻ → 💡 foco" if descarga else "e⁻ ← 🔌 cargador"),
                       showarrow=False, font=dict(color="#dc2626", size=15))
    fig.update_layout(height=470, xaxis=dict(visible=False, range=[-0.5, 8.5]),
                      yaxis=dict(visible=False, range=[-0.7, 6.4], scaleanchor="x"),
                      showlegend=False, margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor="white")
    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns(2)
    if descarga:
        c1.success("**Ánodo (oxidación):** LiC₆ → C₆ + Li⁺ + e⁻")
        c2.success("**Cátodo (reducción):** CoO₂ + Li⁺ + e⁻ → LiCoO₂")
    else:
        c1.warning("**Ánodo (reducción):** C₆ + Li⁺ + e⁻ → LiC₆")
        c2.warning("**Cátodo (oxidación):** LiCoO₂ → CoO₂ + Li⁺ + e⁻")
    st.caption("Nota: una *celda* es la unidad electroquímica; una *batería* es un conjunto de dos o más celdas.")

# --------------------------------------------------------------------------
# Calculadora de Faraday
# --------------------------------------------------------------------------
elif seccion == SECCIONES[2]:
    st.title("🧮 Capacidad específica teórica")
    st.latex(r"Q_{\text{teórica}} = \frac{n\,F}{3.6\,M}\quad [\mathrm{mAh/g}]")
    st.latex(r"\Delta G = -\,n\,F\,E \qquad\qquad E_{\text{específica}} = Q \cdot V_{\text{prom}}")

    preset = st.selectbox("Elige un material o escribe tu propia fórmula",
                          ["(personalizado)"] + [f"{k} — {v['formula']}" for k, v in CATODOS.items()]
                          + ["Grafito — LiC6", "Titanato — Li4Ti5O12", "Silicio — Si", "Ion-sodio — NaFePO4"])
    formula_def = "LiFePO4" if preset == "(personalizado)" else preset.split("— ")[1]
    c1, c2, c3 = st.columns(3)
    formula = c1.text_input("Fórmula química", formula_def)
    n_default = 3.75 if formula.strip() == "Si" else (3.0 if formula.strip() == "Li4Ti5O12" else 1.0)
    n = c2.number_input("n (electrones / Li por fórmula)", 0.1, 10.0, n_default, 0.05)
    v = c3.number_input("Voltaje promedio (V)", 0.0, 6.0, 3.4, 0.05)

    try:
        M = masa_molar(formula)
        q = n * F / (3.6 * M)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Masa molar M", f"{M:.2f} g/mol")
        k2.metric("Capacidad teórica", f"{q:.0f} mAh/g")
        k3.metric("Energía específica", f"{q * v:.0f} Wh/kg", help="Del material activo, no de la celda")
        k4.metric("ΔG por mol", f"{-n * F * v / 1000:.0f} kJ/mol")
        st.caption("Con C6 y n = 1 sale 339 mAh/g por gramo de LiC6; los 372 mAh/g del grafito se "
                   "refieren a la masa de C6 (escribe C6).")
        if formula.strip() == "LiCoO2":
            st.info("En la práctica sólo puede extraerse x ≈ 0.5 de Li en LiCoO₂: prueba n = 0.54 → ~148 mAh/g.")
    except ValueError as e:
        st.error(str(e))

    with st.expander("Tabla de masas atómicas usadas"):
        st.dataframe(pd.DataFrame(MASAS.items(), columns=["Elemento", "g/mol"]), hide_index=True)

# --------------------------------------------------------------------------
# Mapa voltaje vs capacidad
# --------------------------------------------------------------------------
elif seccion == SECCIONES[3]:
    st.title("📈 Potencial promedio vs. capacidad específica")
    st.markdown("Los mejores materiales están **arriba y a la derecha**. Las líneas punteadas son energía constante (Q·V).")
    tipo_q = st.radio("Capacidad", ["Práctica", "Teórica"], horizontal=True)
    sel = st.multiselect("Materiales", list(CATODOS) + list(ANODOS), default=list(CATODOS) + list(ANODOS)[:3])

    fig = go.Figure()
    qs = np.linspace(50, 4000, 400)
    for e in [200, 400, 600, 800, 1000]:
        fig.add_trace(go.Scatter(x=qs, y=e / qs, mode="lines", line=dict(dash="dot", color="#d1d5db"),
                                 hoverinfo="skip", showlegend=False))
        fig.add_annotation(x=np.log10(e / 4.6), y=4.6, text=f"{e} Wh/kg", showarrow=False,
                           font=dict(size=10, color="#9ca3af"))
    for nombre in sel:
        if nombre in CATODOS:
            d = CATODOS[nombre]
            qx = d["q_prac"] if tipo_q == "Práctica" else d["q_teo"]
            sim = "circle"
        else:
            d = ANODOS[nombre]
            qx = d["q_teo"]
            sim = "diamond"
        fig.add_trace(go.Scatter(x=[qx], y=[d["v"]], mode="markers+text", name=nombre, text=[nombre],
                                 textposition="top center", marker=dict(size=16, color=d["color"], symbol=sim)))
    fig.update_layout(height=560, xaxis=dict(title="Capacidad específica (mAh/g)", type="log", range=[1.9, 3.65]),
                      yaxis=dict(title="Potencial vs. Li/Li⁺ (V)", range=[-0.2, 4.9]), showlegend=False,
                      margin=dict(t=20))
    st.plotly_chart(fig, width="stretch")
    st.caption("● cátodos · ◆ ánodos. El voltaje de la celda es la diferencia entre ambos potenciales.")

    st.subheader("Tabla comparativa de cátodos")
    st.dataframe(pd.DataFrame([{"Material": k, "Estructura": d["estructura"], "Capacidad práctica (mAh/g)": d["q_prac"],
                                "Voltaje prom. (V)": d["v"], "Ventajas": d["ventajas"],
                                "Limitaciones": d["limitaciones"]} for k, d in CATODOS.items()]),
                 hide_index=True, width="stretch")

# --------------------------------------------------------------------------
# Estructuras cristalinas y difusión
# --------------------------------------------------------------------------
elif seccion == SECCIONES[4]:
    st.title("🧊 Estructuras cristalinas de cátodos")
    fam = st.radio("Familia estructural",
                   ["Laminar (LiCoO₂, NMC, NCA) — 2D", "Espinela (LiMn₂O₄) — 3D", "Olivino (LiFePO₄) — 1D"],
                   horizontal=True)

    fig = go.Figure()
    g = np.arange(4)
    if fam.startswith("Laminar"):
        X, Y = np.meshgrid(g, g)
        for z, tipo in [(0, "M"), (1, "Li"), (2, "M"), (3, "Li"), (4, "M")]:
            col, nom, size = ("#2563eb", "CoO₆ / MO₆", 9) if tipo == "M" else ("#16a34a", "Li⁺", 7)
            fig.add_trace(go.Scatter3d(x=X.ravel(), y=Y.ravel(), z=np.full(16, z), mode="markers",
                                       marker=dict(size=size, color=col), name=nom, showlegend=z < 2))
            if tipo == "Li":
                fig.add_trace(go.Mesh3d(x=[0, 3, 3, 0], y=[0, 0, 3, 3], z=[z] * 4, i=[0, 0], j=[1, 2], k=[2, 3],
                                        color="#16a34a", opacity=0.15, showlegend=False, hoverinfo="skip"))
        texto = ("Capas de octaedros **CoO₆** que comparten aristas, con **planos de litio** entre ellas. "
                 "Difusión **bidimensional** y buena conductividad electrónica. Problema: **mezcla catiónica** "
                 "(Ni²⁺ 0.69 Å ≈ Li⁺ 0.76 Å) bloquea los planos.")
    elif fam.startswith("Espinela"):
        pts = np.array([(i, j, k) for i in g for j in g for k in g])
        fig.add_trace(go.Scatter3d(x=pts[:, 0], y=pts[:, 1], z=pts[:, 2], mode="markers",
                                   marker=dict(size=8, color="#ea580c"), name="Mn (16d, octaédrico)"))
        li = pts[:-1] + 0.5
        li = li[(li < 3).all(axis=1)]
        fig.add_trace(go.Scatter3d(x=li[:, 0], y=li[:, 1], z=li[:, 2], mode="markers",
                                   marker=dict(size=6, color="#16a34a"), name="Li (8a, tetraédrico)"))
        for ax in range(3):
            for a in [0.5, 1.5, 2.5]:
                for b in [0.5, 1.5, 2.5]:
                    p = np.zeros((2, 3)); p[:, ax] = [0, 3]
                    o = [i for i in range(3) if i != ax]; p[:, o[0]] = a; p[:, o[1]] = b
                    fig.add_trace(go.Scatter3d(x=p[:, 0], y=p[:, 1], z=p[:, 2], mode="lines",
                                               line=dict(color="rgba(22,163,74,0.35)", width=3),
                                               showlegend=False, hoverinfo="skip"))
        texto = ("Espinela cúbica **Fd-3m**: Mn en sitios octaédricos 16d y Li en tetraédricos 8a. "
                 "Red **tridimensional** de canales → alta potencia. Problema: disolución de Mn y "
                 "distorsión de **Jahn-Teller** del Mn³⁺.")
    else:
        X, Z = np.meshgrid(g, g)
        fig.add_trace(go.Scatter3d(x=X.ravel(), y=np.zeros(16) + 1.5, z=Z.ravel(), mode="markers",
                                   marker=dict(size=9, color="#a16207"), name="FeO₆"))
        fig.add_trace(go.Scatter3d(x=X.ravel() + 0.5, y=np.zeros(16) + 1.5, z=Z.ravel() + 0.5, mode="markers",
                                   marker=dict(size=7, color="#9333ea", symbol="diamond"), name="PO₄"))
        for xx in [0.5, 1.5, 2.5]:
            for zz in [0.0, 1.0, 2.0, 3.0]:
                fig.add_trace(go.Scatter3d(x=[xx] * 6, y=np.linspace(0, 3, 6), z=[zz] * 6, mode="markers+lines",
                                           marker=dict(size=5, color="#16a34a"),
                                           line=dict(color="#16a34a", width=4),
                                           name="Canal de Li⁺ (eje b)", showlegend=(xx == 0.5 and zz == 0)))
        texto = ("Olivino ortorrómbico **Pnma**: octaedros FeO₆ y tetraedros PO₄; el litio se alinea en "
                 "**canales unidimensionales**. El enlace covalente P–O lo hace muy seguro. "
                 "Se transforma entre dos fases (LiFePO₄ ↔ FePO₄) → meseta de voltaje muy plana.")
    fig.update_layout(height=520, scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
                                             aspectmode="cube"),
                      margin=dict(l=0, r=0, t=0, b=0), legend=dict(orientation="h"))
    c1, c2 = st.columns([3, 2])
    c1.plotly_chart(fig, width="stretch")
    c2.markdown(texto)
    c2.caption("Modelo esquemático, no a escala. Arrastra para girarlo.")

    st.divider()
    st.subheader("⏱️ Tiempo de difusión: t ≈ L² / D")
    st.markdown("Reducir el tamaño de partícula a escala nanométrica acelera la carga, porque el tiempo crece con el **cuadrado** de la longitud.")
    c1, c2 = st.columns(2)
    L_nm = c1.select_slider("Tamaño de partícula (radio)", options=[10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000],
                            value=1000, format_func=lambda v: f"{v} nm" if v < 1000 else f"{v / 1000:g} µm")
    D_opts = {"LCO (~1e-10 cm²/s)": 1e-10, "LMO (~1e-10 cm²/s)": 1e-10, "NMC (~1e-11 cm²/s)": 1e-11,
              "LFP (~1e-14 cm²/s, aprox.)": 1e-14, "Grafito (~1e-10 cm²/s)": 1e-10}
    D_sel = c2.selectbox("Coeficiente de difusión D (orden de magnitud)", list(D_opts))
    D = D_opts[D_sel]
    L_cm = L_nm * 1e-7
    t = L_cm ** 2 / D

    def fmt_t(s):
        for u, f in [("días", 86400), ("h", 3600), ("min", 60), ("s", 1)]:
            if s >= f:
                return f"{s / f:.1f} {u}"
        return f"{s * 1000:.2f} ms"

    st.metric("Tiempo característico de difusión", fmt_t(t))
    Ls = np.logspace(1, 4, 100)
    fig2 = go.Figure()
    for nom, d in D_opts.items():
        if nom.startswith("LMO"):
            continue
        fig2.add_trace(go.Scatter(x=Ls, y=(Ls * 1e-7) ** 2 / d, name=nom.split(" (")[0]))
    fig2.add_trace(go.Scatter(x=[L_nm], y=[t], mode="markers", marker=dict(size=14, color="red"), name="Tu selección"))
    for y, lab in [(60, "1 min"), (3600, "1 h"), (86400, "1 día")]:
        fig2.add_hline(y=y, line_dash="dot", line_color="#9ca3af", annotation_text=lab)
    fig2.update_layout(height=380, xaxis=dict(title="Tamaño de partícula (nm)", type="log"),
                       yaxis=dict(title="t (s)", type="log"), margin=dict(t=20))
    st.plotly_chart(fig2, width="stretch")
    st.caption("Por eso el LFP se usa en partículas nanométricas recubiertas de carbono.")

# --------------------------------------------------------------------------
# Ánodos
# --------------------------------------------------------------------------
elif seccion == SECCIONES[5]:
    st.title("🪫 Materiales de ánodo")
    st.markdown("¿Cuánto silicio puedo mezclar con el grafito? Más capacidad… pero más expansión.")
    pct_si = st.slider("Contenido de silicio en el ánodo (% en masa)", 0, 100, 10)
    q_mix = (1 - pct_si / 100) * 372 + pct_si / 100 * 3579
    exp_mix = (1 - pct_si / 100) * 10 + pct_si / 100 * 280
    c1, c2, c3 = st.columns(3)
    c1.metric("Capacidad del ánodo", f"{q_mix:.0f} mAh/g", f"{q_mix / 372 - 1:+.0%} vs grafito")
    c2.metric("Expansión de volumen aprox.", f"{exp_mix:.0f} %")
    estado = "✅ Estable" if exp_mix < 30 else ("⚠️ La SEI se fractura con el ciclado" if exp_mix < 80
                                              else "❌ Partículas fracturadas, pérdida de contacto")
    c3.metric("Comportamiento esperado", estado)

    c1, c2 = st.columns(2)
    nombres = [k for k, v in ANODOS.items() if v["expansion"] is not None]
    fig = go.Figure(go.Bar(x=nombres, y=[ANODOS[k]["q_teo"] for k in nombres],
                           marker_color=[ANODOS[k]["color"] for k in nombres], text=[ANODOS[k]["q_teo"] for k in nombres]))
    fig.update_layout(title="Capacidad teórica (mAh/g)", height=380, margin=dict(t=40))
    c1.plotly_chart(fig, width="stretch")
    fig = go.Figure(go.Bar(x=nombres, y=[ANODOS[k]["expansion"] for k in nombres],
                           marker_color=[ANODOS[k]["color"] for k in nombres],
                           text=[f"{ANODOS[k]['expansion']} %" for k in nombres]))
    fig.update_layout(title="Expansión de volumen al litiarse (%)", height=380, margin=dict(t=40))
    c2.plotly_chart(fig, width="stretch")

    # dibujo de la partícula expandiéndose
    r0 = 1.0
    r1 = r0 * (1 + exp_mix / 100) ** (1 / 3)
    th = np.linspace(0, 2 * np.pi, 200)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=r0 * np.cos(th), y=r0 * np.sin(th), fill="toself", name="Sin litio",
                             line_color="#374151"))
    fig.add_trace(go.Scatter(x=r1 * np.cos(th) + 3.2, y=r1 * np.sin(th), fill="toself", name="Litiada",
                             line_color="#b45309"))
    fig.update_layout(height=280, xaxis=dict(visible=False, range=[-1.8, 5]), yaxis=dict(visible=False, scaleanchor="x"),
                      margin=dict(l=0, r=0, t=0, b=0), legend=dict(orientation="h"))
    st.plotly_chart(fig, width="stretch")

    for k, v in ANODOS.items():
        st.markdown(f"- **{k}** — {v['q_teo']} mAh/g a {v['v']} V. {v['nota']}")

# --------------------------------------------------------------------------
# Simulador de celda
# --------------------------------------------------------------------------
elif seccion == SECCIONES[6]:
    st.title("🔬 Simulador de celda")
    st.markdown("Arma tu celda eligiendo cátodo y ánodo. Las curvas son **esquemáticas** (forma típica), no mediciones.")
    c1, c2, c3 = st.columns(3)
    cat = c1.selectbox("Cátodo", list(CATODOS), index=4)
    ano = c2.selectbox("Ánodo", list(ANODOS)[:3], index=0)
    temp = c3.slider("Temperatura (°C)", -20, 60, 25)

    dc, da = CATODOS[cat], ANODOS[ano]
    x = np.linspace(0.001, 0.999, 300)
    v_celda = curva_catodo(cat, x) - da["v"]
    # efecto didáctico de temperatura: polarización a baja T
    v_celda = v_celda - max(0, (25 - temp)) * 0.008
    q_cell = dc["q_prac"] * da["q_teo"] / (dc["q_prac"] + da["q_teo"])
    if temp < 0:
        q_cell *= 1 + temp / 60  # menor capacidad en frío
    v_prom = float(np.mean(v_celda))
    e_mat = q_cell * v_prom

    k1, k2, k3 = st.columns(3)
    k1.metric("Voltaje promedio de la celda", f"{v_prom:.2f} V")
    k2.metric("Capacidad (materiales activos)", f"{q_cell:.0f} mAh/g")
    k3.metric("Energía específica (materiales activos)", f"{e_mat:.0f} Wh/kg",
              help="Una celda real tiene ~40–60 % de esta cifra por colectores, electrolito, carcasa, etc.")

    comparar = st.checkbox("Comparar con todos los cátodos (mismo ánodo)")
    fig = go.Figure()
    nombres = list(CATODOS) if comparar else [cat]
    for nom in nombres:
        d = CATODOS[nom]
        qc = d["q_prac"] * da["q_teo"] / (d["q_prac"] + da["q_teo"])
        fig.add_trace(go.Scatter(x=x * qc, y=curva_catodo(nom, x) - da["v"] - max(0, (25 - temp)) * 0.008,
                                 name=nom, line=dict(color=d["color"], width=4 if nom == cat else 2)))
    fig.update_layout(height=450, xaxis_title="Capacidad entregada (mAh/g de materiales activos)",
                      yaxis_title="Voltaje de la celda (V)", margin=dict(t=20))
    st.plotly_chart(fig, width="stretch")
    if "LFP" in cat:
        st.info("Meseta muy plana: el LFP se transforma entre dos fases (LiFePO₄ / FePO₄).")
    if "LTO" in ano:
        st.info("Con titanato el voltaje baja ~1.5 V, pero no se forma SEI y la vida es excepcional.")
    if "Silicio" in ano:
        st.warning("Con silicio puro la capacidad sube mucho, pero la expansión de ~280 % destruye el electrodo.")
    if temp < 0:
        st.warning("A baja temperatura la difusión es más lenta: menos capacidad y mayor caída de voltaje.")
    if temp > 45 and "LMO" in cat:
        st.error("A temperatura elevada el LiMn₂O₄ sufre disolución de Mn → vida útil corta.")
    if temp > 45 and cat in ("NMC 811", "NCA"):
        st.error("Los cátodos ricos en níquel tienen estabilidad térmica limitada.")

# --------------------------------------------------------------------------
# Selector por aplicación
# --------------------------------------------------------------------------
elif seccion == SECCIONES[7]:
    st.title("🎯 La batería ideal no existe")
    st.markdown("Cada aplicación da prioridad a una propiedad distinta. Ajusta los pesos o elige una aplicación.")
    APPS = {
        "Personalizado": None,
        "📱 Electrónica portátil": dict(energia=5, potencia=2, vida=2, seguridad=3, costo=1),
        "🚗 Vehículo eléctrico (autonomía)": dict(energia=5, potencia=3, vida=3, seguridad=3, costo=3),
        "🚙 Vehículo eléctrico (económico)": dict(energia=2, potencia=3, vida=4, seguridad=4, costo=5),
        "🏭 Almacenamiento en la red": dict(energia=1, potencia=2, vida=5, seguridad=5, costo=5),
        "🔧 Herramientas / alta potencia": dict(energia=2, potencia=5, vida=3, seguridad=3, costo=3),
    }
    app = st.selectbox("Aplicación", list(APPS), index=1)
    base = APPS[app] or dict(energia=3, potencia=3, vida=3, seguridad=3, costo=3)
    props = ["energia", "potencia", "vida", "seguridad", "costo"]
    etiquetas = {"energia": "Energía", "potencia": "Potencia", "vida": "Vida útil", "seguridad": "Seguridad",
                 "costo": "Bajo costo"}
    cols = st.columns(5)
    pesos = {p: cols[i].slider(etiquetas[p], 0, 5, base[p], key=f"{app}-{p}") for i, p in enumerate(props)}

    total = sum(pesos.values()) or 1
    ranking = sorted(((sum(CATODOS[m][p] * w for p, w in pesos.items()) / total, m) for m in CATODOS), reverse=True)
    mejor = ranking[0][1]
    c1, c2 = st.columns([2, 3])
    with c1:
        st.success(f"### Recomendado: {mejor}")
        st.dataframe(pd.DataFrame([{"Material": m, "Puntaje (0–5)": round(s, 2)} for s, m in ranking]),
                     hide_index=True, width="stretch")
    with c2:
        fig = go.Figure()
        for s, m in ranking[:3]:
            vals = [CATODOS[m][p] for p in props]
            fig.add_trace(go.Scatterpolar(r=vals + vals[:1], theta=[etiquetas[p] for p in props] + [etiquetas[props[0]]],
                                          fill="toself", name=m, line_color=CATODOS[m]["color"], opacity=0.6))
        fig.update_layout(height=420, polar=dict(radialaxis=dict(range=[0, 5])), margin=dict(t=30))
        st.plotly_chart(fig, width="stretch")
    st.caption("Calificaciones cualitativas (1–5) basadas en las ventajas y limitaciones de la Tabla 1 del documento.")

# --------------------------------------------------------------------------
# Procesamiento
# --------------------------------------------------------------------------
elif seccion == SECCIONES[8]:
    st.title("🏭 Procesamiento: del precursor a la celda")
    etapas = ["Extracción", "Refinación", "Síntesis", "Mezclado", "Recubrimiento y secado",
              "Calandrado", "Corte y ensamble", "Formación"]
    etapa = st.select_slider("Cadena de fabricación", etapas, value="Síntesis")
    desc = {
        "Extracción": "Salmueras, roca dura (espodumena) o arcillas. Ver sección *Cómo llegar al material*.",
        "Refinación": "Sulfatos de Ni, Mn, Co de alta pureza; Li₂CO₃ o LiOH.",
        "Síntesis": "Coprecipitación de Ni_xMn_yCo_z(OH)₂ (pH, T controlados) → mezcla con Li → calcinación 700–950 °C.",
        "Mezclado": "Material activo + negro de carbono + aglutinante. Cátodo: PVDF en NMP. Ánodo: CMC/SBR en agua.",
        "Recubrimiento y secado": "Capas de decenas de µm sobre Al (cátodo) o Cu (ánodo); hornos continuos.",
        "Calandrado": "Rodillos reducen la porosidad (20–40 %) para subir la densidad de energía.",
        "Corte y ensamble": "Formatos cilíndrico, prismático o bolsa; electrolito inyectado en cuartos secos.",
        "Formación": "Primeros ciclos controlados forman la SEI; puede tardar días y es de las etapas más caras.",
    }
    st.info(f"**{etapa}:** {desc[etapa]}")

    st.subheader("🔥 Calcinación del NMC")
    t_calc = st.slider("Temperatura de calcinación (°C)", 600, 1050, 820, 10)
    grano = 0.2 * np.exp((t_calc - 700) / 120)          # µm, didáctico
    mezcla = 2 + 0.0006 * (t_calc - 820) ** 2           # %, mínimo alrededor de 820 °C (didáctico)
    c1, c2, c3 = st.columns(3)
    c1.metric("Tamaño de grano aprox.", f"{grano:.2f} µm")
    c2.metric("Mezcla catiónica Ni/Li aprox.", f"{min(mezcla, 15):.1f} %")
    if t_calc < 700:
        c3.metric("Resultado", "❌ Reacción incompleta")
    elif t_calc > 950:
        c3.metric("Resultado", "❌ Granos grandes, pérdida de Li")
    else:
        c3.metric("Resultado", "✅ Ventana industrial")
    st.caption("Modelo cualitativo: la temperatura y la atmósfera controlan la mezcla catiónica y el tamaño de grano.")

    st.subheader("🧱 Calandrado del electrodo")
    por = st.slider("Porosidad final del electrodo (%)", 10, 60, 30)
    dens = (1 - por / 100) / (1 - 0.30)
    mojado = np.clip((por - 10) / 20, 0, 1)
    c1, c2 = st.columns(2)
    c1.metric("Densidad de energía volumétrica relativa", f"{dens:.0%}", "referencia: 30 % de porosidad")
    c2.metric("Facilidad de entrada del electrolito", f"{mojado:.0%}")
    if por < 20:
        st.warning("Compresión excesiva: el electrolito no penetra bien → pierde potencia.")
    elif por > 40:
        st.warning("Demasiado poroso: se desperdicia volumen → baja densidad de energía.")
    else:
        st.success("Rango típico (20–40 %).")
    rng = np.random.default_rng(3)
    n = int(250 * (1 - por / 100) * 1.4)
    fig = go.Figure(go.Scatter(x=rng.uniform(0, 10, n), y=rng.uniform(0, 2 + 2 * por / 60, n), mode="markers",
                               marker=dict(size=14, color="#6b7280", opacity=0.85), hoverinfo="skip"))
    fig.add_shape(type="rect", x0=0, x1=10, y0=-0.4, y1=0, fillcolor="#d4a373", line_width=0)
    fig.update_layout(height=230, xaxis_visible=False, yaxis=dict(visible=False, range=[-0.5, 4.2]),
                      margin=dict(l=0, r=0, t=0, b=0), plot_bgcolor="#fef9c3")
    st.plotly_chart(fig, width="stretch")
    st.caption("Partículas de material activo sobre la lámina colectora; el fondo amarillo es el espacio para el electrolito.")

    with st.expander("Verificación del material y de la celda"):
        st.markdown(
            "- **DRX y difracción de neutrones:** fases y parámetros de red (in situ / operando).\n"
            "- **XPS:** composición de la SEI y estado de oxidación superficial.\n"
            "- **Ciclado galvanostático:** capacidad, eficiencia y retención.\n"
            "- **Voltametría cíclica:** potenciales redox.\n"
            "- **EIS:** separa resistencias del electrolito, la SEI y la transferencia de carga."
        )

# --------------------------------------------------------------------------
# Cómo llegar al material
# --------------------------------------------------------------------------
elif seccion == SECCIONES[9]:
    st.title("⛏️ Cómo llegar al material")
    ruta = st.radio("Ruta del litio", ["Salmueras", "Roca dura (espodumena)", "Arcillas (Sonora, México)"], horizontal=True)
    if ruta == "Salmueras":
        st.markdown("Bombeo → pozas de **evaporación solar** → precipitación de **Li₂CO₃**. Consume mucha agua y es lenta; "
                    "alternativa: **extracción directa de litio (DLE)**. Triángulo del litio: Argentina, Bolivia y Chile.")
    elif ruta.startswith("Roca"):
        st.markdown("Trituración → concentración → tratamiento térmico → lixiviación ácida o alcalina → **Li₂CO₃ o LiOH**. "
                    "Australia fue el mayor productor minero en 2025.")
    else:
        st.markdown("~**235 000 ha** en Arivechi, Bacadéhuachi, Huásabas, Divisadero, Granados, Sahuaripa y Nácori Chico. "
                    "Zona de reserva minera de litio desde 2023. El IPN reportó **301 a 5 890 ppm** en Bacadéhuachi; "
                    "falta un proceso rentable para separarlo de la arcilla.")
        ppm = st.slider("Concentración de Li en la arcilla (ppm)", 301, 5890, 2000)
        ton = st.number_input("Toneladas de mineral procesadas", 1, 1_000_000, 1000)
        kg_li = ton * 1000 * ppm / 1e6
        kg_carb = kg_li * (73.89 / (2 * 6.94))
        c1, c2, c3 = st.columns(3)
        c1.metric("Litio contenido", f"{kg_li:,.0f} kg")
        c2.metric("Equivalente en Li₂CO₃", f"{kg_carb:,.0f} kg")
        c3.metric("Celdas LFP de 1 kWh aprox.", f"{kg_carb / 0.6:,.0f}",
                  help="Supone ~0.6 kg de Li₂CO₃ equivalente por kWh (orden de magnitud) y 100 % de recuperación.")

    st.subheader("Concentración de la cadena de suministro")
    datos = pd.DataFrame([("Cobalto (minería)", "RD Congo", 66), ("Grafito (refinación)", "China", 90),
                          ("Manganeso (refinación)", "China", 90)], columns=["Material", "País líder", "Participación (%)"])
    fig = go.Figure(go.Bar(y=datos["Material"], x=datos["Participación (%)"], orientation="h",
                           text=[f"{p} % — {c}" for p, c in zip(datos['Participación (%)'], datos['País líder'])],
                           marker_color=["#2563eb", "#374151", "#ea580c"]))
    fig.update_layout(height=260, xaxis=dict(range=[0, 100], title="% mundial (aprox.)"), margin=dict(t=10))
    st.plotly_chart(fig, width="stretch")

    st.subheader("♻️ Reciclaje: cerrar el ciclo")
    st.markdown("**Pirometalúrgica** (fundición) · **Hidrometalúrgica** (disolución química) · **Directo del cátodo**. "
                "La infraestructura aún no crece al ritmo de los vehículos eléctricos.")

# --------------------------------------------------------------------------
# Quiz
# --------------------------------------------------------------------------
elif seccion == SECCIONES[10]:
    st.title("📝 Pon a prueba lo aprendido")
    PREGUNTAS = [
        ("¿Qué estructura cristalina tiene el LiFePO₄?", ["Laminar R-3m", "Espinela Fd-3m", "Olivino Pnma"], 2),
        ("¿En qué dimensión se difunde el litio en la espinela LiMn₂O₄?", ["1D", "2D", "3D"], 2),
        ("¿Cuál es la capacidad teórica del grafito?", ["148 mAh/g", "372 mAh/g", "3579 mAh/g"], 1),
        ("¿Por qué el silicio aún se usa poco en ánodos?", ["Es muy caro", "Se expande ~280 % en volumen",
                                                            "Tiene bajo voltaje"], 1),
        ("¿Qué material domina el almacenamiento estacionario?", ["LCO", "NCA", "LFP"], 2),
        ("¿Qué capa se forma sobre el grafito en los primeros ciclos?", ["SEI", "PVDF", "NMP"], 0),
        ("Si el tamaño de partícula se reduce a la mitad, el tiempo de difusión…",
         ["se reduce a la mitad", "se reduce a la cuarta parte", "no cambia"], 1),
        ("¿Qué método industrial se usa para sintetizar precursores NMC?", ["Coprecipitación", "Calandrado", "XPS"], 0),
    ]
    with st.form("quiz"):
        resp = [st.radio(f"**{i + 1}. {q}**", ops, index=None, key=f"q{i}") for i, (q, ops, _) in enumerate(PREGUNTAS)]
        enviado = st.form_submit_button("Calificar")
    if enviado:
        aciertos = sum(r == ops[c] for r, (_, ops, c) in zip(resp, PREGUNTAS))
        st.metric("Calificación", f"{aciertos} / {len(PREGUNTAS)}")
        if aciertos == len(PREGUNTAS):
            st.balloons()
        for i, (r, (q, ops, c)) in enumerate(zip(resp, PREGUNTAS)):
            if r != ops[c]:
                st.markdown(f"❌ **{i + 1}.** Respuesta correcta: *{ops[c]}*")
