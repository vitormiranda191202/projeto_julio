import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, joinedload
from datetime import datetime
import logging

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Banco de dados
DATABASE_URL = "postgresql://neondb_owner:npg_yWMlIa8iB1mH@ep-plain-bonus-adrh7qhm-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ----- MODELOS -----
class FichaProducao(Base):
    __tablename__ = "fichas_producao"
    __table_args__ = {"schema": "eguh_vest"}

    id = Column(Integer, primary_key=True, index=True)
    produto = Column(String(150), nullable=False)
    corte = Column(Integer, nullable=False)
    grade = Column(String(50), nullable=False)
    data = Column(Date, nullable=False)
    qt_rolos = Column(Integer, default=0)
    peso_total = Column(Float, default=0.0)

    itens = relationship("ItemFicha", back_populates="ficha", cascade="all, delete-orphan")

class ItemFicha(Base):
    __tablename__ = "itens_ficha"
    __table_args__ = {"schema": "eguh_vest"}

    id = Column(Integer, primary_key=True, index=True)
    ficha_id = Column(Integer, ForeignKey("eguh_vest.fichas_producao.id", ondelete="CASCADE"))
    cor = Column(String(50), nullable=False)
    g1 = Column(Integer, default=0)
    g2 = Column(Integer, default=0)
    g3 = Column(Integer, default=0)
    qt_rolos = Column(Integer, default=0)
    peso_total = Column(Float, default=0.0)

    ficha = relationship("FichaProducao", back_populates="itens")

class EstoqueRolos(Base):
    __tablename__ = "estoque_rolos"
    __table_args__ = {"schema": "eguh_vest"}

    id = Column(Integer, primary_key=True)
    qt_rolos = Column(Integer, nullable=False)
    peso_total = Column(Float, nullable=False)
    cor = Column(String(50), nullable=False)
    data_entrada = Column(Date, default=datetime.now)

Base.metadata.create_all(engine)

