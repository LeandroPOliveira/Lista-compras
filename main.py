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
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.swiper import MDSwiperItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.label import MDLabel


class ContentNavigationDrawer(Screen):
    pass


class Principal(Screen):
    pass


class Inicio(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ListaAtual(Screen):
    lista_em_uso = StringProperty('')
    numero_linhas = NumericProperty(10)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.entrada = None
        self.lista = None
        self.dialog = None
        self.lista_dict = {}
        self.itens_a_remover = []
        self.itens_a_adicionar = []

    def carregar_lista(self, cond_extra=None):
        self.ids.lista.clear_widgets()
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        if cond_extra is None:
            cursor.execute(f'SELECT * FROM {self.lista_em_uso} order by checks ASC')
        else:
            cursor.execute(f'SELECT * FROM {self.lista_em_uso} order by checks ASC, {cond_extra}')
        self.lista = cursor.fetchall()

        for item in self.lista:
            self.lista_dict[item[1]] = item[3]
            self.ids.lista.add_widget(
                OneLineAvatarIconListItem(
                    IconLeftWidget(MDCheckbox(active=True if item[3] == 1 else False),
                                   icon='assets/transparent.png', icon_size='10sp', on_press=self.marcar_item,
                                   text=f"{item[1]}"
                                   ),
                    IconRightWidget(icon='assets/x.ico', icon_size='10sp', on_press=self.remover_item,
                                    text=f"{item[1]}"),
                    text=f"{item[1]}", theme_text_color='Custom', text_color="#df2100", bg_color="#ffffff",
                    radius=[0, 10, 0, 10]
                )
            )

        for item in self.ids.lista.children:
            if item.children[1].children[0].children[0].active:
                item.children[1].children[0].children[0].color = "#c9c8c7"
                item.text = f'[s]{item.text}[/s]'
                item.text_color = "#9c9c9c"

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
        entrada = entrada.text.capitalize()
        dict_index = sum(map((1).__eq__, self.lista_dict.values()))

        self.ids.lista.add_widget(
            OneLineAvatarIconListItem(
                IconLeftWidget(MDCheckbox(),
                               icon_size='10sp', on_press=self.marcar_item,
                               text=f"{entrada}"
                               ),
                IconRightWidget(icon='assets/x.ico', icon_size='10sp', on_press=self.remover_item,
                                text=f"{entrada}"),
                text=f"{entrada}", theme_text_color='Custom', text_color="#df2100", bg_color="#ffffff",
                radius=[0, 10, 0, 10]
            ), dict_index)

        self.itens_a_adicionar.append(entrada)
        self.lista_dict[entrada] = 0

    def remover_item(self, instance):
        self.itens_a_remover.append(instance.text)
        self.ids.lista.remove_widget(instance.parent.parent)

    def marcar_item(self, instance):
        if instance.children[0].state == 'down':
            self.ids.lista.remove_widget(instance.parent.parent)
            self.ids.lista.add_widget(instance.parent.parent)
            self.lista_dict[instance.text] = 1
            instance.children[0].color = "#c9c8c7"
            instance.parent.parent.text = f'[s]{instance.text}[/s]'
            instance.parent.parent.text_color = "#9c9c9c"
        else:
            self.ids.lista.remove_widget(instance.parent.parent)
            dict_index = sum(map((1).__eq__, self.lista_dict.values()))
            self.ids.lista.add_widget(instance.parent.parent, dict_index - 1)
            self.lista_dict[instance.text] = 0
            instance.parent.parent.text = instance.text
            instance.parent.parent.text_color = "#df2100"

    def salvar_lista(self):
        if self.lista_em_uso != '':
            conn = sqlite3.connect('lista_compras')
            cursor = conn.cursor()
            for key, value in self.lista_dict.items():
                if key in self.itens_a_remover:
                    cursor.execute(f'DELETE FROM {self.lista_em_uso} WHERE produto = (?)', (key,))
                if key in self.itens_a_adicionar:
                    cursor.execute(f'INSERT INTO {self.lista_em_uso}(produto, checks) VALUES(?, ?)', (key, 0))
                else:
                    cursor.execute(f'UPDATE {self.lista_em_uso} SET checks = (?) WHERE produto = (?)', (value, key,))

            conn.commit()
            self.ids.lista.clear_widgets()
            self.itens_a_remover.clear()
            self.itens_a_adicionar.clear()
            self.carregar_lista()
            try:
                self.menu.dismiss()
            except AttributeError:
                pass

        def selecionar_tudo(self, instance):
            instance.color = "#c9c8c7"
            if instance.state == 'down':
                for item in self.ids.lista.children:
                    self.lista_dict[item.children[1].children[0].text] = 1
                    item.children[1].children[0].children[0].active = True
                    item.children[1].children[0].children[0].color = "#c9c8c7"
                    item.text = f'[s]{item.text}[/s]'
                    item.text_color = "#9c9c9c"
            else:
                for item in self.ids.lista.children:
                    self.lista_dict[item.children[1].children[0].text] = 0
                    item.children[1].children[0].children[0].active = False
                    item.text = item.children[1].children[0].text
                    item.text_color = "#df2100"

    def ordenar_crescente(self):
        self.salvar_lista()
        self.carregar_lista('produto ASC')
        self.menu.dismiss()

    def ordenar_decrescente(self):
        self.salvar_lista()
        self.carregar_lista('produto DESC')
        self.menu.dismiss()

    def chama_menu(self):
        self.menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Salvar lista",
                "height": dp(56),
                "on_release": self.salvar_lista,
            }, {
                "viewclass": "OneLineListItem",
                "text": "Ordem crescente",
                "height": dp(56),
                "on_release": self.ordenar_crescente,
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Ordem decrescente",
                "height": dp(56),
                "on_release": self.ordenar_decrescente,
            }
        ]
        self.menu = MDDropdownMenu(
            caller=self.ids.menu,
            items=self.menu_items,
            width_mult=4,
        )

        self.menu.open()


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
        resultado.pop(1)  # Excluir tabela 'sqlite_sequence'
        resultado.pop(1)  # Excluir tabela 'produtos' utilizada como busca de itens

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
                                                                     pos_hint={'x': 0.1, 'y': .75},
                                                                     icon_size='18sp', icon_color='black',
                                                                     on_press=self.editar_nome_lista),
                                                        MDIconButton(icon='assets/x.ico', icon_size='15sp',
                                                                     text=linha[1], pos_hint={'x': 0.7, 'y': .75},
                                                                     on_press=self.excluir_lista),
                                                        MDIconButton(text=linha[1],
                                                                     icon='list-box-outline',
                                                                     icon_color='#ff5c00',
                                                                     pos_hint={'center_x': 0.5, 'y': .5},
                                                                     icon_size='80dp',
                                                                     on_press=self.lista_selecionada,
                                                                     size_hint=(.7, .15),
                                                                     halign='center'),
                                                        MDLabel(text=linha[1],
                                                                theme_text_color='Custom',
                                                                text_color="#df2100",
                                                                font_size='30dp',
                                                                halign='center',
                                                                adaptive_size=True,
                                                                pos_hint={'center_x': 0.5, 'y': .1},
                                                                size_hint=(0.6, .1))),
                                       size_hint=(0.8, .25), pos_hint={'x': 0.1, 'y': .4}, md_bg_color="#ffffff",
                                       line_color="ffcc21")

            self.inserir_layout.add_widget(self.label_tabela)
            self.lista.append(self.label_tabela)

        self.insere_swiper2 = MDSwiperItem()
        self.lista.append(self.insere_swiper2)
        self.ids.swiper.add_widget(self.insere_swiper2)
        self.ids.swiper.set_current(1)

    def lista_selecionada(self, instance):
        self.manager.get_screen('lista_atual').lista_em_uso = instance.text
        self.manager.get_screen('lista_atual').carregar_lista()
        self.manager.current = 'lista_atual'

    def editar_nome_lista(self, instance):
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
                    on_press=lambda x: (self.gravar_nome(self.entrada), self.dialog_lista2.dismiss())
                ),
            ],
        )
        self.dialog_lista2.open()

    def gravar_nome(self, entrada):
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()

        cursor.execute(f'ALTER TABLE {self.nome_anterior} RENAME TO {entrada.text}')
        conn.commit()
        self.minhas_listas(dt=None)

    def criar_nova_lista(self):
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
                    on_press=lambda x: (self.gravar_nova_lista(self.entrada), self.dialog_lista.dismiss())
                ),
            ],
        )
        self.dialog_lista.open()

    def gravar_nova_lista(self, entrada):
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

    def excluir_lista(self, instance):
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
                    on_press=lambda x: (self.gravar_exclusao(instance.text), self.dialog3.dismiss())
                ),
            ],
        )
        self.dialog3.open()

    def gravar_exclusao(self, entrada):
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
        self.resultado = None
        self.categoria = None

    def buscar_produtos(self, instance, item):
        self.categoria = item.text
        conn = sqlite3.connect('lista_compras')
        cursor = conn.cursor()
        cursor.execute('select * from produtos WHERE categoria = (?) order by produto ASC', (self.categoria,))
        self.resultado = cursor.fetchall()


