import pandas as pd
import re

# Leer el archivo fuente
csv_path = '2025ccm.csv'
df = pd.read_csv(csv_path, sep=';', dtype=str)

# Excluir la fila TOTAL si existe
df = df[~df['EVALUADORES'].str.strip().str.upper().eq('TOTAL')]

# Transformar a formato largo
df_melted = df.melt(id_vars=['EVALUADORES'], var_name='FechaOriginal', value_name='Pendientes')
df_melted = df_melted.rename(columns={'EVALUADORES': 'OPERADOR'})
df_melted['Proceso'] = 'PRR'
df_melted['Año'] = '2023'

# Convertir fechas al formato 2025-MM-DD para todos
meses = {
    'Ene': '01', 'Feb': '02', 'Mar': '03', 'Abr': '04', 'May': '05', 'Jun': '06',
    'Jul': '07', 'Ago': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dic': '12'
}
def convertir_fecha_2025(fecha_str):
    match = re.match(r'(\d{2})-(\w{3})', fecha_str)
    if match:
        dia, mes = match.groups()
        mes_num = meses.get(mes.title(), '01')
        return f'2025-{mes_num}-{dia}'
    return fecha_str

df_melted['Fecha'] = df_melted['FechaOriginal'].apply(convertir_fecha_2025)

# Limpiar y normalizar claves
df_melted = df_melted[['Fecha', 'Proceso', 'OPERADOR', 'Año', 'Pendientes']]
df_melted = df_melted[df_melted['Pendientes'].notna()]
df_melted['Pendientes'] = df_melted['Pendientes'].replace('', '0').astype(int)
df_melted['OPERADOR'] = df_melted['OPERADOR'].str.strip().str.upper()
df_melted['Año'] = df_melted['Año'].astype(str)

# Leer el histórico existente
historico_path = 'ARCHIVOS/historico_pendientes_operador.csv'
try:
    historico = pd.read_csv(historico_path, dtype=str)
    historico['OPERADOR'] = historico['OPERADOR'].str.strip().str.upper()
    historico['Año'] = historico['Año'].astype(str)
except FileNotFoundError:
    historico = pd.DataFrame(columns=df_melted.columns)

# Merge anti-join para evitar duplicados
claves = ['Fecha', 'Proceso', 'OPERADOR', 'Año']
merge = df_melted.merge(historico[claves], on=claves, how='left', indicator=True)
df_melted_filtrada = merge[merge['_merge'] == 'left_only'].drop(columns=['_merge'])
historico_actualizado = pd.concat([historico, df_melted_filtrada], ignore_index=True)

if not df_melted_filtrada.empty:
    historico_actualizado.to_csv(historico_path, index=False)
    print('Datos agregados al histórico.')
else:
    print('No hay datos nuevos para agregar.') 