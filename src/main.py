import pdfplumber
import os

# Define o caminho para o arquivo PDF de entrada
caminho_pdf = os.path.join("data", "inputs", "Cartão de Ponto.pdf")

print(f"Lendo o arquivo: {caminho_pdf}")

try:
    # Abre o arquivo PDF
    with pdfplumber.open(caminho_pdf) as pdf:
        # Pega a primeira página (índice 0)
        pagina = pdf.pages[0]

        # Extrai todo o texto da página
        texto_da_pagina = pagina.extract_text()

        # Imprime o resultado
        print("\n--- TEXTO EXTRAÍDO COM SUCESSO ---\n")
        print(texto_da_pagina)
        print("\n------------------------------------")

except FileNotFoundError:
    print(f"Erro: O arquivo não foi encontrado em '{caminho_pdf}'. Verifique o caminho e o nome do arquivo.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")