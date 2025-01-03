import flet as ft

# Lista para armazenar os usuários cadastrados
users = []

def main(page: ft.Page):
    page.title = "Sistema de Login e Menu Interativo"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#e6f7ff"

    def on_login_click(e):
        email = email_field.value
        password = password_field.value
        # Verificar se o usuário existe e se as credenciais estão corretas
        user = next((u for u in users if u["email"] == email and u["password"] == password), None)
        if user:
            show_user_page(user)  # Mostra a página do usuário
        else:
            dialog = ft.AlertDialog(title=ft.Text("Credenciais inválidas!"))
            page.dialog = dialog
            dialog.open = True
            page.update()

    def show_register_screen(e):
        def on_register_click(e):
            name = name_field.value
            email = email_field.value
            password = password_field.value

            if name and email and password:
                users.append({"name": name, "email": email, "password": password})
                dialog = ft.AlertDialog(title=ft.Text("Cadastro realizado com sucesso!"))
                page.dialog = dialog
                dialog.open = True
                page.views.pop()  # Voltar para a tela inicial
                page.update()
            else:
                dialog = ft.AlertDialog(title=ft.Text("Por favor, preencha todos os campos!"))
                page.dialog = dialog
                dialog.open = True
                page.update()

        def go_back_to_menu(e):
            page.views.pop()
            page.update()

        name_field = ft.TextField(label="Nome", hint_text="Digite seu nome completo", width=300)
        email_field = ft.TextField(label="Email", hint_text="Digite seu email", width=300)
        password_field = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)

        register_button = ft.ElevatedButton(text="Cadastrar", on_click=on_register_click)

        page.views.append(
            ft.View(
                "/register",
                controls=[
                    ft.Text("Tela de Cadastro", size=20, weight=ft.FontWeight.BOLD),
                    name_field,
                    email_field,
                    password_field,
                    ft.Row(
                        [
                            register_button,
                            ft.ElevatedButton(
                                text="Voltar ao Menu",
                                on_click=go_back_to_menu,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        )
        page.update()

    def show_user_page(user):
        def go_back_to_menu(e):
            page.views.pop()
            page.update()

        def show_menu_screen(title):
            dialog = ft.AlertDialog(title=ft.Text(f"Você clicou em: {title}"))
            page.dialog = dialog
            dialog.open = True
            page.update()

        # Layout em grade com botões e ícones
        grid = ft.GridView(
            expand=1,
            runs_count=2,  # Número de itens por linha (ajuste conforme necessário)
            spacing=20,  # Espaçamento horizontal entre os itens
            run_spacing=20,  # Espaçamento vertical entre os itens
            controls=[
                ft.ElevatedButton(
                    content=ft.Column(
                        [ft.Icon(ft.icons.BOOK, size=30), ft.Text("Agenda de Recados")],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    on_click=lambda _: show_menu_screen("Agenda de Recados"),
                    width=150,
                    height=150,
                    bgcolor="#ff6666",  # Cor de fundo
                ),
                ft.ElevatedButton(
                    content=ft.Column(
                        [ft.Icon(ft.icons.PERSON, size=30), ft.Text("Dados do Professor")],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    on_click=lambda _: show_menu_screen("Dados do Professor"),
                    width=150,
                    height=150,
                    bgcolor="#66b3ff",  # Cor de fundo
                ),
                ft.ElevatedButton(
                    content=ft.Column(
                        [ft.Icon(ft.icons.CALENDAR_MONTH, size=30), ft.Text("Calendário")],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    on_click=lambda _: show_menu_screen("Calendário"),
                    width=150,
                    height=150,
                    bgcolor="#99ff99",  # Cor de fundo
                ),
                ft.ElevatedButton(
                    content=ft.Column(
                        [ft.Icon(ft.icons.LOGIN, size=30), ft.Text("Menu de Entrada e Saída")],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    on_click=lambda _: show_menu_screen("Menu de Entrada e Saída"),
                    width=150,
                    height=150,
                    bgcolor="#ffcc66",  # Cor de fundo
                ),
                ft.ElevatedButton(
                    content=ft.Column(
                        [ft.Icon(ft.icons.PAYMENTS, size=30), ft.Text("Dia de Pagamento")],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    on_click=lambda _: show_menu_screen("Dia de Pagamento"),
                    width=150,
                    height=150,
                    bgcolor="#ff99cc",  # Cor de fundo
                ),
            ],
        )

        # Adicionando o GridView à view
        page.views.append(
            ft.View(
                f"/user/{user['name']}",
                controls=[
                    ft.Text(f"Bem-vindo, {user['name']}!", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Email: {user['email']}", size=16),
                    ft.Divider(),
                    grid,  # Layout em grade com botões
                    ft.ElevatedButton(text="Voltar ao Menu", on_click=go_back_to_menu),
                ],
                vertical_alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
        )
        page.update()

    avatar = ft.CircleAvatar(
        content=ft.Icon(name=ft.icons.PERSON, size=50),
        bgcolor="#003366",
        radius=40
    )

    email_field = ft.TextField(
        label="Email ID",
        hint_text="Digite seu email",
        width=300,
        prefix_icon=ft.icons.EMAIL,
    )

    password_field = ft.TextField(
        label="Senha",
        hint_text="Digite sua senha",
        password=True,
        can_reveal_password=True,
        width=300,
        prefix_icon=ft.icons.LOCK,
    )

    remember_me = ft.Checkbox(label="Remember me")
    forgot_password = ft.TextButton("Forgot Password?", on_click=lambda _: show_register_screen(None))

    login_button = ft.ElevatedButton(text="LOGIN", width=300, on_click=on_login_click)
    register_button = ft.TextButton(text="Cadastrar", on_click=show_register_screen)

    page.add(
        ft.Column(
            [
                avatar,
                email_field,
                password_field,
                ft.Row([remember_me, forgot_password], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                login_button,
                register_button,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
    )

ft.app(target=main)
