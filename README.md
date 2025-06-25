
# 📈 Simulador de Preço Médio e DARF - FIIs

Este é um aplicativo desktop feito em Python com interface gráfica (Tkinter + ttk themes), voltado para controle de **compras e vendas de FIIs (Fundos Imobiliários)**, cálculo de **preço médio**, **apuração de lucro/prejuízo** e geração de **relatórios mensais para fins de IR (Imposto de Renda)**.

---

## 🧰 Tecnologias Utilizadas

- Python 3.x
- Tkinter + TTK Themes
- SQLite3 (banco de dados local)
- Matplotlib (gráficos)
- Openpyxl (exportação para Excel)

---

## 🖥️ Funcionalidades

### ✅ Compras e Vendas
- Registro e edição de operações (compra e venda) de FIIs.
- Armazenamento local em banco de dados SQLite.
- Lista de operações ordenadas por data.

### 📊 Relatórios
- Relatório mensal de vendas com:
  - Quantidade vendida
  - Preço médio de compra
  - Lucro ou prejuízo
- Exportação para planilha Excel (`.xlsx`)
- Gráfico de evolução de cotas por FII ao longo do tempo

### 🌙 Modo Escuro/Claro
- Alternância entre temas com suporte ao tema escuro.

---

## 📸 Imagens do App 
<img width="493" alt="Captura de Tela 2025-06-25 às 15 34 23" src="https://github.com/user-attachments/assets/4a4f43bc-7028-4639-915d-106222d030f0" />
<img width="936" alt="Captura de Tela 2025-06-25 às 15 35 08" src="https://github.com/user-attachments/assets/07de15ed-adce-4add-820d-2e05de21ce6a" />

---

## 🚀 Como Executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/ophsouza/simulador-preco-medio-fiis.git
   cd simulador-preco-medio-fiis
   ```

2. Instale as dependências:
   ```bash
   pip install matplotlib openpyxl ttkthemes
   ```

3. Execute o app:
   ```bash
   python app.py
   ```

---

## 📁 Estrutura de Arquivos

```
📦 simulador-preco-medio-fiis
├── fiis.db                # Banco de dados SQLite
├── app.py                 # Código principal do aplicativo
├── README.md              # Este arquivo
```

---

## 📌 Observações

- A base de dados (`fiis.db`) é criada automaticamente no primeiro uso.
- É possível editar/remover registros com duplo clique ou por botão.

---

## 📃 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais detalhes.

---

## 👨‍💻 Autor

Desenvolvido por [Paulo Henrique Carvalho Souza](https://github.com/ophsouza)
