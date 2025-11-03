import os
import zipfile
import shutil
from datetime import datetime
from flask import Flask, render_template, request, send_file, redirect, url_for

# Importa os módulos de processamento (que estão na subpasta 'processamento')
from processamento.leitor_mst import ler_mst
from processamento.leitor_tombo import ler_tombo
from processamento.comparador import comparar_listas
from processamento.relatorios import gerar_relatorios

app = Flask(__name__)

# Configuração de pastas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
REPORT_FOLDER = os.path.join(BASE_DIR, 'reports')

# Cria as pastas se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORT_FOLDER'] = REPORT_FOLDER

# --- ROTAS DA APLICAÇÃO ---

@app.route('/')
def index():
    """Página inicial com o formulário de upload."""
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar_arquivos():
    """Recebe, processa e retorna os relatórios em um arquivo ZIP."""
    
    # Validação de upload
    if 'mst_file' not in request.files or 'tombo_file' not in request.files:
        return "Erro: É necessário fazer o upload do 'mst.seq' e 'tombo.txt'.", 400

    mst_file = request.files['mst_file']
    tombo_file = request.files['tombo_file']

    if mst_file.filename == '' or tombo_file.filename == '':
        return "Erro: Arquivos não selecionados.", 400

    # 1. Preparação dos caminhos e limpeza
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_folder = os.path.join(app.config['UPLOAD_FOLDER'], timestamp)
    output_folder = os.path.join(app.config['REPORT_FOLDER'], f"relatorios_{timestamp}")
    
    os.makedirs(temp_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    mst_path = os.path.join(temp_folder, 'mst.seq')
    tombo_path = os.path.join(temp_folder, 'tombo.txt')
    
    # 2. Salvar arquivos do usuário
    mst_file.save(mst_path)
    tombo_file.save(tombo_path)

    try:
        # 3. Lógica do 'main.py' (Processamento)

        # Leitura dos dados de inventário (mst.seq)
        lista_classificacao_tombo = ler_mst(mst_path) 
        
        # Leitura dos tombos lidos (tombo.txt)
        tombos_lidos = ler_tombo(tombo_path)
        
        # Comparação (retorna os dados necessários para os relatórios)
        (
            duplicados, 
            nao_encontrados, 
            fora_ordem, 
            lista_classificacao_tombo_ordenada
        ) = comparar_listas(lista_classificacao_tombo, tombos_lidos)
        
        # Mapeamento para o relatório 1 (necessário no seu relatorios.py)
        mapa_classificacao = {c: t for c, t in lista_classificacao_tombo_ordenada}

        # Geração dos Relatórios (Relatórios 2 e 3)
        gerar_relatorios(
            pasta_saida=output_folder,
            duplicados=duplicados,
            nao_encontrados=nao_encontrados,
            mapa_classificacao=mapa_classificacao
        )
        
        # Geração do Relatório 1 (Fora de Ordem - Novo Formato)
        # O relatorio.py original tem uma função chamada 'gerar_relatorio1_novo' (linha 63)
        # É importante que essa função seja chamada corretamente.
        # Assumindo que você a expôs corretamente:
        # from processamento.relatorios import gerar_relatorio1_novo 
        
        # Como a função exata não está no escopo, vou usar a função que gera o relatório 1.
        # Se você estiver usando o 'gerar_relatorios' principal, ele deve gerar todos.
        # Para garantir a geração de todos, vou garantir o Relatório 1:
        
        # OBS: Se a função 'gerar_relatorios' já gerar o Relatório 1, remova a chamada abaixo!
        # from processamento.relatorios import gerar_relatorio1_novo # Adapte a importação
        # gerar_relatorio1_novo(
        #    output_folder, 
        #    fora_ordem, 
        #    tombos_lidos, 
        #    lista_classificacao_tombo_ordenada,
        #    mapa_classificacao # Se necessário
        # )

        # 4. Criação do arquivo ZIP
        zip_base_name = os.path.join(app.config['REPORT_FOLDER'], f"Relatorios_Inventario_{timestamp}")
        zip_path = shutil.make_archive(zip_base_name, 'zip', output_folder)
        zip_filename = os.path.basename(zip_path)

        # 5. Retornar o ZIP para o usuário
        return send_file(
            zip_path, 
            as_attachment=True, 
            download_name=zip_filename,
            mimetype='application/zip'
        )

    except FileNotFoundError:
        return "Erro: Certifique-se de que os arquivos de entrada estão no formato correto e não estão vazios.", 500
    except Exception as e:
        # Erro geral de processamento
        app.logger.error(f"Erro de processamento: {e}")
        return f"Erro no processamento: {e}", 500
    
    finally:
        # 6. Limpeza (deleta a pasta temporária de uploads e a pasta de relatórios)
        if os.path.exists(temp_folder):
             shutil.rmtree(temp_folder)
        if os.path.exists(output_folder):
             shutil.rmtree(output_folder)
        # O zip_path será limpo posteriormente (ou em uma rotina de manutenção)

# Inicia o servidor (apenas para desenvolvimento local)
if __name__ == '__main__':
    # Use: app.run(host='0.0.0.0', port=5000) no Render
    app.run(debug=True)