import functions_framework
from google.cloud import firestore
import json
from datetime import datetime,timezone

# Inicializar o cliente do Firestore
db = firestore.Client()

@functions_framework.http
def insert_to_firestore(request):
    """HTTP Cloud Function para inserir dados no Firestore.
    Args:
        request (flask.Request): O objeto de requisição.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        Uma resposta de sucesso ou erro.
    """
    # Adicionar cabeçalhos CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    if request.method == 'OPTIONS':
        # Handle preflight requests
        return ('', 204, headers)

    request_json = request.get_json(silent=True)

    if request.method == 'POST' and request_json:
        try:
            # Extrair dados do JSON
            prompt_data = request_json.get('prompt_data')
            user_info = request_json.get('user_info')
            timestamp = datetime.utcnow().isoformat()

            if not prompt_data or not user_info:
                return ('Dados inválidos', 400, headers)

            # Construir o caminho do documento
            user_email = user_info.get('email')
            if not user_email:
                return ('Email do usuário não fornecido', 400, headers)

            timestamp = datetime.now(timezone.utc).isoformat()
            prompt_data['timestamp'] = timestamp

            doc_path = f'users/{user_email}/interactions/{timestamp}'

            # Inserir dados no Firestore
            db.document(doc_path).set({
                'prompt_data': prompt_data,
                'user_info': user_info
            })

            return ('Documento inserido com sucesso', 200, headers)
        except Exception as e:
            return ('Erro ao inserir documento: {}'.format(str(e)), 500, headers)
    else:
        return ('Método não permitido ou dados inválidos', 405, headers)