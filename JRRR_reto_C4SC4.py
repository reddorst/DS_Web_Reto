# Se importan las librerías a utilizar

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

# Configuraciones para la página
st.set_page_config(page_title="Performance Dashboard - Socialize Your Knowledge", layout="wide")

# Función para cargar datos con caché para mejorar rendimiento
@st.cache_data
def load_data():
    df = pd.read_csv('Employee_data.csv')
    return df

# Se carga el conjunto de datos desde archivo CSV
df_employees = load_data()

# Función para obtener la fecha actual en formato de texto
def obtener_fecha_actual():
    fecha_actual = datetime.now()
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    return f"{dias[fecha_actual.weekday()]}, {fecha_actual.day} de {meses[fecha_actual.month-1]} de {fecha_actual.year}"

# --- SECCIÓN: ENCABEZADO Y LOGOTIPO ---
# El logo y el título se alinean horizontalmente
col1, col2 = st.columns([1, 4], vertical_alignment="center")
with col1:
    st.image("Logo_SYK.PNG", width=250)
with col2:
    st.title("People Analytics: Dashboard Estratégico de Desempeño y Compensación")
    st.markdown("""
    Esta aplicación permite analizar el rendimiento, salario y bienestar de los colaboradores 
    de **Socialize your knowledge** para optimizar la toma de decisiones estratégicas.
    """)

st.divider()

# --- SECCIÓN: CONTROLES / FILTROS ---
# Agrupar controles en una barra lateral o columnas para dejar espacio a las gráficas
st.sidebar.header("Filtros de Análisis")

# Control de Género
gender_list = df_employees['gender'].unique()
selected_gender = st.sidebar.selectbox("Género", gender_list)

st.sidebar.markdown("<hr style='border: 0; border-top: 1px solid rgba(128, 128, 128, 0.2); margin: 10px 0;'>", unsafe_allow_html=True)

# Control de Rango de Desempeño
score_min, score_max = int(df_employees['performance_score'].min()), int(df_employees['performance_score'].max())
selected_score = st.sidebar.slider("Rango de Puntaje de Desempeño", score_min, score_max, (score_min, score_max))

st.sidebar.markdown("<hr style='border: 0; border-top: 1px solid rgba(128, 128, 128, 0.2); margin: 10px 0;'>", unsafe_allow_html=True)

# Control de Estado Civil
marital_list = df_employees['marital_status'].unique()
selected_marital = st.sidebar.multiselect("Estado Civil", marital_list, default=marital_list)

st.sidebar.markdown("<hr style='border: 0; border-top: 1px solid rgba(128, 128, 128, 0.2); margin: 10px 0;'>", unsafe_allow_html=True)

# Se da la opción al usuario de mostrar la tabla de datos completa
show_data = st.sidebar.checkbox("Mostrar tabla de datos")

# Se coloca la fecha pero en formato de texto para facilitar la lectura
st.sidebar.markdown("<hr style='border: 0; border-top: 1px solid rgba(128, 128, 128, 0.2); margin: 10px 0;'>", unsafe_allow_html=True)
fecha_texto = obtener_fecha_actual()
st.sidebar.markdown(f"<div style='text-align: center;'>{fecha_texto}</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='position: fixed; bottom: 10px; left: 0; width: 15rem; text-align: center;'>Elaborado por:<br>J.R.R.R</div>", unsafe_allow_html=True)


# Filtrado dinámico
df_filtered = df_employees[
    (df_employees['gender'] == selected_gender) &
    (df_employees['performance_score'].between(selected_score[0], selected_score[1])) &
    (df_employees['marital_status'].isin(selected_marital))
]

# --- SECCIÓN: VISUALIZACIONES  ---
# Se mostrarán las gráficas en dos columnas para mejor aprovechamiento del espacio
col_left, col_right = st.columns(2)

