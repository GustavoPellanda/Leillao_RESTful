listarProdutos();

function registerClient() {
  fetch('/clientes', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      nome_cliente: 'John Doe',
      referencia_cliente: 'client1'
    }),
  })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.log(error));
}

function registrarProduto() {
    // Recebe as informações dos inputs:
    const codigo = document.getElementById('Codigo_Produto').value;
    const nome = document.getElementById('Nome_Produto').value;
    const descricao = document.getElementById('Descricao_Produto').value;
    const preco = document.getElementById('Preco_Produto').value;
    const tempo = document.getElementById('Tempo_Produto').value;
  
    // Cria o objeto:
    const infoProduto = {
      codigo: codigo,
      nome: nome,
      descricao: descricao,
      preco_inicial: preco,
      tempo_final: tempo,
      nome_cliente: "Gustavo"
    };
    
    // Envia para o servidor:
    fetch('/produtos', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(infoProduto),
    })
      // Resposta do servidor:
      .then(response => response.json())
      .then(data => console.log(data))
      .catch(error => console.log(error));
  }

// Chamada de registrarProduto:
document.getElementById('enviar_produto').addEventListener('click', function(event) {
  event.preventDefault();
  registrarProduto();
});

function listarProdutos() {
  fetch('/produtos', {
    method: 'GET',
  })
    .then(response => response.json())
    .then(data => {
      // Extrai o array de produtos da resposta json:
      const produtos = data.produtos; 
      
      // Encontra a tabela no html:
      const tableBody = document.querySelector('.vizualizar_produtos table tbody');
      
      // Limpa a tabela preenchida anteriormente:
      tableBody.innerHTML = '';

      // Insere os produtos na tabela:
      produtos.forEach(produto => {
        const { nome, preco_atual, codigo } = produto;

        // Cria as células:
        const row = document.createElement('tr');
        const nomeCell = document.createElement('td');
        nomeCell.textContent = nome;
        const precoCell = document.createElement('td');
        precoCell.textContent = `R$ ${preco_atual.toFixed(2)}`;
        const codigoCell = document.createElement('td');
        codigoCell.textContent = codigo;

        // Insere as células em uma linha:
        row.appendChild(nomeCell);
        row.appendChild(precoCell);
        row.appendChild(codigoCell);

        // Insere as linhas na tabela:
        tableBody.appendChild(row);
      });
    })
    .catch(error => console.log(error));
}

// Chamada de listarProdutos:
function atualizarTabelaProdutos() {
  listarProdutos();
}
setInterval(atualizarTabelaProdutos, 5000);

function fazerLance() {
  // Recebe as informações dos inputs:
  const codigo = document.getElementById('Codigo_Produto').value;
  const lance = document.getElementById('Lance_Produto').value;

  // Cria o objeto:
  const infoLance = {
    codigo: codigo,
    lance: lance,
    nome_cliente: 'Gustavo',
  };
  
  // Envia para o servidor:
  fetch('/lances', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(infoLance)
  })
    // Resposta do servidor:
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.log(error));
}

// Chamada de fazerLance:
document.getElementById('enviar_lance').addEventListener('click', function(event) {
  event.preventDefault();
  fazerLance();
});

function exibeNotificacoes(notificacao) {
  const notificacoesDiv = document.querySelector('.notificacoes');

  // Cria um novo elemento notificação:
  const notificacaoDiv = document.createElement('div');
  notificacaoDiv.classList.add('notificacao');

  // Cria um elemento <p> com a notificação dentro:
  const p = document.createElement('p');
  p.textContent = notificacao;

  // Insere o elemento <p> na <div class="notificacao">:
  notificacaoDiv.appendChild(p);

  // Insere a <div class="notificacao"> na <div class="notificacoes">:
  notificacoesDiv.appendChild(notificacaoDiv);
}

const teste = "Isso é uma notificação de teste";
exibeNotificacoes(teste);
