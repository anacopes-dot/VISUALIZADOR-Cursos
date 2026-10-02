import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página con diseño expandido y título profesional
st.set_page_config(page_title="Dashboard Docente Premium", layout="wide", initial_sidebar_state="expanded")

# --- ESTILOS CSS PERSONALIZADOS PARA DISEÑO VISUAL INTERESANTE ---
st.markdown("""
    <style>
    /* Fondo general y fuentes */
    .main { background-color: #f8f9fa; }
    h1 { color: #1e3a8a; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; text-align: center; margin-bottom: 25px; }
    h3 { color: #2563eb; font-family: 'Helvetica Neue', sans-serif; font-weight: 700; margin-top: 20px; border-bottom: 2px solid #e5e7eb; padding-bottom: 8px; }
    h4 { color: #1e40af; font-weight: 600; margin-top: 15px; }
    
    /* Tarjetas de Métricas Resaltadas (KPIs) */
    .kpi-container {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 22px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        border-left: 6px solid #2563eb;
        text-align: center;
        transition: transform 0.2s;
    }
    .kpi-container:hover { transform: translateY(-3px); }
    .kpi-title { font-size: 14px; font-weight: 700; color: #4b5563; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { font-size: 32px; font-weight: 800; color: #1e3a8a; margin-top: 5px; }
    .kpi-sub { font-size: 13px; color: #10b981; font-weight: 600; margin-top: 2px; }
    
    /* Alertas de Ausentismo Estilizadas */
    .alerta-roja {
        background-color: #fef2f2;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #ef4444;
        color: #991b1b;
        font-weight: 500;
        margin-bottom: 15px;
    }
    .alerta-verde {
        background-color: #ecfdf5;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #10b981;
        color: #065f46;
        font-weight: 500;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Tablero Ejecutivo de Control y Presentismo Docente")

# --- INSTANTE DE CARGA EN BARRA LATERAL ---
st.sidebar.markdown("<h2 style='color:#1e3a8a; font-size:22px; font-weight:700;'>📂 Panel de Archivos</h2>", unsafe_allow_html=True)

file_as = st.sidebar.file_uploader("1. Archivo de Asistencias", type=["xlsx"], key="file_as")
file_ins = st.sidebar.file_uploader("2. Archivo de Inscriptos (Opcional)", type=["xlsx"], key="file_ins")
file_esc = st.sidebar.file_uploader("3. Archivo de Escuelas (Opcional)", type=["xlsx"], key="file_esc")

# Inicialización de variables
df_asistencia, df_inscripciones, df_escuelas = None, None, None

# Lectura robusta tolerante a nombres de pestañas
if file_as:
    try: df_asistencia = pd.read_excel(file_as, sheet_name="Asistencias")
    except:
        try: df_asistencia = pd.read_excel(file_as, sheet_name=0)
        except: pass
if file_ins:
    try: df_inscripciones = pd.read_excel(file_ins, sheet_name="Inscriptos")
    except:
        try: df_inscripciones = pd.read_excel(file_ins, sheet_name=0)
        except: pass
if file_esc:
    try: df_escuelas = pd.read_excel(file_esc, sheet_name="Escuelas")
    except:
        try: df_escuelas = pd.read_excel(file_esc, sheet_name=0)
        except: pass

# --- FUNCIÓN DETECTOR INTELIGENTE DE COLUMNAS ---
def mapear_columna(df_cols, posibles_nombres):
    for nombre in posibles_nombres:
        for c in df_cols:
            if str(c).lower().strip() == nombre.lower().strip():
                return c
    return None

# --- PROCESAMIENTO RECONSTRUCTIVO DEL DISEÑO VIBRANTE ---
if df_asistencia is not None:
    df_asistencia.columns = [str(c).strip() for c in df_asistencia.columns]
    
    # Mapeo inteligente
    col_dni_as = mapear_columna(df_asistencia.columns, ['DNI', 'Documento'])
    col_fecha_as = mapear_columna(df_asistencia.columns, ['FECHA', 'Fecha'])
    col_esc_as = mapear_columna(df_asistencia.columns, ['ESCUELA', 'Escuela'])
    col_dep = mapear_columna(df_asistencia.columns, ['DEPENDENCIA', 'Dependencia', 'DEPENDENCIA FUNCIONAL'])
    col_com = mapear_columna(df_asistencia.columns, ['COMUNA', 'Comuna'])
    col_tur = mapear_columna(df_asistencia.columns, ['TURNO', 'Turno'])
    col_cap = mapear_columna(df_asistencia.columns, ['CAPACITADOR', 'Capacitador'])
    col_form = mapear_columna(df_asistencia.columns, ['Tipo de Formación', 'Formación', 'Tipo de Formacion'])
    col_est = mapear_columna(df_asistencia.columns, ['Estado', 'ESTADO'])

    if col_dni_as: df_asistencia[col_dni_as] = df_asistencia[col_dni_as].astype(str).str.strip()
    if col_fecha_as: df_asistencia[col_fecha_as] = df_asistencia[col_fecha_as].astype(str).str.strip()

    # Variables de base
    docentes_activos_hoja = df_asistencia[col_dni_as].nunique() if col_dni_as else len(df_asistencia)
    escuelas_hoja = df_asistencia[col_esc_as].nunique() if col_esc_as else 0
    fechas_cant = df_asistencia[col_fecha_as].nunique() if col_fecha_as else 0

    # --- DISEÑO INICIAL DE TARJETAS DE ALTO IMPACTO ---
    st.write("### 📌 Indicadores de Convocatoria Actual")
    
    k_col1, k_col2, k_col3 = st.columns(3)
    
    with k_col1:
        st.markdown(f"""
            <div class="kpi-container" style="border-left-color: #2563eb;">
                <div class="kpi-title">👤 Docentes Asistentes Únicos</div>
                <div class="kpi-value">{docentes_activos_hoja:,}</div>
                <div class="kpi-sub">En base a DNI limpios</div>
            </div>
        """, unsafe_allow_html=True)
        
    with k_col2:
        st.markdown(f"""
            <div class="kpi-container" style="border-left-color: #10b981;">
                <div class="kpi-title">🏫 Escuelas con Presencia</div>
                <div class="kpi-value">{escuelas_hoja}</div>
                <div class="kpi-sub">Instituciones activas</div>
            </div>
        """, unsafe_allow_html=True)
        
    with k_col3:
        st.markdown(f"""
            <div class="kpi-container" style="border-left-color: #f59e0b;">
                <div class="kpi-title">📅 Encuentros Auditados</div>
                <div class="kpi-value">{fechas_cant}</div>
                <div class="kpi-sub">Fechas con registros</div>
            </div>
        """, unsafe_allow_html=True)

    # --- SECCIÓN PORCENTAJES DE PRESENTISMO AVANZADO ---
    if df_inscripciones is not None:
        df_inscripciones.columns = [str(c).strip() for c in df_inscripciones.columns]
        col_dni_ins = mapear_columna(df_inscripciones.columns, ['DNI', 'Documento'])
        col_esc_ins = mapear_columna(df_inscripciones.columns, ['ESCUELA', 'Escuela'])
        
        if col_dni_ins:
            df_inscripciones[col_dni_ins] = df_inscripciones[col_dni_ins].astype(str).str.strip()
            total_inscriptos = df_inscripciones[col_dni_ins].nunique()
            pct_real = (docentes_activos_hoja / total_inscriptos * 100) if total_inscriptos > 0 else 0
            
            st.write("### 📈 Curva y Porcentajes Reales de Presentismo")
            
            # Bloque Resaltado de Inscritos
            st.markdown(f"""
                <div class="kpi-container" style="border-left-color: #7c3aed; text-align: left; max-width: 400px; margin-bottom: 20px;">
                    <div class="kpi-title">📋 Población Total de Inscriptos</div>
                    <div class="kpi-value">{total_inscriptos:,}</div>
                    <div class="kpi-sub" style="color: #7c3aed;">El {pct_real:.1f}% del total asistió al menos una vez</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Gráfico de líneas temporales de asistencia diaria
            if col_fecha_as and col_esc_as and col_esc_ins:
                registros_fecha = []
                fechas_unicas = sorted(df_asistencia[col_fecha_as].unique())
                
                for f in fechas_unicas:
                    df_f = df_asistencia[df_asistencia[col_fecha_as] == f]
                    asistieron = df_f[col_dni_as].nunique() if col_dni_as else 0
                    escuelas_hoy = df_f[col_esc_as].unique()
                    
                    debieron_asistir = df_inscripciones[df_inscripciones[col_esc_ins].isin(escuelas_hoy)][col_dni_ins].nunique()
                    pct_dia = (asistieron / debieron_asistir * 100) if debieron_asistir > 0 else 0
                    
                    registros_fecha.append({"Fecha": f, "% Asistencia": round(pct_dia, 1)})
                
                df_p_diario = pd.DataFrame(registros_fecha)
                
                # Gráfico interactivo moderno
                fig_linea = px.line(df_p_diario, x='Fecha', y='% Asistencia', 
                                     title="📈 Evolución de Asistencia Diaria por Encuentro (Sobre Escuelas Convocadas)",
                                     text='% Asistencia', markers=True, template="plotly_white")
                fig_linea.update_traces(line_color='#2563eb', line_width=3, marker=dict(size=8))
                fig_linea.update_layout(title_font_size=16, title_x=0.5)
                
                g_col, t_col = st.columns()
                with g_col:
                    st.plotly_chart(fig_linea, use_container_width=True)
                with t_col:
                    st.write("#### 📋 Promedio General")
                    st.markdown(f"""
                        <div class="kpi-container" style="border-left-color: #3b82f6; background-color:#eff6ff;">
                            <div class="kpi-title">Asistencia Promedio Total</div>
                            <div class="kpi-value">{df_p_diario['% Asistencia'].mean():.2f}%</div>
                        </div>
                    """, unsafe_allow_html=True)

    # --- 3) SECCIÓN DE GRÁFICOS CREATIVOS E INTERACTIVOS ---
    st.write("### 🎨 Análisis Visual de Variables y Categorías")
    
    v_col1, v_col2 = st.columns(2)
    
    with v_col1:
        if col_dep:

