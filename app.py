"""
💈 Barbería: El Rafa — Agenda automática
Aplicación web construida con Streamlit.
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import date, timedelta, datetime
from database import (
    init_db,
    SERVICIOS,
    horarios_disponibles,
    crear_cita,
    cancelar_cita,
    obtener_citas_por_fecha,
    disponibilidad_semanal,
    buscar_citas_por_telefono,
    obtener_pin_barbero,
    cambiar_pin_barbero,
    HORA_APERTURA,
    HORA_CIERRE,
    hoy_colombia,
    ahora_colombia,
)

# ── Inicialización ────────────────────────────────────────────────────
init_db()

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}
DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

# ── Configuración de página ───────────────────────────────────────────
st.set_page_config(
    page_title="Barbería: El Rafa — Reserva tu cita",
    page_icon="💈",
    layout="wide",
)

# ── Estilos CSS profesionales ─────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;500;600;700;800&display=swap');

    /* Forzar fuente global */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ── Paleta ──
       Primario:  #c9a45c (dorado barbería)
       Fondo:     #111318 / #181b22 / #1e222b
       Texto:     #f0ece4 (crema claro)
       Muted:     #9ca3ae
       Éxito:     #5cb97a
       Error:     #e06c6c
    */

    /* Header hero */
    .hero {
        background: linear-gradient(145deg, #111318 0%, #181b22 50%, #1e222b 100%);
        border-radius: 18px;
        padding: 2.8rem 2rem 2rem;
        text-align: center;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(201, 164, 92, 0.25);
        box-shadow: 0 4px 30px rgba(0,0,0,0.3);
    }
    .hero h1 {
        font-family: 'Playfair Display', serif;
        color: #f0ece4;
        font-size: 2.6rem;
        font-weight: 800;
        margin: 0 0 0.4rem;
        letter-spacing: 0.5px;
    }
    .hero h1 span { color: #c9a45c; }
    .hero p {
        color: #9ca3ae;
        font-size: 1.05rem;
        margin: 0;
        font-weight: 400;
        letter-spacing: 0.3px;
    }

    /* Tarjetas de servicio */
    .servicio-card {
        background: linear-gradient(150deg, #181b22, #1e222b);
        border: 1px solid rgba(201, 164, 92, 0.15);
        border-radius: 16px;
        padding: 1.8rem 1rem 1.5rem;
        text-align: center;
        transition: transform 0.2s, border-color 0.2s, box-shadow 0.2s;
    }
    .servicio-card:hover {
        transform: translateY(-4px);
        border-color: rgba(201, 164, 92, 0.5);
        box-shadow: 0 8px 25px rgba(201, 164, 92, 0.08);
    }
    .servicio-card .icono { font-size: 2.2rem; margin-bottom: 0.6rem; }
    .servicio-card h4 {
        font-family: 'Playfair Display', serif;
        color: #f0ece4;
        font-weight: 700;
        font-size: 1.15rem;
        margin: 0 0 0.8rem;
    }
    .servicio-card .detalle {
        display: flex;
        justify-content: center;
        gap: 1rem;
        font-size: 0.85rem;
        color: #9ca3ae;
    }
    .servicio-card .precio {
        background: linear-gradient(135deg, #c9a45c, #b8933e);
        color: #111318;
        font-weight: 800;
        font-size: 0.95rem;
        border-radius: 10px;
        padding: 0.45rem 1rem;
        margin-top: 0.9rem;
        display: inline-block;
        letter-spacing: 0.3px;
    }

    /* Confirmación */
    .confirmacion {
        background: linear-gradient(140deg, #141820 0%, #1a1e28 100%);
        border: 1px solid rgba(92, 185, 122, 0.25);
        border-left: 5px solid #5cb97a;
        border-radius: 16px;
        padding: 1.8rem 2rem;
        margin: 1rem 0;
    }
    .confirmacion h3 {
        color: #5cb97a;
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        margin: 0 0 1rem;
        font-size: 1.3rem;
    }
    .confirmacion .grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.7rem 2rem;
    }
    .confirmacion .item { margin: 0; font-size: 0.95rem; color: #bfc7d1; }
    .confirmacion .item strong { color: #f0ece4; }

    /* ── TABLA SEMANAL ────────────────────────────────────────── */
    .week-nav {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin: 0.5rem 0 1.2rem;
    }
    .week-label {
        font-size: 1.05rem;
        font-weight: 600;
        color: #f0ece4;
        min-width: 260px;
        text-align: center;
    }

    .agenda-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 3px;
        font-size: 0.82rem;
    }
    .agenda-table th {
        background: #1a1e28;
        color: #d4cfc5;
        padding: 10px 6px;
        text-align: center;
        font-weight: 700;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-radius: 8px;
    }
    .agenda-table th.dia-header .dia-nombre { display: block; font-size: 0.72rem; color: #9ca3ae; }
    .agenda-table th.dia-header .dia-num { display: block; font-size: 1.1rem; font-weight: 800; color: #f0ece4; margin-top: 2px; }
    .agenda-table th.dia-header.hoy { border: 2px solid #c9a45c; background: #1e222b; }

    .agenda-table td {
        padding: 7px 4px;
        text-align: center;
        font-weight: 600;
        border-radius: 8px;
        font-size: 0.78rem;
        letter-spacing: 0.3px;
    }
    .hora-cell {
        background: #1a1e28;
        color: #9ca3ae;
        font-weight: 700;
        font-size: 0.82rem;
        white-space: nowrap;
        min-width: 52px;
    }
    .s-libre {
        background: rgba(92, 185, 122, 0.10);
        color: #5cb97a;
        cursor: default;
    }
    .s-ocupado {
        background: rgba(224, 108, 108, 0.10);
        color: #e06c6c;
    }
    .s-pasado {
        background: rgba(100, 116, 139, 0.06);
        color: #4a5260;
    }

    /* Leyenda */
    .leyenda {
        display: flex;
        justify-content: center;
        gap: 1.8rem;
        margin-top: 1rem;
        font-size: 0.82rem;
        color: #9ca3ae;
    }
    .leyenda-item { display: flex; align-items: center; gap: 6px; }
    .leyenda-dot {
        width: 10px; height: 10px;
        border-radius: 50%;
        display: inline-block;
    }
    .dot-libre   { background: #5cb97a; }
    .dot-ocupado { background: #e06c6c; }
    .dot-pasado  { background: #4a5260; }

    /* Resumen disponibilidad */
    .resumen-sem {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        margin-top: 0.8rem;
        flex-wrap: wrap;
    }
    .resumen-chip {
        background: #1a1e28;
        border: 1px solid rgba(201, 164, 92, 0.12);
        border-radius: 10px;
        padding: 0.4rem 0.75rem;
        font-size: 0.75rem;
        color: #9ca3ae;
        text-align: center;
    }
    .resumen-chip strong { color: #c9a45c; display: block; font-size: 0.95rem; }

    /* Section title */
    .section-title {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin: 0.5rem 0 0.2rem;
    }
    .section-title h2 {
        font-family: 'Playfair Display', serif;
        color: #f0ece4;
        font-weight: 700;
        font-size: 1.3rem;
        margin: 0;
        white-space: nowrap;
    }
    .section-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(201, 164, 92, 0.4) 0%, transparent 100%);
    }
</style>
""", unsafe_allow_html=True)

