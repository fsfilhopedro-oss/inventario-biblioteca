# Inventário de Acervo - CLI

Este projeto realiza a verificação de um inventário físico de acervo (livros, teses, etc), comparando os tombos lidos na estante com a ordem esperada definida em um arquivo de referência (`mst.seq`).

## 📁 Estrutura dos Arquivos

### `dados/tombo.txt`
Contém os tombos lidos na estante, um por linha.

```
T10001
T10002
T10003
...
```

### `dados/mst.seq`
Cada linha contém a **classificação** e um ou mais **tombos** separados por `|`. Serve como referência da ordem correta.

```
005.13 P123|T10001|T10002
005.14 B456|T10003
...
```

## ▶️ Como Executar

1. Coloque os arquivos `tombo.txt` e `mst.seq` na pasta `dados/`
2. Execute o programa principal:

```bash
python main.py
```

3. Os relatórios serão gerados na pasta `output/`:

- `RELATOR1.TXT` – Tombos fora de ordem
- `RELATOR2.TXT` – Tombos duplicados
- `RELATOR3.TXT` – Tombos esperados não encontrados
