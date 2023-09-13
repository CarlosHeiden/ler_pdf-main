import tabula
from tabula.io import read_pdf
import pandas  as pd
from IPython.display import display
import re

filename = r"NotaCorretagem_01-08-23_31-08-23.pdf"

data = tabula.read_pdf(filename, pages='all', multiple_tables=True, stream=True, guess=False)
#notas_df = pd.DataFrame(columns=['Data Pregão', 'Num_nf', 'Corretora', 'Cliente', 'Codigo_cliente', 'Valor_nf', 'Total_despesas', 'IRPF'])
print('='*50)
vl_precos = []
for table in data:
    
    df = pd.DataFrame(table)
    #df.info()
    #print(df)
    #operations = list(df[df['Unnamed: 0'].str.contains("C WDO ",na=False)].index)
    nota_fiscal_regex = r"\sWDO\s"
    nota_fiscal = "C WDO "
    match = re.search(nota_fiscal_regex, nota_fiscal)
    if match:
        print("A nota fiscal foi encontrada!")
    else:
        print("A nota fiscal não foi encontrada.")

    
    precos = list(df[df['Unnamed: 0'].str.contains(nota_fiscal_regex,na=False)].index)
    resultado = 0.0
    for current_row in precos:
       
        #date = df['Unnamed: 1'].iloc[1]
        #numero_nf, pg_nf, data_pregao = date.split(" ")
        #vl_precos.append(data_pregao)
        vl_negocios = df['Unnamed: 1'].iloc[current_row]
        preco, d_c = vl_negocios.split(" ")
        preco = preco.replace(',' , '.')

        preco = float(preco)
        if d_c == 'D':
            preco = preco *-1
        else:
            preco = preco

        resultado += preco
        resultado_arredondado = round(resultado,2)
    print(resultado_arredondado)
    print('-'*50)

    vl_precos.append(resultado_arredondado)

print(vl_precos)
print('='*50)
 