with col_left:
    # A. Distribución de Puntajes de Desempeño (Histograma)
    st.markdown("<h3 style='text-align: center;'>Distribución de Desempeño</h3>", unsafe_allow_html=True)
    chart_dist = alt.Chart(df_filtered).mark_bar().encode(
        alt.X("performance_score:Q", bin=True, title="Puntaje"),
        y=alt.Y('count()', title="Cantidad de Empleados"),
        color=alt.Color('count()', scale=alt.Scale(scheme='blues'), legend=None)
    ).properties(height=300)
    st.altair_chart(chart_dist, use_container_width=True)

    # B. Edad vs Salario (Scatter Plot - Relación de variables)
    st.markdown("<h3 style='text-align: center;'>Relación Edad vs. Salario</h3>", unsafe_allow_html=True)
    chart_scatter = alt.Chart(df_filtered).mark_circle(size=60).encode(
        x=alt.X('age:Q', title="Edad"),
        y=alt.Y('salary:Q', title="Salario Anual"),
        color=alt.Color('gender:N', scale=alt.Scale(range=['#1f77b4', '#ff7f0e'])),
        tooltip=['name_employee', 'age', 'salary']
    ).properties(height=300).interactive()
    st.altair_chart(chart_scatter, use_container_width=True)

with col_right:
    # C. Promedio de Horas por Género (Bar Chart Comparativo)
    st.markdown("<h3 style='text-align: center;'>Promedio de Horas Mensuales por Género</h3>", unsafe_allow_html=True)
    
    # Usamos barras horizontales intercambiando X e Y para mejor visualizción
    chart_hours = alt.Chart(df_filtered).mark_bar(
        size=30,           # Controlamos el grosor de la barra para que no se vea ancha
        cornerRadiusEnd=5  # Bordes redondeados
    ).encode(
        y=alt.Y('gender:N', title="Género", sort='-x'), # Eje Y para categorías
        x=alt.X('mean(average_work_hours):Q', title="Promedio de Horas"), # Eje X para valores
        color=alt.Color('gender:N', scale=alt.Scale(range=['#1f77b4', '#ff7f0e']), legend=None),
        tooltip=['gender', alt.Tooltip('mean(average_work_hours):Q', format='.2f')]
    ).properties(
        height=300
    )

    st.altair_chart(chart_hours, use_container_width=True)

    # D. Horas Trabajadas vs Puntaje (Relación de desempeño)
    st.markdown("<h3 style='text-align: center;'>Horas Trabajadas vs. Puntaje de Desempeño</h3>", unsafe_allow_html=True)
    chart_rel = alt.Chart(df_filtered).mark_point().encode(
        x=alt.X('average_work_hours:Q', title="Promedio de Horas Mensuales"),
        y=alt.Y('performance_score:Q', title="Puntaje de Desempeño"),
        color=alt.Color('performance_score:Q', scale=alt.Scale(scheme='blues'), legend=None),
        tooltip=['name_employee', 'performance_score']
    ).properties(height=300)
    st.altair_chart(chart_rel, use_container_width=True)

# --- SECCIÓN: CONCLUSIONES ---
st.divider()
st.markdown("<h3 style='text-align: center;'>Conclusiones del Análisis</h3>", unsafe_allow_html=True)

st.info(f"""
Basado en los filtros aplicados, se analizan **{len(df_filtered)} empleados**. 
1. **Eficiencia Operativa:** El desempeño máximo no está correlacionado con el exceso de horas, premiando la calidad sobre la cantidad.
2. **Ciclo de Vida Profesional:** Los ingresos alcanzan su madurez entre los 35-45 años, alineado a la experiencia estratégica.
3. **Paridad Laboral:** Se observa una distribución equitativa de horas trabajadas entre géneros.
4. **Alerta de Bienestar:** El volumen de ausencias debe monitorearse como indicador preventivo de rotación, independientemente del desempeño actual.
5. **Desempeño:** El puntaje de desempeño promedio para el grupo seleccionado es de **{df_filtered['performance_score'].mean():.2f}**.
""")

st.divider()
if show_data:
    st.markdown("<h3 style='text-align: center;'>Tabla de Datos</h3>", unsafe_allow_html=True)

    st.dataframe(df_filtered, use_container_width=True)
