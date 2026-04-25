# 💈 Barbershop App

Aplicación web de agenda automática para barbería, construida con **Streamlit**.

## Funcionalidades

- **Ver servicios** — Corte, Corte + Barba, Barba (con precios y duración)
- **Seleccionar fecha** — Hasta 30 días en adelante
- **Horarios dinámicos** — Solo muestra los horarios realmente disponibles
- **Reservar cita** — Con nombre y teléfono del cliente
- **Confirmación en pantalla** — Número de cita, detalles y precio
- **Vista barbero** — Consultar todas las citas de un día

## Ejecutar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estructura

| Archivo           | Descripción                                  |
|-------------------|----------------------------------------------|
| `app.py`          | Interfaz principal de Streamlit              |
| `database.py`     | Lógica de base de datos (SQLite)             |
| `requirements.txt`| Dependencias del proyecto                    |
| `barbershop.db`   | Base de datos SQLite (se crea automáticamente)|

License
MIT
