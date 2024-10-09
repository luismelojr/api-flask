from flask import Flask, request, jsonify, send_file
import csv
import os
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import base64
import io
import base64
import json

app = Flask(__name__)

def get_csv_filename():
  today = datetime.now().strftime('%d-%m-%Y')
  return f'dados_{today}.csv'

  
@app.route('/download_csv', methods=['GET'])
def download_csv():
    query_date = request.args.get('date')

    if query_date:
      csv_file = f'dados_{query_date}.csv'
    else:
      csv_file = get_csv_filename()

    # Verifica se o arquivo CSV existe
    if os.path.isfile(csv_file):
        return send_file(csv_file, as_attachment=True)

    return jsonify({'error': 'Arquivo CSV não encontrado.'}), 404

@app.route('/list_csv', methods=['GET'])
def list_csv():
    files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.csv')]
    return jsonify({'files': files})

@app.route('/add_row', methods=['POST'])
def add_row():
    data = request.json
    contact = data['contact']
    name = data['name']
    message = data['message']
    date = data['date']

    dateObj = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
    formatedDate = dateObj.strftime('%d/%m/%Y %H:%M:%S')

    csv_file = get_csv_filename()

    try:
        if not os.path.exists(csv_file):
            with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Contato', 'Nome', 'Mensagem', 'Data'])

        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([contact, name, message, formatedDate])

        return jsonify({'message': 'Dados salvos com sucesso!'}), 200
    except Exception as e:
        return jsonify({'message': 'Erro ao salvar os dados!'}), 500


# Rota para gerar um gráfico
def plot_graph(data):
    plt.figure(figsize=(10, 6))
    labels = []
    values = []

    def process_data(data, parent_key=''):
        for key, value in data.items():
            if isinstance(value, dict):
                process_data(value, f"{parent_key}{key} - ")
            elif isinstance(value, (int, float)):
                labels.append(f"{parent_key}{key}")  
                values.append(value)
            elif isinstance(value, str):
                labels.append(f"{parent_key}{key}")  
                values.append(0)  # Definindo como zero para fins de gráfico

    process_data(data['content'])

    # Gerando o gráfico
    bar_positions = np.arange(len(labels))
    plt.bar(bar_positions, values, color='green', alpha=0.7)

    # Adiciona linhas tracejadas ao fundo do gráfico
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Adiciona valores acima das barras
    for i, v in enumerate(values):
        plt.text(i, v + 5, str(v), ha='center', fontsize=10)

    plt.xticks(bar_positions, labels, rotation=90)
    plt.ylabel('Valores')
    plt.title('Gráfico Dinâmico')
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    plt.close()
    buffer.seek(0)

    img_str = base64.b64encode(buffer.read()).decode('utf-8')
    return img_str


@app.route('/generate_graph', methods=['POST'])
def generate_graph():
    json_data = request.json

    if not json_data or 'content' not in json_data:
        return jsonify({'error': 'Invalid JSON format.'}), 400

    # Chama a função para gerar o gráfico
    img_base64 = plot_graph(json_data)

    return jsonify({'image': img_base64})



if __name__ == '__main__':
    # Obter a porta designada pelo Railway ou usar a porta 5000 para desenvolvimento local
    port = int(os.environ.get("PORT", 5000))
    # Executar a aplicação Flask
    app.run(host='0.0.0.0', port=port)