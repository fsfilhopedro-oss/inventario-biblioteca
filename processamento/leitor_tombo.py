# processamento/leitor_tombo.py
def ler_tombo(caminho_arquivo):
    """Lê os tombos do arquivo tombo.txt e retorna uma lista."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return [linha.strip() for linha in f if linha.strip()]
    except FileNotFoundError:
        print(f"Arquivo {caminho_arquivo} não encontrado.")
        return []
    except Exception as e:
        print(f"Erro ao ler {caminho_arquivo}: {e}")
        return []
