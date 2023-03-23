import sqlite3
from kivy.config import Config
from kivy.uix.screenmanager import Screen, ScreenManager
Config.set('graphics', 'resizable', '1')
Config.set('graphics', 'width', '389')
Config.set('graphics', 'height', '700')
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.card import MDCard
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.lang import Builder
from kivymd.uix.textfield import MDTextField
from kivy.properties import Clock, StringProperty, NumericProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.swiper import MDSwiperItem


class ContentNavigationDrawer(Screen):
    pass


class Principal(Screen):
    pass


class Inicio(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ListaAtual(Screen):
    lista_em_uso = StringProperty('lista')
    numero_linhas = NumericProperty(10)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entrada = None
        self.dados_listagem = None
        self.completos = None
        self.icones = None
        self.lista = []
        self.produtos = []
        self.lista_produtos = []
        self.dialog = None
        self.lista_dict = {}
        self.itens_a_remover = []
        self.itens_a_adicionar = []

    def carregar_lista(self):
        self.lista.clear(), self.produtos.clear(), self.ids.lista.clear_widgets()
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {self.lista_em_uso} order by checks ASC')
        self.lista = cursor.fetchall()
        self.numero_linhas = len(self.lista)
        self.ids.lista.add_widget(
            OneLineAvatarIconListItem(
                IconLeftWidget(MDCheckbox(),
                               on_press=self.selecionar_tudo,
                               ),
                IconRightWidget(icon='refresh', on_press=lambda x: self.atualizar_lista()),
                text=self.lista_em_uso, bg_color="#df2100", theme_text_color='Custom', text_color="white",
                radius=[10, 10, 10, 10]))

        for item in self.lista:
            self.lista_dict[item[1]] = item[3]
            self.ids.lista.add_widget(
                OneLineAvatarIconListItem(
                    IconLeftWidget(MDCheckbox(active=True if item[3] == 1 else False),
                                   icon='transparent.png', icon_size='10sp', on_press=self.marcar_item,
                                   text=f"{item[1]}"
                                   ),
                    IconRightWidget(icon='icons/x.ico', icon_size='10sp', on_press=self.remover_item,
                                    text=f"{item[1]}"),
                    text=f"{item[1]}", theme_text_color='Custom', text_color="#df2100", bg_color="#e6dedc", radius=[10, 10, 10, 10]
                )
            )

        # self.lista_dict = sorted(self.lista_dict.items(), key=lambda item: item[1])

    def novo_item(self):
        self.entrada = MDTextField()
        self.dialog = MDDialog(
            title="Novo produto:",
            type="custom",
            content_cls=MDBoxLayout(
                self.entrada,
                orientation="vertical",
                spacing="12dp",
                size_hint_y=None,
                height="60dp",
            ),
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    theme_text_color="Custom",
                    on_press=lambda x: self.dialog.dismiss()

                ),
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    on_press=lambda x: (self.adicionar_item(self.entrada), self.dialog.dismiss())
                ),
            ],
        )
        self.dialog.open()

    def adicionar_item(self, entrada):
        self.atualizar_lista()
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        cursor.execute(f'INSERT INTO {self.lista_em_uso}(produto, checks) VALUES(?, ?)', (entrada.text, 0))
        conn.commit()
        self.ids.lista.clear_widgets()
        self.carregar_lista()
        # self.itens_a_adicionar.append(entrada.text)
        # self.lista_dict[entrada.text] = 0
        self.numero_linhas = self.numero_linhas + 1
        self.atualizar_lista()

    def remover_item(self, instance):
        self.itens_a_remover.append(instance.text)
        self.ids.lista.remove_widget(instance.parent.parent)

        # self.atualizar_lista()
        # conn = sqlite3.connect('lista_compras')
        # cursor = conn.cursor()
        # cursor.execute(f'DELETE FROM {self.lista_em_uso} WHERE produto = (?)', (instance.text,))
        # conn.commit()
        # self.ids.lista.clear_widgets()
        # self.carregar_lista()

    def marcar_item(self, instance):
        # instance.parent.parent.text_color = 'blue'
        # instance.children[0].color_active = 'grey'
        for item in self.ids.lista.children:
            if instance.parent in item.children:
                if self.lista_dict[instance.text] == 0:
                    self.lista_dict[instance.text] = 1
                else:
                    self.lista_dict[instance.text] = 0

    def atualizar_lista(self):
        print(self.itens_a_remover)
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        for key, value in self.lista_dict.items():
            if key in self.itens_a_remover:
                cursor.execute(f'DELETE FROM {self.lista_em_uso} WHERE produto = (?)', (key,))
            # if key in self.itens_a_adicionar:
            #     cursor.execute(f'INSERT INTO {self.lista_em_uso}(produto, checks) VALUES(?, ?)', (key, 0))
            else:
                cursor.execute(f'UPDATE {self.lista_em_uso} SET checks = (?) WHERE produto = (?)', (value, key,))


        conn.commit()
        self.ids.lista.clear_widgets()
        self.itens_a_remover.clear()
        # self.itens_a_adicionar.clear()
        self.carregar_lista()

        # conn = sqlite3.connect('lista_compras')
        # cursor = conn.cursor()
        #
        # for item in self.ids.lista.children:
        #     if instance.parent in item.children:
        #         cursor.execute(f'select * FROM {self.lista_em_uso} WHERE produto = (?)', (instance.text,))
        #         self.pega_check = cursor.fetchall()
        #         self.pega_check = self.pega_check[0][3]
        #         if self.pega_check == 0:
        #             self.atualiza_check = 1
        #         else:
        #             self.atualiza_check = 0
        #         cursor.execute(f'UPDATE {self.lista_em_uso} SET checks = (?) WHERE produto = (?)',
        #                        (self.atualiza_check, instance.text,))
        #
        #         conn.commit()
        #         self.ids.lista.clear_widgets()
        #         self.carregar_lista()

    def selecionar_tudo(self, instance):
        if instance.children[0].state == 'down':
            for item in self.ids.lista.children:
                self.lista_dict[item.children[1].children[0].text] = 1
                item.children[1].children[0].children[0].active = True
        else:
            for item in self.ids.lista.children:
                self.lista_dict[item.children[1].children[0].text] = 0
                item.children[1].children[0].children[0].active = False


