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
    
    # ... (Código de validação de upload e setup de paths) ...
    if 'mst_file' not in request.files or 'tombo_file' not in request.files:
        return "Erro: É necessário fazer o upload do 'mst.seq' e 'tombo.txt'.", 400
    
    mst_file = request.files['mst_file']
    tombo_file = request.files['tombo_file']
    
    # 1. Preparação de pastas temporárias
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_folder = os.path.join(app.config['UPLOAD_FOLDER'], timestamp)
    output_folder = os.path.join(app.config['REPORT_FOLDER'], f"relatorios_{timestamp}")
    
    os.makedirs(temp_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    mst_path = os.path.join(temp_folder, 'mst.seq')
    tombo_path = os.path.join(temp_folder, 'tombo.txt')
    
    mst_file.save(mst_path)
    tombo_file.save(tombo_path)

    try:
        # 2. Lógica de Leitura e Processamento

        # Leitura dos dados de inventário (mst.seq)
        lista_classificacao_tombo = ler_mst(mst_path) 
        
        # Leitura dos tombos lidos (tombo.txt)
        tombos_lidos = ler_tombo(tombo_path)
        
        # CORREÇÃO: comparador.py retorna 3 valores (fora_ordem, duplicados, nao_encontrados)
        # A ordem de atribuição segue a ordem do seu main.py:
        fora_ordem, duplicados, nao_encontrados = comparar_listas(tombos_lidos, lista_classificacao_tombo)
        
        # CORREÇÃO: gerar_relatorios recebe 6 argumentos, conforme seu main.py
        gerar_relatorios(
            fora_ordem, 
            duplicados, 
            nao_encontrados, 
            lista_classificacao_tombo, 
            output_folder, # O caminho onde os relatórios serão salvos (pasta_saida)
            tombos_lidos
        )

        # 3. Criação do arquivo ZIP
        zip_base_name = os.path.join(app.config['REPORT_FOLDER'], f"Relatorios_Inventario_{timestamp}")
        zip_path = shutil.make_archive(zip_base_name, 'zip', output_folder)
        zip_filename = os.path.basename(zip_path)

        # 4. Retornar o ZIP para o usuário
        return send_file(
            zip_path, 
            as_attachment=True, 
            download_name=zip_filename,
            mimetype='application/zip'
        )

    except Exception as e:
        # Erro geral de processamento
        app.logger.error(f"Erro de processamento: {e}")
        # Limpa o diretório de arquivos temporários antes de retornar o erro
        if os.path.exists(temp_folder): shutil.rmtree(temp_folder)
        if os.path.exists(output_folder): shutil.rmtree(output_folder)
        return f"Erro no processamento: {e}", 500
    
    finally:
        # 5. Limpeza (deleta a pasta temporária de uploads e a pasta de relatórios)
        if os.path.exists(temp_folder):
             shutil.rmtree(temp_folder)
        if os.path.exists(output_folder):
             shutil.rmtree(output_folder)

# Inicia o servidor (apenas para desenvolvimento local)
if __name__ == '__main__':
    # Use: app.run(host='0.0.0.0', port=5000) no Render
    app.run(debug=True)