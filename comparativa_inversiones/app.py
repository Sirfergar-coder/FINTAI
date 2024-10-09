import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Comparativa de Inversión: ETF vs Fondo de Inversión vs Plan de Pensiones")

# Filtros iniciales
tipo_impositivo_ahorro = st.number_input("Tipo Impositivo Rendimiento del Capital (%)", min_value=0.0, max_value=50.0, value=19.0) / 100
col1, col2 = st.columns(2)
with col1:
    tiempo_inversion = st.number_input("Horizonte Temporal (años)", min_value=1, max_value=50, value=20)
with col2:
    inversion_inicial = st.number_input("Inversión Inicial (€)", min_value=0.0, value=10000.0)

# Parámetros ETF
st.header("ETF")
col1, col2, col3, col4 = st.columns(4)
with col1:
    rendimiento_etf = st.number_input("Rentabilidad Anual ETF (%)", min_value=-100.0, max_value=100.0, value=5.0) / 100
with col2:
    coste_etf_gestion = st.number_input("Coste Gestión ETF (%)", min_value=0.0, max_value=5.0, value=0.2) / 100
with col3:
    tipo_coste_etf_transaccion = st.selectbox("Tipo de Coste Compraventa ETF", ["Porcentaje", "Fijo"], index=0)
with col4:
    if tipo_coste_etf_transaccion == "Porcentaje":
        coste_etf_transaccion = st.number_input("Coste Compraventa ETF (%)", min_value=0.0, max_value=5.0, value=0.1) / 100
    else:
        coste_etf_transaccion = st.number_input("Coste Compraventa Fijo (€/transacción)", min_value=0.0, value=5.0)

# Tabla de ventas anuales en desplegable
with st.expander("Ventas Anuales", expanded=False):
    df_ventas = pd.DataFrame({"Año": range(1, tiempo_inversion + 1), "Ventas": [0] * tiempo_inversion})
    ventas_anuales = [st.number_input(f"Ventas en el año {año}", min_value=0, key=f"ventas_{año}") for año in range(1, tiempo_inversion + 1)]
    df_ventas["Ventas"] = ventas_anuales

# Número total de compraventas
total_compraventas = df_ventas["Ventas"].sum()
st.write(f"Número total de compraventas: {total_compraventas}")

# Parámetros Fondo de Inversión
st.header("Fondo de Inversión")
col1, col2 = st.columns(2)
with col1:
    rendimiento_fondo = st.number_input("Rentabilidad Anual Fondo de Inversión (%)", min_value=-100.0, max_value=100.0, value=5.0) / 100
with col2:
    coste_fondo_gestion = st.number_input("Coste Gestión Fondo de Inversión (%)", min_value=0.0, max_value=5.0, value=1.5) / 100

# Función para calcular el rendimiento con costes de transacción y ahorro fiscal
def calcular_rendimiento(inversion_inicial, tiempo, rentabilidad, coste_gestion, coste_transaccion, ventas, tipo_impositivo, tipo_coste):
    valor_inicial = inversion_inicial
    inversion = inversion_inicial
    coste_total_gestion = 0
    coste_total_transaccion = 0
    impuestos_totales = 0

    valores = [inversion]
    costes_transaccion_anuales = [0] * (tiempo + 1)
    impuestos_anuales = [0] * (tiempo + 1)
    for año in range(1, tiempo + 1):
        # Aplicar los costes de compraventa si hubo ventas en ese año
        if ventas[año - 1] > 0:
            if tipo_coste == "Porcentaje":
                coste_traspaso = inversion * coste_transaccion * ventas[año - 1]
            else:
                coste_traspaso = coste_transaccion * ventas[año - 1]
            inversion -= coste_traspaso
            coste_total_transaccion += coste_traspaso
            costes_transaccion_anuales[año] = coste_traspaso

            # Calcular impuestos por las ventas realizadas
            ganancia_venta = inversion - valor_inicial
            impuestos_venta = max(ganancia_venta, 0) * tipo_impositivo
            inversion -= impuestos_venta
            impuestos_totales += impuestos_venta
            valor_inicial = inversion
            impuestos_anuales[año] = impuestos_venta

        # Calcular el rendimiento después de aplicar el coste de gestión
        coste_gestion_anual = inversion * coste_gestion
        coste_total_gestion += coste_gestion_anual
        inversion *= (1 + rentabilidad)
        inversion -= coste_gestion_anual
        valores.append(inversion)
      
    ganancias_finales = valores[-1] - valor_inicial
    impuestos_finales = max(ganancias_finales, 0) * tipo_impositivo
    resultado_final =  valores[-1] - impuestos_finales
    ganancia_neta = resultado_final - valor_inicial

    return valores, coste_total_transaccion, impuestos_totales, costes_transaccion_anuales, impuestos_anuales, coste_total_gestion, ganancias_finales, impuestos_finales, resultado_final, ganancia_neta