# ── Encabezado Hero ──────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>💈 Barbería: <span>El Rafa</span> 💈</h1>
    <p>Reserva tu cita en segundos</p>
</div>
""", unsafe_allow_html=True)

components.html(
        """
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700&display=swap" rel="stylesheet">
        <div style="display:flex;justify-content:center;margin-top:-10px;margin-bottom:14px;font-family:'Inter',sans-serif;">
                <div style="
                        background: rgba(201, 164, 92, 0.06);
                        border: 1px solid rgba(201, 164, 92, 0.2);
                        border-radius: 22px;
                        padding: 9px 20px;
                        display: inline-flex;
                        align-items: center;
                        gap: 12px;
                ">
                        <span style="font-size:14px;">🇨🇴</span>
                        <span id="hora-colombia" style="font-size:16px;font-weight:700;color:#c9a45c;min-width:100px;letter-spacing:0.5px;">--:--:--</span>
                        <span style="color:#6b7280;font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:1px;">COL</span>
                        <span style="color:#3a3f4a;font-size:14px;">│</span>
                        <span style="font-size:13px;">📅</span>
                        <span id="fecha-colombia" style="font-size:13px;font-weight:600;color:#d4cfc5;min-width:220px;">Cargando fecha...</span>
                </div>
        </div>
        <script>
            function actualizarFechaHoraCO() {
                const ahora = new Date();
                const hora = ahora.toLocaleTimeString('es-CO', {
                    timeZone: 'America/Bogota',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: true
                });
                const fecha = ahora.toLocaleDateString('es-CO', {
                    timeZone: 'America/Bogota',
                    weekday: 'long',
                    day: '2-digit',
                    month: 'long',
                    year: 'numeric'
                });

                const horaEl = document.getElementById('hora-colombia');
                const fechaEl = document.getElementById('fecha-colombia');
                if (horaEl) horaEl.textContent = hora;
                if (fechaEl) {
                    const fechaFormateada = fecha.charAt(0).toUpperCase() + fecha.slice(1);
                    fechaEl.textContent = fechaFormateada;
                }
            }

            actualizarFechaHoraCO();
            setInterval(actualizarFechaHoraCO, 1000);
        </script>
        """,
        height=70,
)

# ── Sección: Servicios ───────────────────────────────────────────────
st.markdown("""
<div class="section-title">
    <h2>Nuestros Servicios</h2>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

