import time
import threading
from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

class Servidor_Leilao(object):
    def __init__(self):
        self.produtos = []
        self.lances = {}
        self.thread_verificacao = None

    def inicia_thread_esgotar(self):
        if self.thread_verificacao is None or not self.thread_verificacao.is_alive():
            self.thread_verificacao = threading.Thread(target=self.esgotar_leiloes)
            self.thread_verificacao.start()
    
    def registrar_produto(self, codigo, nome, descricao, preco_inicial, tempo_final, nome_cliente):
        # Confere se o código já foi registrado:
        for produto in self.produtos:
            if produto["codigo"] == codigo:
                return "CODIGO_JA_EXISTENTE"
        
        # Calcula o tempo limite do leilão:
        tempo_final_segundos = tempo_final * 1 #3600 para horas
        prazo_final = time.time() + tempo_final_segundos 

        produto = {
            "codigo": codigo,
            "nome": nome,
            "descricao": descricao,
            "preco_inicial": preco_inicial,
            "preco_atual": preco_inicial, # Será atualizado quando lances forem feitos
            "prazo_final": prazo_final,
            "tempo_restante": prazo_final - time.time(), # Calcula o tempo restante em segundos
            "nome_cliente": nome_cliente
        }
        self.produtos.append(produto)
        
        hora = datetime.now().strftime("%H:%M:%S")
        info_notificacao = {
            "message": f"{hora} | Novo produto registrado por {nome_cliente}: {nome}. Preço Inicial: R${preco_inicial:.2f}"
        }
        socketio.emit('notification', info_notificacao)
        
        print(f"Produto '{nome}' registrado por '{nome_cliente}' com prazo final de {tempo_final} horas e preço inicial de R${preco_inicial:.2f}") 
        return "PRODUTO_ACEITO"

    # Retorna todos os produtos registrados:
    def obter_produtos(self):
        if not self.produtos:
            return "Nenhum produto cadastrado"
        
        return self.produtos
    
    def fazer_lance(self, codigo, lance, nome_cliente):
        # Verifica se o código do produto está registrado:
        if codigo not in [produto["codigo"] for produto in self.produtos]:
            print(f"Produto {codigo} não encontrado.")
            return "CODIGO_INEXISTENTE"
    
        # Verifica se o lance é maior que os anteriores:
        if codigo in self.lances:
            if lance <= self.lances[codigo]["lance"]:
                print(f"Lance de {nome_cliente} não supera lance anterior no produto {codigo}.")
                return "LANCE_REJEITADO"

        # Atualiza o registro de lances:
        lance_registro = {
            "codigo_produto": codigo,
            "lance": lance,
            "nome_cliente": nome_cliente
        }
        self.lances[codigo] = lance_registro

        # Atualiza o preço atual do produto:
        for produto in self.produtos:
            if produto["codigo"] == codigo:
                produto["preco_atual"] = lance
                break
        
        hora = datetime.now().strftime("%H:%M:%S")
        info_notificacao = {
            "message": f"{hora} | Novo lance registrado no produto {codigo} por {nome_cliente}. Valor do Lance: R${lance:.2f}"
        }
        socketio.emit('notification', info_notificacao)
        
        print(f"Lance de {nome_cliente} registrado no produto {codigo} com valor R${lance:.2f}")
        return "LANCE_APROVADO"

    # Calcula o tempo restante dos leilões:
    def esgotar_leiloes(self):
        while True:
            agora = time.time()
            for produto in self.produtos:
                tempo_restante = produto['prazo_final'] - agora
                if tempo_restante <= 0:
                    codigo = produto['codigo']
                    preco_final = produto["preco_atual"]
                    
                    self.lances.pop(codigo, None) # Deleta os lances
                    self.produtos.remove(produto) # Deleta o produto
                    
                    print(f"Lances do produto {codigo} expirados.")
                    
                    hora = datetime.now().strftime("%H:%M:%S")
                    info_notificacao = {
                        "message": f"{hora} | Leilão do produto {codigo} finalizado. Preço Final: R${preco_final:.2f}"
                    }
                    socketio.emit('notification', info_notificacao)
                else:
                    print(f"Tempo restante para o produto {produto['codigo']}: {tempo_restante:.2f} segundos")
            time.sleep(10) #Tempo entre as verificações

servidor = Servidor_Leilao()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/produtos', methods=['POST'])
def registrar_produto():
    data = request.get_json()
    
    codigo = int(data['codigo'])
    nome = data['nome']
    descricao = data['descricao']
    preco_inicial = float(data['preco_inicial'])
    tempo_final = float(data['tempo_final'])
    nome_cliente = data['nome_cliente']
    
    servidor.inicia_thread_esgotar()
    
    resposta = servidor.registrar_produto(codigo, nome, descricao, preco_inicial, tempo_final, nome_cliente)
    return jsonify({'resposta': resposta})

@app.route('/produtos', methods=['GET'])
def obter_produtos():
    produtos = servidor.obter_produtos()
    return jsonify({'produtos': produtos})

@app.route('/lances', methods=['POST'])
def fazer_lance():
    data = request.get_json()
    codigo = int(data['codigo'])
    lance = float(data['lance'])
    nome_cliente = data['nome_cliente']
    resposta = servidor.fazer_lance(codigo, lance, nome_cliente)
    
    return jsonify({'resposta': resposta})

if __name__ == '__main__':
    socketio.run(app, debug=True)
