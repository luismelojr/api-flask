from flask import Flask, request, jsonify, send_file
import csv
import os
from datetime import datetime

app = Flask(__name__)

def get_csv_filename():
  today = datetime.now().strftime('%d-%m-%Y')
  return f'dados_{today}.csv'

@app.route('/webhook', methods=['POST'])
def webhook():
  data = request.json
  contact = data['data']['key']['remoteJid'] if 'data' in data and 'key' in data['data'] and 'remoteJid' in data['data']['key'] else None
  name = data['data']['pushName'] if 'data' in data and 'pushName' in data['data'] else None
  message = data['data']['message']['conversation'] if 'data' in data and 'message' in data['data'] and 'conversation' in data['data']['message'] else None
  date = data['date_time'] if 'date_time' in data else None
  dateObj = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
  formatedDate = dateObj.strftime('%d/%m/%Y %H:%M:%S')

  if "s.whatsapp.net" not in contact:
    return jsonify({'message': 'Contato não é um número de WhatsApp!', 'data': data}), 400
  
  csv_file = get_csv_filename()

  try:
    if not os.path.exists(csv_file):
      with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Contato', 'Nome', 'Mensagem', 'Data'])

    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
      writer = csv.writer(file)
      writer.writerow([contact, name, message, formatedDate])

    return jsonify({'message': 'Dados salvos com sucesso!', 'data': data}), 200
  except Exception as e:
    return jsonify({'message': 'Erro ao salvar os dados!', 'data': data}), 500

  
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

  


if __name__ == '__main__':
  app.run(debug=True, port=5000)