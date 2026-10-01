import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Control de Presentismo Docente", layout="wide")
st.title("📊 Panel de Presentismo: Asistencias, Inscriptos y Escuelas")

# --- BARRA LATERAL: CARGA DE LAS TRES HOJAS OFICIALES ---
st.sidebar.header("📂 Carga de Hojas Oficiales")

# 1. HOJA: ASISTENCIAS
st.sidebar.subheader("1. Hoja: Asistencias (Por Curso)")
opcion_as = st.sidebar.radio("Origen de Asistencias:", ["Subir Excel (.xlsx)", "Link Google Sheets"], key="op_as")
df_asistencia = None

if opcion_as == "Subir Excel (.xlsx)":
    file_as = st.sidebar.file_uploader("Subir archivo de Asistencias", type=["xlsx"], key="file_as")
    if file_as:
        try:
            df_asistencia = pd.read_excel(file_as)
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
else:
    url_as = st.sidebar.text_input("Link Google Sheet de Asistencias:", key="url_as")
    if url_as:
        try:
            url_csv = url_as.split("/edit?") + "/export?format=csv" if "edit?" in url_as else url_as
            df_asistencia = pd.read_csv(url_csv)
        except Exception as e:
            st.sidebar.error(f"Error de enlace: {e}")

# 2. HOJA: INSCRIPTOS
st.sidebar.write("---")
st.sidebar.subheader("2. Hoja: Inscriptos (Total General)")
opcion_ins = st.sidebar.radio("Origen de Inscriptos:", ["Subir Excel (.xlsx)", "Link Google Sheets"], key="op_ins")
df_inscripciones = None

if opcion_ins == "Subir Excel (.xlsx)":
    file_ins = st.sidebar.file_uploader("Subir archivo de Inscriptos", type=["xlsx"], key="file_ins")
    if file_ins:
        try:
            df_inscripciones = pd.read_excel(file_ins)
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
else:
    url_ins = st.sidebar.text_input("Link Google Sheet de Inscriptos:", key="url_ins")
    if url_ins:
        try:
            url_csv_ins = url_ins.split("/edit?") + "/export?format=csv" if "edit?" in url_ins else url_ins
            df_inscripciones = pd.read_csv(url_csv_ins)
        except Exception as e:
            st.sidebar.error(f"Error de enlace: {e}")

# 3. HOJA: ESCUELAS
st.sidebar.write("---")
st.sidebar.subheader("3. Hoja: Escuelas (Maestra)")
opcion_esc = st.sidebar.radio("Origen de Escuelas:", ["Subir Excel (.xlsx)", "Link Google Sheets"], key="op_esc")
df_escuelas = None

if opcion_esc == "Subir Excel (.xlsx)":
    file_esc = st.sidebar.file_uploader("Subir archivo de Escuelas", type=["xlsx"], key="file_esc")
    if file_esc:
        try:
            df_escuelas = pd.read_excel(file_esc)
        except Exception as e:
            st.sidebar.error(f"Error: {e}")
else:
    url_esc = st.sidebar.text_input("Link Google Sheet de Escuelas:", key="url_esc")
    if url_esc:
        try:
            url_csv_esc = url_esc.split("/edit?") + "/export?format=csv" if "edit?" in url_esc else url_esc
            df_escuelas = pd.read_csv(url_csv_esc)
        except Exception as e:
            st.sidebar.error(f"Error de enlace: {e}")

# --- DETECTOR INTELIGENTE DE COLUMNAS ---
def mapear_columna(df_cols, posibles_nombres):
    for nombre in posibles_nombres:
        for c in df_cols:
            if c.lower().strip() == nombre.lower().strip():
                return c
    return None

