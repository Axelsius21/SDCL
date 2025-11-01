import flet as ft
import sqlite3
from datetime import datetime, date
import hashlib

class LaboratorioApp:
    def __init__(self):
        self.db_name = "laboratorio.db"
        self.init_db()
        
    def init_db(self):
        """Inicializa la base de datos"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tabla de reservas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dia TEXT NOT NULL,
                turno TEXT NOT NULL,
                docente TEXT NOT NULL,
                carrera TEXT NOT NULL,
                curso TEXT NOT NULL,
                horario TEXT NOT NULL,
                periodo TEXT NOT NULL,
                fecha_inicio DATE,
                fecha_fin DATE,
                fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                nombre TEXT NOT NULL,
                email TEXT,
                rol TEXT DEFAULT 'usuario',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insertar usuario administrador por defecto si no existe
        cursor.execute('SELECT COUNT(*) FROM usuarios WHERE username = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            password_hash = self.hash_password('admin123')
            cursor.execute('''
                INSERT INTO usuarios (username, password, nombre, email, rol)
                VALUES (?, ?, ?, ?, ?)
            ''', ('admin', password_hash, 'Administrador', 'admin@laboratorio.com', 'admin'))
        
        conn.commit()
        conn.close()

    def hash_password(self, password):
        """Encripta la contraseña usando SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verificar_password(self, password, password_hash):
        """Verifica si la contraseña coincide con el hash"""
        return self.hash_password(password) == password_hash

    # ========== MÉTODOS PARA USUARIOS ==========
    
    def agregar_usuario(self, username, password, nombre, email=None, rol='usuario'):
        """Agrega un nuevo usuario a la base de datos"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO usuarios (username, password, nombre, email, rol)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, password_hash, nombre, email, rol))
            
            conn.commit()
            conn.close()
            return True, "Usuario agregado exitosamente"
        except sqlite3.IntegrityError:
            return False, "El nombre de usuario ya existe"
        except Exception as e:
            return False, f"Error al agregar usuario: {str(e)}"

    def obtener_usuarios(self):
        """Obtiene todos los usuarios"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, nombre, email, rol, fecha_creacion FROM usuarios ORDER BY username')
        usuarios = cursor.fetchall()
        conn.close()
        return usuarios

    def obtener_usuario_por_id(self, id_usuario):
        """Obtiene un usuario específico por ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, nombre, email, rol FROM usuarios WHERE id = ?', (id_usuario,))
        usuario = cursor.fetchone()
        conn.close()
        return usuario

    def actualizar_usuario(self, id_usuario, username, nombre, email=None, rol='usuario', cambiar_password=False, nueva_password=None):
        """Actualiza un usuario existente"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if cambiar_password and nueva_password:
                password_hash = self.hash_password(nueva_password)
                cursor.execute('''
                    UPDATE usuarios 
                    SET username = ?, password = ?, nombre = ?, email = ?, rol = ?
                    WHERE id = ?
                ''', (username, password_hash, nombre, email, rol, id_usuario))
            else:
                cursor.execute('''
                    UPDATE usuarios 
                    SET username = ?, nombre = ?, email = ?, rol = ?
                    WHERE id = ?
                ''', (username, nombre, email, rol, id_usuario))
            
            conn.commit()
            conn.close()
            return True, "Usuario actualizado exitosamente"
        except sqlite3.IntegrityError:
            return False, "El nombre de usuario ya existe"
        except Exception as e:
            return False, f"Error al actualizar usuario: {str(e)}"

    def eliminar_usuario(self, id_usuario):
        """Elimina un usuario por ID"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # No permitir eliminar al usuario admin
            cursor.execute('SELECT username FROM usuarios WHERE id = ?', (id_usuario,))
            usuario = cursor.fetchone()
            if usuario and usuario[0] == 'admin':
                return False, "No se puede eliminar al usuario administrador principal"
            
            cursor.execute('DELETE FROM usuarios WHERE id = ?', (id_usuario,))
            
            conn.commit()
            conn.close()
            return True, "Usuario eliminado exitosamente"
        except Exception as e:
            return False, f"Error al eliminar usuario: {str(e)}"

    def autenticar_usuario(self, username, password):
        """Autentica un usuario"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, password, nombre, rol FROM usuarios WHERE username = ?', (username,))
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario and self.verificar_password(password, usuario[2]):
            return True, usuario
        return False, None

    # ========== MÉTODOS PARA RESERVAS (EXISTENTES) ==========
    
    def agregar_reserva(self, dia, turno, docente, carrera, curso, horario, periodo, fecha_inicio=None, fecha_fin=None):
        """Agrega una nueva reserva a la base de datos"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reservas (dia, turno, docente, carrera, curso, horario, periodo, fecha_inicio, fecha_fin)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (dia, turno, docente, carrera, curso, horario, periodo, fecha_inicio, fecha_fin))
        
        conn.commit()
        conn.close()
        return True

    def obtener_reserva_por_id(self, id_reserva):
        """Obtiene una reserva específica por ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM reservas WHERE id = ?', (id_reserva,))
        reserva = cursor.fetchone()
        conn.close()
        return reserva

    def actualizar_reserva(self, id_reserva, dia, turno, docente, carrera, curso, horario, periodo, fecha_inicio=None, fecha_fin=None):
        """Actualiza una reserva existente"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE reservas 
            SET dia = ?, turno = ?, docente = ?, carrera = ?, curso = ?, horario = ?, periodo = ?, fecha_inicio = ?, fecha_fin = ?
            WHERE id = ?
        ''', (dia, turno, docente, carrera, curso, horario, periodo, fecha_inicio, fecha_fin, id_reserva))
        
        conn.commit()
        conn.close()
        return True

    def obtener_reservas(self):
        """Obtiene todas las reservas"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM reservas ORDER BY dia, horario
        ''')
        
        reservas = cursor.fetchall()
        conn.close()
        return reservas

    def eliminar_reserva(self, id_reserva):
        """Elimina una reserva por ID"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM reservas WHERE id = ?', (id_reserva,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error al eliminar reserva {id_reserva}: {str(e)}")
            return False

def main(page: ft.Page):
    # Configuración de la página
    page.title = "Sistema de Control de Laboratorio"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # Variables de estado
    current_view = "login"
    reserva_editando = None
    usuario_editando = None
    usuario_autenticado = None
    
    # Instancia de la aplicación
    app = LaboratorioApp()
    
    # Dropdowns predefinidos
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    turnos = ["Mañana", "Tarde", "Noche"]
    carreras = ["Ingenieria Comercial", "Empresariales", "ADM. De Empresas", "Contabilidad", "Economia"]
    roles = ["admin", "usuario"]
    
    # ========== COMPONENTES DEL LOGIN ==========
    
    login_username = ft.TextField(
        label="Usuario",
        hint_text="Ingrese su nombre de usuario",
        width=300,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        prefix_icon=ft.Icons.PERSON
    )
    
    login_password = ft.TextField(
        label="Contraseña",
        hint_text="Ingrese su contraseña",
        width=300,
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        prefix_icon=ft.Icons.LOCK
    )
    
    login_mensaje = ft.Text("", color=ft.Colors.RED)
    
    # ========== COMPONENTES DE GESTIÓN DE USUARIOS ==========
    
    # Para agregar/editar usuarios
    user_username = ft.TextField(
        label="Nombre de usuario",
        hint_text="Ingrese nombre de usuario único",
        width=300,
        border_color=ft.Colors.BLUE_400,
        filled=True
    )
    
    user_password = ft.TextField(
        label="Contraseña",
        hint_text="Ingrese contraseña",
        width=300,
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.BLUE_400,
        filled=True
    )
    
    user_nombre = ft.TextField(
        label="Nombre completo",
        hint_text="Ingrese nombre completo",
        width=300,
        border_color=ft.Colors.BLUE_400,
        filled=True
    )
    
    user_email = ft.TextField(
        label="Email",
        hint_text="Ingrese email (opcional)",
        width=300,
        border_color=ft.Colors.BLUE_400,
        filled=True
    )
    
    user_rol = ft.Dropdown(
        label="Rol",
        options=[ft.dropdown.Option(rol) for rol in roles],
        width=300,
        border_color=ft.Colors.BLUE_400,
        filled=True
    )
    
    user_cambiar_password = ft.Checkbox(
        label="Cambiar contraseña",
        value=False
    )
    
    user_mensaje = ft.Text("", color=ft.Colors.GREEN)
    
    # ========== COMPONENTES DEL FORMULARIO DE RESERVAS ==========
    
    dropdown_dia = ft.Dropdown(
        label="Día de la semana",
        hint_text="Seleccione un día",
        options=[ft.dropdown.Option(dia) for dia in dias],
        width=300,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    dropdown_turno = ft.Dropdown(
        label="Turno",
        hint_text="Seleccione turno",
        options=[ft.dropdown.Option(turno) for turno in turnos],
        width=300,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    textfield_docente = ft.TextField(
        label="Nombre del docente",
        hint_text="Ingrese nombre completo",
        width=400,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    dropdown_carrera = ft.Dropdown(
        label="Carrera",
        hint_text="Seleccione carrera",
        options=[ft.dropdown.Option(carrera) for carrera in carreras],
        width=400,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    textfield_curso = ft.TextField(
        label="Curso/Materia",
        hint_text="Ingrese nombre del curso",
        width=400,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    textfield_horario = ft.TextField(
        label="Horario específico",
        hint_text="Ej: 08:00-10:00",
        width=400,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    radio_periodo = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="semestre", label="Todo el semestre"),
            ft.Radio(value="fechas", label="Fechas específicas")
        ])
    )
    
    datepicker_inicio = ft.TextField(
        label="Fecha inicio",
        hint_text="YYYY-MM-DD",
        width=200,
        visible=False,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    datepicker_fin = ft.TextField(
        label="Fecha fin",
        hint_text="YYYY-MM-DD",
        width=200,
        visible=False,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    mensaje_texto = ft.Text("", color=ft.Colors.GREEN)
    
    # ========== CONTROLES PARA LA VISTA DE EDICIÓN ==========
    
    edit_dropdown_dia = ft.Dropdown(
        label="Día de la semana",
        options=[ft.dropdown.Option(dia) for dia in dias],
        width=300,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    edit_dropdown_turno = ft.Dropdown(
        label="Turno",
        options=[ft.dropdown.Option(turno) for turno in turnos],
        width=300,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    edit_textfield_docente = ft.TextField(
        label="Nombre del docente",
        width=400,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    edit_dropdown_carrera = ft.Dropdown(
        label="Carrera",
        options=[ft.dropdown.Option(carrera) for carrera in carreras],
        width=400,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    edit_textfield_curso = ft.TextField(
        label="Curso/Materia",
        width=400,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    edit_textfield_horario = ft.TextField(
        label="Horario específico",
        width=400,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    edit_radio_periodo = ft.RadioGroup(
        content=ft.Column([
            ft.Radio(value="semestre", label="Todo el semestre"),
            ft.Radio(value="fechas", label="Fechas específicas")
        ])
    )
    
    edit_datepicker_inicio = ft.TextField(
        label="Fecha inicio",
        hint_text="YYYY-MM-DD",
        width=200,
        visible=False,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    edit_datepicker_fin = ft.TextField(
        label="Fecha fin",
        hint_text="YYYY-MM-DD",
        width=200,
        visible=False,
        border_color=ft.Colors.BLUE_400,
        filled=True,
        fill_color=ft.Colors.WHITE
    )
    
    # ========== BARRA LATERAL DE MÓDULOS ==========
    
    def crear_barra_lateral():
        """Crea la barra lateral con los módulos del sistema"""
        if not usuario_autenticado:
            return ft.Container(width=0)
        
        # Información del usuario
        user_info = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(ft.Icons.PERSON, size=40, color=ft.Colors.BLUE_700),
                    width=60,
                    height=60,
                    bgcolor=ft.Colors.BLUE_100,
                    border_radius=30,
                    alignment=ft.alignment.center
                ),
                ft.Text(usuario_autenticado[3], 
                       weight=ft.FontWeight.BOLD,
                       size=16,
                       text_align=ft.TextAlign.CENTER),
                ft.Text(f"Rol: {usuario_autenticado[4]}", 
                       size=12, 
                       color=ft.Colors.GREY_600,
                       text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.GREY_300))
        )
        
        # Botones de módulos
        modulos = [
            {"icon": ft.Icons.ADD_BOX, "label": "Nueva Reserva", "view": mostrar_nueva_reserva},
            {"icon": ft.Icons.LIST_ALT, "label": "Ver Reservas", "view": mostrar_reservas},
        ]
        
        # Agregar módulo de gestión de usuarios solo para administradores
        if usuario_autenticado and usuario_autenticado[4] == 'admin':
            modulos.append({"icon": ft.Icons.PEOPLE, "label": "Gestión de Usuarios", "view": mostrar_gestion_usuarios})
        
        modulos.append({"icon": ft.Icons.INFO, "label": "Información", "view": mostrar_informacion})
        
        botones_modulos = []
        for modulo in modulos:
            boton = ft.TextButton(
                content=ft.Row([
                    ft.Icon(modulo["icon"], color=ft.Colors.BLUE_700, size=20),
                    ft.Text(modulo["label"], size=14, weight=ft.FontWeight.W_500),
                ], alignment=ft.MainAxisAlignment.START),
                style=ft.ButtonStyle(
                    color=ft.Colors.BLUE_700,
                    bgcolor=ft.Colors.TRANSPARENT,
                    padding=15,
                    overlay_color=ft.Colors.BLUE_50,
                ),
                on_click=lambda e, vista=modulo["view"]: vista()
            )
            botones_modulos.append(boton)
        
        # Botón de cerrar sesión
        boton_cerrar_sesion = ft.TextButton(
            content=ft.Row([
                ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.RED_600, size=20),
                ft.Text("Cerrar Sesión", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.RED_600),
            ], alignment=ft.MainAxisAlignment.START),
            style=ft.ButtonStyle(
                color=ft.Colors.RED_600,
                bgcolor=ft.Colors.TRANSPARENT,
                padding=15,
                overlay_color=ft.Colors.RED_50,
            ),
            on_click=lambda e: cerrar_sesion()
        )
        
        return ft.Container(
            content=ft.Column([
                user_info,
                ft.Container(
                    content=ft.Column(botones_modulos, spacing=0),
                    padding=ft.padding.symmetric(vertical=10),
                    expand=True
                ),
                ft.Divider(),
                boton_cerrar_sesion,
            ], spacing=0),
            width=250,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.only(right=ft.border.BorderSide(1, ft.Colors.GREY_300)),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=4,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(2, 0),
            )
        )
    
    # ========== BARRA SUPERIOR ==========
    
    barra_superior = ft.Container(
        content=ft.Row([
            ft.Text(
                "SISTEMA DE CONTROL DE LABORATORIO", 
                color=ft.Colors.WHITE, 
                weight=ft.FontWeight.BOLD,
                size=18
            ),
            ft.Container(expand=True),
            ft.Text(
                f"Usuario: {usuario_autenticado[3] if usuario_autenticado else 'No autenticado'}",
                color=ft.Colors.WHITE,
                size=14
            ) if usuario_autenticado else ft.Container(),
        ], alignment=ft.MainAxisAlignment.START),
        bgcolor=ft.Colors.BLUE_700,
        padding=15,
        height=60
    )
    
    # ========== FUNCIONALIDADES DE AUTENTICACIÓN ==========
    
    def iniciar_sesion(e):
        nonlocal usuario_autenticado
        username = login_username.value.strip()
        password = login_password.value.strip()
        
        if not username or not password:
            login_mensaje.value = "Por favor complete todos los campos"
            login_mensaje.color = ft.Colors.RED
            page.update()
            return
        
        autenticado, usuario = app.autenticar_usuario(username, password)
        
        if autenticado:
            usuario_autenticado = usuario
            login_mensaje.value = ""
            # Actualizar la interfaz para mostrar los módulos
            actualizar_interfaz_principal()
            mostrar_nueva_reserva()
        else:
            login_mensaje.value = "Usuario o contraseña incorrectos"
            login_mensaje.color = ft.Colors.RED
            page.update()
    
    def cerrar_sesion():
        nonlocal usuario_autenticado, current_view
        usuario_autenticado = None
        current_view = "login"
        # Volver a la interfaz de login
        actualizar_interfaz_principal()
        mostrar_login()
    
    def actualizar_interfaz_principal():
        """Actualiza la interfaz principal según el estado de autenticación"""
        main_container.controls.clear()
        
        if usuario_autenticado:
            # Interfaz con barra lateral y contenido
            main_container.controls.append(
                ft.Row([
                    crear_barra_lateral(),
                    ft.Container(
                        content=content_area,
                        expand=True,
                        padding=20
                    )
                ], expand=True)
            )
        else:
            # Solo barra superior para login
            main_container.controls.append(
                ft.Column([
                    barra_superior,
                    ft.Container(
                        content=content_area,
                        expand=True
                    )
                ], expand=True)
            )
        
        page.update()
    
    # ========== FUNCIONALIDADES DE GESTIÓN DE USUARIOS ==========
    
    def limpiar_formulario_usuario():
        user_username.value = ""
        user_password.value = ""
        user_nombre.value = ""
        user_email.value = ""
        user_rol.value = "usuario"
        user_cambiar_password.value = False
        user_mensaje.value = ""
    
    def agregar_usuario_handler(e):
        if not all([user_username.value, user_password.value, user_nombre.value]):
            user_mensaje.value = "Por favor complete todos los campos obligatorios"
            user_mensaje.color = ft.Colors.RED
            page.update()
            return
        
        exito, mensaje = app.agregar_usuario(
            user_username.value,
            user_password.value,
            user_nombre.value,
            user_email.value,
            user_rol.value
        )
        
        user_mensaje.value = mensaje
        user_mensaje.color = ft.Colors.GREEN if exito else ft.Colors.RED
        
        if exito:
            limpiar_formulario_usuario()
            mostrar_gestion_usuarios()
        
        page.update()
    
    def editar_usuario_handler(e):
        nonlocal usuario_editando
        
        if not usuario_editando:
            return
        
        if not all([user_username.value, user_nombre.value]):
            user_mensaje.value = "Por favor complete todos los campos obligatorios"
            user_mensaje.color = ft.Colors.RED
            page.update()
            return
        
        if user_cambiar_password.value and not user_password.value:
            user_mensaje.value = "Para cambiar la contraseña, debe ingresar una nueva"
            user_mensaje.color = ft.Colors.RED
            page.update()
            return
        
        exito, mensaje = app.actualizar_usuario(
            usuario_editando,
            user_username.value,
            user_nombre.value,
            user_email.value,
            user_rol.value,
            user_cambiar_password.value,
            user_password.value if user_cambiar_password.value else None
        )
        
        user_mensaje.value = mensaje
        user_mensaje.color = ft.Colors.GREEN if exito else ft.Colors.RED
        
        if exito:
            mostrar_gestion_usuarios()
        
        page.update()
    
    def eliminar_usuario_handler(id_usuario):
        exito, mensaje = app.eliminar_usuario(id_usuario)
        
        user_mensaje.value = mensaje
        user_mensaje.color = ft.Colors.GREEN if exito else ft.Colors.RED
        
        if exito:
            mostrar_gestion_usuarios()
        
        page.update()
    
    def mostrar_edicion_usuario(id_usuario):
        nonlocal usuario_editando
        usuario_editando = id_usuario
        
        usuario = app.obtener_usuario_por_id(id_usuario)
        if not usuario:
            mostrar_gestion_usuarios()
            return
        
        id_user, username, nombre, email, rol = usuario
        
        user_username.value = username
        user_nombre.value = nombre
        user_email.value = email if email else ""
        user_rol.value = rol
        user_password.value = ""
        user_cambiar_password.value = False
        
        content_area.controls.clear()
        content_area.controls.append(crear_formulario_usuario("Editar Usuario", editar_usuario_handler, True))
        page.update()

    def cancelar_edicion_usuario(e=None):
        """Cancela la edición/agregado de usuario y vuelve a la gestión de usuarios."""
        nonlocal usuario_editando
        usuario_editando = None
        limpiar_formulario_usuario()
        mostrar_gestion_usuarios()
        page.update()
    
    def crear_formulario_usuario(titulo, handler_func, es_edicion=False):
        return ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_700, size=30),
                                ft.Text(titulo, 
                                       size=22, 
                                       weight=ft.FontWeight.BOLD,
                                       color=ft.Colors.BLUE_900),
                            ]),
                            padding=ft.padding.only(bottom=20)
                        ),
                        
                        user_username,
                        user_nombre,
                        user_email,
                        user_rol,
                        
                        ft.Container(height=10),
                        
                        user_password if not es_edicion else ft.Column([
                            user_cambiar_password,
                            user_password
                        ]),
                        
                        ft.Container(height=20),
                        
                        ft.Row([
                            ft.ElevatedButton(
                                "Guardar",
                                icon=ft.Icons.SAVE,
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor=ft.Colors.GREEN_600,
                                    padding=15
                                ),
                                on_click=handler_func
                            ),
                            ft.OutlinedButton(
                                "Cancelar",
                                icon=ft.Icons.ARROW_BACK,
                                style=ft.ButtonStyle(padding=15),
                                on_click=cancelar_edicion_usuario
                            )
                        ], spacing=20),
                        
                        ft.Container(
                            content=user_mensaje,
                            padding=10,
                            bgcolor=ft.Colors.GREY_50,
                            border_radius=8,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            visible=bool(user_mensaje.value)
                        )
                    ]),
                    padding=30
                ),
                elevation=3
            ),
            padding=20,
            expand=True
        )
    
    # ========== VISTAS ==========
    
    def mostrar_login():
        nonlocal current_view
        current_view = "login"
        
        content_area.controls.clear()
        content_area.controls.append(
            ft.Container(
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Container(
                                content=ft.Icon(ft.Icons.COMPUTER, size=80, color=ft.Colors.BLUE_700),
                                alignment=ft.alignment.center,
                                padding=20
                            ),
                            ft.Text("Sistema de Control de Laboratorio", 
                                   size=24, 
                                   weight=ft.FontWeight.BOLD,
                                   text_align=ft.TextAlign.CENTER),
                            ft.Text("Inicie sesión para continuar", 
                                   size=16,
                                   color=ft.Colors.GREY_600,
                                   text_align=ft.TextAlign.CENTER),
                            
                            ft.Container(height=30),
                            
                            login_username,
                            login_password,
                            
                            ft.Container(height=20),
                            
                            ft.ElevatedButton(
                                "Iniciar Sesión",
                                icon=ft.Icons.LOGIN,
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor=ft.Colors.BLUE_600,
                                    padding=20
                                ),
                                on_click=iniciar_sesion,
                                width=300
                            ),
                            
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Credenciales por defecto:", weight=ft.FontWeight.BOLD),
                                    ft.Text("Usuario: admin"),
                                    ft.Text("Contraseña: admin123"),
                                ]),
                                padding=20,
                                bgcolor=ft.Colors.YELLOW_50,
                                border_radius=8,
                                margin=20
                            ),
                            
                            ft.Container(
                                content=login_mensaje,
                                padding=10,
                                visible=bool(login_mensaje.value)
                            )
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=40,
                        width=500
                    ),
                    elevation=5
                ),
                alignment=ft.alignment.center,
                expand=True
            )
        )
        page.update()
    
    def mostrar_gestion_usuarios():
        if not usuario_autenticado or usuario_autenticado[4] != 'admin':
            mostrar_nueva_reserva()
            return
        
        nonlocal current_view
        current_view = "gestion_usuarios"
        
        usuarios = app.obtener_usuarios()
        
        usuarios_container = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=10)
        
        if not usuarios:
            usuarios_container.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=50, color=ft.Colors.GREY_400),
                            ft.Text("No hay usuarios registrados", 
                                   size=18, 
                                   weight=ft.FontWeight.BOLD),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=40
                    )
                )
            )
        else:
            for usuario in usuarios:
                id_user, username, nombre, email, rol, fecha_creacion = usuario
                
                boton_editar = ft.TextButton(
                    "Editar",
                    icon=ft.Icons.EDIT,
                    style=ft.ButtonStyle(color=ft.Colors.BLUE),
                    on_click=lambda e, id=id_user: mostrar_edicion_usuario(id)
                )
                
                boton_eliminar = ft.TextButton(
                    "Eliminar",
                    icon=ft.Icons.DELETE,
                    style=ft.ButtonStyle(color=ft.Colors.RED),
                    on_click=lambda e, id=id_user: eliminar_usuario_handler(id)
                )
                
                usuarios_container.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_700),
                                    title=ft.Text(nombre, weight=ft.FontWeight.BOLD),
                                    subtitle=ft.Text(f"Usuario: {username} | Rol: {rol}"),
                                ),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Row([
                                            ft.Text("📧 Email:", weight=ft.FontWeight.BOLD),
                                            ft.Text(email if email else "No especificado"),
                                        ]),
                                        ft.Row([
                                            ft.Text("📅 Creado:", weight=ft.FontWeight.BOLD),
                                            ft.Text(fecha_creacion.split()[0]),
                                        ]),
                                    ], spacing=5),
                                    padding=ft.padding.only(left=16, right=16, bottom=10)
                                ),
                                ft.Row([boton_editar, boton_eliminar], alignment=ft.MainAxisAlignment.END)
                            ]),
                            padding=10
                        ),
                        elevation=2
                    )
                )
        
        content_area.controls.clear()
        content_area.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.PEOPLE, color=ft.Colors.BLUE_700),
                                    title=ft.Text("Gestión de Usuarios", 
                                                size=22, 
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.BLUE_900),
                                    subtitle=ft.Text(f"Total: {len(usuarios)} usuarios"),
                                    trailing=ft.ElevatedButton(
                                        "Agregar Usuario",
                                        icon=ft.Icons.ADD,
                                        on_click=lambda e: (
                                            limpiar_formulario_usuario(),
                                            content_area.controls.clear(),
                                            content_area.controls.append(
                                                crear_formulario_usuario("Agregar Usuario", agregar_usuario_handler, False)
                                            ),
                                            page.update()
                                        )
                                    )
                                ),
                                ft.Divider(),
                                usuarios_container
                            ]),
                            padding=20
                        ),
                        elevation=3
                    )
                ]),
                padding=20,
                expand=True
            )
        )
        page.update()
    
    # ========== FUNCIONALIDADES EXISTENTES DE RESERVAS ==========
    
    def mostrar_fechas(e):
        if radio_periodo.value == "fechas":
            datepicker_inicio.visible = True
            datepicker_fin.visible = True
        else:
            datepicker_inicio.visible = False
            datepicker_fin.visible = False
        page.update()
    
    radio_periodo.on_change = mostrar_fechas
    
    def editar_mostrar_fechas(e):
        if edit_radio_periodo.value == "fechas":
            edit_datepicker_inicio.visible = True
            edit_datepicker_fin.visible = True
        else:
            edit_datepicker_inicio.visible = False
            edit_datepicker_fin.visible = False
        page.update()
    
    edit_radio_periodo.on_change = editar_mostrar_fechas
    
    def limpiar_formulario(e):
        dropdown_dia.value = None
        dropdown_turno.value = None
        textfield_docente.value = ""
        dropdown_carrera.value = None
        textfield_curso.value = ""
        textfield_horario.value = ""
        radio_periodo.value = None
        datepicker_inicio.value = ""
        datepicker_fin.value = ""
        datepicker_inicio.visible = False
        datepicker_fin.visible = False
        mensaje_texto.value = ""
        page.update()
    
    def agregar_reserva_handler(e):
        if not all([
            dropdown_dia.value,
            dropdown_turno.value,
            textfield_docente.value.strip(),
            dropdown_carrera.value,
            textfield_curso.value.strip(),
            textfield_horario.value.strip(),
            radio_periodo.value
        ]):
            mensaje_texto.value = "❌ Por favor complete todos los campos obligatorios"
            mensaje_texto.color = ft.Colors.RED
            page.update()
            return
        
        if radio_periodo.value == "fechas":
            if not datepicker_inicio.value.strip() or not datepicker_fin.value.strip():
                mensaje_texto.value = "❌ Para período con fechas específicas, complete ambas fechas"
                mensaje_texto.color = ft.Colors.RED
                page.update()
                return
            
            try:
                datetime.strptime(datepicker_inicio.value, "%Y-%m-%d")
                datetime.strptime(datepicker_fin.value, "%Y-%m-%d")
            except ValueError:
                mensaje_texto.value = "❌ Formato de fecha incorrecto. Use YYYY-MM-DD"
                mensaje_texto.color =ft.Colors.RED
                page.update()
                return
        
        fecha_inicio = datepicker_inicio.value if radio_periodo.value == "fechas" else None
        fecha_fin = datepicker_fin.value if radio_periodo.value == "fechas" else None
        periodo_texto = "Todo el semestre" if radio_periodo.value == "semestre" else f"{fecha_inicio} a {fecha_fin}"
        
        try:
            app.agregar_reserva(
                dia=dropdown_dia.value,
                turno=dropdown_turno.value,
                docente=textfield_docente.value,
                carrera=dropdown_carrera.value,
                curso=textfield_curso.value,
                horario=textfield_horario.value,
                periodo=periodo_texto,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            
            mensaje_texto.value = "✅ Reserva agregada exitosamente!"
            mensaje_texto.color = ft.Colors.GREEN
            limpiar_formulario(e)
            page.update()
            
        except Exception as ex:
            mensaje_texto.value = f"❌ Error al guardar: {str(ex)}"
            mensaje_texto.color = ft.Colors.RED
            page.update()

    def eliminar_reserva_handler(reserva_id):
        exito = app.eliminar_reserva(reserva_id)
        
        if exito:
            mensaje_texto.value = f"✅ Reserva eliminada exitosamente!"
            mensaje_texto.color = ft.Colors.GREEN
            mostrar_reservas()
        else:
            mensaje_texto.value = f"❌ Error al eliminar la reserva"
            mensaje_texto.color = ft.Colors.RED
        
        page.update()
    
    def guardar_edicion(e):
        nonlocal reserva_editando
        
        if not reserva_editando:
            return
        
        if not all([
            edit_dropdown_dia.value,
            edit_dropdown_turno.value,
            edit_textfield_docente.value.strip(),
            edit_dropdown_carrera.value,
            edit_textfield_curso.value.strip(),
            edit_textfield_horario.value.strip(),
            edit_radio_periodo.value
        ]):
            mensaje_texto.value = "❌ Por favor complete todos los campos obligatorios"
            mensaje_texto.color = ft.Colors.RED
            page.update()
            return
        
        if edit_radio_periodo.value == "fechas":
            if not edit_datepicker_inicio.value.strip() or not edit_datepicker_fin.value.strip():
                mensaje_texto.value = "❌ Para período con fechas específicas, complete ambas fechas"
                mensaje_texto.color = ft.Colors.RED
                page.update()
                return
            
            try:
                datetime.strptime(edit_datepicker_inicio.value, "%Y-%m-%d")
                datetime.strptime(edit_datepicker_fin.value, "%Y-%m-%d")
            except ValueError:
                mensaje_texto.value = "❌ Formato de fecha incorrecto. Use YYYY-MM-DD"
                mensaje_texto.color = ft.Colors.RED
                page.update()
                return
        
        fecha_inicio = edit_datepicker_inicio.value if edit_radio_periodo.value == "fechas" else None
        fecha_fin = edit_datepicker_fin.value if edit_radio_periodo.value == "fechas" else None
        periodo_texto = "Todo el semestre" if edit_radio_periodo.value == "semestre" else f"{fecha_inicio} a {fecha_fin}"
        
        try:
            app.actualizar_reserva(
                reserva_editando,
                dia=edit_dropdown_dia.value,
                turno=edit_dropdown_turno.value,
                docente=edit_textfield_docente.value,
                carrera=edit_dropdown_carrera.value,
                curso=edit_textfield_curso.value,
                horario=edit_textfield_horario.value,
                periodo=periodo_texto,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            
            mensaje_texto.value = "✅ Reserva actualizada exitosamente!"
            mensaje_texto.color = ft.Colors.GREEN
            mostrar_reservas()
            
        except Exception as ex:
            mensaje_texto.value = f"❌ Error al actualizar: {str(ex)}"
            mensaje_texto.color = ft.Colors.RED
            page.update()
    
    def mostrar_nueva_reserva():
        if not usuario_autenticado:
            mostrar_login()
            return
        
        nonlocal current_view
        current_view = "nueva_reserva"
        
        content_area.controls.clear()
        
        formulario_content = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ADD_CIRCLE, color=ft.Colors.BLUE_700, size=30),
                        ft.Text("Nueva Reserva de Laboratorio", 
                               size=22, 
                               weight=ft.FontWeight.BOLD,
                               color=ft.Colors.BLUE_900),
                    ]),
                    padding=ft.padding.only(bottom=20)
                ),
                
                ft.Container(
                    content=ft.Row([
                        ft.Container(content=dropdown_dia, expand=1),
                        ft.Container(width=20),
                        ft.Container(content=dropdown_turno, expand=1),
                    ]),
                    padding=ft.padding.only(bottom=15)
                ),
                
                ft.Container(content=textfield_docente, padding=ft.padding.only(bottom=15)),
                ft.Container(content=dropdown_carrera, padding=ft.padding.only(bottom=15)),
                ft.Container(content=textfield_curso, padding=ft.padding.only(bottom=15)),
                ft.Container(content=textfield_horario, padding=ft.padding.only(bottom=20)),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text("Período de reserva:", 
                               weight=ft.FontWeight.BOLD,
                               size=16,
                               color=ft.Colors.BLUE_800),
                        ft.Container(content=radio_periodo, padding=ft.padding.only(left=10, top=10)),
                    ]),
                    padding=ft.padding.only(bottom=15)
                ),
                
                ft.Container(
                    content=ft.Row([
                        ft.Container(content=datepicker_inicio, expand=1),
                        ft.Container(width=20),
                        ft.Container(content=datepicker_fin, expand=1),
                    ]),
                    padding=ft.padding.only(bottom=25),
                    visible=datepicker_inicio.visible
                ),
                
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            "Agregar Reserva",
                            icon=ft.Icons.SAVE,
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.GREEN_600,
                                padding=15
                            ),
                            on_click=agregar_reserva_handler
                        ),
                        ft.OutlinedButton(
                            "Limpiar Formulario",
                            icon=ft.Icons.CLEAR,
                            style=ft.ButtonStyle(padding=15),
                            on_click=limpiar_formulario
                        )
                    ], spacing=20),
                    padding=ft.padding.only(bottom=20)
                ),
                
                ft.Container(
                    content=mensaje_texto,
                    padding=10,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    visible=bool(mensaje_texto.value)
                )
            ]),
            padding=30
        )
        
        content_area.controls.append(
            ft.Container(
                content=ft.Card(content=formulario_content, elevation=3),
                padding=20,
                expand=True
            )
        )
        page.update()
    
    def mostrar_edicion(reserva_id):
        if not usuario_autenticado:
            mostrar_login()
            return
        
        nonlocal current_view, reserva_editando
        current_view = "editar_reserva"
        reserva_editando = reserva_id
        
        reserva = app.obtener_reserva_por_id(reserva_id)
        if not reserva:
            mostrar_reservas()
            return
        
        id_reserva, dia, turno, docente, carrera, curso, horario, periodo, fecha_inicio, fecha_fin, fecha_reserva = reserva
        
        edit_dropdown_dia.value = dia
        edit_dropdown_turno.value = turno
        edit_textfield_docente.value = docente
        edit_dropdown_carrera.value = carrera
        edit_textfield_curso.value = curso
        edit_textfield_horario.value = horario
        
        if "semestre" in periodo:
            edit_radio_periodo.value = "semestre"
            edit_datepicker_inicio.visible = False
            edit_datepicker_fin.visible = False
        else:
            edit_radio_periodo.value = "fechas"
            if fecha_inicio and fecha_fin:
                edit_datepicker_inicio.value = fecha_inicio
                edit_datepicker_fin.value = fecha_fin
            edit_datepicker_inicio.visible = True
            edit_datepicker_fin.visible = True
        
        content_area.controls.clear()
        
        formulario_edicion = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.EDIT, color=ft.Colors.BLUE_700, size=30),
                        ft.Text("Editar Reserva de Laboratorio", 
                               size=22, 
                               weight=ft.FontWeight.BOLD,
                               color=ft.Colors.BLUE_900),
                    ]),
                    padding=ft.padding.only(bottom=20)
                ),
                
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Reserva actual:", weight=ft.FontWeight.BOLD, size=16),
                            ft.Text(f"ID: {id_reserva}"),
                            ft.Text(f"Curso: {curso}"),
                            ft.Text(f"Día: {dia} - Turno: {turno}"),
                            ft.Text(f"Docente: {docente}"),
                        ], spacing=5),
                        padding=15
                    ),
                    elevation=2
                ),
                
                ft.Text("Modifique los campos necesarios:", 
                       weight=ft.FontWeight.BOLD,
                       size=16,
                       color=ft.Colors.BLUE_800),
                
                ft.Container(
                    content=ft.Row([
                        ft.Container(content=edit_dropdown_dia, expand=1),
                        ft.Container(width=20),
                        ft.Container(content=edit_dropdown_turno, expand=1),
                    ]),
                    padding=ft.padding.only(bottom=15)
                ),
                
                ft.Container(content=edit_textfield_docente, padding=ft.padding.only(bottom=15)),
                ft.Container(content=edit_dropdown_carrera, padding=ft.padding.only(bottom=15)),
                ft.Container(content=edit_textfield_curso, padding=ft.padding.only(bottom=15)),
                ft.Container(content=edit_textfield_horario, padding=ft.padding.only(bottom=20)),
                
                ft.Container(
                    content=ft.Column([
                        ft.Text("Período de reserva:", 
                               weight=ft.FontWeight.BOLD,
                               size=16,
                               color=ft.Colors.BLUE_800),
                        ft.Container(content=edit_radio_periodo, padding=ft.padding.only(left=10, top=10)),
                    ]),
                    padding=ft.padding.only(bottom=15)
                ),
                
                ft.Container(
                    content=ft.Row([
                        ft.Container(content=edit_datepicker_inicio, expand=1),
                        ft.Container(width=20),
                        ft.Container(content=edit_datepicker_fin, expand=1),
                    ]),
                    padding=ft.padding.only(bottom=25),
                    visible=edit_datepicker_inicio.visible
                ),
                
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            "Guardar Cambios",
                            icon=ft.Icons.SAVE,
                            style=ft.ButtonStyle(
                                color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.GREEN_600,
                                padding=15
                            ),
                            on_click=guardar_edicion
                        ),
                        ft.OutlinedButton(
                            "Cancelar",
                            icon=ft.Icons.ARROW_BACK,
                            style=ft.ButtonStyle(padding=15),
                            on_click=lambda e: mostrar_reservas()
                        )
                    ], spacing=20),
                    padding=ft.padding.only(bottom=20)
                ),
                
                ft.Container(
                    content=mensaje_texto,
                    padding=10,
                    bgcolor=ft.Colors.GREY_50,
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    visible=bool(mensaje_texto.value)
                )
            ]),
            padding=30
        )
        
        content_area.controls.append(
            ft.Container(
                content=ft.Card(content=formulario_edicion, elevation=3),
                padding=20,
                expand=True
            )
        )
        page.update()
    
    def mostrar_reservas():
        if not usuario_autenticado:
            mostrar_login()
            return
        
        nonlocal current_view
        current_view = "ver_reservas"
        
        reservas_container = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, spacing=10)
        
        reservas = app.obtener_reservas()
        
        if not reservas:
            reservas_container.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.INBOX, size=50, color=ft.Colors.GREY_400),
                            ft.Text("No hay reservas registradas", 
                                   size=18, 
                                   weight=ft.FontWeight.BOLD),
                            ft.Text("Agregue la primera reserva usando el formulario",
                                   color=ft.Colors.GREY_600)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=40
                    )
                )
            )
        else:
            for reserva in reservas:
                id_reserva, dia, turno, docente, carrera, curso, horario, periodo, fecha_inicio, fecha_fin, fecha_reserva = reserva
                
                boton_editar = ft.TextButton(
                    "Editar",
                    icon=ft.Icons.EDIT,
                    style=ft.ButtonStyle(color=ft.Colors.BLUE),
                    on_click=lambda e, id=id_reserva: mostrar_edicion(id)
                )
                
                boton_eliminar = ft.TextButton(
                    "Eliminar",
                    icon=ft.Icons.DELETE,
                    style=ft.ButtonStyle(color=ft.Colors.RED),
                    on_click=lambda e, id=id_reserva: eliminar_reserva_handler(id)
                )
                
                reservas_container.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.COMPUTER, color=ft.Colors.BLUE_700),
                                    title=ft.Text(f"{curso}", weight=ft.FontWeight.BOLD, size=16),
                                    subtitle=ft.Text(f"{dia} - {turno} | Docente: {docente}"),
                                ),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Row([ft.Text("📅 Horario:", weight=ft.FontWeight.BOLD), ft.Text(horario)]),
                                        ft.Row([ft.Text("📚 Período:", weight=ft.FontWeight.BOLD), ft.Text(periodo)]),
                                        ft.Row([ft.Text("🕐 Reservado:", weight=ft.FontWeight.BOLD), ft.Text(fecha_reserva.split()[0])]),
                                    ], spacing=5),
                                    padding=ft.padding.only(left=16, right=16, bottom=10)
                                ),
                                ft.Row([boton_editar, boton_eliminar], alignment=ft.MainAxisAlignment.END)
                            ]),
                            padding=10
                        ),
                        elevation=2
                    )
                )
        
        content_area.controls.clear()
        content_area.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.LIST_ALT, color=ft.Colors.BLUE_700),
                                    title=ft.Text("Reservas Existentes", 
                                                size=22, 
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.BLUE_900),
                                    subtitle=ft.Text(f"Total: {len(reservas)} reservas"),
                                ),
                                ft.Divider(),
                                reservas_container
                            ]),
                            padding=20
                        ),
                        elevation=3
                    )
                ]),
                padding=20,
                expand=True
            )
        )
        page.update()
    
    def mostrar_informacion():
        if not usuario_autenticado:
            mostrar_login()
            return
        
        nonlocal current_view
        current_view = "informacion"
        
        content_area.controls.clear()
        content_area.controls.append(
            ft.Container(
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.ListTile(
                                leading=ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE_700),
                                title=ft.Text("Sistema de Control de Laboratorio", 
                                            size=22, 
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.BLUE_900),
                                subtitle=ft.Text("Gestión académica de reservas"),
                            ),
                            ft.Divider(),
                            ft.Container(
                                content=ft.Column([
                                    ft.ListTile(
                                        leading=ft.Icon(ft.Icons.COMPUTER, color=ft.Colors.GREEN_600),
                                        title=ft.Text("Laboratorio de Informática"),
                                        subtitle=ft.Text("Sistema de reservas académicas"),
                                    ),
                                    ft.Text("Características del sistema:", 
                                           weight=ft.FontWeight.BOLD,
                                           size=16),
                                    ft.Text("• Gestión de reservas por día y turno"),
                                    ft.Text("• Control por docente y carrera"),
                                    ft.Text("• Diferentes períodos de reserva"),
                                    ft.Text("• Sistema de autenticación de usuarios"),
                                    ft.Text("• Gestión de usuarios con roles"),
                                    ft.Text("• Base de datos SQLite integrada"),
                                    ft.Text("\nDesarrollado con Python y Flet",
                                           weight=ft.FontWeight.BOLD,
                                           color=ft.Colors.BLUE_600)
                                ], spacing=10),
                                padding=20
                            )
                        ]),
                        padding=20
                    ),
                    elevation=3
                ),
                padding=20,
                expand=True
            )
        )
        page.update()
    
    # ========== INTERFAZ PRINCIPAL ==========
    
    # Área de contenido principal
    content_area = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE)
    
    # Contenedor principal que cambia según la autenticación
    main_container = ft.Column(expand=True)
    
    # Layout principal
    page.add(main_container)
    
    # Mostrar la vista inicial (login)
    actualizar_interfaz_principal()
    mostrar_login()

if __name__ == "__main__":
    ft.app(target=main)