class MinhasListas(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lista = []
        Clock.schedule_once(self.minhas_listas)

    def minhas_listas(self, dt=None):
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sqlite_master where type="table"')
        resultado = cursor.fetchall()
        resultado.pop(1)
        resultado.pop(1)

        if len(self.lista) != 0:
            for i in self.lista:
                self.ids.swiper.remove_widget(i)

        self.lista.clear()
        for index, linha in enumerate(resultado):
            self.insere_swiper = MDSwiperItem()  # Criar um "swiper" para cada tabela
            self.ids.swiper.add_widget(self.insere_swiper)
            self.lista.append(self.insere_swiper)
            self.inserir_layout = MDFloatLayout()  # Adicionar layout para organizar os widgets
            self.insere_swiper.add_widget(self.inserir_layout)

            # inserir os rótulos para cada item
            self.label_tabela = MDCard(MDRelativeLayout(MDIconButton(icon='pencil', text=linha[1],
                                                                     pos_hint={'center_x': 0.3, 'y': .2},
                                                                     on_press=self.editar_lista),
                                                        MDIconButton(icon='icons/x.ico', icon_size='15sp',
                                                                     text=linha[1], pos_hint={'center_x': 0.7, 'y': .2},
                                                                     on_press=self.apagar_lista),
                                                        MDRectangleFlatButton(text=linha[1],
                                                                              pos_hint={'center_x': 0.5, 'y': .5},
                                                                              text_color='#f8ebff',
                                                                              md_bg_color="#4a1fe1",
                                                                              on_press=self.lista_selecionada,
                                                                              font_size='20dp', size_hint=(.7, .2),
                                                                              halign='center')),
                                       size_hint=(1, .3), pos_hint={'x': 0, 'y': .3}, md_bg_color="#ffffff",
                                       line_color="ffcc21")

            self.inserir_layout.add_widget(self.label_tabela)

            self.lista.append(self.label_tabela)

        self.insere_swiper2 = MDSwiperItem()
        self.lista.append(self.insere_swiper2)
        self.ids.swiper.add_widget(self.insere_swiper2)
        self.ids.swiper.set_current(1)

    def lista_selecionada(self, instance):
        self.manager.get_screen('lista_atual').lista_em_uso = instance.text
        self.manager.current = 'lista_atual'

    def editar_lista(self, instance):
        self.nome_anterior = instance.text
        self.entrada = MDTextField(text=instance.text)
        self.dialog_lista2 = MDDialog(
            title="Editar lista:",
            type="custom",
            content_cls=MDBoxLayout(
                self.entrada,
                orientation="vertical",
                spacing="12dp",
                size_hint_y=None,
                height="60dp",
            ),
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    theme_text_color="Custom",
                    on_press=lambda x: self.dialog_lista2.dismiss()

                ),
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    on_press=lambda x: (self.editar_nome(self.entrada), self.dialog_lista2.dismiss())
                ),
            ],
        )
        self.dialog_lista2.open()

    def editar_nome(self, entrada):
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()

        cursor.execute(f'ALTER TABLE {self.nome_anterior} RENAME TO {entrada.text}')
        conn.commit()
        self.minhas_listas(dt=None)

    def nova_lista(self):
        self.entrada = MDTextField()
        self.dialog_lista = MDDialog(
            title="Nova lista:",
            type="custom",
            content_cls=MDBoxLayout(
                self.entrada,
                orientation="vertical",
                spacing="12dp",
                size_hint_y=None,
                height="60dp",
            ),
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    theme_text_color="Custom",
                    on_press=lambda x: self.dialog_lista.dismiss()

                ),
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    on_press=lambda x: (self.adicionar_lista(self.entrada), self.dialog_lista.dismiss())
                ),
            ],
        )
        self.dialog_lista.open()

    def adicionar_lista(self, entrada):
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()

        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {entrada.text} (
        id integer PRIMARY KEY AUTOINCREMENT,
        produto text NOT NULL,
        categoria text,
        checks integer);''')

        conn.commit()
        self.manager.get_screen('lista_atual').lista_em_uso = entrada.text
        try:
            self.ids.lista.clear_widgets()
        except AttributeError:
            pass
        self.manager.current = 'lista_atual'

    def apagar_lista(self, instance):
        self.dialog3 = MDDialog(
            text="Confirma a exclusão?",
            buttons=[
                MDFlatButton(
                    text="CANCELAR",
                    theme_text_color="Custom",
                    on_press=lambda x: self.dialog3.dismiss()
                ),
                MDFlatButton(
                    text="CONFIRMAR",
                    theme_text_color="Custom",
                    on_press=lambda x: (self.apagar(instance.text), self.dialog3.dismiss())
                ),
            ],
        )
        self.dialog3.open()


    def apagar(self, entrada):
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        cursor.execute(f'DROP TABLE {entrada}')
        conn.commit()
        self.dialog_data = MDDialog(text=f"Lista excluida com sucesso!",
                                    radius=[20, 7, 20, 7], )
        self.dialog_data.open()
        self.minhas_listas()


class Pesquisar(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def buscar_produtos(self, instance, item):
        self.lista_produtos = self.manager.get_screen('lista_atual').lista_produtos
        self.categoria = item.text
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        cursor.execute('select * from produtos WHERE categoria = (?) order by produto ASC', (self.categoria,))
        self.lista_produtos.clear()
        self.resultado = cursor.fetchall()

        for produto in self.resultado:
            self.lista_produtos.append((produto[1],))


class Produtos(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def catalogo_produtos(self):
        print(self.manager.get_screen('lista_atual').lista_produtos)
        self.dados_listagem = MDDataTable(pos_hint={'x': 0.15, 'y': 0.2},
                                          size_hint=(.7, .6),
                                          rows_num=len(self.manager.get_screen('lista_atual').lista_produtos),
                                          background_color_header=get_color_from_hex("#ebf52a"),
                                          background_color_selected_cell=get_color_from_hex("#f5f7cd"),
                                          check=True,
                                          column_data=[("[color=#0d0d0d]Produto[/color]", dp(50))
                                                       ],
                                          row_data=self.manager.get_screen('lista_atual').lista_produtos, elevation=1)

        self.ids.lista_produtos.add_widget(self.dados_listagem)

    def adicionar_itens(self):
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        itens = self.dados_listagem.get_row_checks()

        for item in itens:
            cursor.execute('INSERT INTO lista(produto, categoria, checks) VALUES(?, ?, ?)', (''.join(item),
                                                                                             self.manager.get_screen(
                                                                                                 'pesquisar').categoria,
                                                                                             0))
            conn.commit()
            self.manager.get_screen('lista_atual').ids.lista.clear_widgets()
            self.manager.get_screen('lista_atual').carregar_lista()


class WindowManager(ScreenManager):
    pass


class Example(MDApp):
    def build(self):
        # self.theme_cls.theme_style = "Dark"
        return Builder.load_file('main.kv')


Example().run()
