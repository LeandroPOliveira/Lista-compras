import math
import sqlite3
from kivy.config import Config
from kivy.uix.screenmanager import Screen
Config.set('graphics', 'resizable', '1')
Config.set('graphics', 'width', '389')
Config.set('graphics', 'height', '700')
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


class Principal(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entrada = None
        self.dados_listagem = None
        self.completos = None
        self.icones = None
        self.lista = []
        self.produtos = []
        self.dialog = None
        Clock.schedule_once(self.carregar_lista)

    def carregar_lista(self, dt):
        self.lista.clear(), self.produtos.clear()
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM lista')
        self.lista = cursor.fetchall()
        for item in self.lista:
            self.produtos.append(item[1])
        self.icones = ['X'] * len(self.produtos)
        self.completos = list(zip(self.produtos, self.icones))
        self.dados_listagem = MDDataTable(pos_hint={'x': 0.15, 'y': 0.2},
                                          size_hint=(.7, .6),
                                          rows_num=len(self.completos),
                                          background_color_header=get_color_from_hex("#ebf52a"),
                                          background_color_selected_cell=get_color_from_hex("#f5f7cd"),
                                          check=True,
                                          column_data=[("[color=#0d0d0d]Produto[/color]", dp(35)),
                                                       ("[color=#0d0d0d][/color]", dp(10))],
                                          row_data=self.completos, elevation=1)

        self.ids.scroll.add_widget(self.dados_listagem)
        self.dados_listagem.bind(on_row_press=self.on_row_press)
        self.dados_listagem.bind(on_check_press=self.on_check_press)

    def on_row_press(self, instance_table, instance_row):
        # instance_row.ids.check.state = 'down'
        if instance_row.index % 2 != 0:
            self.remover(instance_row.index)
        else:
            pass

    def on_check_press(self, instance_table, current_row):
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        print(self.dados_listagem.get_row_checks())
        print(current_row[0])
        cursor.execute('DELETE FROM lista WHERE produto = (?)', (current_row[0],))
        cursor.execute('INSERT INTO lista(produto) VALUES(?)', (current_row[0],))
        conn.commit()
        self.carregar_lista(dt=None)

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
                    on_press=lambda x:(self.adicionar(self.entrada), self.dialog.dismiss())
                ),
            ],
        )
        self.dialog.open()

    def adicionar(self, entrada):
        # print(entrada.text)
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO lista(produto) VALUES(?)', (entrada.text,))
        conn.commit()
        self.ids.scroll.clear_widgets()
        self.carregar_lista(dt=None)

    def remover(self, row):
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM lista WHERE produto = (?)', (self.lista[math.floor(row/2)][1],))
        conn.commit()
        self.ids.scroll.clear_widgets()
        self.carregar_lista(dt=None)

    def teste(self, instance, item):
        print('teste', item.text)


class Example(MDApp):
    def build(self):
        # self.theme_cls.theme_style = "Dark"
        return Builder.load_file('list.kv')


Example().run()
