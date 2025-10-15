import pdfplumber
import os
import pandas as pd
import re

def processar_holerite_final(caminho_pdf, caminho_exemplo_excel, caminho_saida_excel):
    """
    Processa um PDF de holerite, extrai os dados manualmente com regex,
    e os estrutura para corresponder exatamente ao arquivo de exemplo.
    """
    print(f"Processando o arquivo: {caminho_pdf}")
    print(f"Usando o exemplo: {caminho_exemplo_excel}")

    try:
        # 1. Ler o arquivo de exemplo para obter a lista de todas as colunas necessárias
        # Usamos read_csv porque o arquivo que temos é um .csv
        df_exemplo = pd.read_csv(caminho_exemplo_excel)
        colunas_finais = df_exemplo.columns.tolist()
        
        # 2. Criar um dicionário em branco para armazenar nosso resultado final
        resultado = {col: None for col in colunas_finais}

        with pdfplumber.open(caminho_pdf) as pdf:
            pagina = pdf.pages[0]
            texto_completo = pagina.extract_text()

            # 3. Extrair dados do cabeçalho do PDF
            match_mes_ano = re.search(r'Mês/Ano:\s*(\d{2})/(\d{4})', texto_completo)
            if match_mes_ano:
                resultado['Mês'] = int(match_mes_ano.group(1))
                resultado['Ano'] = int(match_mes_ano.group(2))

            # 4. Extrair os dados da tabela principal linha por linha
            padrao_tabela = re.compile(r'(\d{4})\s+(.*?)\s+([\d,.-]+)\s+([\d,.-]+)\s*([\d,.-]*)')
            for linha in texto_completo.split('\n'):
                match = padrao_tabela.search(linha)
                if match:
                    codigo, desc, ref, prov, desc_val = match.groups()
                    coluna_ref = f"({codigo}) {desc.strip()} QUANTIDADE"
                    coluna_valor = f"({codigo}) {desc.strip()} VALOR"
                    
                    if coluna_ref in resultado:
                        resultado[coluna_ref] = ref
                    if coluna_valor in resultado:
                        resultado[coluna_valor] = prov if prov.strip() and float(prov.replace('.','').replace(',','.')) > 0 else desc_val

            # 5. Extrair os totais do rodapé
            match_totais = re.search(r'Total Vencimentos\s*([\d.,]+)\s*Total Descontos\s*([\d.,]+)\s*Líquido a Receber\s*([\d.,]+)', texto_completo)
            if match_totais:
                resultado['Base Cálculo INSS'] = match_totais.group(1)
                resultado['Líquido a Receber'] = match_totais.group(3)

        # 6. Converter o dicionário de resultado para um DataFrame e salvar
        df_final = pd.DataFrame([resultado])
        df_final.to_excel(caminho_saida_excel, index=False)
        
        print(f"Arquivo Excel final do holerite gerado com sucesso em: {caminho_saida_excel}")

    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado. Verifique se os arquivos de entrada estão na pasta 'data/inputs'.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

# --- CAMINHOS DOS ARQUIVOS CORRIGIDOS ---
pdf_input = os.path.join("data", "inputs", "Exemplo-Holerite-01.pdf")
# Agora lê o exemplo da pasta de inputs
exemplo_input = os.path.join("data", "inputs", "Exemplo-Holerite-01.xlsx - Exemplo-Holerite-01.csv")
# E salva o resultado na pasta de outputs
excel_output = os.path.join("data", "outputs", "Holerite Final Formatado.xlsx")

# Executar a função
processar_holerite_final(pdf_input, exemplo_input, excel_output)