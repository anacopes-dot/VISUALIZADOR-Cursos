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


# --- ENTORNO DE PROCESAMIENTO ---
if df_asistencia is not None and df_inscripciones is not None and df_escuelas is not None:
    
    # Limpieza estándar de columnas (quitar espacios invisibles)
    df_asistencia.columns = [str(c).strip() for c in df_asistencia.columns]
    df_inscripciones.columns = [str(c).strip() for c in df_inscripciones.columns]
    df_escuelas.columns = [str(c).strip() for c in df_escuelas.columns]
    
    # Homologar campos clave a Texto Limpio para cruces perfectos
    for df_tmp in [df_asistencia, df_inscripciones, df_escuelas]:
        for col in ['DNI', 'FECHA', 'ESCUELA', 'Escuela', 'TURNO', 'COMUNA', 'DEPENDENCIA', 'CAPACITADOR', 'Tipo de Formación']:
            if col in df_tmp.columns:
                df_tmp[col] = df_tmp[col].astype(str).str.strip()

    # Detectar variaciones de la columna Escuela
    col_esc_as = 'ESCUELA' if 'ESCUELA' in df_asistencia.columns else 'Escuela'
    col_esc_ins = 'ESCUELA' if 'ESCUELA' in df_inscripciones.columns else 'Escuela'
    col_esc_mae = 'ESCUELA' if 'ESCUELA' in df_escuelas.columns else 'Escuela'

    # --- CÁLCULOS CRUCIALES DE POBLACIÓN ---
    total_inscriptos = df_inscripciones['DNI'].nunique()
    docentes_asistieron_al_menos_una = df_asistencia['DNI'].nunique()
    
    dnis_asistieron = set(df_asistencia['DNI'].unique())
    df_no_asistieron_nunca = df_inscripciones[~df_inscripciones['DNI'].isin(dnis_asistieron)]
    total_no_asistieron = df_no_asistieron_nunca['DNI'].nunique()

    # --- 1) METRICAS RESALTADAS DE CONVOCATORIA GENERAL ---
    st.write("### 📌 Estado General de Inscripción y Convocatoria")
    kpi1, kpi2, kpi3 = st.columns(3)
    
    with kpi1:
        st.metric(label="👤 Total Docentes Inscriptos", value=f"{total_inscriptos:,}")
    with kpi2:
        pct_al_menos_una = (docentes_asistieron_al_menos_una / total_inscriptos * 100) if total_inscriptos > 0 else 0
        st.metric(label="✅ Asistieron Al Menos Una Vez (Hoja Asistencias)", value=f"{docentes_asistieron_al_menos_una:,} ({pct_al_menos_una:.1f}%)")
    with kpi3:
        pct_no_asistieron = (total_no_asistieron / total_inscriptos * 100) if total_inscriptos > 0 else 0
        st.metric(label="🚨 No Asistieron Nunca", value=f"{total_no_asistieron:,} ({pct_no_asistieron:.1f}%)")

    st.write("---")

    # --- 2) ANALISIS DE PRESENTISMO DIARIO BASADO EN CONVOCATORIA ---
    st.write("### 📅 Porcentaje de Asistencia Diaria (Por Fecha Convocada)")
    
    if 'FECHA' in df_asistencia.columns:
        registros_fecha = []
        fechas_unicas = sorted(df_asistencia['FECHA'].unique())
        
        for fecha in fechas_unicas:
            df_asistentes_dia = df_asistencia[df_asistencia['FECHA'] == fecha]
            asistentes_reales = df_asistentes_dia['DNI'].nunique()
            
            # Escuelas que registraron actividad esta fecha en la hoja Asistencias
            escuelas_convocadas_dia = df_asistentes_dia[col_esc_as].unique()
            
            # Universo de docentes de la hoja Inscriptos que pertenecen a estas escuelas
            total_debieron_asistir = df_inscripciones[df_inscripciones[col_esc_ins].isin(escuelas_convocadas_dia)]['DNI'].nunique()
            
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
            st.dataframe(df_presentismo_diario.style.format({'% Asistencia Diaria': '{:.2f}%'}), use_container_width=True, hide_index=True)
    else:
        st.error("No se encontró el campo 'FECHA' en la hoja de Asistencias.")

    st.write("---")

    # --- 3) DESGLOSES SOLICITADOS (CANTIDAD DE DOCENTES POR CATEGORÍA) ---
    st.write("### 🗂️ Distribución y Desglose de Docentes Inscriptos (Hoja Asistencias)")
    
    pestanas = st.tabs(["Estado y Dependencia", "Escuela y Comuna", "Turno y Formación", "Capacitador"])
    
    with pestanas:
        c1, c2 = st.columns(2)
        with c1:
            if 'Estado' in df_asistencia.columns:
                st.write("#### Docentes por Estado")
                df_est = df_asistencia.groupby('Estado')['DNI'].nunique().reset_index(name='Docentes Únicos')
                st.plotly_chart(px.bar(df_est, x='Estado', y='Docentes Únicos', color='Estado', title="Docentes por Estado"), use_container_width=True)
        with c2:
            if 'DEPENDENCIA' in df_asistencia.columns:
                st.write("#### Docentes por Dependencia Funcional")
                df_dep = df_asistencia.groupby('DEPENDENCIA')['DNI'].nunique().reset_index(name='Docentes Únicos')
                st.plotly_chart(px.pie(df_dep, names='DEPENDENCIA', values='Docentes Únicos', title="Distribución por Dependencia"), use_container_width=True)

    with pestanas:
        if col_esc_as:
            st.write("#### Cantidad de Docentes Asistentes por Escuela")
            df_esc_cant = df_asistencia.groupby(col_esc_as)['DNI'].nunique().reset_index(name='Docentes Únicos').sort_values(by='Docentes Únicos', ascending=False)
            st.dataframe(df_esc_cant, use_container_width=True, hide_index=True)
        if 'COMUNA' in df_asistencia.columns:
            st.write("#### Docentes por Comuna")
            df_com = df_asistencia.groupby('COMUNA')['DNI'].nunique().reset_index(name='Docentes Únicos')
            st.plotly_chart(px.bar(df_com, x='COMUNA', y='Docentes Únicos', title="Docentes por Comuna"), use_container_width=True)

    with pestanas:
        c3, c4 = st.columns(2)
        with c3:
            if 'TURNO' in df_asistencia.columns:
                df_tur = df_asistencia.groupby('TURNO')['DNI'].nunique().reset_index(name='Docentes Únicos')
                st.plotly_chart(px.pie(df_tur, names='TURNO', values='Docentes Únicos', title="Docentes por Turno"), use_container_width=True)
        with c4:
            if 'Tipo de Formación' in df_asistencia.columns:
                st.write("#### Docentes por Tipo de Formación")

