# LaundryDesk — backend con JWT

Backend en Django + Django REST Framework + PostgreSQL siguiendo `openapi_equipo.yaml`.

Esta versión evoluciona el CRUD de S05-S06-A1 con autenticación JWT y protección de rutas administrativas.

## 1. Preparar el entorno

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Completa en `.env` la conexión a PostgreSQL y define un secreto JWT real:

```env
JWT_SECRET=<secreto-largo-y-aleatorio>
JWT_EXPIRATION=3600
```

`.env` no debe subirse al repositorio.

## 2. Base de datos

El esquema físico se crea con `S05_S06_A1/esquema_bd.sql` y la migración de autenticación agrega el correo único al administrador cuando corresponda.

Si tu base proviene de la entrega anterior y todavía tiene `admin_temporal`, consérvalo: el primer `POST /api/v1/auth/register` lo transforma en la cuenta real conservando el UUID.

## 3. Levantar servidor

```bash
python manage.py runserver
```

API: `http://127.0.0.1:8000/api/v1/`

## 4. Flujo de autenticación

1. `POST /api/v1/auth/register` — inicializa la única cuenta administrativa.
2. `POST /api/v1/auth/login` — devuelve JWT Bearer.
3. `GET /api/v1/auth/me` — valida el JWT y devuelve la cuenta autenticada.

## 5. Protección de rutas

JWT es la autenticación por defecto y las operaciones administrativas requieren `IsAuthenticated`.

Permanecen públicas las operaciones que el contrato define como públicas, como horarios, seguimiento y la consulta normal de servicios activos. Las escrituras de servicios/horarios y todos los endpoints administrativos de pedidos requieren token.

El listado de servicios admite `?incluir_inactivos=true` únicamente con JWT válido.

## 6. Identidad del administrador

Los CRUD protegidos ya no usan `ADMIN_ID_TEMPORAL`. La creación de pedidos, el historial inicial y los cambios de estado toman el administrador de `request.user`, obtenido del token JWT validado.

## 7. Pruebas

Consulta `revision_seguridad.md` para la matriz de rutas y las pruebas manuales esperadas: sin token → 401, token alterado → 401, token válido → operación autorizada. El control por roles no aplica al MVP porque existe un único administrador.
