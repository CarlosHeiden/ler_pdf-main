import tabula
import re
import datetime
from tabula.io import read_pdf
import pandas  as pd
from IPython.display import display

filename = input('Digite o caminho para arquivo PDF: ')

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
        #if match:
        #    print("A condiçao foi encontrada!")
        #else:
        #    print("A condiçao não foi encontrada.")

        
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
        #if match:
         #   print("A nota fiscal foi encontrada!")
        #else:
        #    print("A nota fiscal não foi encontrada.")

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
        irpf_mes = total_mes * 0.20
        despesas_mes = notas_df['Total_despesas'].sum()
        dias_positivos = len(notas_df[notas_df['Valor_nf']>0])
        dias_negativos = len(notas_df[notas_df['Valor_nf']<0])
        percentual_positivos = (dias_positivos / (dias_positivos + dias_negativos)) * 100

    
       
    print(notas_df)
    print('='*50)
    print('\n**Resumo das operacoes**\n')
    print(f'Quantidade total de contratos = {total_contratos_mes}')
    print(f'Custo por operacao deste = R$ {despesas_mes/total_contratos_mes}')
    print(f"Percentual de dias positivos: {percentual_positivos:.2f}%")
    print(f'Quantidade de dias positivos = {dias_positivos}')
    print(f'Quantidade de dias negativos = {dias_negativos}\n')
    print(f'A soma do valor total das notas deste = R$ {total_mes}')
    
    
    #calcula irpf  no caso de lucro
    if irpf_mes >0:
        print(f'\nO IRPF a ser pago neste mês é de :R$ {irpf_mes:.2f} ')
    else:
        print(f'Resultado do mes negativo, isento pgto IRPF')


    # salva-o  dataframe como um arquivo do Excel ,inserindo ano e mes ao nome do arquivo
    
    dia, mes, ano = data_pregao.split('/')
    caminho = input('Digite o caminho para salvar arquivo excel com os dados do pdf: ')
    path_salve = f'{caminho}/notas_corretagem_{ano}_{mes}.xlsx'
    notas_df.to_excel(path_salve, index=False)



except Exception as e:
    print("Ocorreu um erro:", str(e))

print('='*50)