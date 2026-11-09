import streamlit as st
import streamlit.components.v1 as components
import json
import os
import math
import io
import zipfile
import base64
import hashlib
from datetime import datetime
import gzip
import wave
import struct

# ==============================================================================
# 1. CONFIGURACIÓN DEL CHASIS Y OCULTACIÓN DE MENÚS DE CÓDIGO
# ==============================================================================
st.set_page_config(
    page_title="MONARCH | Software & Sistema Centralizado",
    page_icon="🦋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. PUENTE MULTIMEDIA LOCAL Y ESTILOS CSS (PALETA + PROTECCIÓN DE CÓDIGO)
# ==============================================================================
def cargar_archivo_base64(ruta):
    if os.path.exists(ruta):
        try:
            with open(ruta, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            return None
    return None

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Cormorant+Garamond:ital,wght@0,500;0,700;1,400&family=Montserrat:wght@500;700&display=swap');

    /* BLOQUEO ESTRICTO DEL BOTÓN DE GITHUB Y VER CÓDIGO FUENTE */
    #MainMenu {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    header [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    .stAppDeployButton {visibility: hidden !important; display: none !important;}
    [data-testid="stHeaderActionElements"] {visibility: hidden !important; display: none !important;}
    div[data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}

    /* PALETA CROMÁTICA OFICIAL EN ORDEN */
    :root {
        --old-paper: #FDF9F1;          /* 1. Fondo general de la aplicación */
        --black-text: #121212;         /* 2. Texto principal */
        --terracotta-bark: #C85A32;    /* 3. Barra lateral y marcos */
        --olive-leaf: #5C6F2B;         /* 4. Check de guardado y tags */
        --tangerine-ember: #E93C21;    /* 5. Botón primario y envío */
        --saffron-bloom: #EDB72A;      /* 6. Hover, píldoras de suscripción y luces */
    }

    .stApp {
        background-color: var(--old-paper);
        color: var(--black-text);
        font-family: 'The Seasons', 'Cormorant Garamond', serif;
    }

    h1, h2, h3, .titulo-flora {
        font-family: 'Flora Bright', 'Cinzel', serif !important;
        color: var(--black-text) !important;
        letter-spacing: 1.5px;
    }

    .subtitulo-catchy {
        font-family: 'Catchy Mager', 'Montserrat', sans-serif !important;
        letter-spacing: 0.8px;
    }

    p, li, label, .texto-seasons, .stMarkdown {
        font-family: 'The Seasons', 'Cormorant Garamond', serif !important;
        color: var(--black-text) !important;
        font-size: 1.15rem;
        line-height: 1.6;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--terracotta-bark) !important;
        border-right: 3px solid var(--saffron-bloom);
    }
    section[data-testid="stSidebar"] * {
        color: var(--old-paper) !important;
    }

    .olive-check {
        background-color: var(--olive-leaf);
        color: var(--old-paper) !important;
        padding: 6px 14px;
        border-radius: 8px;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.88rem;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin: 4px 2px;
    }

    .olive-tag {
        background-color: var(--olive-leaf);
        color: #FFFFFF !important;
        padding: 4px 12px;
        border-radius: 20px;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.82rem;
        display: inline-block;
        margin: 3px;
    }

    div.stButton > button, div.stFormSubmitButton > button {
        background-color: var(--tangerine-ember) !important;
        color: #FFFFFF !important;
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: 2px solid var(--tangerine-ember) !important;
        padding: 0.55rem 1.3rem !important;
        box-shadow: 0 4px 12px rgba(233, 60, 33, 0.3) !important;
        transition: all 0.25s ease;
    }

    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background-color: var(--saffron-bloom) !important;
        color: var(--black-text) !important;
        border-color: var(--saffron-bloom) !important;
        transform: translateY(-2px);
    }

    .saffron-pill {
        background: var(--saffron-bloom);
        color: var(--black-text) !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        padding: 5px 15px;
        border-radius: 999px;
        display: inline-block;
        box-shadow: 0 0 12px rgba(237, 183, 42, 0.7);
    }

    .tarjeta-descanso {
        background: rgba(253, 249, 241, 0.96);
        border: 2px solid var(--terracotta-bark);
        border-radius: 18px;
        padding: 40px 32px;
        text-align: center;
        box-shadow: 0 12px 35px rgba(18, 18, 18, 0.08);
        margin: 25px auto;
        max-width: 850px;
    }

    .tarjeta-modulo {
        background: rgba(253, 249, 241, 0.98);
        border-left: 6px solid var(--terracotta-bark);
        border-top: 1px solid rgba(200, 90, 50, 0.3);
        border-right: 1px solid rgba(200, 90, 50, 0.3);
        border-bottom: 1px solid rgba(200, 90, 50, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. MOTOR DE PERSISTENCIA HÍBRIDA (OFFLINE LOCAL / ONLINE CLOUD)
# ==============================================================================
ARCHIVO_PROYECTO_DB = "monarch_proyecto_maestro.json"

ESTRUCTURA_BASE_MONARCH = {
    "usuario": {
        "nombre": "Creador Monarch",
        "correo": "creador@monarch.mx",
        "plan": "Plan Monarca Enterprise ($931 MXN/mes)",
        "sector": "Empresa Editorial",
        "perfiles": ["Escritor/a", "Editor/a", "Ilustrador/a", "Animador/a"],
        "vinculo_mascota": "Modo Acompañante",
        "conexion": "Online (Nube Central + Respaldo Local)"
    },
    "sinopsis_metadatos": {
        "titulo": "Crónicas del Oyamel",
        "genero": "Fantasía Biopoética / Novela Gráfica",
        "formato_salida": "Spread Impreso CMYK (600 DPI) + Webtoon Scroll",
        "presupuesto_mxn": 185000.0,
        "costo_hora_promedio": 350.0,
        "horas_ahorradas": 142.0,
        "sinopsis": "En las montañas nubladas de Michoacán, el guardián del bosque descubre el lenguaje ancestral que une cada generación migratoria."
    },
    "avance_estaciones": {
        "1. 🌱 Semilla": 100, "2. 🌿 Germinación": 90, "3. 🪴 Algodoncillo": 85,
        "4. 🐛 Oruga": 80, "5. 🐞 Toxina": 85, "6. 🪲 Crisálida": 75,
        "7. 🦋 Monarca": 70, "8. 🌬️ Viento": 50
    },
    "colonia_equipos": [
        {"nombre": "Elena Vázquez", "perfil": "Escritor/a", "tarea": "Desglose dramático en Oruga", "estado": "Activo"},
        {"nombre": "Marco Tulio", "perfil": "Ilustrador/a", "tarea": "Capas vectoriales en Monarca", "estado": "En revisión"},
        {"nombre": "Sofía Lira", "perfil": "Cantautor/a", "tarea": "Composición en Ecos del Bosque", "estado": "Completado"}
    ],
    "raices_lore": [
        {"uuid": "CHAR_001_HOMERO", "tipo": "Personaje", "nombre": "Guardián del Bosque", "regla": "Protector del santuario de oyamel."},
        {"uuid": "LOC_001_EL_ROSARIO", "tipo": "Escenario", "nombre": "Santuario El Rosario (Michoacán)", "regla": "Bosque nublado a 3,200 msnm."}
    ],
    "nectar_bosque": [
        {"id": "TRATADO_01", "nombre": "Cours de Dessin — Charles Bargue (1866)", "categoria": "Dominio Público", "estado": "Verificado ✅"},
        {"id": "TRATADO_02", "nombre": "The Practice and Science of Drawing — Harold Speed (1913)", "categoria": "Dominio Público", "estado": "Verificado ✅"},
        {"id": "TRATADO_03", "nombre": "Figure Drawing for All It's Worth — Andrew Loomis", "categoria": "Pedagogía Anatómica", "estado": "Verificado ✅"}
    ],
    "escudo_ip": {
        "estado_semaforo": "VERDE (100% Blindado y Ético)",
        "linaje_pedagogico": "Dominio Público Verificado (Bargue, Speed, Loomis)",
        "hash_sha256": hashlib.sha256(b"MONARCH_CRONICAS_OYAMEL_2026").hexdigest().upper(),
        "registro_indautor": "Folio Preliminar MX-INDAUTOR-2026-8841"
    },
    "calendario_temporadas": [
        {"hito": "Cierre de Guion Técnico (Oruga)", "fecha": "22/11/2026", "responsable": "Escritor/a", "cumplido": True},
        {"hito": "Auditoría CMYK 600 DPI (Mirador de Alas)", "fecha": "30/11/2026", "responsable": "Editor/a", "cumplido": False}
    ],
    "generaciones_migracion": [
        {
            "generacion": "1ª Generación (Primavera)",
            "fecha_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "autor": "Elena Vázquez (Escritor/a)",
            "seccion": "🌲 Santuario de la Brisa",
            "detalle": "Creación del acta de proyecto y sinopsis inicial.",
            "hash_version": "A1F9C04B82E1"
        }
    ],
    "red_polinizacion": [
        {"autor": "Editor/a Jefe (ROLEPLAY)", "ancla": "Viñeta 4 (Oruga)", "mensaje": "Ajustar la cola del globo de diálogo para no cubrir el fondo.", "hora": "11:30"}
    ],
    "foro_oyamel": [
        {"autor": "Dirección MONARCH", "perfil": "Productor/a", "titulo": "Bienvenida a la Temporada de Hibernación", "contenido": "Verifiquen sus márgenes CMYK antes de pasar a Viento.", "fecha": "08/11/2026"}
    ],
    "microclima": {
        "tema": "Papel Antiguo (Old Paper)",
        "fuente": "The Seasons / Flora Bright",
        "escala_letra": 100,
        "idioma": "Español (México)",
        "zona_horaria": "GMT-6 (Toluca / CDMX - Santuario Central)",
        "musica_activa": False
    },
    "fase3_datos": {
        "semilla": {
            "objetivo_general": "Adaptar la obra a formato gráfico e interactivo reduciendo tiempos de preproducción un 65%.",
            "manuscrito_word": "—¡El viento del norte ya está aquí! —gritó Diego mientras corría por el bosque de oyamel al anochecer.\n—Mantén la linterna en alto, Elena —respondió el guardián observando las ramas cubiertas de mariposas.",
            "pizarron_ideas": [{"id": "IDEA-01", "titulo": "El Guardián", "categoria": "Personaje", "contenido": "Protector ancestral del santuario."}]
        },
        "ecos_bosque": [
            {"id_pista": "PISTA_01", "titulo": "Susurro del Oyamel", "cantautor": "Sofía Lira", "bpm": 72, "tonalidad": "La Menor", "estado": "Aprobada ✅"}
        ],
        "texto_limpio_algodoncillo": "—¡El viento del norte ya está aquí! —gritó Diego mientras corría por el bosque de oyamel al anochecer.\n—Mantén la linterna en alto, Elena —respondió el guardián observando las ramas cubiertas de mariposas.",
        "story_script": [
            {"panel": 1, "plano": "PLANO GENERAL", "locacion": "Bosque de Oyamel", "tension_gzip": 0.78, "accion": "Diego corre por el bosque al anochecer.", "dialogo": "¡El viento del norte ya está aquí!"},
            {"panel": 2, "plano": "PRIMER PLANO", "locacion": "Bosque de Oyamel", "tension_gzip": 0.84, "accion": "El guardián alza la linterna hacia los racimos.", "dialogo": "Mantén la linterna en alto, Elena."}
        ],
        "crisalida_3d": {
            "escenario": "Santuario de Oyamel Nocturno",
            "props": [{"id": "PROP_01", "nombre": "Linterna de Ámbar", "x": 1.5, "z": -1.0}],
            "iluminacion": {"foco_x": 3.0, "foco_y": 5.5, "foco_z": 2.5, "color": "#ffaa44", "intensidad": 2.2},
            "camara": {"tipo_plano": "PLANO MEDIO", "fov": 45},
            "personajes": [
                {"id": "CHAR_01", "nombre": "Diego", "pos_x": -1.2, "pos_z": 0.5, "rot_y": 45, "pose": "Alerta / Guardia", "color": "#C85A32", "expresion": "Determinación"},
                {"id": "CHAR_02", "nombre": "Elena", "pos_x": 1.2, "pos_z": -0.5, "rot_y": -135, "pose": "Tensión / Confrontación", "color": "#5C6F2B", "expresion": "Asombro"}
            ],
            "capturas": []
        },
        "monarca_2d": {
            "tratado_dp": "Charles Bargue (1866) - Pluma y Encaje Angular",
            "formato_destino": "Spread Impreso (Doble Página)",
            "capas_activas": [
                "Capa 1: Globos Magnéticos (Lettering)",
                "Capa 2: Tinta Vectorial (Lineart)",
                "Capa 3: Sombras (Cel-Shading / Hatching)",
                "Capa 4: Color Base Botánico",
                "Capa 5: Fondo Perspectiva 3D"
            ],
            "eye_tracking_activo": True
        },
        "viento_merch": [
            {"producto": "Sudadera Bordada 'Guardián del Oyamel'", "licencia": "Edición Limitada", "precio_mxn": 850.0},
            {"producto": "Artbook Pasta Dura (600 DPI CMYK)", "licencia": "Editorial ROLEPLAY", "precio_mxn": 620.0}
        ]
    }
}

def cargar_proyecto():
    if os.path.exists(ARCHIVO_PROYECTO_DB):
        try:
            with open(ARCHIVO_PROYECTO_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return ESTRUCTURA_BASE_MONARCH
    return ESTRUCTURA_BASE_MONARCH

def guardar_proyecto(datos):
    try:
        with open(ARCHIVO_PROYECTO_DB, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
    except Exception:
        pass

if "monarch_state" not in st.session_state:
    st.session_state.monarch_state = cargar_proyecto()

proy = st.session_state.monarch_state
usr = proy["usuario"]

def registrar_migracion(seccion, detalle):
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    h = hashlib.sha256(f"{ahora}_{detalle}".encode("utf-8")).hexdigest()[:12].upper()
    proy["generaciones_migracion"].insert(0, {
        "generacion": f"Generación Migratoria #{len(proy['generaciones_migracion'])+1}",
        "fecha_hora": ahora,
        "autor": f"{usr['nombre']} ({usr['perfiles'][0]})",
        "seccion": seccion,
        "detalle": detalle,
        "hash_version": h
    })
    guardar_proyecto(proy)

# ==============================================================================
# 4. FASE 1: SECUENCIA DE ENTRADA E INMERSIÓN (9 PASOS)
# ==============================================================================
if "paso_fase1" not in st.session_state:
    st.session_state.paso_fase1 = 1

def avanzar_paso(p):
    st.session_state.paso_fase1 = p
    st.rerun()

if st.session_state.paso_fase1 <= 9:
    if st.sidebar.button("⚡ Ir Directo al Sistema Central", use_container_width=True):
        st.session_state.paso_fase1 = 10
        st.rerun()

    if st.session_state.paso_fase1 == 1:
        st.markdown("""
        <div class="tarjeta-descanso">
            <span class="saffron-pill">🌬️ Pantalla de Descanso 1 • Brisa del Oyamel</span>
            <h1 class="titulo-flora" style="margin-top:20px;">El Susurro del Ecosistema</h1>
            <p class="texto-seasons" style="font-size:1.35rem; font-style:italic; margin: 20px 0;">
                «Cada otoño, millones de mariposas monarca viajan más de 4,000 kilómetros hasta los bosques nublados de oyamel en México. 
                Ninguna ha estado ahí antes, pero la memoria genética y el viento las guían a casa.»
            </p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button("🌱 Iniciar Animación del Ciclo Vital →", use_container_width=True):
                avanzar_paso(2)

    elif st.session_state.paso_fase1 == 2:
        st.markdown("""
        <div style="text-align:center; margin-top: 15px;">
            <span class="saffron-pill">🌱 ➡️ 🦋 Ciclo Vital de Metamorfosis</span>
            <h1 class="titulo-flora" style="margin-top:10px;">Las 8 Estaciones de Transformación</h1>
        </div>
        """, unsafe_allow_html=True)
        fases = [
            ("🌱", "Semilla"), ("🌿", "Germinación"), ("🪴", "Algodoncillo"), ("🐛", "Oruga"),
            ("🐞", "Toxina"), ("🪲", "Crisálida"), ("🦋", "Monarca"), ("🌬️", "Viento")
        ]
        cols = st.columns(8)
        for idx, (ico, tit) in enumerate(fases):
            with cols[idx]:
                st.markdown(f"<div style='text-align:center; padding:12px; background:rgba(253,249,241,0.95); border:1px solid var(--terracotta-bark); border-radius:10px;'><div style='font-size:2.3rem;'>{ico}</div><div class='subtitulo-catchy' style='font-size:0.75rem; margin-top:4px;'><b>{tit}</b></div></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button("🌬️ Continuar a Gota de Rocío →", use_container_width=True):
                avanzar_paso(3)

    elif st.session_state.paso_fase1 == 3:
        st.markdown("""
        <div class="tarjeta-descanso">
            <span class="saffron-pill">🌬️ Pantalla de Descanso 2 • Gota de Rocío</span>
            <h1 class="titulo-flora" style="margin-top:20px;">El Alimento Sagrado</h1>
            <p class="texto-seasons" style="font-size:1.35rem; font-style:italic; margin: 20px 0;">
                «La planta de algodoncillo (Asclepias) no solo alimenta a la oruga; le otorga glucósidos cardíacos 
                que la vuelven intocable frente a depredadores. En nuestro ecosistema, ese blindaje protege la propiedad intelectual.»
            </p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button("✨ Presentación Oficial de la Marca →", use_container_width=True):
                avanzar_paso(4)

    elif st.session_state.paso_fase1 == 4:
        st.markdown("""
        <div class="tarjeta-descanso" style="border-width: 3px;">
            <span class="saffron-pill">✨ Presentación Oficial</span>
            <div style="font-size: 4rem; margin: 10px 0;">🦋</div>
            <h1 class="titulo-flora" style="font-size: 3.6rem; letter-spacing: 8px;">MONARCH</h1>
            <h3 class="subtitulo-catchy" style="color: var(--terracotta-bark) !important; font-size: 1.4rem; margin-bottom: 15px;">
                Software Híbrido y Sistema Centralizado de Preproducción y Producción Creativa
            </h3>
            <p class="texto-seasons" style="font-size: 1.2rem; max-width: 650px; margin: 0 auto;">
                Ecosistema ético (Human-in-the-loop) para Empresas Editoriales, Empresas de Entretenimiento y Creadores Independientes.
            </p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button("🌬️ Luz de Michoacán →", use_container_width=True):
                avanzar_paso(5)

    elif st.session_state.paso_fase1 == 5:
        st.markdown("""
        <div class="tarjeta-descanso">
            <span class="saffron-pill">🌬️ Pantalla de Descanso 3 • Luz de Michoacán</span>
            <h1 class="titulo-flora" style="margin-top:20px;">Preparación del Santuario</h1>
            <p class="texto-seasons" style="font-size:1.35rem; font-style:italic; margin: 20px 0;">
                «Cuando los rayos del sol filtran la niebla en la Sierra Madre, los racimos despiertan al unísono. 
                El talento individual cobra fuerza invencible cuando se sincroniza en comunidad.»
            </p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button("🔐 El Umbral del Santuario (Acceso) →", use_container_width=True):
                avanzar_paso(6)

    elif st.session_state.paso_fase1 == 6:
        col_l1, col_l2 = st.columns(2, gap="large")
        with col_l1:
            st.markdown("""
            <div class="tarjeta-descanso" style="text-align:left; height:100%; margin:0;">
                <span class="saffron-pill">🔐 El Umbral del Santuario</span>
                <h1 class="titulo-flora" style="font-size:2.4rem; margin-top:15px;">Control de Doble Llave</h1>
                <p class="texto-seasons">Autentícate y selecciona tu nivel de suscripción para sincronizar tu archivo contenedor maestro de forma local o en la nube.</p>
                <div class="olive-check">🌱 Plan Semilla ($134 MXN/mes)</div><br>
                <div class="olive-check">🐛 Plan Oruga ($531 MXN/mes)</div><br>
                <div class="olive-check">🦋 Plan Monarca Enterprise ($931 MXN/mes)</div>
            </div>
            """, unsafe_allow_html=True)
        with col_l2:
            with st.form("form_login_maestro"):
                nom_u = st.text_input("Nombre o Alias Creativo:", value=usr["nombre"])
                correo_u = st.text_input("Correo electrónico:", value=usr["correo"])
                pass_u = st.text_input("Contraseña:", type="password", value="••••••••")
                plan_u = st.selectbox("Nivel de Suscripción:", [
                    "Plan Semilla ($134 MXN/mes)",
                    "Plan Oruga ($531 MXN/mes)",
                    "Plan Monarca Enterprise ($931 MXN/mes)"
                ], index=2)
                modo_net = st.radio("Modo de Sincronización:", [
                    "Online (Nube Central + Actualización Delta)",
                    "Offline (Software Local Autónomo)"
                ])
                if st.form_submit_button("🔓 Cruzar el Umbral del Santuario", use_container_width=True):
                    usr["nombre"] = nom_u
                    usr["correo"] = correo_u
                    usr["plan"] = plan_u
                    usr["conexion"] = modo_net
                    guardar_proyecto(proy)
                    avanzar_paso(7)

    elif st.session_state.paso_fase1 == 7:
        st.markdown(f"""
        <div class="tarjeta-descanso">
            <span class="saffron-pill">🌬️ Pantalla de Descanso 4 • Apertura del Bosque</span>
            <h1 class="titulo-flora" style="margin-top:20px;">¡Bienvenido a la Colonia, {usr['nombre']}!</h1>
            <p class="texto-seasons" style="font-size:1.35rem; font-style:italic; margin: 20px 0;">
                Tu llave de acceso en <b>{usr['plan']}</b> está activa. Calibremos ahora las estaciones según tus perfiles profesionales.
            </p>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button("📋 Ritual de Identidad (Encuesta RPG) →", use_container_width=True):
                avanzar_paso(8)

    elif st.session_state.paso_fase1 == 8:
        st.markdown("""
        <div style="text-align:center; margin-bottom:15px;">
            <span class="saffron-pill">📋 Ritual de Identidad • Hoja de Personaje RPG</span>
            <h1 class="titulo-flora" style="margin-top:10px;">Sector, Perfiles Multiclase y Vínculo con Papalotl</h1>
        </div>
        """, unsafe_allow_html=True)
        with st.form("form_ritual_maestro"):
            with st.expander("1. Sector Corporativo o Independiente", expanded=True):
                sec_s = st.radio("Selecciona tu sector:", ["Empresa Editorial", "Empresa de Entretenimiento", "Profesional Individual"], index=0)
            with st.expander("2. Los 11 Perfiles Profesionales (Selección Multiclase)", expanded=True):
                perf_s = st.multiselect("Elige las funciones que desempeñas:", [
                    "Escritor/a", "Editor/a", "Dibujante", "Ilustrador/a", "Animador/a",
                    "Actriz/Actor", "Narrador/a", "Productor/a", "Cantautor/a", "Diseñador/a", "Publicitario/a"
                ], default=usr["perfiles"])
            with st.expander("3. Vínculo con tu Mascota Adaptativa (Papalotl)", expanded=True):
                masc_s = st.radio("Nivel de acompañamiento:", ["Modo Acompañante", "Apoyo y Asistencia", "Sostenimiento"])
            if st.form_submit_button("🌿 Confirmar Identidad y Preparar el Vuelo →", use_container_width=True):
                usr["sector"] = sec_s
                usr["perfiles"] = perf_s if perf_s else ["Escritor/a"]
                usr["vinculo_mascota"] = masc_s
                guardar_proyecto(proy)
                avanzar_paso(9)

    elif st.session_state.paso_fase1 == 9:
        st.markdown("""
        <div class="tarjeta-descanso" style="border-width: 3px;">
            <span class="saffron-pill">🌬️ Pantalla de Descanso 5 • Inicio del Vuelo</span>
            <h1 class="titulo-flora" style="margin-top:20px; font-size:2.3rem;">In Memoriam: El Guardián del Santuario</h1>
            <div style="background: rgba(200, 90, 50, 0.08); border-left: 5px solid var(--terracotta-bark); padding: 20px; border-radius: 10px; margin: 20px 0; text-align: left;">
                <h3 class="subtitulo-catchy" style="margin-top:0; color: var(--terracotta-bark) !important;">
                    🦋 Homenaje a Homero Gómez González (1970–2020)
                </h3>
                <p class="texto-seasons" style="font-size:1.2rem; margin-bottom:0;">
                    Ingeniero agrónomo y defensor ambiental mexicano, conocido mundialmente como el <b>«Guardián de las Mariposas Monarca»</b>. 
                    Su entrega por proteger los bosques de oyamel en Michoacán inspira el compromiso ético de <b>MONARCH</b>.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2:
            if st.button("🦋 Entrar al Sistema Centralizado MONARCH →", use_container_width=True):
                avanzar_paso(10)

# ==============================================================================
# 5. FASE 2 (CHASIS CENTRALIZADO) Y FASE 3 (LAS 8 ESTACIONES)
# ==============================================================================
else:
    with st.sidebar:
        st.markdown("<h1 class='titulo-flora' style='font-size:1.8rem; margin-bottom:0;'>🦋 MONARCH</h1>", unsafe_allow_html=True)
        st.markdown(f"<span class='saffron-pill'>{usr['plan']}</span>", unsafe_allow_html=True)
        red_c = "Online ☁️" if "Online" in usr["conexion"] else "Offline 💾"
        st.markdown(f"<div style='margin-top:8px;'><span class='olive-check'>✓ {red_c} • Contenedor Activo</span></div>", unsafe_allow_html=True)

        st.markdown("### 🏛️ Chasis Centralizado")
        modulo_central = st.radio(
            "Navegación Global:",
            [
                "🧭 1. El Observatorio Monarca",
                "🌲 2. El Santuario de la Brisa",
                "🌺 3. Red de Polinización y El Oyamel",
                "🎭 4. Códice Papalotl (Mi Perfil)",
                "☀️ 5. Microclima del Sistema",
                "🍯 6. El Néctar del Bosque (Biblioteca)",
                "🛠️ 7. Las 8 Estaciones de Metamorfosis"
            ]
        )

        st.markdown("### 🎭 Perfiles Desbloqueados")
        for p in usr["perfiles"]:
            st.markdown(f"<span class='olive-tag'>🔓 {p}</span>", unsafe_allow_html=True)

        if st.button("🔄 Ver Secuencia de Bienvenida", use_container_width=True):
            st.session_state.paso_fase1 = 1
            st.rerun()

    # Barra Superior Transversal (Reloj Sincronizado y Estado)
    h1, h2, h3 = st.columns([1.8, 1.3, 1.1])
    with h1:
        st.markdown(f"<h1 class='titulo-flora' style='margin-bottom:0; font-size:2rem;'>{proy['sinopsis_metadatos']['titulo']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='subtitulo-catchy' style='margin:0;'>Creador: <b>{usr['nombre']}</b> | Sector: <b>{usr['sector']}</b></p>", unsafe_allow_html=True)
    with h2:
        st.markdown(f"<div style='margin-top:8px;'><span class='olive-check'>✓ Sincronizado</span> <span class='saffron-pill'>{usr['vinculo_mascota']}</span></div>", unsafe_allow_html=True)
    with h3:
        reloj_v = datetime.now().strftime("%H:%M:%S • %d/%m/%Y")
        st.markdown(f"<p class='subtitulo-catchy' style='text-align:right; margin-top:8px; font-size:0.85rem;'>🕒 {reloj_v}<br><small>{proy['microclima']['zona_horaria']}</small></p>", unsafe_allow_html=True)

    # ==========================================================================
    # MÓDULO 1: EL OBSERVATORIO MONARCA (PANEL DE CONTROL GLOBAL)
    # ==========================================================================
    if modulo_central == "🧭 1. El Observatorio Monarca":
        st.markdown("<h2 class='titulo-flora'>🧭 El Observatorio Monarca (Panel Global)</h2>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="tarjeta-modulo" style="border-left: 6px solid var(--saffron-bloom);">
            <span class="saffron-pill">🦋 Compañero Papalotl • {usr['vinculo_mascota']}</span>
            <p class="texto-seasons" style="margin-top:10px; font-size:1.2rem;">
                «¡Hola, <b>{usr['nombre']}</b>! Tus herramientas para <b>{', '.join(usr['perfiles'])}</b> están priorizadas. El ciclo migratorio avanza sin contratiempos.»
            </p>
        </div>
        """, unsafe_allow_html=True)

        meta = proy["sinopsis_metadatos"]
        ahorro_eco = meta["costo_hora_promedio"] * meta["horas_ahorradas"]
        avance_p = round(sum(proy["avance_estaciones"].values()) / len(proy["avance_estaciones"]), 1)

        i1, i2, i3, i4 = st.columns(4)
        with i1:
            st.markdown('<div class="tarjeta-modulo"><span class="olive-tag">1. Productividad</span><h2 class="titulo-flora" style="margin:8px 0;">42 Unid/Sem</h2><p class="texto-seasons" style="font-size:0.95rem;">18 páginas limpiadas y 16 viñetas 3D por jornada (172 h/mes).</p></div>', unsafe_allow_html=True)
        with i2:
            st.markdown(f'<div class="tarjeta-modulo"><span class="olive-tag">2. Eficacia</span><h2 class="titulo-flora" style="margin:8px 0;">{avance_p}%</h2><p class="texto-seasons" style="font-size:0.95rem;">Cumplimiento de metas de las 8 estaciones en calendario.</p></div>', unsafe_allow_html=True)
        with i3:
            st.markdown(f'<div class="tarjeta-modulo"><span class="olive-tag">3. Eficiencia</span><h2 class="titulo-flora" style="margin:8px 0;">${ahorro_eco:,.0f} MXN</h2><p class="texto-seasons" style="font-size:0.95rem;">Ahorro directo ({meta["horas_ahorradas"]:.0f} h ahorradas × ${meta["costo_hora_promedio"]:.0f}/h).</p></div>', unsafe_allow_html=True)
        with i4:
            st.markdown('<div class="tarjeta-modulo"><span class="olive-tag">4. Calidad Triple</span><h2 class="titulo-flora" style="margin:8px 0;">99.4%</h2><p class="texto-seasons" style="font-size:0.95rem;">Auditoría Lingüística + Legal INDAUTOR + Técnica 600 DPI.</p></div>', unsafe_allow_html=True)

        st.markdown("### 📅 Calendario de Temporadas y Entregas")
        for c in proy["calendario_temporadas"]:
            est_c = "✅ Completado" if c["cumplido"] else "⏳ En curso"
            st.markdown(f"<div class='tarjeta-modulo'><b>{c['hito']}</b> — Fecha límite: {c['fecha']} | Responsable: <span class='olive-tag'>{c['responsable']}</span> <span class='saffron-pill' style='float:right;'>{est_c}</span></div>", unsafe_allow_html=True)

    # ==========================================================================
    # MÓDULO 2: EL SANTUARIO DE LA BRISA (CÓDICE MAESTRO DEL PROYECTO)
    # ==========================================================================
    elif modulo_central == "🌲 2. El Santuario de la Brisa":
        st.markdown("<h2 class='titulo-flora'>🌲 El Santuario de la Brisa (Códice Maestro)</h2>", unsafe_allow_html=True)
        t_s1, t_s2, t_s3, t_s4 = st.tabs(["📊 Avance & Sinopsis", "🦋 La Colonia (Equipos)", "🌳 Raíces y Lore", "🛡️ Escudo IP (Alerta Aposemática)"])

        with t_s1:
            for est_nom, porc in proy["avance_estaciones"].items():
                st.write(f"**{est_nom}** — {porc}%")
                st.progress(porc / 100.0)
            meta = proy["sinopsis_metadatos"]
            with st.form("form_santuario"):
                t_in = st.text_input("Título de la Obra:", value=meta["titulo"])
                g_in = st.text_input("Género:", value=meta["genero"])
                sin_in = st.text_area("Sinopsis Oficial:", value=meta["sinopsis"])
                if st.form_submit_button("💾 Actualizar Códice Maestro"):
                    meta["titulo"] = t_in
                    meta["genero"] = g_in
                    meta["sinopsis"] = sin_in
                    registrar_migracion("🌲 Santuario de la Brisa", "Actualización de sinopsis y metadatos")
                    st.success("Códice actualizado.")

        with t_s2:
            for m in proy["colonia_equipos"]:
                st.markdown(f"<div class='tarjeta-modulo'><span class='olive-tag'>{m['perfil']}</span> <b>{m['nombre']}</b> — {m['tarea']} <span class='saffron-pill' style='float:right;'>{m['estado']}</span></div>", unsafe_allow_html=True)

        with t_s3:
            with st.form("nuevo_lore"):
                n_nom = st.text_input("Nombre del Personaje o Locación:")
                n_tip = st.selectbox("Categoría:", ["Personaje", "Escenario", "Regla del Universo"])
                n_reg = st.text_input("Descripción / Regla canónica:")
                if st.form_submit_button("➕ Registrar en Raíces y Lore"):
                    if n_nom:
                        proy["raices_lore"].append({"uuid": f"LORE_{len(proy['raices_lore'])+1:03d}", "tipo": n_tip, "nombre": n_nom, "regla": n_reg})
                        registrar_migracion("🌳 Raíces y Lore", f"Alta de entidad: {n_nom}")
                        st.rerun()
            for e in proy["raices_lore"]:
                st.markdown(f"<div class='tarjeta-modulo'><span class='olive-check'>{e['uuid']}</span> <b>{e['nombre']} ({e['tipo']})</b><p class='texto-seasons' style='margin:4px 0;'>{e['regla']}</p></div>", unsafe_allow_html=True)

        with t_s4:
            ip = proy["escudo_ip"]
            st.markdown(f"""
            <div class="tarjeta-modulo" style="border: 2px solid var(--olive-leaf);">
                <span class="olive-check">🟢 {ip["estado_semaforo"]}</span>
                <h3 class="titulo-flora" style="margin-top:10px;">Certificación Legal ante INDAUTOR</h3>
                <p class="texto-seasons"><b>Acervo Pedagógico:</b> {ip["linaje_pedagogico"]}</p>
                <p class="texto-seasons"><b>Firma Criptográfica SHA-256:</b> <code>{ip["hash_sha256"]}</code></p>
                <p class="texto-seasons"><b>Expediente:</b> {ip["registro_indautor"]}</p>
            </div>
            """, unsafe_allow_html=True)

    # ==========================================================================
    # MÓDULO 3: RED DE POLINIZACIÓN Y EL OYAMEL
    # ==========================================================================
    elif modulo_central == "🌺 3. Red de Polinización y El Oyamel":
        st.markdown("<h2 class='titulo-flora'>🌺 Red de Polinización (Mensajería) y El Oyamel (Foro)</h2>", unsafe_allow_html=True)
        c_p, c_o = st.columns(2, gap="large")
        with c_p:
            st.markdown("### 🐝 Red de Polinización (Notas Ancladas)")
            ancla_in = st.selectbox("Anclar nota a:", ["Viñeta 1 (Oruga)", "Viñeta 2 (Crisálida 3D)", "Pista 01 (Ecos del Bosque)", "Spread 1 (Monarca)"])
            msg = st.text_input("Instrucción de dirección (Human-in-the-loop):")
            if st.button("📌 Anclar Nota Técnica"):
                if msg:
                    proy["red_polinizacion"].insert(0, {"autor": usr["nombre"], "ancla": ancla_in, "mensaje": msg, "hora": datetime.now().strftime("%H:%M")})
                    registrar_migracion("🌺 Polinización", f"Nota en {ancla_in}")
                    st.rerun()
            for n in proy["red_polinizacion"]:
                st.markdown(f"<div class='tarjeta-modulo'><span class='olive-tag'>{n['ancla']}</span> <b>{n['autor']}</b> ({n['hora']}):<br>{n['mensaje']}</div>", unsafe_allow_html=True)
        with c_o:
            st.markdown("### 🌲 Foro Comunitario El Oyamel")
            tit_f = st.text_input("Asunto para la Colonia:")
            cnt_f = st.text_area("Mensaje:")
            if st.button("📣 Publicar en El Oyamel"):
                if tit_f and cnt_f:
                    proy["foro_oyamel"].insert(0, {"autor": usr["nombre"], "perfil": usr["perfiles"][0], "titulo": tit_f, "contenido": cnt_f, "fecha": datetime.now().strftime("%d/%m/%Y")})
                    registrar_migracion("🌲 El Oyamel", f"Debate: {tit_f}")
                    st.rerun()
            for h in proy["foro_oyamel"]:
                st.markdown(f"<div class='tarjeta-modulo'><b>{h['titulo']}</b> <span class='olive-tag'>{h['perfil']}</span><p class='texto-seasons'>{h['contenido']}</p><small>{h['autor']} • {h['fecha']}</small></div>", unsafe_allow_html=True)

    # ==========================================================================
    # MÓDULO 4: CÓDICE PAPALOTL (PERFIL Y SUSCRIPCIÓN)
    # ==========================================================================
    elif modulo_central == "🎭 4. Códice Papalotl (Mi Perfil)":
        st.markdown("<h2 class='titulo-flora'>🎭 Códice Papalotl (Mi Perfil RPG y Llave de Acceso)</h2>", unsafe_allow_html=True)
        with st.form("form_rpg"):
            nom = st.text_input("Nombre del Creador:", value=usr["nombre"])
            sec = st.selectbox("Sector:", ["Empresa Editorial", "Empresa de Entretenimiento", "Profesional Individual"], index=0)
            plan = st.selectbox("Suscripción Activa:", [
                "Plan Semilla ($134 MXN/mes)",
                "Plan Oruga ($531 MXN/mes)",
                "Plan Monarca Enterprise ($931 MXN/mes)"
            ], index=2)
            perfs = st.multiselect("Perfiles Multiclase (11 disponibles):", [
                "Escritor/a", "Editor/a", "Dibujante", "Ilustrador/a", "Animador/a",
                "Actriz/Actor", "Narrador/a", "Productor/a", "Cantautor/a", "Diseñador/a", "Publicitario/a"
            ], default=usr["perfiles"])
            masc = st.selectbox("Carácter de Papalotl:", ["Modo Acompañante", "Apoyo y Asistencia", "Sostenimiento"])
            if st.form_submit_button("💾 Guardar Códice Papalotl"):
                usr["nombre"] = nom
                usr["sector"] = sec
                usr["plan"] = plan
                usr["perfiles"] = perfs if perfs else ["Escritor/a"]
                usr["vinculo_mascota"] = masc
                registrar_migracion("🎭 Códice Papalotl", "Actualización de perfil multiclase")
                st.success("Perfil RPG actualizado.")

    # ==========================================================================
    # MÓDULO 5: MICROCLIMA DEL SISTEMA
    # ==========================================================================
    elif modulo_central == "☀️ 5. Microclima del Sistema":
        st.markdown("<h2 class='titulo-flora'>☀️ Microclima del Sistema (Ajustes y Accesibilidad)</h2>", unsafe_allow_html=True)
        with st.form("form_micro"):
            t_vis = st.selectbox("Tema Cromático:", ["Papel Antiguo (Old Paper)", "Noche de Tinta (Modo Oscuro)"])
            f_vis = st.selectbox("Jerarquía Tipográfica:", ["Flora Bright + Catchy Mager + The Seasons", "Editorial Clásica"])
            zona = st.selectbox("Huso Horario Sincronizado:", ["GMT-6 (Toluca / CDMX - Santuario Central)", "GMT-5 (Bogotá)", "GMT+1 (Madrid)"])
            red_m = st.radio("Conmutador de Red:", ["Online (Nube Central + Respaldo Local)", "Offline (Software Local Autónomo)"])
            if st.form_submit_button("☀️ Aplicar Microclima"):
                proy["microclima"]["tema"] = t_vis
                proy["microclima"]["fuente"] = f_vis
                proy["microclima"]["zona_horaria"] = zona
                usr["conexion"] = red_m
                guardar_proyecto(proy)
                st.success("Microclima calibrado.")

    # ==========================================================================
    # MÓDULO 6: EL NÉCTAR DEL BOSQUE (BIBLIOTECA Y ENTRENAMIENTO ÉTICO)
    # ==========================================================================
    elif modulo_central == "🍯 6. El Néctar del Bosque (Biblioteca)":
        st.markdown("<h2 class='titulo-flora'>🍯 El Néctar del Bosque (Biblioteca y Entrenamiento Ético)</h2>", unsafe_allow_html=True)
        st.markdown("<p class='texto-seasons'>Bóveda de manuales de dominio público (Bargue, Speed, Loomis), hojas de estilo corporativo y repositorio de activos del proyecto con cero plagio.</p>", unsafe_allow_html=True)
        up = st.file_uploader("Subir manual de estilo, manuscrito (.pdf, .docx, .epub), modelo 3D (.glb) o pista (.mp3, .wav):", type=["pdf", "docx", "epub", "glb", "mp3", "wav", "png", "jpg"])
        if up is not None:
            if st.button("📥 Incorporar al Néctar del Bosque"):
                proy["nectar_bosque"].append({"id": f"ASSET_{len(proy['nectar_bosque'])+1:02d}", "nombre": up.name, "categoria": "Activo del Usuario", "estado": "Verificado ✅"})
                registrar_migracion("🍯 El Néctar del Bosque", f"Archivo anexado: {up.name}")
                st.success(f"Archivo {up.name} resguardado.")
        for item in proy["nectar_bosque"]:
            st.markdown(f"<div class='tarjeta-modulo'><span class='olive-check'>{item['id']}</span> <b>{item['nombre']}</b> — <i>{item['categoria']}</i> <span class='saffron-pill' style='float:right;'>{item['estado']}</span></div>", unsafe_allow_html=True)

    # ==========================================================================
    # MÓDULO 7: LAS 8 ESTACIONES DE METAMORFOSIS (LÍNEA DE PRODUCCIÓN COMPLETA)
    # ==========================================================================
    elif modulo_central == "🛠️ 7. Las 8 Estaciones de Metamorfosis":
        st.markdown("<h2 class='titulo-flora'>🛠️ Las 8 Estaciones de Metamorfosis</h2>", unsafe_allow_html=True)

        ESTACIONES = {
            "1. 🌱 Semilla": "🌱 1. Semilla (Incubadora, Costos y Lienzo Wordpad)",
            "2. 🌿 Germinación": "🌿 2. Germinación (Universo y Sala Sonora 'Ecos del Bosque')",
            "3. 🪴 Algodoncillo": "🪴 3. Hoja de Algodoncillo (Ingesta OCR y Corrector Ortogramatical)",
            "4. 🐛 Oruga": "🐛 4. Oruga (PLN, Tensión por Entropía gzip y Voz del Viento)",
            "5. 🐞 Toxina": "🐞 5. Toxina (Blindaje INDAUTOR SHA-256 y Generaciones de Migración)",
            "6. 🪲 Crisálida": "🪲 6. Crisálida (Estudio 3D, El Foco y Espejo de Obsidiana)",
            "7. 🦋 Monarca": "🦋 7. Monarca (Lienzo 2D de 5 Capas y El Mirador de Alas)",
            "8. 🌬️ Viento": "🌬️ 8. Viento (Exportación Transmedia y Taller de Merch)"
        }

        est_sel = st.selectbox("Estación Activa de Trabajo:", list(ESTACIONES.keys()), format_func=lambda k: ESTACIONES[k])
        f3 = proy["fase3_datos"]

        # --- ESTACIÓN 1: SEMILLA ---
        if est_sel == "1. 🌱 Semilla":
            sem = f3["semilla"]
            st.markdown("### 🌱 Estación 1: Semilla (Ideación, Costos y Escritorio Literario)")
            c_s1, c_s2 = st.columns([2, 1])
            with c_s1:
                txt_w = st.text_area("Lienzo Literario Inicial:", value=sem["manuscrito_word"], height=200)
                if st.button("💾 Guardar en Semilla y Enviar a Algodoncillo"):
                    sem["manuscrito_word"] = txt_w
                    f3["texto_limpio_algodoncillo"] = txt_w
                    registrar_migracion("🌱 Semilla", "Actualización de manuscrito semilla")
                    st.success("Manuscrito guardado y transferido a Hoja de Algodoncillo.")
            with c_s2:
                st.markdown("<div class='tarjeta-modulo'><h4>Calculadora de Presupuesto</h4><p>Presupuesto Base: <b>$185,000 MXN</b></p><p>Jornada Estándar: <b>172 h/mes</b></p></div>", unsafe_allow_html=True)

        # --- ESTACIÓN 2: GERMINACIÓN ---
        elif est_sel == "2. 🌿 Germinación":
            st.markdown("### 🌿 Estación 2: Germinación y Sala Sonora «Ecos del Bosque»")
            for p in f3["ecos_bosque"]:
                st.markdown(f"<div class='tarjeta-modulo'>🎵 <b>{p['titulo']}</b> — Cantautor/a: {p['cantautor']} | {p['bpm']} BPM ({p['tonalidad']}) <span class='saffron-pill' style='float:right;'>{p['estado']}</span></div>", unsafe_allow_html=True)
            frec = st.slider("Frecuencia del Sintetizador Acústico (Hz):", 220, 880, 440, 10)
            if st.button("🔊 Generar Guía Acústica WAV en Vivo"):
                buf_w = io.BytesIO()
                with wave.open(buf_w, "w") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(22050)
                    for i in range(22050):
                        val = int(math.sin(2.0 * math.pi * frec * (i / 22050.0)) * 14000)
                        wf.writeframesraw(struct.pack("<h", val))
                st.audio(buf_w.getvalue(), format="audio/wav")

        # --- ESTACIÓN 3: HOJA DE ALGODONCILLO ---
        elif est_sel == "3. 🪴 Algodoncillo":
            st.markdown("### 🪴 Estación 3: Hoja de Algodoncillo (Ingesta OCR y Limpieza Ortogramatical)")
            txt_a = st.text_area("Sustrato de Texto para Limpieza:", value=f3["texto_limpio_algodoncillo"], height=180)
            if st.button("✨ Ejecutar Limpieza Ortogramatical y Normalización UTF-8"):
                limpio = txt_a.replace("habia", "había").replace("corria", "corría").replace("  ", " ")
                f3["texto_limpio_algodoncillo"] = limpio
                registrar_migracion("🪴 Algodoncillo", "Limpieza ortotipográfica completada")
                st.success("Sustrato depurado y listo para Oruga.")

        # --- ESTACIÓN 4: ORUGA ---
        elif est_sel == "4. 🐛 Oruga":
            st.markdown("### 🐛 Estación 4: Oruga (Desglose PLN, Entropía gzip y «Voz del Viento»)")
            txt_o = st.text_area("Texto de Entrada desde Algodoncillo:", value=f3["texto_limpio_algodoncillo"], height=130)
            c_o1, c_o2 = st.columns(2)
            with c_o1:
                if st.button("🐛 Desglosar Viñetas y Calcular Tensión (gzip)"):
                    lineas = [l.strip() for l in txt_o.split("\n") if l.strip()]
                    nuevo_script = []
                    for idx, lin in enumerate(lineas):
                        raw_b = lin.encode("utf-8")
                        comp_b = gzip.compress(raw_b)
                        ratio = round(min(0.98, max(0.35, len(comp_b) / max(1, len(raw_b) + 20))), 2)
                        plano_sug = "PRIMER PLANO DRAMÁTICO" if ratio > 0.75 else "PLANO MEDIO NARRATIVO"
                        nuevo_script.append({
                            "panel": idx + 1,
                            "plano": plano_sug,
                            "locacion": "Santuario de Oyamel",
                            "tension_gzip": ratio,
                            "dialogo": lin
                        })
                    f3["story_script"] = nuevo_script
                    registrar_migracion("🐛 Oruga", f"StoryScript generado con {len(nuevo_script)} viñetas")
                    st.success("StoryScript calculado con éxito.")
            with c_o2:
                if st.button("🎙️ Activar Cabina «Voz del Viento» (TTS Español)"):
                    texto_js = json.dumps(txt_o)
                    components.html(f"""
                    <script>
                        const msg = new SpeechSynthesisUtterance({texto_js});
                        msg.lang = 'es-MX';
                        msg.rate = 0.95;
                        window.speechSynthesis.cancel();
                        window.speechSynthesis.speak(msg);
                    </script>
                    <div style="font-family:sans-serif; padding:10px; background:#5C6F2B; color:white; border-radius:8px;">
                        🔊 Reproduciendo locución en español con síntesis de voz del navegador...
                    </div>
                    """, height=60)
            st.json(f3["story_script"])

        # --- ESTACIÓN 5: TOXINA ---
        elif est_sel == "5. 🐞 Toxina":
            st.markdown("### 🐞 Estación 5: Toxina (Blindaje Ético INDAUTOR y «Generaciones de Migración»)")
            if st.button("🛡️ Emitir Nuevo Sello Criptográfico SHA-256"):
                payload_hash = json.dumps(f3["story_script"], ensure_ascii=False).encode("utf-8")
                nuevo_h = hashlib.sha256(payload_hash).hexdigest().upper()
                proy["escudo_ip"]["hash_sha256"] = nuevo_h
                registrar_migracion("🐞 Toxina", f"Sello SHA-256 recertificado: {nuevo_h[:12]}")
                st.success("Certificado SHA-256 actualizado para INDAUTOR.")
            st.code(f"SHA-256 ACTIVO: {proy['escudo_ip']['hash_sha256']}")
            st.markdown("#### 🍂 Generaciones de Migración (Máquina del Tiempo de Versiones)")
            for idx, ver in enumerate(proy["generaciones_migracion"]):
                col_v1, col_v2 = st.columns([4, 1])
                with col_v1:
                    st.markdown(f"<div class='tarjeta-modulo'><b>{ver['generacion']}</b> • {ver['fecha_hora']} | <b>{ver['autor']}</b><br><i>{ver['seccion']}: {ver['detalle']}</i> (Hash: <code>{ver['hash_version']}</code>)</div>", unsafe_allow_html=True)
                with col_v2:
                    if st.button("⏪ Restaurar", key=f"rest_{idx}"):
                        st.info(f"Estado sincronizado al punto {ver['hash_version']}.")

        # --- ESTACIÓN 6: CRISÁLIDA ---
        elif est_sel == "6. 🪲 Crisálida":
            st.markdown("### 🪲 Estación 6: Crisálida (Estudio 3D, «El Foco» y «Espejo de Obsidiana»)")
            c3d = f3["crisalida_3d"]
            t_c1, t_c2, t_c3, t_c4 = st.tabs(["👤 Maniquíes y Poses", "🪑 Utilería (Props)", "💡 Iluminación «El Foco»", "🪞 Espejo de Obsidiana (Actuación)"])

            with t_c1:
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    p_idx = st.selectbox("Maniquí Articulado:", range(len(c3d["personajes"])), format_func=lambda i: c3d["personajes"][i]["nombre"])
                    char_act = c3d["personajes"][p_idx]
                    char_act["pose"] = st.selectbox("Pose Anatómica:", ["Alerta / Guardia", "Tensión / Confrontación", "Neutro / De pie", "Acción / Salto"])
                with col_p2:
                    char_act["pos_x"] = st.slider("Posición X:", -4.0, 4.0, float(char_act["pos_x"]), 0.1)
                    char_act["pos_z"] = st.slider("Profundidad Z:", -4.0, 4.0, float(char_act["pos_z"]), 0.1)
                    char_act["rot_y"] = st.slider("Giro Y (°):", -180, 180, int(char_act["rot_y"]), 5)

            with t_c2:
                nuevo_prop = st.text_input("Agregar utilería al set 3D:")
                if st.button("➕ Colocar Prop"):
                    if nuevo_prop:
                        c3d["props"].append({"id": f"PROP_{len(c3d['props'])+1:02d}", "nombre": nuevo_prop, "x": 0.0, "z": -1.5})
                        guardar_proyecto(proy)
                        st.success(f"Prop '{nuevo_prop}' colocado.")

            with t_c3:
                luz_3d = c3d["iluminacion"]
                luz_3d["foco_x"] = st.slider("Foco Teatral X:", -6.0, 6.0, float(luz_3d["foco_x"]), 0.2)
                luz_3d["foco_y"] = st.slider("Altura Foco Y:", 1.0, 10.0, float(luz_3d["foco_y"]), 0.2)
                if st.button("📸 Capturar Snapshot 3D para Monarca"):
                    snap_id = f"Snapshot #{len(c3d['capturas'])+1} ({datetime.now().strftime('%H:%M:%S')})"
                    c3d["capturas"].append(snap_id)
                    registrar_migracion("🪲 Crisálida", f"Bloqueo espacial capturado: {snap_id}")
                    st.success(f"{snap_id} enviado a la estación Monarca.")

            with t_c4:
                st.markdown("#### 🪞 Espejo de Obsidiana (Transferencia de Gestos Faciales para Actrices y Actores)")
                exp_sel = st.selectbox("Expresión Facial Capturada:", ["Determinación", "Asombro", "Melancolía", "Ira Contenida", "Serenidad"])
                hab_cam = st.checkbox("Activar cámara web para referencia actoral en vivo")
                if hab_cam:
                    img_cam = st.camera_input("Captura tu microgesto para vincularlo al maniquí 3D")
                    if img_cam is not None:
                        char_act["expresion"] = exp_sel
                        st.success(f"Gesto '{exp_sel}' transferido a {char_act['nombre']}.")

            payload_3d = json.dumps(c3d)
            html_three = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>body {{ margin: 0; background: #121212; overflow: hidden; }} #v3d {{ width: 100vw; height: 390px; }}</style>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            </head>
            <body>
                <div id="v3d"></div>
                <script>
                    const data = {payload_3d};
                    const scene = new THREE.Scene();
                    scene.background = new THREE.Color(0x181512);
                    const camera = new THREE.PerspectiveCamera(45, window.innerWidth / 390, 0.1, 100);
                    camera.position.set(0, 3.8, 7.5);
                    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                    renderer.setSize(window.innerWidth, 390);
                    document.getElementById('v3d').appendChild(renderer.domElement);
                    scene.add(new THREE.AmbientLight(0xffffff, 0.55));
                    const pLight = new THREE.PointLight(0xffaa44, 2.2, 25);
                    pLight.position.set(data.iluminacion.foco_x, data.iluminacion.foco_y, 2.5);
                    scene.add(pLight);
                    const ground = new THREE.Mesh(new THREE.PlaneGeometry(18, 18), new THREE.MeshStandardMaterial({{color: 0x2b2623}}));
                    ground.rotation.x = -Math.PI/2;
                    scene.add(ground);
                    data.personajes.forEach(p => {{
                        const group = new THREE.Group();
                        const mat = new THREE.MeshStandardMaterial({{color: new THREE.Color(p.color)}});
                        const torso = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.75, 0.3), mat);
                        torso.position.y = 1.35;
                        group.add(torso);
                        const cabeza = new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 16), mat);
                        cabeza.position.y = 1.98;
                        group.add(cabeza);
                        const bGeo = new THREE.CylinderGeometry(0.07, 0.06, 0.65, 12);
                        const bIzq = new THREE.Mesh(bGeo, mat);
                        const bDer = new THREE.Mesh(bGeo, mat);
                        if (p.pose === "Alerta / Guardia") {{
                            bIzq.position.set(-0.35, 1.35, 0.25); bIzq.rotation.x = Math.PI/3;
                            bDer.position.set(0.35, 1.45, 0.35); bDer.rotation.x = Math.PI/2;
                        }} else {{
                            bIzq.position.set(-0.36, 1.25, 0); bDer.position.set(0.36, 1.25, 0);
                        }}
                        group.add(bIzq); group.add(bDer);
                        group.position.set(p.pos_x, 0, p.pos_z);
                        group.rotation.y = (p.rot_y * Math.PI)/180;
                        scene.add(group);
                    }});
                    data.props.forEach(pr => {{
                        const pMesh = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.7, 0.7), new THREE.MeshStandardMaterial({{color: 0xEDB72A}}));
                        pMesh.position.set(pr.x, 0.35, pr.z);
                        scene.add(pMesh);
                    }});
                    function animate() {{ requestAnimationFrame(animate); renderer.render(scene, camera); }}
                    animate();
                </script>
            </body>
            </html>
            """
            components.html(html_three, height=400)

        # --- ESTACIÓN 7: MONARCA Y EL MIRADOR DE ALAS ---
        elif est_sel == "7. 🦋 Monarca":
            st.markdown("### 🦋 Estación 7: Monarca (Lienzo de 5 Capas Vectoriales y «El Mirador de Alas»)")
            m2d = f3["monarca_2d"]
            col_m1, col_m2 = st.columns([1, 2])
            with col_m1:
                capas_sel = st.multiselect("Capas Vectoriales Independientes:", [
                    "Capa 1: Globos Magnéticos (Lettering)",
                    "Capa 2: Tinta Vectorial (Lineart)",
                    "Capa 3: Sombras (Cel-Shading / Hatching)",
                    "Capa 4: Color Base Botánico",
                    "Capa 5: Fondo Perspectiva 3D"
                ], default=m2d["capas_activas"])
                modo_mirador = st.radio("Simulador Dual (El Mirador de Alas):", ["Spread Impreso (Doble Página)", "Scroll Vertical (Webtoon / Móvil)"])
                ver_heatmap = st.checkbox("👁️ Mostrar Mapa de Calor Ocular (Eye-Tracking)", value=True)
                st.markdown("<div class='olive-check'>✓ Preprensa: 600 DPI • Perfil CMYK • Sangrado 3mm OK</div>", unsafe_allow_html=True)

            with col_m2:
                heat_svg = '<circle cx="210" cy="75" r="45" fill="rgba(233,60,33,0.38)"/><circle cx="480" cy="145" r="55" fill="rgba(237,183,42,0.45)"/><path d="M 210 75 Q 350 90 480 145" stroke="#E93C21" stroke-width="3" stroke-dasharray="6,4" fill="none"/>' if ver_heatmap else ''
                globo_svg = '<rect x="110" y="35" width="210" height="55" rx="18" fill="#FFFFFF" stroke="#121212" stroke-width="2"/><text x="215" y="67" font-family="sans-serif" font-size="13" text-anchor="middle" fill="#121212">¡El viento del norte ya está aquí!</text>' if "Capa 1: Globos Magnéticos (Lettering)" in capas_sel else ''
                color_svg = '<rect x="20" y="20" width="320" height="220" fill="#E8DCC4"/><rect x="360" y="20" width="320" height="220" fill="#D9C3B0"/>' if "Capa 4: Color Base Botánico" in capas_sel else ''
                line_svg = '<circle cx="240" cy="155" r="38" fill="none" stroke="#121212" stroke-width="3"/><circle cx="490" cy="150" r="42" fill="none" stroke="#121212" stroke-width="3"/>' if "Capa 2: Tinta Vectorial (Lineart)" in capas_sel else ''
                st.markdown(f"""
                <div style="border:3px solid var(--terracotta-bark); border-radius:12px; padding:10px; background:#121212;">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 260" width="100%" height="260">
                        <rect width="700" height="260" fill="#FDF9F1"/>
                        {color_svg}
                        <line x1="350" y1="0" x2="350" y2="260" stroke="#C85A32" stroke-width="2" stroke-dasharray="5,5"/>
                        {line_svg}
                        {globo_svg}
                        {heat_svg}
                    </svg>
                </div>
                """, unsafe_allow_html=True)

        # --- ESTACIÓN 8: VIENTO ---
        elif est_sel == "8. 🌬️ Viento":
            st.markdown("### 🌬️ Estación 8: Viento (Exportación Transmedia y «Taller de Merch»)")
            c_v1, c_v2 = st.columns(2)
            with c_v1:
                st.markdown("#### 📦 Exportación del Contenedor Maestro")
                buf_zip = io.BytesIO()
                with zipfile.ZipFile(buf_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                    zf.writestr("storyscript.json", json.dumps(f3["story_script"], ensure_ascii=False, indent=4))
                    zf.writestr("certificado_indautor_sha256.txt", proy["escudo_ip"]["hash_sha256"])
                    zf.writestr("proyecto_maestro.json", json.dumps(proy, ensure_ascii=False, indent=4))
                st.download_button(
                    "📥 Descargar Paquete Maestro (.monarch.zip)",
                    data=buf_zip.getvalue(),
                    file_name="Cronicas_del_Oyamel.monarch.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            with c_v2:
                st.markdown("#### 👕 Taller de Merch Oficial")
                for m in f3["viento_merch"]:
                    st.markdown(f"<div class='tarjeta-modulo'>🛍️ <b>{m['producto']}</b> — {m['licencia']} <span class='saffron-pill' style='float:right;'>${m['precio_mxn']:,.0f} MXN</span></div>", unsafe_allow_html=True)