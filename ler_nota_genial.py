import tabula
from tabula.io import read_pdf
import pandas  as pd
from IPython.display import display
import re

filename = r"NotaCorretagem_01-08-23_31-08-23.pdf"

try:
    #ler arquivo pdf e cria DataFrame
    data = tabula.read_pdf(filename, pages='all', multiple_tables=True, stream=True, guess=False)
    notas_df = pd.DataFrame(columns=['Data Pregão', 'Num_nf', 'Corretora', 'Cliente', 'Codigo_cliente', 'Qtd_Contratos',  'Vl_Operacoes', 'Total_despesas', 'IRPF(1%)', 'Valor_nf'])
    print('='*50)

    # loop para iterar dados da tabela e cria novo df para manipular dados
    for table in data:
        
        df = pd.DataFrame(table)
        #df.info()
        #print(df)

    #criando variaveis para receber valores das tabelas pdf

        date = df['Unnamed: 1'].iloc[1]

        numero_nf, pg_nf, data_pregao = date.split(" ")
    
        nome_corretora = df['Unnamed: 0'].iloc[3]
        
        nome_cliente =  df['Unnamed: 0'].iloc[8]
        
        codigos=  df['Unnamed: 1'].iloc[10]
        codigo_cliente, cod_corretor = codigos.split("|")

        #obtem indice e verifica se nao eh ultimo indice do df
        primeiro_indice = df[df['Unnamed: 1'].str.contains("Total líquido da nota", na=False)].index
        if not primeiro_indice.empty:
            primeiro_indice = primeiro_indice[0]  # Obtém o primeiro índice
            if primeiro_indice + 1 < len(df):
                valor_negocios = df.at[primeiro_indice + 1, 'NOTA DE CORRETAGEM']
            else:
                print("Não há próxima linha na mesma coluna, pois o índice está no final do DataFrame.")
        else:
            print("Nenhum índice correspondente encontrado.")

        c_v, valor, debito_credito = valor_negocios.split(" ")
        valor_nf = ""
        if debito_credito == "D":
            valor_nf =float(valor.replace(',', '.'))
            valor_negocios = valor_nf *-1 # Obtem valor dos negocios
        else:
            valor_nf =float(valor.replace(',', '.'))
            valor_negocios = valor_nf # Obtem valor dos negocios

        indice_despesas = df[df['Unnamed: 1'].str.contains("Total das despesas", na=False)].index
        if not indice_despesas.empty:
            indice_despesas = indice_despesas[0]  # Obtém o primeiro índice
            if indice_despesas + 1 < len(df):
                total_despesas = " "
                total_despesas = df.at[indice_despesas + 1, 'Unnamed: 2']
                total_despesas_nf =float(total_despesas.replace(',', '.'))# Obtem total despesas 
            else:
                print("Não há próxima linha na mesma coluna, pois o índice está no final do DataFrame.")
        else:
            print("Nenhum índice correspondente encontrado.")

        indice_irpf = df[df['Unnamed: 0'].str.contains("IRRF IRRF Day Trade ", na=False)].index
        if not indice_irpf.empty:
            indice_irpf = indice_irpf[0]  # Obtém o primeiro índice
            if indice_irpf + 1 < len(df):
                irpf = " "
                irpf = df.at[indice_irpf + 1, 'NOTA DE CORRETAGEM']
                valor_irpf, dado_zero = irpf.split(" ")
                irpf_nf =float(valor_irpf.replace(',', '.'))# Obtem IRPF
            else:
                print("Não há próxima linha na mesma coluna, pois o índice está no final do DataFrame.")
        else:
            print("Nenhum índice correspondente encontrado.")

        # extrai a quantidade de contratos negociados no dia utilizando expressoes regulares
        nota_fiscal_regex = r"\sWDO\s"
        nota_fiscal = "C WDO "
        match = re.search(nota_fiscal_regex, nota_fiscal)
        if match:
            print("A condiçao foi encontrada!")
        else:
            print("A condiçao não foi encontrada.")

        
        operations = list(df[df['Unnamed: 0'].str.contains(nota_fiscal_regex,na=False)].index)
        qtd_contratos= 0

        for current_row in operations:
            negocios = df['NOTA DE CORRETAGEM'].iloc[current_row]
            qtd, preco, tipo_negocio, tipo_negocio2 = negocios.split(" ")
            qtd = int(qtd)
            qtd_contratos += qtd  # Obtem quantidade de contratos

        #extrai valor financeriro das operaçoes do dia utilizando expressoes regulares
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
            vl_negocios = df['Unnamed: 1'].iloc[current_row]
            preco, d_c = vl_negocios.split(" ")
            preco = preco.replace(',' , '.')
            preco = float(preco)
            if d_c == 'D':
                preco = preco *-1
            else:
                preco = preco

            resultado += preco
            resultado_arredondado = round(resultado,2) # Obtem valor das operaçoeS, arredonda para 2 casa decimais

        #cria lista de variaveis  com valores extraidos das tabelas pdf, serao incluidas no notas_df como linha
        dados_nf =[
            data_pregao, numero_nf, nome_corretora, nome_cliente, codigo_cliente, qtd_contratos, resultado_arredondado,  total_despesas_nf, irpf_nf,  valor_negocios 
            ]
        
        # Adicione uma nova linha de dados ao DataFrame usando loc
        next_index = len(notas_df)
        notas_df.loc[next_index] = dados_nf
        total_contratos_mes = notas_df['Qtd_Contratos'].sum()
        total_mes = notas_df['Valor_nf'].sum()
        despesas_mes = notas_df['Total_despesas'].sum()
       
    print(notas_df)
    print(f'Quantidade total de contratos mes = {total_contratos_mes}')
    print(f'Custo por operacao deste mes = R$ {despesas_mes/total_contratos_mes}')
    print(f'Valor total das notas = R$ {total_mes}')

    #cria arquivo excel com valores de notas_df
    notas_df.to_excel('notas_corretagem_genial.xlsx', index=False)

 

except Exception as e:
    print("Ocorreu um erro:", str(e))

print('='*50)