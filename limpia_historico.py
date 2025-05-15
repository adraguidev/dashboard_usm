import pandas as pd

# Cargar el histórico
ruta = 'ARCHIVOS/historico_pendientes_operador.csv'
df = pd.read_csv(ruta, dtype=str)

# Normalizar nombres de operador
if 'OPERADOR' in df.columns:
    df['OPERADOR'] = df['OPERADOR'].str.strip().str.upper()

# Ordenar por Fecha (y por el orden de aparición en el archivo)
df = df.sort_values('Fecha')

# Dejar solo el último registro para cada combinación clave
clave = ['Fecha', 'Proceso', 'OPERADOR', 'Año']
df = df.drop_duplicates(subset=clave, keep='last')

# Guardar el histórico limpio
df.to_csv(ruta, index=False)
print('Histórico limpiado y normalizado. Solo queda el último registro por combinación clave.') 