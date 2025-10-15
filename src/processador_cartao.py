import pdfplumber
import os
import pandas as pd
import re

def processar_cartao_ponto(caminho_pdf, caminho_excel):
    """
    Processa um PDF de cartão de ponto, extrai os dados e salva em Excel
    no formato exato do arquivo de exemplo, usando um período pré-definido.
    """
    print(f"Processando o arquivo: {caminho_pdf}")
    
    # --- DADOS DO PERÍODO (DEFINIDOS MANUALMENTE PARA ESTE ARQUIVO) ---
    MES = "10"
    ANO = "2011"
    
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            pagina = pdf.pages[0]
            
            # 1. Extrair a tabela principal
            tabela_bruta = pagina.extract_tables()[0]
            df = pd.DataFrame(tabela_bruta[1:], columns=tabela_bruta[0])
            df.rename(columns={'Dia': 'Data'}, inplace=True)
            
            # 2. Formatar a coluna de Data
            df['Data'] = df['Data'].str.extract(r'(\d{2})')
            # Usa o MÊS e ANO definidos acima para construir a data completa
            df['Data'] = df['Data'].apply(lambda dia: f"{dia}/{MES}/{ANO}" if dia else None)

            # 3. Extrair todos os horários da coluna 'Entrada Saida'
            coluna_horarios_nome = 'Entrada Saida'
            if coluna_horarios_nome in df.columns:
                horarios_extraidos = df[coluna_horarios_nome].apply(
                    lambda x: re.findall(r'(\d{2}:\d{2})', x) if isinstance(x, str) else []
                )
                
                # 4. Criar todas as 12 colunas de horário
                for i in range(6):
                    entrada_col = f'Entrada{i+1}'
                    saida_col = f'Saída{i+1}'
                    
                    df[entrada_col] = horarios_extraidos.apply(lambda h: h[i*2] if len(h) > i*2 else None)
                    df[saida_col] = horarios_extraidos.apply(lambda h: h[i*2+1] if len(h) > i*2+1 else None)

            # 5. Selecionar e reordenar as colunas para a saída final
            colunas_finais = [
                'Data', 
                'Entrada1', 'Saída1', 'Entrada2', 'Saída2',
                'Entrada3', 'Saída3', 'Entrada4', 'Saída4',
                'Entrada5', 'Saída5', 'Entrada6', 'Saída6'
            ]
            
            # Garante que todas as colunas existam antes de tentar selecionar
            for col in colunas_finais:
                if col not in df.columns:
                    df[col] = None
            
            df_final = df[colunas_finais]

            df_final.to_excel(caminho_excel, index=False)
            print(f"Arquivo Excel finalizado com sucesso em: {caminho_excel}")

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

# --- Caminhos dos arquivos ---
pdf_input = os.path.join("data", "inputs", "Exemplo-Cartao-Ponto-01.pdf")
excel_output = os.path.join("data", "outputs", "Cartão de Ponto Processado.xlsx")

processar_cartao_ponto(pdf_input, excel_output)