class Produtos(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.produtos_selecionados = []

    def catalogo_produtos(self):
        self.ids.lista_produtos.clear_widgets()
        for item in self.manager.get_screen('pesquisar').resultado:
            self.ids.lista_produtos.add_widget(
                OneLineAvatarIconListItem(
                    IconLeftWidget(MDCheckbox(),
                                   icon_size='10sp',
                                   text=f"{item[1]}"
                                   ),
                    IconRightWidget(icon='assets/x.ico', icon_size='10sp',
                                    text=f"{item[1]}"),
                    text=f"{item[1]}", theme_text_color='Custom', text_color="#df2100", bg_color="#ffffff",
                    radius=[0, 10, 0, 10]
                )
            )
        # self.dados_listagem = MDDataTable(pos_hint={'x': 0.15, 'y': 0.2},
        #                                   size_hint=(.7, .6),
        #                                   rows_num=len(self.manager.get_screen('lista_atual').lista_produtos),
        #                                   background_color_header=get_color_from_hex("#ebf52a"),
        #                                   background_color_selected_cell=get_color_from_hex("#f5f7cd"),
        #                                   check=True,
        #                                   column_data=[("[color=#0d0d0d]Produto[/color]", dp(50))
        #                                                ],
        #                                   row_data=self.manager.get_screen('lista_atual').lista_produtos, elevation=1)
        #
        # self.ids.lista_produtos.add_widget(self.dados_listagem)

    def adicionar_itens(self):
        for item in reversed(self.ids.lista_produtos.children):
            if item.children[1].children[0].children[0].active:
                self.manager.get_screen('lista_atual').adicionar_item(item.children[1].children[0])
    

class WindowManager(ScreenManager):
    pass


class MinhaLista(MDApp):

    def build(self):
        # self.ref_lista_atual = ListaAtual()
        return Builder.load_file('main.kv')


MinhaLista().run()
