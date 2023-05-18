import time
import threading
from flask import Flask, jsonify, request, render_template

class Servidor_Leilao(object):
    def __init__(self):
        self.clientes = {}
        self.produtos = []
        self.lances = {}
        self.thread_verificacao = None
    
    def start_verification_thread(self):
        if self.thread_verificacao is None or not self.thread_verificacao.is_alive():
            self.thread_verificacao = threading.Thread(target=self.esgotar_leiloes)
            self.thread_verificacao.start()

    def registrar_cliente(self, nome_cliente, referenciaCliente):
        self.clientes[referenciaCliente] = nome_cliente
        print(f"Novo cliente registrado: {nome_cliente}")

    def registrar_produto(self, codigo, nome, descricao, preco_inicial, tempo_final, nome_cliente):
        # Calcula o tempo limite do leilão
        tempo_final_segundos = tempo_final * 1 #3600
        prazo_final = time.time() + tempo_final_segundos 

        produto = {
            "codigo": codigo,
            "nome": nome,
            "descricao": descricao,
            "preco_inicial": preco_inicial,
            "preco_atual": preco_inicial, # Será atualizado quando lances forem feitos
            "prazo_final": prazo_final,
            "tempo_restante": prazo_final - time.time(),  # Calcular o tempo restante em segundos
            "nome_cliente": nome_cliente
        }
        self.produtos.append(produto)
        
        print(f"Produto '{nome}' registrado por '{nome_cliente}' com prazo final de {tempo_final} horas e preço inicial de R${preco_inicial:.2f}") 

    # Retorna todos os produtos registrados:
    def obter_produtos(self):
        if not self.produtos:
            return "Nenhum produto cadastrado"
        
        return self.produtos
    
    def fazer_lance(self, codigo, lance, nome_cliente):
        # Verifica se o lance é maior que os anteriores:
        if codigo in self.lances:
            if lance <= self.lances[codigo]["lance"]:
                print(f"Lance de {nome_cliente} não supera lance anterior no produto {codigo}.")
                return False

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

        print(f"Lance de {nome_cliente} registrado no produto {codigo} com valor R${lance:.2f}")
        return True

    # Calcula o tempo restante dos leilões:
    def esgotar_leiloes(self):
        while True:
            agora = time.time()
            for produto in self.produtos:
                tempo_restante = produto['prazo_final'] - agora
                if tempo_restante <= 0:
                    # Deleta:
                    codigo = produto['codigo']
                    nome = produto['nome']
                    self.lances.pop(codigo, None)
                    self.produtos.remove(produto)
                    print(f"Lances do produto {codigo} expirados.")
                else:
                    print(f"Tempo restante para o produto {produto['codigo']}: {tempo_restante:.2f} segundos")
            time.sleep(10) #Tempo entre as verificações

app = Flask(__name__)
servidor = Servidor_Leilao()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/clientes', methods=['POST'])
def registrar_cliente():
    data = request.get_json()
    nome_cliente = data['nome_cliente']
    referencia_cliente = data['referencia_cliente']
    servidor.registrar_cliente(nome_cliente, referencia_cliente)
    return jsonify({'message': 'Cliente registrado com sucesso'})

@app.route('/produtos', methods=['POST'])
def registrar_produto():
    data = request.get_json()
    codigo = data['codigo']
    nome = data['nome']
    descricao = data['descricao']
    preco_inicial = float(data['preco_inicial'])
    tempo_final = float(data['tempo_final'])
    nome_cliente = data['nome_cliente']
    servidor.registrar_produto(codigo, nome, descricao, preco_inicial, tempo_final, nome_cliente)
    servidor.start_verification_thread()
    return jsonify({'message': 'Produto registrado com sucesso'})

@app.route('/produtos', methods=['GET'])
def obter_produtos():
    produtos = servidor.obter_produtos()
    return jsonify({'produtos': produtos})

@app.route('/lances', methods=['POST'])
def fazer_lance():
    data = request.get_json()
    codigo = data['codigo']
    lance = data['lance']
    nome_cliente = data['nome_cliente']
    sucesso = servidor.fazer_lance(codigo, lance, nome_cliente)
    return jsonify({'success': sucesso})
    
if __name__ == '__main__':
    app.run(debug=True)