# ----- APLICATIVO -----
class FichaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📋 Sistema de Produção e Estoque")
        self.root.geometry("1300x800")
        self.root.configure(bg="#f0f0f0")

        # Estilo
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, font=("Helvetica", 10))
        self.style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        self.style.configure("TEntry", padding=5)
        self.style.configure("Treeview", rowheight=25, font=("Helvetica", 10))
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        # Abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.ficha_frame = tk.Frame(self.notebook, bg="#f0f0f0")
        self.estoque_frame = tk.Frame(self.notebook, bg="#f0f0f0")

        self.notebook.add(self.ficha_frame, text="📋 Ficha de Produção")
        self.notebook.add(self.estoque_frame, text="📦 Estoque de Rolos")

        self.items = []

        # Ficha
        self.create_ficha_header()
        self.create_items_frame()
        self.create_item_form()
        self.create_ficha_buttons()

        # Estoque
        self.create_estoque_widgets()

    # ----- CABEÇALHO FICHA -----
    def create_ficha_header(self):
        header_frame = tk.LabelFrame(
            self.ficha_frame, text="Dados da Ficha", font=("Helvetica", 12, "bold"),
            bg="#f0f0f0", padx=10, pady=10
        )
        header_frame.pack(fill="x", pady=10)

        tk.Label(header_frame, text="Produto:", bg="#f0f0f0").grid(row=0, column=0, padx=5, sticky="w")
        self.produto_entry = ttk.Entry(header_frame, width=20)
        self.produto_entry.grid(row=0, column=1, padx=5)
        tk.Label(header_frame, text="Corte:", bg="#f0f0f0").grid(row=0, column=2, padx=5, sticky="w")
        self.corte_entry = ttk.Entry(header_frame, width=10)
        self.corte_entry.grid(row=0, column=3, padx=5)
        tk.Label(header_frame, text="Grade:", bg="#f0f0f0").grid(row=0, column=4, padx=5, sticky="w")
        self.grade_entry = ttk.Entry(header_frame, width=10)
        self.grade_entry.grid(row=0, column=5, padx=5)
        tk.Label(header_frame, text="Data (dd/mm/yyyy):", bg="#f0f0f0").grid(row=0, column=6, padx=5, sticky="w")
        self.data_entry = ttk.Entry(header_frame, width=15)
        self.data_entry.grid(row=0, column=7, padx=5)
        self.data_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

    # ----- ITENS -----
    def create_items_frame(self):
        items_frame = tk.LabelFrame(
            self.ficha_frame, text="Itens (Cores e Tamanhos)",
            font=("Helvetica", 12, "bold"), bg="#f0f0f0", padx=10, pady=10
        )
        items_frame.pack(fill="both", expand=True, pady=10)

        self.tree = ttk.Treeview(
            items_frame, columns=("Cor", "G1", "G2", "G3", "Qt Rolos", "Peso Total", "Total"), show="headings"
        )
        for col in ("Cor", "G1", "G2", "G3", "Qt Rolos", "Peso Total", "Total"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(items_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(items_frame, text="Remover Item", command=self.remover_item).pack(pady=5)

    # ----- FORMULÁRIO DE ITENS -----
    def create_item_form(self):
        form_frame = tk.Frame(self.ficha_frame, bg="#f0f0f0")
        form_frame.pack(fill="x", pady=10)

        tk.Label(form_frame, text="Cor:", bg="#f0f0f0").grid(row=0, column=0, padx=5)
        self.cor_entry = ttk.Entry(form_frame, width=20)
        self.cor_entry.grid(row=0, column=1, padx=5)
        tk.Label(form_frame, text="G1:", bg="#f0f0f0").grid(row=0, column=2, padx=5)
        self.g1_entry = ttk.Entry(form_frame, width=5)
        self.g1_entry.grid(row=0, column=3, padx=5)
        tk.Label(form_frame, text="G2:", bg="#f0f0f0").grid(row=0, column=4, padx=5)
        self.g2_entry = ttk.Entry(form_frame, width=5)
        self.g2_entry.grid(row=0, column=5, padx=5)
        tk.Label(form_frame, text="G3:", bg="#f0f0f0").grid(row=0, column=6, padx=5)
        self.g3_entry = ttk.Entry(form_frame, width=5)
        self.g3_entry.grid(row=0, column=7, padx=5)
        tk.Label(form_frame, text="Qt. Rolos:", bg="#f0f0f0").grid(row=0, column=8, padx=5)
        self.qt_rolos_item_entry = ttk.Entry(form_frame, width=5)
        self.qt_rolos_item_entry.grid(row=0, column=9, padx=5)
        tk.Label(form_frame, text="Peso Total:", bg="#f0f0f0").grid(row=0, column=10, padx=5)
        self.peso_total_item_entry = ttk.Entry(form_frame, width=5)
        self.peso_total_item_entry.grid(row=0, column=11, padx=5)

        ttk.Button(form_frame, text="Adicionar Item", command=self.adicionar_item).grid(row=0, column=12, padx=10)

    # ----- BOTÕES FICHA -----
    def create_ficha_buttons(self):
        btn_frame = tk.Frame(self.ficha_frame, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Salvar Ficha", command=self.salvar_ficha).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Listar Fichas", command=self.listar_fichas).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Limpar Formulário", command=self.limpar_formulario).pack(side="left", padx=5)

    # ----- ADICIONAR / REMOVER ITENS -----
    def adicionar_item(self):
        cor = self.cor_entry.get().strip()
        try:
            g1 = int(self.g1_entry.get() or 0)
            g2 = int(self.g2_entry.get() or 0)
            g3 = int(self.g3_entry.get() or 0)
            qt_rolos = int(self.qt_rolos_item_entry.get() or 0)
            peso_total = float(self.peso_total_item_entry.get() or 0)
        except ValueError:
            messagebox.showerror("Erro", "Valores inválidos nos campos numéricos")
            return
        if not cor or qt_rolos <= 0 or peso_total <= 0:
            messagebox.showerror("Erro", "Preencha todos os campos corretamente")
            return
        total = g1 + g2 + g3
        self.items.append((cor, g1, g2, g3, qt_rolos, peso_total, total))
        self.tree.insert("", "end", values=(cor, g1, g2, g3, qt_rolos, peso_total, total))
        self.cor_entry.delete(0, tk.END)
        self.g1_entry.delete(0, tk.END)
        self.g2_entry.delete(0, tk.END)
        self.g3_entry.delete(0, tk.END)
        self.qt_rolos_item_entry.delete(0, tk.END)
        self.peso_total_item_entry.delete(0, tk.END)

    def remover_item(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um item para remover")
            return
        item = self.tree.item(selection[0])["values"]
        self.items = [i for i in self.items if tuple(i) != tuple(item)]
        self.tree.delete(selection[0])

    # ----- SALVAR FICHA -----
    def salvar_ficha(self):
        try:
            produto = self.produto_entry.get().strip()
            corte = int(self.corte_entry.get())
            grade = self.grade_entry.get().strip()
            data = datetime.strptime(self.data_entry.get().strip(), "%d/%m/%Y").date()

            if not produto or not grade or not self.items:
                messagebox.showerror("Erro", "Preencha todos os campos e adicione pelo menos um item")
                return

            with SessionLocal() as db:
                # Verificar estoque antes de salvar
                for cor, g1, g2, g3, qt_rolos, peso_total, total in self.items:
                    estoque_cor = db.query(EstoqueRolos).filter(EstoqueRolos.cor == cor).first()
                    if not estoque_cor or estoque_cor.qt_rolos < qt_rolos:
                        messagebox.showerror(
                            "Erro",
                            f"Estoque insuficiente para a cor {cor}. Disponível: {estoque_cor.qt_rolos if estoque_cor else 0}"
                        )
                        return

                # Criar ficha
                ficha = FichaProducao(
                    produto=produto,
                    corte=corte,
                    grade=grade,
                    data=data,
                    qt_rolos=sum(item[4] for item in self.items),
                    peso_total=sum(item[5] for item in self.items)
                )
                db.add(ficha)
                db.flush()

                # Adicionar itens e subtrair do estoque
                for cor, g1, g2, g3, qt_rolos, peso_total, total in self.items:
                    ficha.itens.append(ItemFicha(
                        cor=cor, g1=g1, g2=g2, g3=g3, qt_rolos=qt_rolos, peso_total=peso_total
                    ))
                    estoque = db.query(EstoqueRolos).filter(EstoqueRolos.cor == cor).first()
                    estoque.qt_rolos -= qt_rolos
                    db.add(estoque)

                db.commit()

            messagebox.showinfo("Sucesso", "Ficha salva com sucesso!")
            self.limpar_formulario()
            self.listar_estoque()  # Atualiza a tela de estoque
        except Exception as e:
            logger.error(f"Erro ao salvar ficha: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar ficha: {e}")

    # ----- LIMPAR FORMULÁRIO -----
    def limpar_formulario(self):
        self.produto_entry.delete(0, tk.END)
        self.corte_entry.delete(0, tk.END)
        self.grade_entry.delete(0, tk.END)
        self.data_entry.delete(0, tk.END)
        self.data_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.items.clear()
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.cor_entry.delete(0, tk.END)
        self.g1_entry.delete(0, tk.END)
        self.g2_entry.delete(0, tk.END)
        self.g3_entry.delete(0, tk.END)
        self.qt_rolos_item_entry.delete(0, tk.END)
        self.peso_total_item_entry.delete(0, tk.END)

    # ----- FUNÇÕES DE ESTOQUE -----
    def create_estoque_widgets(self):
        estoque_frame = self.estoque_frame

        self.estoque_tree = ttk.Treeview(estoque_frame, columns=("ID", "Qt Rolos", "Peso Total", "Cor", "Data Entrada"), show="headings")
        for col in ("ID", "Qt Rolos", "Peso Total", "Cor", "Data Entrada"):
            self.estoque_tree.heading(col, text=col)
            self.estoque_tree.column(col, width=100, anchor="center")
        self.estoque_tree.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(estoque_frame, orient="vertical", command=self.estoque_tree.yview)
        self.estoque_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Formulário
        form_frame = tk.Frame(estoque_frame, bg="#f0f0f0")
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Qt. Rolos:", bg="#f0f0f0").grid(row=0, column=0, padx=5)
        self.add_qt_rolos = ttk.Entry(form_frame, width=10)
        self.add_qt_rolos.grid(row=0, column=1, padx=5)
        tk.Label(form_frame, text="Peso Total (kg):", bg="#f0f0f0").grid(row=0, column=2, padx=5)
        self.add_peso_total = ttk.Entry(form_frame, width=10)
        self.add_peso_total.grid(row=0, column=3, padx=5)
        tk.Label(form_frame, text="Cor:", bg="#f0f0f0").grid(row=0, column=4, padx=5)
        self.add_cor = ttk.Entry(form_frame, width=15)
        self.add_cor.grid(row=0, column=5, padx=5)

        ttk.Button(form_frame, text="Adicionar Rolo", command=self.adicionar_rolos).grid(row=0, column=6, padx=5)
        ttk.Button(form_frame, text="Remover Rolo", command=self.remover_rolos).grid(row=0, column=7, padx=5)
        ttk.Button(form_frame, text="Atualizar Estoque", command=self.listar_estoque).grid(row=0, column=8, padx=5)

        self.listar_estoque()

    def adicionar_rolos(self):
        try:
            qt = int(self.add_qt_rolos.get())
            peso = float(self.add_peso_total.get())
            cor = self.add_cor.get().strip()
            if qt <= 0 or peso <= 0 or not cor:
                raise ValueError
        except:
            messagebox.showerror("Erro", "Digite valores válidos para rolos, peso e cor")
            return
        try:
            with SessionLocal() as db:
                rolo = EstoqueRolos(qt_rolos=qt, peso_total=peso, cor=cor, data_entrada=datetime.now().date())
                db.add(rolo)
                db.commit()
            messagebox.showinfo("Sucesso", "Rolo adicionado ao estoque")
            self.add_qt_rolos.delete(0, tk.END)
            self.add_peso_total.delete(0, tk.END)
            self.add_cor.delete(0, tk.END)
            self.listar_estoque()
        except Exception as e:
            logger.error(f"Erro ao adicionar rolo: {e}")
            messagebox.showerror("Erro", f"Erro ao adicionar rolo: {e}")

    def remover_rolos(self):
        selection = self.estoque_tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um rolo para remover")
            return
        rolo_id = self.estoque_tree.item(selection[0])["values"][0]
        try:
            with SessionLocal() as db:
                rolo = db.query(EstoqueRolos).filter(EstoqueRolos.id == rolo_id).first()
                if rolo:
                    db.delete(rolo)
                    db.commit()
                    self.listar_estoque()
                    messagebox.showinfo("Sucesso", "Rolo removido do estoque")
        except Exception as e:
            logger.error(f"Erro ao remover rolo: {e}")
            messagebox.showerror("Erro", f"Erro ao remover rolo: {e}")

    def listar_estoque(self):
        try:
            with SessionLocal() as db:
                rol = db.query(EstoqueRolos).all()
            for row in self.estoque_tree.get_children():
                self.estoque_tree.delete(row)
            for r in rol:
                self.estoque_tree.insert("", "end", values=(r.id, r.qt_rolos, r.peso_total, r.cor, r.data_entrada.strftime("%d/%m/%Y")))
        except Exception as e:
            logger.error(f"Erro ao listar estoque: {e}")
            messagebox.showerror("Erro", f"Erro ao listar estoque: {e}")

    # ----- LISTAR FICHAS COM CRUD -----
    def listar_fichas(self):
        try:
            with SessionLocal() as db:
                fichas = db.query(FichaProducao).options(joinedload(FichaProducao.itens)).all()

            if not fichas:
                messagebox.showinfo("Aviso", "Nenhuma ficha cadastrada")
                return

            list_window = tk.Toplevel(self.root)
            list_window.title("📑 Fichas Cadastradas")
            list_window.geometry("1300x600")
            list_window.configure(bg="#f0f0f0")

            colunas = ("ID", "Produto", "Corte", "Grade", "Data", "Cor", "G1", "G2", "G3", "Qt Rolos", "Peso Total", "Total")
            tree = ttk.Treeview(list_window, columns=colunas, show="headings")

            for col in colunas:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor="center")

            tree.pack(fill="both", expand=True, padx=20, pady=10)
            scrollbar = ttk.Scrollbar(list_window, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side="right", fill="y")

            for f in fichas:
                for item in f.itens:
                    total = (item.g1 or 0) + (item.g2 or 0) + (item.g3 or 0)
                    tree.insert(
                        "",
                        "end",
                        values=(f.id, f.produto, f.corte, f.grade, f.data.strftime("%d/%m/%Y"),
                                item.cor, item.g1, item.g2, item.g3, item.qt_rolos, item.peso_total, total)
                    )

            # Botões CRUD
            def deletar():
                sel = tree.selection()
                if not sel:
                    messagebox.showwarning("Aviso", "Selecione uma ficha para deletar")
                    return
                ficha_id = tree.item(sel[0])["values"][0]
                if messagebox.askyesno("Confirmar", f"Deletar ficha {ficha_id}?"):
                    with SessionLocal() as db:
                        ficha = db.query(FichaProducao).filter(FichaProducao.id==ficha_id).first()
                        if ficha:
                            db.delete(ficha)
                            db.commit()
                    messagebox.showinfo("Sucesso", "Ficha deletada")
                    list_window.destroy()
                    self.listar_fichas()

            def editar():
                selection = tree.selection()
                if not selection:
                    messagebox.showwarning("Aviso", "Selecione uma ficha para editar")
                    return
                
                # Obtém o ID da ficha da linha selecionada
                ficha_id = tree.item(selection[0])["values"][0]

                with SessionLocal() as db:
                    ficha = db.query(FichaProducao).options(joinedload(FichaProducao.itens)).filter(FichaProducao.id == ficha_id).first()
                    if not ficha:
                        messagebox.showerror("Erro", "Ficha não encontrada")
                        return

                    # Janela de edição
                    edit_window = tk.Toplevel(list_window)
                    edit_window.title(f"✏️ Editar Ficha {ficha.id}")
                    edit_window.geometry("1000x600")
                    edit_window.configure(bg="#f0f0f0")

                    # Campos do cabeçalho
                    tk.Label(edit_window, text="Produto:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="w")
                    produto_entry = ttk.Entry(edit_window, width=40)
                    produto_entry.insert(0, ficha.produto)
                    produto_entry.grid(row=0, column=1, padx=5, pady=5)

                    tk.Label(edit_window, text="Corte:", bg="#f0f0f0").grid(row=0, column=2, padx=5, pady=5, sticky="w")
                    corte_entry = ttk.Entry(edit_window, width=10)
                    corte_entry.insert(0, ficha.corte)
                    corte_entry.grid(row=0, column=3, padx=5, pady=5)

                    tk.Label(edit_window, text="Grade:", bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=5, sticky="w")
                    grade_entry = ttk.Entry(edit_window, width=20)
                    grade_entry.insert(0, ficha.grade)
                    grade_entry.grid(row=1, column=1, padx=5, pady=5)

                    tk.Label(edit_window, text="Data (dd/mm/yyyy):", bg="#f0f0f0").grid(row=1, column=2, padx=5, pady=5, sticky="w")
                    data_entry = ttk.Entry(edit_window, width=15)
                    data_entry.insert(0, ficha.data.strftime("%d/%m/%Y") if ficha.data else "")
                    data_entry.grid(row=1, column=3, padx=5, pady=5)

                    # Tabela de itens
                    colunas_itens = ("ID", "Cor", "G1", "G2", "G3", "Qt Rolos", "Peso Total")
                    items_tree = ttk.Treeview(edit_window, columns=colunas_itens, show="headings", height=10)
                    for col in colunas_itens:
                        items_tree.heading(col, text=col)
                        items_tree.column(col, width=120, anchor="center")
                    items_tree.grid(row=2, column=0, columnspan=6, padx=10, pady=10, sticky="nsew")
                    
                    # Scrollbar
                    scrollbar_itens = ttk.Scrollbar(edit_window, orient="vertical", command=items_tree.yview)
                    items_tree.configure(yscroll=scrollbar_itens.set)
                    scrollbar_itens.grid(row=2, column=6, sticky='ns')

                    # Preenche com os itens existentes
                    for item in ficha.itens:
                        items_tree.insert("", "end", values=(item.id, item.cor, item.g1, item.g2, item.g3, item.qt_rolos, item.peso_total))

                    # Função para editar item
                    def editar_item():
                        sel = items_tree.selection()
                        if not sel:
                            messagebox.showwarning("Aviso", "Selecione um item para editar")
                            return

                        item_values = items_tree.item(sel[0])["values"]
                        item_id, cor, g1, g2, g3, qt_rolos, peso_total = item_values

                        # Nova janela para editar
                        item_window = tk.Toplevel(edit_window)
                        item_window.title("Editar Item da Ficha")

                        labels = ["Cor", "G1", "G2", "G3", "Qt Rolos", "Peso Total"]
                        entries = []

                        for i, val in enumerate([cor, g1, g2, g3, qt_rolos, peso_total]):
                            tk.Label(item_window, text=labels[i]).grid(row=i, column=0, padx=5, pady=5)
                            e = ttk.Entry(item_window)
                            e.insert(0, val)
                            e.grid(row=i, column=1, padx=5, pady=5)
                            entries.append(e)

                        def salvar_item():
                            try:
                                novo_cor = entries[0].get().strip()
                                novo_g1 = int(entries[1].get())
                                novo_g2 = int(entries[2].get())
                                novo_g3 = int(entries[3].get())
                                novo_qt = int(entries[4].get())
                                novo_peso = float(entries[5].get())

                                # Atualiza na Treeview
                                items_tree.item(sel[0], values=(item_id, novo_cor, novo_g1, novo_g2, novo_g3, novo_qt, novo_peso))
                                item_window.destroy()
                            except Exception as e:
                                messagebox.showerror("Erro", f"Erro ao editar item: {e}")

                        ttk.Button(item_window, text="Salvar", command=salvar_item).grid(row=6, column=0, columnspan=2, pady=10)

                    # Botão para editar item
                    ttk.Button(edit_window, text="Editar Item Selecionado", command=editar_item).grid(row=3, column=0, columnspan=6, pady=5)

                    # Salvar alterações da ficha
                    def salvar_edicao():
                        try:
                            ficha.produto = produto_entry.get().strip()
                            ficha.corte = int(corte_entry.get())
                            ficha.grade = grade_entry.get().strip()
                            ficha.data = datetime.strptime(data_entry.get().strip(), "%d/%m/%Y").date()

                            # Remove itens antigos
                            ficha.itens.clear()
                            db.flush()

                            # Adiciona os novos itens da tabela
                            for row in items_tree.get_children():
                                _, cor, g1, g2, g3, qt_rolos, peso_total = items_tree.item(row)["values"]
                                ficha.itens.append(
                                    ItemFicha(
                                        cor=cor,
                                        g1=int(g1),
                                        g2=int(g2),
                                        g3=int(g3),
                                        qt_rolos=int(qt_rolos),
                                        peso_total=float(peso_total)
                                    )
                                )

                            db.commit()
                            messagebox.showinfo("Sucesso", "Ficha editada com sucesso!")
                            edit_window.destroy()
                            list_window.destroy()
                            self.listar_fichas()
                        except Exception as e:
                            db.rollback()
                            messagebox.showerror("Erro", f"Erro ao salvar alterações: {e}")

                    ttk.Button(edit_window, text="Salvar Alterações", command=salvar_edicao).grid(row=4, column=0, columnspan=6, pady=20)
                    
            btn_frame = tk.Frame(list_window, bg="#f0f0f0")
            btn_frame.pack(pady=10)

            ttk.Button(btn_frame, text="Deletar Ficha", command=deletar).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Editar Ficha", command=editar).pack(side="left", padx=5)

        except Exception as e:
            logger.error(f"Erro ao listar fichas: {e}")
            messagebox.showerror("Erro", "Erro ao carregar fichas do banco de dados")

# ----- INICIALIZAÇÃO -----
if __name__ == "__main__":
    root = tk.Tk()
    app = FichaApp(root)
    root.mainloop()