# Cálculos para ETF
valores_etf, coste_total_etf, impuestos_ventas_etf, costes_transaccion_etf, impuestos_etf_anuales, coste_total_gestion_etf, ganancias_finales_etf, impuestos_finales_etf, resultado_final_etf, ganancia_neta_etf = calcular_rendimiento(
    inversion_inicial,
    tiempo_inversion,
    rendimiento_etf,
    coste_etf_gestion,
    coste_etf_transaccion,
    df_ventas["Ventas"].tolist(),
    tipo_impositivo_ahorro,
    tipo_coste_etf_transaccion
)
impuestos_totales_etf = impuestos_ventas_etf + impuestos_finales_etf

# Cálculos para Fondo de Inversión
valores_fondo, coste_total_fondo, impuestos_ventas_fondo, _, impuestos_fondo_anuales, coste_total_gestion_fondo, ganancias_finales_fondo, impuestos_finales_fondo, resultado_final_fondo, ganancia_neta_fondo = calcular_rendimiento(
    inversion_inicial,
    tiempo_inversion,
    rendimiento_fondo,
    coste_fondo_gestion,
    0,  # Fondo de inversión no tiene coste de transacción por defecto
    [0] * tiempo_inversion,
    tipo_impositivo_ahorro,
    "Fijo"
)

impuestos_totales_fondo = impuestos_ventas_fondo + impuestos_finales_fondo

# Resultados
st.header("Resultados Finales")

col1, col2 = st.columns(2)

with col1:
    st.subheader("ETF")
    st.write(f"Valor Bruto Final: {valores_etf[-1]:,.2f} €")
    st.write(f"Coste Total de Gestión: {coste_total_gestion_etf:,.2f} €")
    st.write(f"Coste Total de Transacción: {coste_total_etf:,.2f} €")
    st.write(f"Impuestos pagados en las Ventas: {impuestos_ventas_etf:,.2f} €")
    st.write(f"Impuestos último día: {impuestos_finales_etf:,.2f} €")
    st.write(f"Impuestos Totales: {impuestos_totales_etf:,.2f} €")
    st.write(f"**Valor Neto Final: {resultado_final_etf:,.2f} €**")

with col2:
    st.subheader("Fondo de Inversión")
    st.write(f"Valor Bruto Final: {valores_fondo[-1]:,.2f} €")
    st.write(f"Coste Total de Gestión: {coste_total_gestion_fondo:,.2f} €")
    st.write(f"Coste Total de Transacción: {coste_total_fondo:,.2f} €")
    st.write(f"Impuestos pagados en las Ventas: {impuestos_ventas_fondo:,.2f} €")
    st.write(f"Impuestos último día: {impuestos_finales_fondo:,.2f} €")
    st.write(f"Impuestos Totales: {impuestos_totales_fondo:,.2f} €")
    st.write(f"**Valor Neto Final: {resultado_final_fondo:,.2f} €**")

# Gráfico
st.header("Evolución de la Inversión")

df = pd.DataFrame({
    'Años': range(0, tiempo_inversion + 1),
    'ETF': valores_etf,
    'Fondo de Inversión': valores_fondo,
    'Diferencia (ETF - Fondo)': [etf - fondo for etf, fondo in zip(valores_etf, valores_fondo)],
    'Comisiones ETF': costes_transaccion_etf,
    'Impuestos ETF': impuestos_etf_anuales
}).set_index('Años')

# Crear gráfico interactivo
import plotly.express as px
fig = px.line(df.reset_index(), x='Años', y=['ETF', 'Fondo de Inversión'], labels={'value': 'Valor (€)', 'Años': 'Años', 'variable': 'Tipo de Inversión'}, title='Evolución de la Inversión', color_discrete_map={'ETF': '#1f77b4', 'Fondo de Inversión': '#ff7f0e'})
fig.update_traces(line=dict(width=2))

# Añadir el valor neto final como último punto en el gráfico
fig.add_scatter(x=[tiempo_inversion], y=[resultado_final_etf], mode='markers+text', name='Valor Neto ETF', text=[f'{resultado_final_etf:,.2f} €'], textposition='top center', marker=dict(color='#1f77b4', size=10))
fig.add_scatter(x=[tiempo_inversion], y=[resultado_final_fondo], mode='markers+text', name='Valor Neto Fondo', text=[f'{resultado_final_fondo:,.2f} €'], textposition='top center', marker=dict(color='#ff7f0e', size=10))

st.plotly_chart(fig)