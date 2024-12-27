import flet as ft

# Lista para armazenar os usuários cadastrados
users = []


def main(page: ft.Page):
    page.title = "Login e Cadastro"
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

    def show_forgot_password_screen(e):
        def on_confirm_click(e):
            if email_field.value:
                dialog = ft.AlertDialog(title=ft.Text("Um link de redefinição foi enviado para o seu email."))
                page.dialog = dialog
                dialog.open = True
                page.views.pop()
                page.update()
            else:
                dialog = ft.AlertDialog(title=ft.Text("Por favor, insira um email válido."))
                page.dialog = dialog
                dialog.open = True
                page.update()

        def go_back_to_menu(e):
            page.views.pop()
            page.update()

        email_field = ft.TextField(label="Email", hint_text="Digite seu email cadastrado", width=300)

        confirm_button = ft.ElevatedButton(text="Confirmar", on_click=on_confirm_click)

        page.views.append(
            ft.View(
                "/forgot_password",
                controls=[
                    ft.Text("Redefinir Senha", size=20, weight=ft.FontWeight.BOLD),
                    email_field,
                    ft.Row(
                        [
                            confirm_button,
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

        def show_agenda_screen(e):
            dialog = ft.AlertDialog(title=ft.Text("Agenda de Recados"))
            page.dialog = dialog
            dialog.open = True
            page.update()

        def show_teacher_data_screen(e):
            dialog = ft.AlertDialog(title=ft.Text("Dados do Professor"))
            page.dialog = dialog
            dialog.open = True
            page.update()

        def show_calendar_screen(e):
            dialog = ft.AlertDialog(title=ft.Text("Calendário"))
            page.dialog = dialog
            dialog.open = True
            page.update()

        def show_entry_exit_screen(e):
            dialog = ft.AlertDialog(title=ft.Text("Menu de Entrada e Saída"))
            page.dialog = dialog
            dialog.open = True
            page.update()

        def show_payment_day_screen(e):
            dialog = ft.AlertDialog(title=ft.Text("Dia de Pagamento"))
            page.dialog = dialog
            dialog.open = True
            page.update()

        page.views.append(
            ft.View(
                f"/user/{user['name']}",
                controls=[
                    ft.Text(f"Bem-vindo, {user['name']}!", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Email: {user['email']}", size=16),
                    ft.ElevatedButton(text="Agenda de Recados", on_click=show_agenda_screen),
                    ft.ElevatedButton(text="Dados do Professor", on_click=show_teacher_data_screen),
                    ft.ElevatedButton(text="Calendário", on_click=show_calendar_screen),
                    ft.ElevatedButton(text="Menu de Entrada e Saída", on_click=show_entry_exit_screen),
                    ft.ElevatedButton(text="Dia de Pagamento", on_click=show_payment_day_screen),
                    ft.ElevatedButton(text="Voltar ao Menu", on_click=go_back_to_menu),
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
        label="Password",
        hint_text="Digite sua senha",
        password=True,
        can_reveal_password=True,
        width=300,
        prefix_icon=ft.icons.LOCK,
    )

    remember_me = ft.Checkbox(label="Remember me")
    forgot_password = ft.TextButton("Forgot Password?", on_click=show_forgot_password_screen)

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
