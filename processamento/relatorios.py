import os
from datetime import datetime
from processamento.leitor_mst import chave_classificacao

def salvar_lista_em_txt(lista, caminho):
    with open(caminho, 'w', encoding='utf-8') as f:
        for item in lista:
            f.write(f"{item}\n")

def gerar_relatorio1_novo(fora_ordem, lista_classificacao_tombo, tombos_lidos, pasta_saida):
    """
    Gera o relatório 1 no formato novo:
    Itens fora de ordem na ordem da leitura (tombo.txt),
    mostrando classificação, tombo e marcação FORA DE ORDEM.
    Reduz o contexto com "..." quando não está próximo de um item fora de ordem.
    """
    mapa_classificacao = {tombo: classificacao for classificacao, tombo in lista_classificacao_tombo}
    tombos_fora_ordem = set(item["tombo"] for item in fora_ordem)

    caminho = os.path.join(pasta_saida, "RELATOR1.TXT")
    data_hoje = datetime.today().strftime('%d/%m/%Y')

    # Identifica índices dos tombos fora de ordem
    indices_fora_ordem = set(i for i, t in enumerate(tombos_lidos) if t in tombos_fora_ordem)
    indices_para_exibir = set()
    for idx in indices_fora_ordem:
        indices_para_exibir.update(range(max(0, idx - 5), min(len(tombos_lidos), idx + 6)))

    with open(caminho, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE ITENS FORA DE ORDEM (ORDEM DE LEITURA)\n")
        f.write(f"Gerado em: {data_hoje}\n\n")
        f.write(f"Total de tombos lidos: {len(tombos_lidos)}\n\n")

        pulando = False
        for i, tombo in enumerate(tombos_lidos, start=1):
            if i - 1 in indices_para_exibir:
                classificacao = mapa_classificacao.get(tombo, "??")
                status = "FORA DE ORDEM" if tombo in tombos_fora_ordem else ""
                f.write(f"{i:04d} - {classificacao:<30} - {tombo:<15} {status}\n")
                pulando = False
            else:
                if not pulando:
                    f.write("...\n")
                    pulando = True

        f.write("\n------------------------------------------------------------\n")
        f.write("FIM DO RELATÓRIO\n")
        f.write(f"Total de tombos lidos: {len(tombos_lidos)}\n")

def gerar_relatorios(fora_ordem, duplicados, nao_encontrados, lista_classificacao_tombo, pasta_saida, tombos_lidos):
    os.makedirs(pasta_saida, exist_ok=True)

    # --- RELATOR1 com formato novo ---
    gerar_relatorio1_novo(fora_ordem, lista_classificacao_tombo, tombos_lidos, pasta_saida)

    # --- RELATOR2 ---
    data_hoje = datetime.today().strftime('%d/%m/%Y')
    relator2_path = os.path.join(pasta_saida, 'RELATOR2.TXT')
    with open(relator2_path, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE ITENS DUPLICADOS\n")
        f.write(f"Gerado em: {data_hoje}\n\n")
        f.write(f"Total de itens duplicados: {len(duplicados)}\n\n")

        for i, tombo in enumerate(duplicados, start=1):
            f.write(f"{tombo}\n")

        f.write("\n------------------------------------------------------------\n")
        f.write("FIM DO RELATÓRIO\n")
        f.write(f"Total de itens duplicados: {len(duplicados)}\n")

    # --- RELATOR3 ---
    relator3_path = os.path.join(pasta_saida, 'RELATOR3.TXT')

    dict_tombo_class = {tombo: classificacao for classificacao, tombo in lista_classificacao_tombo}
    lista_nao_encontrados = []
    for tombo in nao_encontrados:
        classificacao = dict_tombo_class.get(tombo, "??")
        lista_nao_encontrados.append((classificacao, tombo))

    lista_nao_encontrados.sort(key=lambda x: chave_classificacao(x[0]))

    with open(relator3_path, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE ITENS NÃO ENCONTRADOS\n")
        f.write(f"Gerado em: {data_hoje}\n\n")
        f.write(f"Total de itens não encontrados: {len(lista_nao_encontrados)}\n\n")

        for i, (classificacao, tombo) in enumerate(lista_nao_encontrados, start=1):
            f.write(f"{classificacao:<30} - {tombo}\n")

        f.write("\n------------------------------------------------------------\n")
        f.write("FIM DO RELATÓRIO\n")
        f.write(f"Total de itens não encontrados: {len(lista_nao_encontrados)}\n")