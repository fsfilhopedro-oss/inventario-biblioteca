import re

# Ordem especial de símbolos para ordenação
ORDEM_SIMBOLOS = {
    ' ': 0,
    '+': 1,
    '/': 2,
    ':': 3,
    '(': 4,
    '-': 5,
    '.': 6
}

def simbolo_ordenado(c):
    if c == '[':
        c = '('  # Trata '[' como equivalente a '('
    if c.isdigit():
        return (1, int(c))
    elif c.isalpha():
        return (2, c.upper())
    elif c in ORDEM_SIMBOLOS:
        return (0, ORDEM_SIMBOLOS[c])
    else:
        return (3, c)

def chave_classificacao(classe):
    """
    Ordena classificações considerando:
    1. O prefixo numérico como string ASCII, preservando zeros à esquerda.
    2. O restante da classificação, caractere por caractere, com regras especiais.
    """
    match = re.search(r'[ +/:()\-[.A-Za-z]', classe)
    if match:
        pos = match.start()
        prefixo = classe[:pos]
        sufixo = classe[pos:]
    else:
        prefixo = classe
        sufixo = ''

    etapa1 = prefixo  # ordena como string ASCII preservando zeros à esquerda
    etapa2 = [simbolo_ordenado(c) for c in sufixo]

    return (etapa1, etapa2)

def ler_mst(caminho_arquivo):
    """
    Lê os dados do arquivo mst.seq.
    Cada linha contém uma classificação seguida de tombos, separados por '|'.
    Os tombos são separados por ponto '.'.
    Retorna uma lista de tuplas: (classificacao, tombo), ordenada por classificação.
    """
    resultado = []
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue
                partes = linha.split('|')
                classificacao = partes[0].strip()
                if len(partes) > 1:
                    tombos = partes[1].strip().split('.')
                    for tombo in tombos:
                        tombo = tombo.strip()
                        if tombo:
                            resultado.append((classificacao, tombo))

        resultado.sort(key=lambda x: chave_classificacao(x[0]))
        return resultado

    except FileNotFoundError:
        print(f"Arquivo {caminho_arquivo} não encontrado.")
        return []
    except Exception as e:
        print(f"Erro ao ler {caminho_arquivo}: {e}")
        return []