iconos_servicio = {"Corte": "✂️", "Corte + Barba": "💇‍♂️", "Barba": "🪒"}

cols = st.columns(len(SERVICIOS))
for col, (nombre, info) in zip(cols, SERVICIOS.items()):
    with col:
        icono = iconos_servicio.get(nombre, "✂️")
        st.markdown(f"""
        <div class="servicio-card">
            <div class="icono">{icono}</div>
            <h4>{nombre}</h4>
            <div class="detalle">
                <span>⏱ {info['duracion_min']} min</span>
            </div>
            <div class="precio">${info['precio']:,.0f} COP</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Sección: Reservar cita ───────────────────────────────────────────
st.markdown("""
<div class="section-title">
    <h2>📅 Reservar Cita</h2>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    nombre_cliente = st.text_input(
        "Nombre completo",
        placeholder="Ej: Juan Pérez",
    )

with col2:
    telefono_cliente = st.text_input(
        "Teléfono",
        placeholder="Ej: 310-555-1234",
    )

col3, col4 = st.columns(2)

with col3:
    servicio = st.selectbox(
        "Servicio",
        options=list(SERVICIOS.keys()),
    )

with col4:
    fecha = st.date_input(
        "Fecha",
        min_value=hoy_colombia(),
        max_value=hoy_colombia() + timedelta(days=30),
        value=hoy_colombia(),
    )

# Horarios disponibles (se actualiza en tiempo real)
slots = horarios_disponibles(fecha, servicio)

if slots:
    hora = st.selectbox("Horario disponible", options=slots)
else:
    st.warning("No hay horarios disponibles para esta fecha y servicio.")
    hora = None

enviado = st.button("Reservar cita", type="primary", use_container_width=True)

# ── Procesamiento ────────────────────────────────────────────────────
if enviado:
    errores: list[str] = []
    if not nombre_cliente.strip():
        errores.append("El nombre es obligatorio.")
    if not telefono_cliente.strip():
        errores.append("El teléfono es obligatorio.")
    if hora is None:
        errores.append("No hay horarios disponibles.")

    if errores:
        for e in errores:
            st.error(e)
    else:
        slots_actuales = horarios_disponibles(fecha, servicio)
        if hora not in slots_actuales:
            st.error("Ese horario acaba de ser reservado. Por favor elige otro.")
        else:
            cita_id, referencia = crear_cita(
                cliente=nombre_cliente.strip(),
                telefono=telefono_cliente.strip(),
                servicio=servicio,
                fecha=fecha,
                hora=hora,
            )

            st.balloons()

            dia_nombre = DIAS_ES[fecha.weekday()]
            mes_nombre = MESES_ES[fecha.month]
            fecha_fmt = f"{dia_nombre} {fecha.day} de {mes_nombre}, {fecha.year}"

            st.markdown(f"""
            <div class="confirmacion">
                <h3>✅ ¡Cita confirmada!</h3>
                <div class="grid">
                    <p class="item"><strong>📌 Código de reserva:</strong> <span style="color:#c9a45c;font-size:1.15rem;font-weight:800;letter-spacing:2px;">{referencia}</span></p>
                    <p class="item"><strong>Cliente:</strong> {nombre_cliente.strip()}</p>
                    <p class="item"><strong>Teléfono:</strong> {telefono_cliente.strip()}</p>
                    <p class="item"><strong>Servicio:</strong> {servicio}</p>
                    <p class="item"><strong>Fecha:</strong> {fecha_fmt}</p>
                    <p class="item"><strong>Hora:</strong> {hora} hrs</p>
                    <p class="item"><strong>Precio:</strong> ${SERVICIOS[servicio]['precio']:,.0f} COP</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.info(f"📌 Tu código de reserva es **{referencia}**. Para cancelar, busca tu cita con tu número de teléfono.")
# ── Sección: Cancelar cita ──────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="section-title">
    <h2>❌ Cancelar Cita</h2>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

tel_cancelar = st.text_input(
    "Ingresa tu número de teléfono para buscar tus citas",
    placeholder="Ej: 3101234567",
    key="tel_cancelar",
)

if tel_cancelar and tel_cancelar.strip():
    mis_citas = buscar_citas_por_telefono(tel_cancelar.strip())
    if not mis_citas:
        st.info("No se encontraron citas futuras con ese número de teléfono.")
    else:
        st.markdown(f"Se encontraron **{len(mis_citas)}** cita(s) próxima(s):")
        for cita in mis_citas:
            dia_fecha = date.fromisoformat(cita['fecha'])
            dia_nombre = DIAS_ES[dia_fecha.weekday()]
            mes_nombre = MESES_ES[dia_fecha.month]
            fecha_fmt = f"{dia_nombre} {dia_fecha.day} de {mes_nombre}"
            with st.container():
                col_info, col_btn = st.columns([3, 1])
                with col_info:
                    st.markdown(
                        f"📅 **{fecha_fmt}** a las **{cita['hora']}** hrs — "
                        f"*{cita['servicio']}* (Ref: {cita['referencia']})"
                    )
                with col_btn:
                    if st.button("❌ Cancelar", key=f"cancel_{cita['referencia']}", type="primary"):
                        resultado = cancelar_cita(cita['referencia'])
                        if resultado:
                            st.success(
                                f"✅ Cita cancelada: **{resultado['servicio']}** "
                                f"el {resultado['fecha']} a las {resultado['hora']}. "
                                f"El horario ha quedado disponible."
                            )
                            st.rerun()
                        else:
                            st.error("No se pudo cancelar la cita.")
# ── Sección: Disponibilidad semanal ──────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="section-title">
    <h2>📊 Disponibilidad Semanal</h2>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

# Estado para la semana activa
if "semana_offset" not in st.session_state:
    st.session_state.semana_offset = 0

# Navegación semanal con botones
col_prev, col_label, col_next = st.columns([1, 4, 1])

with col_prev:
    if st.button("◀ Anterior", use_container_width=True, disabled=st.session_state.semana_offset <= 0):
        st.session_state.semana_offset -= 1
        st.rerun()

with col_next:
    if st.button("Siguiente ▶", use_container_width=True, disabled=st.session_state.semana_offset >= 3):
        st.session_state.semana_offset += 1
        st.rerun()

# Calcular rango de la semana
hoy = hoy_colombia()
inicio_semana = hoy - timedelta(days=hoy.weekday()) + timedelta(weeks=st.session_state.semana_offset)
# No permitir retroceder antes de hoy
if inicio_semana < hoy:
    inicio_semana = hoy

fin_semana = inicio_semana + timedelta(days=6)

mes_inicio = MESES_ES[inicio_semana.month]
mes_fin = MESES_ES[fin_semana.month]

if inicio_semana.month == fin_semana.month:
    rango_label = f"{inicio_semana.day} – {fin_semana.day} de {mes_inicio}, {inicio_semana.year}"
else:
    rango_label = f"{inicio_semana.day} {mes_inicio} – {fin_semana.day} {mes_fin}, {fin_semana.year}"

with col_label:
    st.markdown(
        f'<div class="week-label" style="text-align:center; padding: 0.5rem 0; font-size:1.05rem; font-weight:600; color:#f0ece4;">{rango_label}</div>',
        unsafe_allow_html=True,
    )

# Generar datos de la semana
datos_semana = disponibilidad_semanal(inicio_semana)

ahora_str = ahora_colombia().strftime("%H:%M")
DIAS_CORTOS = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]

# Construir tabla HTML profesional
html = '<table class="agenda-table"><thead><tr><th style="min-width:52px;">HORA</th>'
for dia in datos_semana["dias"]:
    es_hoy = dia["fecha"] == hoy
    clase_hoy = " hoy" if es_hoy else ""
    dia_idx = dia["fecha"].weekday()
    dia_nombre_corto = DIAS_CORTOS[dia_idx]
    dia_num = dia["fecha"].day
    html += f'<th class="dia-header{clase_hoy}"><span class="dia-nombre">{dia_nombre_corto}</span><span class="dia-num">{dia_num}</span></th>'
html += '</tr></thead><tbody>'

for idx, slot in enumerate(datos_semana["slots"]):
    html += f'<tr><td class="hora-cell">{slot}</td>'
    for dia in datos_semana["dias"]:
        disponible = dia["disponibilidad"][idx]
        es_pasado = dia["fecha"] < hoy or (dia["fecha"] == hoy and slot <= ahora_str)
        if es_pasado:
            html += '<td class="s-pasado">—</td>'
        elif disponible:
            html += '<td class="s-libre">Disponible</td>'
        else:
            html += '<td class="s-ocupado">Ocupado</td>'
    html += '</tr>'
html += '</tbody></table>'

st.markdown(html, unsafe_allow_html=True)

# Leyenda
st.markdown("""
<div class="leyenda">
    <div class="leyenda-item"><span class="leyenda-dot dot-libre"></span> Disponible</div>
    <div class="leyenda-item"><span class="leyenda-dot dot-ocupado"></span> Ocupado</div>
    <div class="leyenda-item"><span class="leyenda-dot dot-pasado"></span> No disponible</div>
</div>
""", unsafe_allow_html=True)

# ── Sección: Vista barbero ───────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="section-title">
    <h2>🔐 Panel del Barbero</h2>
    <div class="section-line"></div>
</div>
""", unsafe_allow_html=True)

# Inicializar estado de autenticación
if "barbero_auth" not in st.session_state:
    st.session_state.barbero_auth = False

if not st.session_state.barbero_auth:
    st.markdown('<p style="color:#9ca3af;font-size:0.9rem;">Ingresa el PIN de 4 dígitos para acceder.</p>', unsafe_allow_html=True)
    col_pin, col_btn_pin = st.columns([2, 1])
    with col_pin:
        pin_input = st.text_input(
            "PIN del barbero",
            type="password",
            max_chars=4,
            placeholder="••••",
            key="pin_barbero_input",
            label_visibility="collapsed",
        )
    with col_btn_pin:
        if st.button("Ingresar", type="primary", use_container_width=True, key="btn_pin_login"):
            if pin_input and pin_input.strip() == obtener_pin_barbero():
                st.session_state.barbero_auth = True
                st.rerun()
            else:
                st.error("PIN incorrecto.")
else:
    # ── Barbero autenticado ──
    col_title_b, col_logout = st.columns([4, 1])
    with col_title_b:
        st.markdown('<p style="color:#5cb97a;font-weight:600;">✅ Acceso autorizado</p>', unsafe_allow_html=True)
    with col_logout:
        if st.button("Cerrar sesión", key="btn_logout_barbero"):
            st.session_state.barbero_auth = False
            st.rerun()

    # Pestañas: Citas del día | Cambiar PIN
    tab_citas, tab_pin = st.tabs(["📋 Citas del día", "🔑 Cambiar PIN"])

    with tab_citas:
        fecha_consulta = st.date_input(
            "Selecciona una fecha",
            value=hoy_colombia(),
            key="fecha_consulta_barbero",
        )
        citas_del_dia = obtener_citas_por_fecha(fecha_consulta)

        if citas_del_dia:
            dia_nombre = DIAS_ES[fecha_consulta.weekday()]
            mes_nombre = MESES_ES[fecha_consulta.month]
            st.markdown(f"**{len(citas_del_dia)} cita(s) — {dia_nombre} {fecha_consulta.day} de {mes_nombre}:**")
            for c in citas_del_dia:
                ref = c.get('referencia', '—')
                precio = SERVICIOS.get(c['servicio'], {}).get('precio', 0)
                with st.container():
                    col_info_b, col_cancel_b = st.columns([4, 1])
                    with col_info_b:
                        st.markdown(
                            f"🕐 **{c['hora']}** — *{c['servicio']}* (${precio:,.0f} COP)\n\n"
                            f"👤 {c['cliente']} · 📞 {c['telefono']} · Ref: `{ref}`"
                        )
                    with col_cancel_b:
                        if st.button("❌ Cancelar", key=f"barber_cancel_{ref}", type="secondary", use_container_width=True):
                            resultado = cancelar_cita(ref)
                            if resultado:
                                st.success(f"Cita de {resultado['cliente']} cancelada.")
                                st.rerun()
                            else:
                                st.error("No se pudo cancelar.")
                    st.markdown("---")
        else:
            st.info("No hay citas agendadas para esta fecha.")

    with tab_pin:
        st.markdown("Cambia tu PIN de acceso:")
        pin_actual = st.text_input("PIN actual", type="password", max_chars=4, key="pin_actual_change")
        pin_nuevo = st.text_input("Nuevo PIN (4 dígitos)", type="password", max_chars=4, key="pin_nuevo_change")
        pin_confirmar = st.text_input("Confirmar nuevo PIN", type="password", max_chars=4, key="pin_confirmar_change")
        if st.button("Cambiar PIN", type="primary", key="btn_cambiar_pin"):
            if not pin_actual or not pin_nuevo or not pin_confirmar:
                st.error("Completa todos los campos.")
            elif len(pin_nuevo) != 4 or not pin_nuevo.isdigit():
                st.error("El nuevo PIN debe ser exactamente 4 dígitos.")
            elif pin_nuevo != pin_confirmar:
                st.error("Los PINs nuevos no coinciden.")
            else:
                if cambiar_pin_barbero(pin_actual, pin_nuevo):
                    st.success("✅ PIN cambiado exitosamente.")
                else:
                    st.error("El PIN actual es incorrecto.")

# ── Footer ────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#6b7280; font-size:0.82rem;">💈 Barbería: El Rafa · Hecho con Streamlit 💈</p>',
    unsafe_allow_html=True,
)
