import math
import sqlite3

from kivy.config import Config
from kivy.uix.screenmanager import Screen


Config.set('graphics', 'resizable', '1')
Config.set('graphics', 'width', '389')
Config.set('graphics', 'height', '700')
from kivy.lang import Builder
from kivymd.uix.textfield import MDTextField
from kivy.properties import StringProperty, Clock
from kivymd.app import MDApp
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem, TwoLineAvatarIconListItem, ImageRightWidget, \
    IconLeftWidget, OneLineListItem, IconRightWidget
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.icon_definitions import md_icons
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.datatables import MDDataTable
import random
from functools import partial
from kivy.metrics import dp
from kivy.utils import get_color_from_hex

class Principal(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lista = []
        self.nomes = ['ze', 'bastio', 'mane']
        self.dialog = None
        Clock.schedule_once(self.carregar_lista)

    def carregar_lista(self, dt):
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM lista')
        self.produtos = []
        self.lista = cursor.fetchall()
        # self.completos = []
        for item in self.lista:
            self.produtos.append(item[1])
        self.icones = ['X'] * len(self.produtos)
        self.completos = list(zip(self.produtos, self.icones))
        self.dados_listagem = MDDataTable(pos_hint={'x': 0.1, 'y': 0.2},
                                          size_hint=(.8, .7),
                                          rows_num=len(self.completos),
                                          background_color_header=get_color_from_hex("#0bbd6d"),
                                          background_color_selected_cell=get_color_from_hex("#d2f7e7"),
                                          check=True,
                                          column_data=[("[color=#ffffff]Produto[/color]", dp(50)),
                                                       ("[color=#FFA07A][/color]", dp(10))],
                                          row_data=self.completos, elevation=1)

        self.ids.scroll.add_widget(self.dados_listagem)
        self.dados_listagem.bind(on_row_press=self.on_row_press)
        self.dados_listagem.bind(on_check_press=self.on_check_press)
    def on_row_press(self, current_row, instance_row):
        '''Called when a table row is clicked.'''
        print(instance_row.index)

        if instance_row.index % 2 != 0:
            self.remover(instance_row.index)
        else:
            pass

    def on_check_press(self, instance_table, current_row):
        '''Called when the check box in the table row is checked.'''

        print(instance_table, current_row)

    def novo_item(self):
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()

        self.entrada = MDTextField()
        self.dialog = MDDialog(
            title="Novo item:",
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


class Example(MDApp):
    def build(self):
        # self.theme_cls.theme_style = "Dark"
        return Builder.load_file('list.kv')


Example().run()
