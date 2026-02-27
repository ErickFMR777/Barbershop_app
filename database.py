"""
Módulo de base de datos para la aplicación de barbería.
Usa SQLite para almacenar las citas de los clientes.
"""

import sqlite3
import os
import random
from datetime import datetime, date, time, timedelta, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "barbershop.db")

# ── Zona horaria Colombia (UTC-5) ─────────────────────────────────────
TZ_COLOMBIA = timezone(timedelta(hours=-5))
ANTICIPACION_MIN = 60  # Minutos de anticipación mínima para reservar


def ahora_colombia() -> datetime:
    """Devuelve la fecha/hora actual en zona horaria de Colombia."""
    return datetime.now(TZ_COLOMBIA)


def hoy_colombia() -> date:
    """Devuelve la fecha actual en Colombia."""
    return ahora_colombia().date()

# ── Servicios disponibles ──────────────────────────────────────────────
SERVICIOS = {
    "Corte": {"duracion_min": 45, "precio": 15000},
    "Corte + Barba": {"duracion_min": 60, "precio": 20000},
    "Barba": {"duracion_min": 15, "precio": 5000},
}

# ── Horario de atención ───────────────────────────────────────────────
HORA_APERTURA = 9   # 09:00
HORA_CIERRE = 19    # 19:00 (última cita posible depende del servicio)
INTERVALO_MIN = 30  # Bloques de 30 minutos


