from processamento.leitor_mst import chave_classificacao

def comparar_listas(tombos_lidos, lista_classificacao_tombo):
    tombos_esperados = [tombo for _, tombo in lista_classificacao_tombo]
    classificacoes = [c for c, _ in lista_classificacao_tombo]

    # 1. Duplicados
    vistos = set()
    duplicados = set()
    for t in tombos_lidos:
        if t in vistos:
            duplicados.add(t)
        else:
            vistos.add(t)

    indices = {tombo: i for i, tombo in enumerate(tombos_esperados)}

    fora_ordem = []
    # Variável para controlar sequência fora de ordem consecutiva
    grupo_fora_ordem = []

    ultimo_indice = None
    for i, t in enumerate(tombos_lidos):
        if t not in indices:
            continue  # ignora tombos que não estão na referência

        pos = indices[t]

        if ultimo_indice is None or pos >= ultimo_indice:
            # Está na ordem, antes de atualizar, salva grupo fora de ordem se houver
            if grupo_fora_ordem:
                fora_ordem.extend(grupo_fora_ordem)
                grupo_fora_ordem = []
        else:
            # Quebra de ordem detectada
            entrada = {
                "classificacao": classificacoes[pos],
                "tombo": t,
                "anterior": {
                    "classificacao": classificacoes[pos - 1] if pos > 0 else None,
                    "tombo": tombos_esperados[pos - 1] if pos > 0 else None
                },
                "proximo": {
                    "classificacao": classificacoes[pos + 1] if pos + 1 < len(classificacoes) else None,
                    "tombo": tombos_esperados[pos + 1] if pos + 1 < len(tombos_esperados) else None
                },
                "anterior_lido": {
                    "classificacao": None,
                    "tombo": tombos_lidos[i - 1] if i > 0 else None
                },
                "proximo_lido": {
                    "classificacao": None,
                    "tombo": tombos_lidos[i + 1] if i + 1 < len(tombos_lidos) else None
                }
            }
            # Preenche classificações dos vizinhos lidos
            if entrada["anterior_lido"]["tombo"] in indices:
                idx = indices[entrada["anterior_lido"]["tombo"]]
                entrada["anterior_lido"]["classificacao"] = classificacoes[idx]
            if entrada["proximo_lido"]["tombo"] in indices:
                idx = indices[entrada["proximo_lido"]["tombo"]]
                entrada["proximo_lido"]["classificacao"] = classificacoes[idx]

            grupo_fora_ordem.append(entrada)

        ultimo_indice = pos

    # Ao final, adicionar grupo restante
    if grupo_fora_ordem:
        fora_ordem.extend(grupo_fora_ordem)

    fora_ordem.sort(key=lambda x: chave_classificacao(x["classificacao"]))

    # 3. Não encontrados
    set_lidos = set(tombos_lidos)
    set_esperados = set(tombos_esperados)
    nao_encontrados = sorted(set_esperados - set_lidos)

    return fora_ordem, sorted(duplicados), nao_encontrados