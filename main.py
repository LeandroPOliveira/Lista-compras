import os
import sqlite3
from kivy.config import Config
from kivy.uix.screenmanager import Screen, ScreenManager


Config.set('graphics', 'resizable', '1')
Config.set('graphics', 'width', '389')
Config.set('graphics', 'height', '700')
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.lang import Builder
from kivymd.uix.textfield import MDTextField
from kivy.properties import Clock
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.swiper import MDSwiperItem


class ContentNavigationDrawer(Screen):
    pass


class Principal(Screen):
    pass


class Inicio(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ListaAtual(Screen):
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
        Clock.schedule_once(self.carregar_lista)

    def carregar_lista(self, dt):
        self.lista.clear(), self.produtos.clear()
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM lista order by checks ASC')
        self.lista = cursor.fetchall()
        self.ids.lista.add_widget(
            OneLineAvatarIconListItem(
                IconLeftWidget(MDCheckbox(),
                               icon='transparent.png', icon_size='10sp', on_press=self.marcar_item, text=''
                               ),
                text='Produtos', bg_color='yellow'))

        for item in self.lista:

            self.ids.lista.add_widget(
                OneLineAvatarIconListItem(
                    IconLeftWidget(MDCheckbox(active=True if item[3] == 1 else False),
                        icon='transparent.png', icon_size='10sp', on_press=self.marcar_item, text=f"{item[1]}"
                    ),
                    IconRightWidget(icon='icons/x.ico', icon_size='10sp', on_press=self.remover_item, text=f"{item[1]}"),
                    text=f"{item[1]}"
                )
            )

    def novo_item(self):
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
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
                    on_press=lambda x:self.dialog.dismiss()

                ),
                MDFlatButton(
                    text="OK",
                    theme_text_color="Custom",
                    on_press=lambda x:(self.adicionar_item(self.entrada), self.dialog.dismiss())
                ),
            ],
        )
        self.dialog.open()

    def adicionar_item(self, entrada):
        # print(entrada.text)
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO lista(produto, checks) VALUES(?, ?)', (entrada.text, 0))
        conn.commit()
        self.ids.lista.clear_widgets()
        self.carregar_lista(dt=None)

    def remover_item(self, instance):
        print(instance.text)
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM lista WHERE produto = (?)', (instance.text,))
        conn.commit()
        self.ids.lista.clear_widgets()
        self.carregar_lista(dt=None)

    def marcar_item(self, instance):
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()

        print(instance.text)
        for item in self.ids.lista.children:

            if instance.parent in item.children:
                cursor.execute('select * FROM lista WHERE produto = (?)', (instance.text,))
                self.pega_check = cursor.fetchall()
                self.pega_check = self.pega_check[0][3]
                if self.pega_check == 0:
                    self.atualiza_check = 1
                else:
                    self.atualiza_check = 0
                cursor.execute('UPDATE lista SET checks = (?) WHERE produto = (?)', (self.atualiza_check, instance.text,))
                # cursor.execute('INSERT INTO lista(produto) VALUES(?, ?)', (instance.text, 0))
                conn.commit()
                self.ids.lista.clear_widgets()
                self.carregar_lista(dt=None)

                # self.ids.lista.remove_widget(item)
                # self.ids.lista.add_widget(item)


class MinhasListas(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lista = []
        self.lista_icon = []
        self.lista2 = []

    def inserir(self):

        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sqlite_master where type="table"')
        resultado = cursor.fetchall()
        for index, linha in enumerate(resultado):

            self.lista.append([])
            self.insere_swiper = MDSwiperItem()  # Criar um "swiper" para cada tabela
            self.lista2.append(self.insere_swiper)
            self.ids.swiper.add_widget(self.insere_swiper)

            self.inserir_layout = MDFloatLayout()  # Adicionar layout para organizar os widgets
            self.insere_swiper.add_widget(self.inserir_layout)

            # inserir os rótulos para cada item
            self.label_tabela = MDLabel(pos_hint={'x': 0, 'y': .72}, font_size=20, text='Nome da tabela',
                                        size_hint=(1, .2), halign='center')
            self.inserir_layout.add_widget(self.label_tabela)

            self.num_tabela = MDLabel(text=linha[1], pos_hint={'x': 0.15, 'y': .76}, color=(33 / 255, 150 / 255, 243 / 255, 1),
                                      font_size='25dp', size_hint=(.7, .02), halign='center')
            self.inserir_layout.add_widget(self.num_tabela)
            self.lista[index].append(self.num_tabela)

            self.lista[index].append(self.num_tabela)

        self.insere_swiper2 = MDSwiperItem()
        self.lista2.append(self.insere_swiper2)
        self.ids.swiper.add_widget(self.insere_swiper2)
        self.ids.swiper.set_current(1)


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
        print(self.resultado)
        for produto in self.resultado:
            self.lista_produtos.append((produto[1],))

        print(self.lista_produtos)
        # self.manager.get_screen('produtos').catalogo_produtos()


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
        print(itens)
        for item in itens:
            cursor.execute('INSERT INTO lista(produto, categoria, checks) VALUES(?, ?, ?)', (''.join(item),
                                                                    self.manager.get_screen('pesquisar').categoria, 0))
            conn.commit()
            self.manager.get_screen('lista_atual').ids.lista.clear_widgets()
            self.manager.get_screen('lista_atual').carregar_lista(dt=None)


class WindowManager(ScreenManager):
    pass


class Example(MDApp):
    def build(self):
        # self.theme_cls.theme_style = "Dark"
        return Builder.load_file('main.kv')


Example().run()