# --- ENTORNO DE PROCESAMIENTO ---
if df_asistencia is not None or df_inscripciones is not None or df_escuelas is not None:
    
    st.write("### 🔍 Estado de Carga de las Hojas")
    c_check1, c_check2, c_check3 = st.columns(3)
    with c_check1:
        if df_asistencia is not None: st.success(f"✅ Hoja Asistencias cargada ({len(df_asistencia)} filas)")
        else: st.warning("⏳ Esperando Hoja Asistencias...")
    with c_check2:
        if df_inscripciones is not None: st.success(f"✅ Hoja Inscriptos cargada ({len(df_inscripciones)} filas)")
        else: st.warning("⏳ Esperando Hoja Inscriptos...")
    with c_check3:
        if df_escuelas is not None: st.success(f"✅ Hoja Escuelas cargada ({len(df_escuelas)} filas)")
        else: st.warning("⏳ Esperando Hoja Escuelas...")

    # Si falta alguna hoja, mostrar ayuda visual interactiva para que el usuario sepa qué pasa
    if df_asistencia is None or df_inscripciones is None or df_escuelas is None:
        st.info("💡 **Nota:** Para ver los gráficos avanzados y los porcentajes de presentismo diario, recordá que debés cargar las **3 hojas juntas** en la barra lateral de la izquierda.")
        
        # Mostrar vista previa de lo que haya cargado para asegurar que no esté roto
        df_actual = df_asistencia if df_asistencia is not None else (df_inscripciones if df_inscripciones is not None else df_escuelas)
        st.write("#### Vista previa del archivo cargado:")
        st.dataframe(df_actual.head(5), use_container_width=True)

    else:
        # --- PROCESAMIENTO COMPLETO CUANDO ESTÁN LAS 3 HOFAS ---
        # Limpieza de nombres de columnas
        df_asistencia.columns = [str(c).strip() for c in df_asistencia.columns]
        df_inscripciones.columns = [str(c).strip() for c in df_inscripciones.columns]
        df_escuelas.columns = [str(c).strip() for c in df_escuelas.columns]

        # Mapeo inteligente tolerante a errores
        col_dni_as = mapear_columna(df_asistencia.columns, ['DNI', 'Documento'])
        col_dni_ins = mapear_columna(df_inscripciones.columns, ['DNI', 'Documento'])
        col_fecha_as = mapear_columna(df_asistencia.columns, ['FECHA', 'Fecha'])
        
        col_esc_as = mapear_columna(df_asistencia.columns, ['ESCUELA', 'Escuela'])
        col_esc_ins = mapear_columna(df_inscripciones.columns, ['ESCUELA', 'Escuela'])
        col_esc_mae = mapear_columna(df_escuelas.columns, ['ESCUELA', 'Escuela'])
        
        col_dep = mapear_columna(df_asistencia.columns, ['DEPENDENCIA', 'Dependencia', 'DEPENDENCIA FUNCIONAL'])
        col_com = mapear_columna(df_asistencia.columns, ['COMUNA', 'Comuna'])
        col_tur = mapear_columna(df_asistencia.columns, ['TURNO', 'Turno'])
        col_cap = mapear_columna(df_asistencia.columns, ['CAPACITADOR', 'Capacitador'])
        col_form = mapear_columna(df_asistencia.columns, ['Tipo de Formación', 'Formación', 'Tipo de Formacion'])
        col_est = mapear_columna(df_asistencia.columns, ['Estado', 'ESTADO'])

        # Homologar tipos de datos
        if col_dni_as: df_asistencia[col_dni_as] = df_asistencia[col_dni_as].astype(str).str.strip()
        if col_dni_ins: df_inscripciones[col_dni_ins] = df_inscripciones[col_dni_ins].astype(str).str.strip()
        if col_fecha_as: df_asistencia[col_fecha_as] = df_asistencia[col_fecha_as].astype(str).str.strip()

        # --- 1) MÉTRICAS RESALTADAS (KPIs) ---
        st.write("---")
        st.write("### 📌 Estado General de Inscripción y Convocatoria")
        
        total_inscriptos = df_inscripciones[col_dni_ins].nunique() if col_dni_ins else 0
        docentes_asistieron_al_menos_una = df_asistencia[col_dni_as].nunique() if col_dni_as else 0
        
        dnis_asistieron = set(df_asistencia[col_dni_as].unique()) if col_dni_as else set()
        df_no_asistieron_nunca = df_inscripciones[~df_inscripciones[col_dni_ins].isin(dnis_asistieron)] if col_dni_ins else pd.DataFrame()
        total_no_asistieron = df_no_asistieron_nunca[col_dni_ins].nunique() if col_dni_ins else 0

        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric(label="👤 Total Docentes Inscriptos", value=f"{total_inscriptos:,}")
        with kpi2:
            pct_al_menos_una = (docentes_asistieron_al_menos_una / total_inscriptos * 100) if total_inscriptos > 0 else 0
            st.metric(label="✅ Asistieron Al Menos Una Vez", value=f"{docentes_asistieron_al_menos_una:,} ({pct_al_menos_una:.1f}%)")
        with kpi3:
            pct_no_asistieron = (total_no_asistieron / total_inscriptos * 100) if total_inscriptos > 0 else 0
            st.metric(label="🚨 No Asistieron Nunca", value=f"{total_no_asistieron:,} ({pct_no_asistieron:.1f}%)")

        st.write("---")

        # --- 2) ANÁLISIS DE PRESENTISMO DIARIO ---
        st.write("### 📅 Porcentaje de Asistencia Diaria (Por Fecha Convocada)")
        if col_fecha_as and col_dni_as and col_esc_as and col_esc_ins:
            registros_fecha = []
            fechas_unicas = sorted(df_asistencia[col_fecha_as].unique())
            
            for fecha in fechas_unicas:
                df_asistentes_dia = df_asistencia[df_asistencia[col_fecha_as] == fecha]
                asistentes_reales = df_asistentes_dia[col_dni_as].nunique()
                escuelas_convocadas_dia = df_asistentes_dia[col_esc_as].unique()
                
                total_debieron_asistir = df_inscripciones[df_inscripciones[col_esc_ins].isin(escuelas_convocadas_dia)][col_dni_ins].nunique() if col_dni_ins else 0
                porcentaje_diario = (asistentes_reales / total_debieron_asistir * 100) if total_debieron_asistir > 0 else 0
                
                registros_fecha.append({
                    "Fecha": fecha,
                    "Asistieron Reales": asistentes_reales,
                    "Debían Asistir (Escuelas Convocadas)": total_debieron_asistir,
                    "% Asistencia Diaria": porcentaje_diario
                })
                
            df_presentismo_diario = pd.DataFrame(registros_fecha)
            promedio_asistencia_total = df_presentismo_diario['% Asistencia Diaria'].mean()
            
            c_graf, c_tab = st.columns()
            with c_graf:
                fig_diario = px.line(df_presentismo_diario, x='Fecha', y='% Asistencia Diaria',
                                     title="Evolución del Presentismo Real por Fecha de Encuentro",
                                     markers=True, labels={'% Asistencia Diaria': '% de Presentismo'})
                st.plotly_chart(fig_diario, use_container_width=True)
                
            with c_tab:
                st.markdown(f"**Promedio de Asistencia Total del Curso:** `{promedio_asistencia_total:.2f}%`")
