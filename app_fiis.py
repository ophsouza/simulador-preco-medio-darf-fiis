import os
import sys
import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from collections import defaultdict
from ttkthemes import ThemedTk
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from openpyxl import Workbook


class AppPrecoMedioFIIs:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Preço Médio e DARF - FIIs")
        self.root.geometry("900x750")


        self.tema_escuro = True
        self.aplicar_tema("equilux")


        self.frame_tema = ttk.Frame(root)
        self.frame_tema.pack(fill="x", padx=10, pady=5)


        self.toggle_tema_var = tk.BooleanVar(value=self.tema_escuro)
        self.chk_tema = ttk.Checkbutton(
            self.frame_tema, text="Modo Escuro",
            variable=self.toggle_tema_var,
            command=self.alternar_tema
        )
        self.chk_tema.pack(anchor="e")


        self.conn = sqlite3.connect("fiis.db")
        self.cursor = self.conn.cursor()
        self.criar_tabelas()


        self.compras = []
        self.vendas = []
        self.carregar_compras_salvas()
        self.carregar_vendas_salvas()


        self.aba = ttk.Notebook(root)
        self.aba.pack(fill="both", expand=True)


        self.frame_compras = ttk.Frame(self.aba)
        self.frame_vendas = ttk.Frame(self.aba)
        self.frame_relatorios = ttk.Frame(self.aba)


        self.aba.add(self.frame_compras, text="Compras")
        self.aba.add(self.frame_vendas, text="Vendas")
        self.aba.add(self.frame_relatorios, text="Relatórios")


        self.criar_interface_compras()
        self.criar_interface_vendas()
        self.criar_interface_relatorios()


    def aplicar_tema(self, nome_tema):
        self.root.set_theme(nome_tema)
        self.tema_atual = nome_tema


    def alternar_tema(self):
        if self.toggle_tema_var.get():
            self.aplicar_tema("equilux")
        else:
            self.aplicar_tema("arc")


    def criar_tabelas(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS compras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fii TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco REAL NOT NULL,
                data TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fii TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco REAL NOT NULL,
                data TEXT NOT NULL
            )
        """)
        self.conn.commit()


    def carregar_compras_salvas(self):
        self.cursor.execute("SELECT id, fii, quantidade, preco, data FROM compras ORDER BY data")
        self.compras.clear()
        for row in self.cursor.fetchall():
            self.compras.append(row)


    def carregar_vendas_salvas(self):
        self.cursor.execute("SELECT id, fii, quantidade, preco, data FROM vendas ORDER BY data")
        self.vendas.clear()
        for row in self.cursor.fetchall():
            self.vendas.append(row)


    # ----------- ABA COMPRAS -----------
    def criar_interface_compras(self):
        frame = self.frame_compras


        entrada = ttk.LabelFrame(frame, text="Adicionar / Editar Compra", padding=10)
        entrada.pack(padx=10, pady=10, fill="x")


        ttk.Label(entrada, text="FII:").grid(row=0, column=0, sticky="e")
        self.fii_entry = ttk.Entry(entrada, width=15)
        self.fii_entry.grid(row=0, column=1, padx=5, pady=2)


        ttk.Label(entrada, text="Quantidade:").grid(row=1, column=0, sticky="e")
        self.qtd_entry = ttk.Entry(entrada, width=15)
        self.qtd_entry.grid(row=1, column=1, padx=5, pady=2)


        ttk.Label(entrada, text="Preço unitário (R$):").grid(row=2, column=0, sticky="e")
        self.preco_entry = ttk.Entry(entrada, width=15)
        self.preco_entry.grid(row=2, column=1, padx=5, pady=2)


        ttk.Label(entrada, text="Data (DD-MM-AAAA):").grid(row=3, column=0, sticky="e")
        self.data_compra_entry = ttk.Entry(entrada, width=15)
        self.data_compra_entry.grid(row=3, column=1, padx=5, pady=2)
        self.data_compra_entry.insert(0, datetime.date.today().isoformat())


        self.id_editando = None


        self.btn_adicionar_compras = ttk.Button(entrada, text="Adicionar Compra", command=self.adicionar_ou_editar_compra)
        self.btn_adicionar_compras.grid(row=4, column=0, columnspan=2, pady=10)


        lista_frame = ttk.Frame(frame)
        lista_frame.pack(padx=10, pady=5, fill="both", expand=True)


        self.lista_compras = tk.Listbox(lista_frame, height=10, font=("Segoe UI", 10))
        self.lista_compras.pack(side=tk.LEFT, fill="both", expand=True)


        scrollbar = ttk.Scrollbar(lista_frame, orient="vertical", command=self.lista_compras.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.lista_compras.config(yscrollcommand=scrollbar.set)


        self.lista_compras.bind("<Double-Button-1>", self.editar_compra_selecionada)


        ttk.Button(frame, text="Remover Compra Selecionada", command=self.remover_compra).pack(pady=5)


        self.atualizar_lista_compras()


    def atualizar_lista_compras(self):
        self.lista_compras.delete(0, tk.END)
        for (id_, fii, qtd, preco, data) in self.compras:
            self.lista_compras.insert(tk.END, f"{data} - {fii}: {qtd} cotas a R$ {preco:.2f}")


    def adicionar_ou_editar_compra(self):
        fii = self.fii_entry.get().strip().upper()
        try:
            qtd = int(self.qtd_entry.get())
            preco = float(self.preco_entry.get())
            data = self.data_compra_entry.get().strip()
            datetime.datetime.strptime(data, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser inteiro, preço número válido e data no formato AAAA-MM-DD.")
            return
        if not fii:
            messagebox.showerror("Erro", "Informe o nome do FII.")
            return
        if qtd <= 0 or preco <= 0:
            messagebox.showerror("Erro", "Quantidade e preço devem ser maiores que zero.")
            return


        if self.id_editando is None:
            # Inserir nova
            self.cursor.execute("INSERT INTO compras (fii, quantidade, preco, data) VALUES (?, ?, ?, ?)", (fii, qtd, preco, data))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Compra adicionada com sucesso.")
        else:
            # Atualizar existente
            self.cursor.execute("UPDATE compras SET fii=?, quantidade=?, preco=?, data=? WHERE id=?", (fii, qtd, preco, data, self.id_editando))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Compra editada com sucesso.")
            self.id_editando = None
            self.btn_adicionar_compras.config(text="Adicionar Compra")


        self.limpar_campos_compra()
        self.carregar_compras_salvas()
        self.atualizar_lista_compras()


    def editar_compra_selecionada(self, event):
        selecionado = self.lista_compras.curselection()
        if not selecionado:
            return
        idx = selecionado[0]
        id_, fii, qtd, preco, data = self.compras[idx]
        self.id_editando = id_
        self.fii_entry.delete(0, tk.END)
        self.fii_entry.insert(0, fii)
        self.qtd_entry.delete(0, tk.END)
        self.qtd_entry.insert(0, str(qtd))
        self.preco_entry.delete(0, tk.END)
        self.preco_entry.insert(0, str(preco))
        self.data_compra_entry.delete(0, tk.END)
        self.data_compra_entry.insert(0, data)
        self.btn_adicionar_compras.config(text="Salvar Alterações")


    def remover_compra(self):
        selecionado = self.lista_compras.curselection()
        if not selecionado:
            messagebox.showinfo("Remover", "Selecione uma compra para remover.")
            return
        idx = selecionado[0]
        id_ = self.compras[idx][0]
        self.cursor.execute("DELETE FROM compras WHERE id=?", (id_,))
        self.conn.commit()
        self.carregar_compras_salvas()
        self.atualizar_lista_compras()
        messagebox.showinfo("Remover", "Compra removida com sucesso.")


    def limpar_campos_compra(self):
        self.fii_entry.delete(0, tk.END)
        self.qtd_entry.delete(0, tk.END)
        self.preco_entry.delete(0, tk.END)
        self.data_compra_entry.delete(0, tk.END)
        self.data_compra_entry.insert(0, datetime.date.today().isoformat())
        self.btn_adicionar_compras.config(text="Adicionar Compra")
        self.id_editando = None


    # ----------- ABA VENDAS -----------
    def criar_interface_vendas(self):
        frame = self.frame_vendas


        entrada = ttk.LabelFrame(frame, text="Adicionar / Editar Venda", padding=10)
        entrada.pack(padx=10, pady=10, fill="x")


        ttk.Label(entrada, text="FII:").grid(row=0, column=0, sticky="e")
        self.fii_venda_entry = ttk.Entry(entrada, width=15)
        self.fii_venda_entry.grid(row=0, column=1, padx=5, pady=2)


        ttk.Label(entrada, text="Quantidade:").grid(row=1, column=0, sticky="e")
        self.qtd_venda_entry = ttk.Entry(entrada, width=15)
        self.qtd_venda_entry.grid(row=1, column=1, padx=5, pady=2)


        ttk.Label(entrada, text="Preço unitário (R$):").grid(row=2, column=0, sticky="e")
        self.preco_venda_entry = ttk.Entry(entrada, width=15)
        self.preco_venda_entry.grid(row=2, column=1, padx=5, pady=2)


        ttk.Label(entrada, text="Data (DD-MM-AAAA):").grid(row=3, column=0, sticky="e")
        self.data_venda_entry = ttk.Entry(entrada, width=15)
        self.data_venda_entry.grid(row=3, column=1, padx=5, pady=2)
        self.data_venda_entry.insert(0, datetime.date.today().isoformat())


        self.id_editando_venda = None


        self.btn_adicionar_vendas = ttk.Button(entrada, text="Adicionar Venda", command=self.adicionar_ou_editar_venda)
        self.btn_adicionar_vendas.grid(row=4, column=0, columnspan=2, pady=10)


        lista_frame = ttk.Frame(frame)
        lista_frame.pack(padx=10, pady=5, fill="both", expand=True)


        self.lista_vendas = tk.Listbox(lista_frame, height=10, font=("Segoe UI", 10))
        self.lista_vendas.pack(side=tk.LEFT, fill="both", expand=True)


        scrollbar = ttk.Scrollbar(lista_frame, orient="vertical", command=self.lista_vendas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        self.lista_vendas.config(yscrollcommand=scrollbar.set)


        self.lista_vendas.bind("<Double-Button-1>", self.editar_venda_selecionada)


        ttk.Button(frame, text="Remover Venda Selecionada", command=self.remover_venda).pack(pady=5)


        self.atualizar_lista_vendas()


    def atualizar_lista_vendas(self):
        self.lista_vendas.delete(0, tk.END)
        for (id_, fii, qtd, preco, data) in self.vendas:
            self.lista_vendas.insert(tk.END, f"{data} - {fii}: {qtd} cotas a R$ {preco:.2f}")


    def adicionar_ou_editar_venda(self):
        fii = self.fii_venda_entry.get().strip().upper()
        try:
            qtd = int(self.qtd_venda_entry.get())
            preco = float(self.preco_venda_entry.get())
            data = self.data_venda_entry.get().strip()
            datetime.datetime.strptime(data, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser inteiro, preço número válido e data no formato AAAA-MM-DD.")
            return
        if not fii:
            messagebox.showerror("Erro", "Informe o nome do FII.")
            return
        if qtd <= 0 or preco <= 0:
            messagebox.showerror("Erro", "Quantidade e preço devem ser maiores que zero.")
            return


        if self.id_editando_venda is None:
            self.cursor.execute("INSERT INTO vendas (fii, quantidade, preco, data) VALUES (?, ?, ?, ?)", (fii, qtd, preco, data))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Venda adicionada com sucesso.")
        else:
            self.cursor.execute("UPDATE vendas SET fii=?, quantidade=?, preco=?, data=? WHERE id=?", (fii, qtd, preco, data, self.id_editando_venda))
            self.conn.commit()
            messagebox.showinfo("Sucesso", "Venda editada com sucesso.")
            self.id_editando_venda = None
            self.btn_adicionar_vendas.config(text="Adicionar Venda")


        self.limpar_campos_venda()
        self.carregar_vendas_salvas()
        self.atualizar_lista_vendas()


    def editar_venda_selecionada(self, event):
        selecionado = self.lista_vendas.curselection()
        if not selecionado:
            return
        idx = selecionado[0]
        id_, fii, qtd, preco, data = self.vendas[idx]
        self.id_editando_venda = id_
        self.fii_venda_entry.delete(0, tk.END)
        self.fii_venda_entry.insert(0, fii)
        self.qtd_venda_entry.delete(0, tk.END)
        self.qtd_venda_entry.insert(0, str(qtd))
        self.preco_venda_entry.delete(0, tk.END)
        self.preco_venda_entry.insert(0, str(preco))
        self.data_venda_entry.delete(0, tk.END)
        self.data_venda_entry.insert(0, data)
        self.btn_adicionar_vendas.config(text="Salvar Alterações")


    def remover_venda(self):
        selecionado = self.lista_vendas.curselection()
        if not selecionado:
            messagebox.showinfo("Remover", "Selecione uma venda para remover.")
            return
        idx = selecionado[0]
        id_ = self.vendas[idx][0]
        self.cursor.execute("DELETE FROM vendas WHERE id=?", (id_,))
        self.conn.commit()
        self.carregar_vendas_salvas()
        self.atualizar_lista_vendas()
        messagebox.showinfo("Remover", "Venda removida com sucesso.")


    def limpar_campos_venda(self):
        self.fii_venda_entry.delete(0, tk.END)
        self.qtd_venda_entry.delete(0, tk.END)
        self.preco_venda_entry.delete(0, tk.END)
        self.data_venda_entry.delete(0, tk.END)
        self.data_venda_entry.insert(0, datetime.date.today().isoformat())
        self.btn_adicionar_vendas.config(text="Adicionar Venda")
        self.id_editando_venda = None


    # ----------- ABA RELATÓRIOS -----------
    def criar_interface_relatorios(self):
        frame = self.frame_relatorios


        ttk.Label(frame, text="Relatório Mensal para IR (vendas agrupadas por mês):", font=("Segoe UI", 12, "bold")).pack(pady=10)


        self.tree_relatorio = ttk.Treeview(frame, columns=("mes_ano", "fii", "qtd_vendida", "preco_medio_compra", "lucro_prejuizo"), show="headings")
        self.tree_relatorio.heading("mes_ano", text="Mês/Ano")
        self.tree_relatorio.heading("fii", text="FII")
        self.tree_relatorio.heading("qtd_vendida", text="Qtd. Vendida")
        self.tree_relatorio.heading("preco_medio_compra", text="Preço Médio Compra (R$)")
        self.tree_relatorio.heading("lucro_prejuizo", text="Lucro/Prejuízo (R$)")
        self.tree_relatorio.pack(fill="both", expand=True, padx=10, pady=5)


        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)


        ttk.Button(btn_frame, text="Gerar Relatório Mensal IR", command=self.gerar_relatorio_ir).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Exportar Relatório para Excel", command=self.exportar_excel_relatorio).pack(side="left", padx=5)


        ttk.Label(frame, text="Gráfico de Evolução de Cotas por FII:", font=("Segoe UI", 12, "bold")).pack(pady=10)
        self.fig, self.ax = plt.subplots(figsize=(7,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


        ttk.Button(frame, text="Gerar Gráfico Evolução", command=self.gerar_grafico_evolucao).pack(pady=5)


    def gerar_relatorio_ir(self):
        # Limpar árvore
        for item in self.tree_relatorio.get_children():
            self.tree_relatorio.delete(item)


        # Construir relatório mensal agrupado por fii e mes/ano, calcular lucro/prejuízo
        # Passo 1: Calcular preço médio compra por FII até data da venda (peso por qtd)
        compras_por_fii = defaultdict(list)
        for _, fii, qtd, preco, data in self.compras:
            compras_por_fii[fii].append((data, qtd, preco))


        # Função para preço médio até data
        def preco_medio_ate(fii, data_limite):
            compras = compras_por_fii.get(fii, [])
            total_qtd = 0
            total_valor = 0
            for d, q, p in compras:
                if d <= data_limite:
                    total_qtd += q
                    total_valor += q * p
            return (total_valor / total_qtd) if total_qtd > 0 else 0


        # Agrupar vendas por mes/ano e fii
        vendas_agrupadas = defaultdict(lambda: {"qtd": 0, "preco_venda_medio": 0, "total_venda": 0, "lucro": 0})
        for _, fii, qtd, preco, data in self.vendas:
            mes_ano = data[:7]
            key = (mes_ano, fii)
            item = vendas_agrupadas[key]
            # Média ponderada preço venda
            total_venda_anterior = item["total_venda"]
            qtd_anterior = item["qtd"]
            item["qtd"] += qtd
            item["total_venda"] += qtd * preco
            item["preco_venda_medio"] = item["total_venda"] / item["qtd"]
            pm_compra = preco_medio_ate(fii, data)
            lucro = qtd * (preco - pm_compra)
            item["lucro"] += lucro


        # Inserir no treeview
        for (mes_ano, fii), dados in sorted(vendas_agrupadas.items()):
            self.tree_relatorio.insert("", tk.END, values=(
                mes_ano,
                fii,
                dados["qtd"],
                f"{preco_medio_ate(fii, mes_ano + '-31'):.2f}",
                f"{dados['lucro']:.2f}",
            ))


    def exportar_excel_relatorio(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("Todos arquivos", "*.*")],
            title="Salvar relatório como"
        )
        if not path:
            return


        wb = Workbook()
        ws = wb.active
        ws.title = "Relatório IR Mensal"


        # Cabeçalho
        ws.append(["Mês/Ano", "FII", "Qtd. Vendida", "Preço Médio Compra (R$)", "Lucro/Prejuízo (R$)"])


        # Inserir dados do treeview
        for item in self.tree_relatorio.get_children():
            ws.append(self.tree_relatorio.item(item)["values"])


        try:
            wb.save(path)
            messagebox.showinfo("Exportar", f"Relatório exportado com sucesso em:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar arquivo:\n{e}")


    def gerar_grafico_evolucao(self):
        self.ax.clear()


        # Evolução de cotas acumuladas por FII ao longo do tempo
        # Considerar compras + vendas (vendas subtraem)
        datas = set()
        fii_set = set()
        for _, fii, _, _, data in self.compras + self.vendas:
            datas.add(data)
            fii_set.add(fii)
        datas = sorted(datas)
        fii_list = sorted(fii_set)


        # Construir série temporal acumulada
        acumulado = {fii: [] for fii in fii_list}
        qtd_total = {fii: 0 for fii in fii_list}
        idx_data = {d: i for i, d in enumerate(datas)}


        # Para cada data, somar compras e vendas
        delta_por_fii_data = {fii: [0]*len(datas) for fii in fii_list}
        for _, fii, qtd, _, data in self.compras:
            delta_por_fii_data[fii][idx_data[data]] += qtd
        for _, fii, qtd, _, data in self.vendas:
            delta_por_fii_data[fii][idx_data[data]] -= qtd


        # Calcular acumulado por data
        for fii in fii_list:
            soma = 0
            for v in delta_por_fii_data[fii]:
                soma += v
                acumulado[fii].append(soma)


        for fii in fii_list:
            self.ax.plot(datas, acumulado[fii], label=fii)


        self.ax.set_title("Evolução de Cotas Acumuladas por FII")
        self.ax.set_xlabel("Data")
        self.ax.set_ylabel("Quantidade de Cotas")
        self.ax.legend()
        self.ax.grid(True)
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha="right")


        self.fig.tight_layout()
        self.canvas.draw()



if __name__ == "__main__":
    root = ThemedTk(theme="equilux")
    app = AppPrecoMedioFIIs(root)
    root.mainloop()