def _get_connection() -> sqlite3.Connection:
    """Devuelve una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crea la tabla de citas si no existe."""
    conn = _get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            referencia  TEXT    NOT NULL UNIQUE,
            cliente     TEXT    NOT NULL,
            telefono    TEXT    NOT NULL,
            servicio    TEXT    NOT NULL,
            fecha       TEXT    NOT NULL,
            hora        TEXT    NOT NULL,
            creado_en   TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS configuracion (
            clave  TEXT PRIMARY KEY,
            valor  TEXT NOT NULL
        )
    """)
    # PIN por defecto: 0000
    conn.execute("""
        INSERT OR IGNORE INTO configuracion (clave, valor)
        VALUES ('pin_barbero', '0000')
    """)
    conn.commit()
    conn.close()


def obtener_pin_barbero() -> str:
    """Devuelve el PIN actual del barbero."""
    conn = _get_connection()
    row = conn.execute(
        "SELECT valor FROM configuracion WHERE clave = 'pin_barbero'"
    ).fetchone()
    conn.close()
    return row["valor"] if row else "0000"


def cambiar_pin_barbero(pin_actual: str, pin_nuevo: str) -> bool:
    """
    Cambia el PIN del barbero si el pin_actual es correcto.
    Retorna True si se cambió, False si el PIN actual no coincide.
    """
    if pin_actual != obtener_pin_barbero():
        return False
    conn = _get_connection()
    conn.execute(
        "UPDATE configuracion SET valor = ? WHERE clave = 'pin_barbero'",
        (pin_nuevo,),
    )
    conn.commit()
    conn.close()
    return True


def _generar_referencia() -> str:
    """Genera un código de referencia único de 5 dígitos."""
    conn = _get_connection()
    for _ in range(100):  # Máximo 100 intentos
        codigo = f"{random.randint(10000, 99999)}"
        existe = conn.execute(
            "SELECT 1 FROM citas WHERE referencia = ?", (codigo,)
        ).fetchone()
        if not existe:
            conn.close()
            return codigo
    conn.close()
    # Fallback: usar timestamp
    return str(int(datetime.now().timestamp()))[-5:]


def obtener_citas_por_fecha(fecha: date) -> list[dict]:
    """Devuelve todas las citas para una fecha dada."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM citas WHERE fecha = ? ORDER BY hora",
        (fecha.isoformat(),),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def horarios_disponibles(fecha: date, servicio: str) -> list[str]:
    """
    Calcula los horarios disponibles para un servicio en una fecha.
    Siempre se reservan bloques completos de 30 min:
      - Barba (15 min)       → 1 bloque  = 30 min
      - Corte (45 min)       → 2 bloques = 60 min
      - Corte + Barba (60 min) → 2 bloques = 60 min
    Devuelve una lista de strings "HH:MM".
    """
    duracion = SERVICIOS[servicio]["duracion_min"]
    bloques_necesarios = max(1, -(-duracion // INTERVALO_MIN))  # ceil division
    duracion_efectiva = bloques_necesarios * INTERVALO_MIN  # duración redondeada a bloques

    # Generar todos los slots posibles del día (usando duración efectiva)
    todos_los_slots: list[str] = []
    hora_actual = HORA_APERTURA * 60  # en minutos desde medianoche
    limite = HORA_CIERRE * 60
    while hora_actual + duracion_efectiva <= limite:
        hh, mm = divmod(hora_actual, 60)
        todos_los_slots.append(f"{hh:02d}:{mm:02d}")
        hora_actual += INTERVALO_MIN

    # Obtener las citas ya reservadas para esa fecha
    citas = obtener_citas_por_fecha(fecha)
    horas_ocupadas: set[str] = set()
    for cita in citas:
        dur_cita = SERVICIOS.get(cita["servicio"], {}).get("duracion_min", INTERVALO_MIN)
        bloques_cita = max(1, -(-dur_cita // INTERVALO_MIN))
        # Marcar TODOS los bloques completos que ocupa la cita
        base_min = int(cita["hora"][:2]) * 60 + int(cita["hora"][3:5])
        for b in range(bloques_cita):
            t = base_min + b * INTERVALO_MIN
            hh, mm = divmod(t, 60)
            horas_ocupadas.add(f"{hh:02d}:{mm:02d}")

    # Filtrar: un servicio necesita N bloques consecutivos libres
    disponibles: list[str] = []
    for slot in todos_los_slots:
        slot_min = int(slot[:2]) * 60 + int(slot[3:5])
        libre = True
        for b in range(bloques_necesarios):
            t = slot_min + b * INTERVALO_MIN
            hh, mm = divmod(t, 60)
            if f"{hh:02d}:{mm:02d}" in horas_ocupadas:
                libre = False
                break
        if libre:
            disponibles.append(slot)

    # Si la fecha es hoy, eliminar horarios que no cumplan la anticipación mínima
    if fecha == hoy_colombia():
        ahora_co = ahora_colombia()
        # Hora mínima = hora actual + anticipación (ej: 11:52 + 60min = 12:52)
        minimo = ahora_co + timedelta(minutes=ANTICIPACION_MIN)
        hora_minima = minimo.strftime("%H:%M")
        disponibles = [h for h in disponibles if h >= hora_minima]

    return disponibles


def crear_cita(cliente: str, telefono: str, servicio: str, fecha: date, hora: str) -> tuple[int, str]:
    """Inserta una nueva cita y devuelve (ID, referencia)."""
    referencia = _generar_referencia()
    conn = _get_connection()
    cursor = conn.execute(
        """
        INSERT INTO citas (referencia, cliente, telefono, servicio, fecha, hora)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (referencia, cliente, telefono, servicio, fecha.isoformat(), hora),
    )
    conn.commit()
    cita_id = cursor.lastrowid
    conn.close()
    return cita_id, referencia


def cancelar_cita(referencia: str) -> dict | None:
    """
    Cancela (elimina) una cita por su código de referencia.
    Devuelve los datos de la cita cancelada, o None si no existía.
    """
    conn = _get_connection()
    cita = conn.execute(
        "SELECT * FROM citas WHERE referencia = ?", (referencia,)
    ).fetchone()
    if not cita:
        conn.close()
        return None
    datos = dict(cita)
    conn.execute("DELETE FROM citas WHERE referencia = ?", (referencia,))
    conn.commit()
    conn.close()
    return datos


def buscar_citas_por_telefono(telefono: str) -> list[dict]:
    """
    Devuelve las citas futuras (desde hoy) asociadas a un teléfono.
    """
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM citas WHERE telefono = ? AND fecha >= ? ORDER BY fecha, hora",
        (telefono, hoy_colombia().isoformat()),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def bloques_ocupados_por_fecha(fecha: date) -> set[str]:
    """
    Devuelve el conjunto de bloques de 30 min ocupados en una fecha.
    Cada cita marca N bloques hacia adelante según su duración.
    """
    citas = obtener_citas_por_fecha(fecha)
    ocupados: set[str] = set()
    for cita in citas:
        dur_cita = SERVICIOS.get(cita["servicio"], {}).get("duracion_min", INTERVALO_MIN)
        bloques = max(1, -(-dur_cita // INTERVALO_MIN))
        base_min = int(cita["hora"][:2]) * 60 + int(cita["hora"][3:5])
        for b in range(bloques):
            t = base_min + b * INTERVALO_MIN
            hh, mm = divmod(t, 60)
            ocupados.add(f"{hh:02d}:{mm:02d}")
    return ocupados


def disponibilidad_semanal(fecha_inicio: date) -> dict:
    """
    Genera la disponibilidad semanal por bloques individuales de 30 min.
    Cada bloque se marca como libre u ocupado independientemente.
    """
    # Generar todos los bloques de 30 min del día
    todos_los_slots: list[str] = []
    hora_actual = HORA_APERTURA * 60
    limite = HORA_CIERRE * 60
    while hora_actual < limite:
        hh, mm = divmod(hora_actual, 60)
        todos_los_slots.append(f"{hh:02d}:{mm:02d}")
        hora_actual += INTERVALO_MIN

    dias_semana_es = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    dias: list[dict] = []

    for i in range(7):
        dia = fecha_inicio + timedelta(days=i)
        nombre_dia = dias_semana_es[dia.weekday()]
        etiqueta = f"{nombre_dia} {dia.strftime('%d/%m')}"

        ocupados = bloques_ocupados_por_fecha(dia)
        disponibilidad = [slot not in ocupados for slot in todos_los_slots]

        dias.append({
            "fecha": dia,
            "nombre": etiqueta,
            "disponibilidad": disponibilidad,
        })

    return {"slots": todos_los_slots, "dias": dias}
