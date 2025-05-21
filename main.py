#!/usr/bin/python

import random
import urllib.parse
import requests
from time import sleep
import os, signal, sys
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from rich.style import Style
import pystyle
from pystyle import Colors, Colorate

from carparktool import CarParkTool


def signal_handler(sig, frame):
    print("\n Bye Bye...")
    sys.exit(0)


def gradient_text(text, colors):
    lines = text.splitlines()
    height = len(lines)
    width = max(len(line) for line in lines)
    colorful_text = Text()
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            if char != " ":
                color_index = int(
                    (
                        (x / (width - 1 if width > 1 else 1))
                        + (y / (height - 1 if height > 1 else 1))
                    )
                    * 0.5
                    * (len(colors) - 1)
                )
                color_index = min(
                    max(color_index, 0), len(colors) - 1
                )  # Ensure the index is within bounds
                style = Style(color=colors[color_index])
                colorful_text.append(char, style=style)
            else:
                colorful_text.append(char)
        colorful_text.append("\n")
    return colorful_text


def banner(console):
    os.system("cls" if os.name == "nt" else "clear")
    brand_name = "Подпишись на канал @termcar"


    text = Text(brand_name, style="bold black")

    console.print(text)
    console.print(
        "[bold white] ============================================================[/bold white]"
    )
    console.print(
        "[bold yellow]      Пожалуйста, войдите в CPM перед использованием этого инструмента[/bold yellow]"
    )
    console.print("[bold red]      Совместное использование ключа доступа запрещено и будет заблокировано[/bold red]")
    console.print(
        "[bold white] ============================================================[/bold white]"
    )


def load_player_data(cpm):
    response = cpm.get_player_data()

    if response.get("ok"):
        data = response.get("data")

        if all(key in data for key in ["floats", "localID", "money"]):

            console.print(
                "[bold][red]========[/red][ ИНФОРМАЦИЯ ИГРОКА ][red]========[/red][/bold]"
            )

            console.print(
                f"[bold white]   >> Ник        : {data.get('Name', 'UNDEFINED')}[/bold white]"
            )
            console.print(
                f"[bold white]   >> LocalID     : {data.get('localID', 'UNDEFINED')}[/bold white]"
            )
            console.print(
                f"[bold white]   >> Денег      : {data.get('money', 'UNDEFINED')}[/bold white]"
            )
            console.print(
                f"[bold white]   >> Монет       : {data.get('coin', 'UNDEFINED')}[/bold white]"
            )
        else:
            console.print(
                "[bold red] '! ERROR: новые учетные записи должны быть зарегистрированы в игре хотя бы один раз (✘)[/bold red]"
            )
            exit(1)
    else:
        console.print(
            "[bold red] '! ERROR: seems like your login is not properly set !.[/bold red]"
        )
        exit(1)


def load_key_data(cpm):

    data = cpm.get_key_data()

    console.print(
        "[bold][red]========[/red][ ИНФОРМАЦИЯ О КЛЮЧЕ ][red]========[/red][/bold]"
    )

    console.print(
        f"[bold white]   >> Ключ  [/bold white]: [black]{data.get("access_key")}[/black]"
    )

    console.print(
        f"[bold white]   >> Telegram ID : {data.get('telegram_id')}[/bold white]"
    )

    console.print(
        f"[bold white]   >> Balance     : {data.get('coins') if not data.get('is_unlimited') else 'Unlimited'}[/bold white]"
    )


def prompt_valid_value(content, tag, password=False):
    while True:
        value = Prompt.ask(content, password=password)
        if not value or value.isspace():
            console.print(
                f"[bold red]{tag} cannot be empty or just spaces. Please try again (✘)[/bold red]"
            )
        else:
            return value


def load_client_details():
    response = requests.get("http://ip-api.com/json")
    data = response.json()
    console.print(
        "[bold red] =============[bold white][ ЛОКАЦИЯ ][/bold white]=============[/bold red]"
    )
    console.print(
        f"[bold white]    >> Страна    : {data.get('country')} {data.get('zip')}[/bold white]"
    )
    console.print(
        "[bold red] ===============[bold white][ МЕНЮ ][/bold white]===========[/bold red]"
    )


def interpolate_color(start_color, end_color, fraction):
    start_rgb = tuple(int(start_color[i : i + 2], 16) for i in (1, 3, 5))
    end_rgb = tuple(int(end_color[i : i + 2], 16) for i in (1, 3, 5))
    interpolated_rgb = tuple(
        int(start + fraction * (end - start)) for start, end in zip(start_rgb, end_rgb)
    )
    return "{:02x}{:02x}{:02x}".format(*interpolated_rgb)


def rainbow_gradient_string(customer_name):
    modified_string = ""
    num_chars = len(customer_name)
    start_color = "{:06x}".format(random.randint(0, 0xFFFFFF))
    end_color = "{:06x}".format(random.randint(0, 0xFFFFFF))
    for i, char in enumerate(customer_name):
        fraction = i / max(num_chars - 1, 1)
        interpolated_color = interpolate_color(start_color, end_color, fraction)
        modified_string += f"[{interpolated_color}]{char}"
    return modified_string


if __name__ == "__main__":
    console = Console()
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        banner(console)
        acc_email = prompt_valid_value(
            "[bold][?] Введите Email[/bold]", "Email", password=False
        )
        acc_password = prompt_valid_value(
            "[bold][?] Введите пароль[/bold]", "Password", password=False
        )
        acc_access_key = prompt_valid_value(
            "[bold][?] Введите ключ[/bold]", "Access Key", password=False
        )
        console.print("[bold yellow][%] Trying to Login[/bold yellow]: ", end=None)
        cpm = CarParkTool(acc_access_key)
        login_response = cpm.login(acc_email, acc_password)
        if login_response != 0:
            if login_response == 100:
                console.print("[bold red]УЧЕТНАЯ ЗАПИСЬ НЕ НАЙДЕНА. (✘)[/bold red]")
                sleep(2)
                continue
            elif login_response == 101:
                console.print("[bold red]НЕВЕРНЫЙ ПАРОЛЬ. (✘)[/bold red]")
                sleep(2)
                continue
            elif login_response == 103:
                console.print("[bold red]НЕДЕЙСТВИТЕЛЬНЫЙ КЛЮЧ. (✘)[/bold red]")
                sleep(2)
                continue
            else:
                console.print("[bold red]пробуйте снова[/bold red]")
                console.print(
                    "[bold yellow] '!Примечание: убедитесь, что вы заполнили все поля!.[/bold yellow]"
                )
                sleep(2)
                continue
        else:
            console.print("[bold green]УСПЕШНО (✔)[/bold green]")
            sleep(1)
        while True:
            banner(console)
            load_player_data(cpm)
            load_key_data(cpm)
            load_client_details()
            choices = [
                "00",
                "0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10",
                "11",
                "12",
                "13",
                "14",
                "15",
                "16",
                "17",
                "18",
                "19",
                "20",
                "21",
                "22",
                "23",
                "24",
                "25",
                "26",
            ]
            console.print(
                "[bold yellow][bold white](01)[/bold white]: Увеличить денег                [bold red]1.5K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](02)[/bold white]: Увеличить монет                [bold red]1.5K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](03)[/bold white]: Ранг Кинг                      [bold red]8K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](04)[/bold white]: Изменить ID                    [bold red]4.5K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](05)[/bold white]: Изменить имя                   [bold red]100[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](06)[/bold white]: Изменить имя (Радуга)          [bold red]100[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](07)[/bold white]: Номерные знаки                 [bold red]2K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](08)[/bold white]: Удалить учётную запись         [bold red]Free[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](09)[/bold white]: Регистр учетной записи         [bold red]Free[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](10)[/bold white]: Удалить друзей                 [bold red]500[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](11)[/bold white]: Разблокировать Lamborghinis (ios only) [bold red]5K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](12)[/bold white]: Разблокировать все автомобили          [bold red]6K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](13)[/bold white]: Разблокировать все автомобильные мигалки    [bold red]3.5K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](14)[/bold white]: Разблокировать двигатель W16       [bold red]4K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](15)[/bold white]: Разблокировать все гудки           [bold red]3K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](16)[/bold white]: Разблокировать отключить урон          [bold red]3K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](17)[/bold white]: Разблокировать неограниченное топливо       [bold red]3K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](18)[/bold white]: Разблокировать дома                  [bold red]4K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](19)[/bold white]: Разблокировать дым                   [bold red]4K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](20)[/bold white]: Разблокировать колеса                [bold red]4K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](21)[/bold white]: Разблокировать оборудования M        [bold red]3K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](22)[/bold white]: Разблокировать оборудования F        [bold red]3K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](23)[/bold white]: Изменить проигрывание в гонках       [bold red]1K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](24)[/bold white]: Изменить победы в гонках             [bold red]1K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](25)[/bold white]: Клонировать аккаунт                  [bold red]7K[/bold red][/bold yellow]"
            )
            console.print(
                "[bold yellow][bold white](0) [/bold white]: Выход из скрипта [/bold yellow]"
            )

            console.print(
                "[bold red]===============[bold white][ CPM Nevada ][/bold white]===============[/bold red]"
            )

            service = IntPrompt.ask(
                f"[bold][?] Select a Service [red][1-{choices[-1]} or 0][/red][/bold]",
                choices=choices,
                show_choices=False,
            )

            console.print(
                "[bold red]===============[bold white][ CPM Nevada ][/bold white]===============[/bold red]"
            )

            if service == 0:  # Exit
                console.print("[bold white] Thank You for using my tool[/bold white]")
            elif service == 1:  # Increase Money
                console.print(
                    "[bold yellow][bold white][?][/bold white] Insert how much money do you want[/bold yellow]"
                )
                amount = IntPrompt.ask("[?] Amount")
                console.print("[%] Saving your data: ", end=None)
                if amount > 0 and amount <= 500000000:
                    if cpm.set_player_money(amount):
                        console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                        console.print(
                            "[bold green]======================================[/bold green]"
                        )
                        answ = Prompt.ask(
                            "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                        )
                        if answ == "y":
                            console.print(
                                "[bold white] Thank You for using my tool[/bold white]"
                            )
                        else:
                            continue
                    else:
                        console.print("[bold red]FAILED (✘)[/bold red]")
                        console.print(
                            "[bold red]please try again later! (✘)[/bold red]"
                        )
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]FAILED (✘)[/bold red]")
                    console.print("[bold red]please use valid values! (✘)[/bold red]")
                    sleep(2)
                    continue
            elif service == 2:  # Increase Coins
                console.print(
                    "[bold yellow][bold white][?][/bold white] Insert how much coins do you want[/bold yellow]"
                )
                amount = IntPrompt.ask("[?] Amount")
                print("[ % ] Saving your data: ", end="")
                if amount > 0 and amount <= 500000:
                    if cpm.set_player_coins(amount):
                        console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                        console.print(
                            "[bold green]======================================[/bold green]"
                        )
                        answ = Prompt.ask(
                            "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                        )
                        if answ == "y":
                            console.print(
                                "[bold white] Thank You for using my tool[/bold white]"
                            )
                        else:
                            continue
                    else:
                        console.print("[bold red]FAILED[/bold red]")
                        console.print("[bold red]Please Try Again[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print(
                        "[bold yellow] 'Please use valid values[/bold yellow]"
                    )
                    sleep(2)
                    continue
            elif service == 3:  # King Rank
                console.print(
                    "[bold red][!] Note:[/bold red]: if the king rank doesn't appear in game, close it and open few times.",
                    end=None,
                )
                console.print(
                    "[bold red][!] Note:[/bold red]: please don't do King Rank on same account twice.",
                    end=None,
                )
                sleep(2)
                console.print("[%] Giving you a King Rank: ", end=None)
                if cpm.set_player_rank():
                    console.print("[bold yellow] 'SUCCESSFUL[/bold yellow]")
                    console.print(
                        "[bold yellow] '======================================[/bold yellow]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 4:  # Change ID
                console.print("[bold yellow] '[?] Enter your new ID[/bold yellow]")
                new_id = Prompt.ask("[?] ID")
                console.print("[%] Saving your data: ", end=None)
                if (
                    len(new_id) >= 8
                    and len(new_id)
                    <= 9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
                    and (" " in new_id) == False
                ):
                    if cpm.set_player_localid(new_id.upper()):
                        console.print("[bold yellow] 'SUCCESSFUL[/bold yellow]")
                        console.print(
                            "[bold yellow] '======================================[/bold yellow]"
                        )
                        answ = Prompt.ask(
                            "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                        )
                        if answ == "y":
                            console.print(
                                "[bold white] Thank You for using my tool[/bold white]"
                            )
                        else:
                            continue
                    else:
                        console.print("[bold red]FAILED[/bold red]")
                        console.print("[bold red]Please Try Again[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold yellow] 'Please use valid ID[/bold yellow]")
                    sleep(2)
                    continue
            elif service == 5:  # Change Name
                console.print("[bold yellow] '[?] Enter your new Name[/bold yellow]")
                new_name = Prompt.ask("[?] Name")
                console.print("[%] Saving your data: ", end=None)
                if len(new_name) >= 0 and len(new_name) <= 999999999:
                    if cpm.set_player_name(new_name):
                        console.print("[bold yellow] 'SUCCESSFUL[/bold yellow]")
                        console.print(
                            "[bold yellow] '======================================[/bold yellow]"
                        )
                        answ = Prompt.ask(
                            "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                        )
                        if answ == "y":
                            console.print(
                                "[bold white] Thank You for using my tool[/bold white]"
                            )
                        else:
                            continue
                    else:
                        console.print("[bold red]FAILED[/bold red]")
                        console.print("[bold red]Please Try Again[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print(
                        "[bold yellow] 'Please use valid values[/bold yellow]"
                    )
                    sleep(2)
                    continue
            elif service == 6:  # Change Name Rainbow
                console.print(
                    "[bold yellow] '[?] Enter your new Rainbow Name[/bold yellow]"
                )
                new_name = Prompt.ask("[?] Name")
                console.print("[%] Saving your data: ", end=None)
                if len(new_name) >= 0 and len(new_name) <= 999999999:
                    if cpm.set_player_name(rainbow_gradient_string(new_name)):
                        console.print("[bold yellow] 'SUCCESSFUL[/bold yellow]")
                        console.print(
                            "[bold yellow] '======================================[/bold yellow]"
                        )
                        answ = Prompt.ask(
                            "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                        )
                        if answ == "y":
                            console.print(
                                "[bold white] Thank You for using my tool[/bold white]"
                            )
                        else:
                            continue
                    else:
                        console.print("[bold red]FAILED[/bold red]")
                        console.print("[bold red]Please Try Again[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print(
                        "[bold yellow] 'Please use valid values[/bold yellow]"
                    )
                    sleep(2)
                    continue
            elif service == 7:  # Number Plates
                console.print("[%] Giving you a Number Plates: ", end=None)
                if cpm.set_player_plates():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 8:  # Account Delete
                console.print(
                    "[bold yellow] '[!] After deleting your account there is no going back !![/bold yellow]"
                )
                answ = Prompt.ask(
                    "[?] Do You want to Delete this Account ?!",
                    choices=["y", "n"],
                    default="n",
                )
                if answ == "y":
                    cpm.delete()
                    console.print("[bold yellow] 'SUCCESSFUL[/bold yellow]")
                    console.print(
                        "[bold yellow] '======================================[/bold yellow]"
                    )
                    console.print(
                        "[bold yellow] f'Thank You for using our tool, please join our telegram channe: @{__CHANNEL_USERNAME__}[/bold yellow]"
                    )
                else:
                    continue
            elif service == 9:  # Account Register
                console.print("[bold yellow] '[!] Registring new Account[/bold yellow]")
                acc2_email = prompt_valid_value(
                    "[?] Account Email", "Email", password=False
                )
                acc2_password = prompt_valid_value(
                    "[?] Account Password", "Password", password=False
                )
                console.print("[%] Creating new Account: ", end=None)
                status = cpm.register(acc2_email, acc2_password)
                if status == 0:
                    console.print("[bold yellow] 'SUCCESSFUL[/bold yellow]")
                    console.print(
                        "[bold yellow] '======================================[/bold yellow]"
                    )
                    console.print(
                        "[bold yellow] f'INFO: In order to tweak this account with Telmun[/bold yellow]"
                    )
                    console.print(
                        "[bold yellow] 'you most sign-in to the game using this account[/bold yellow]"
                    )
                    sleep(2)
                    continue
                elif status == 105:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print(
                        "[bold yellow] 'This email is already exists ![/bold yellow]"
                    )
                    sleep(2)
                    continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 10:  # Delete Friends
                console.print("[%] Deleting your Friends: ", end=None)
                if cpm.delete_player_friends():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 11:  # Unlock All Lamborghinis
                console.print(
                    "[!] Note: this function takes a while to complete, please don't cancel.",
                    end=None,
                )
                console.print("[%] Unlocking All Lamborghinis: ", end=None)
                if cpm.unlock_all_lamborghinis():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 12:  # Unlock All Cars
                console.print("[%] Unlocking All Cars: ", end=None)
                if cpm.unlock_all_cars():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 13:  # Unlock All Cars Siren
                console.print("[%] Unlocking All Cars Siren: ", end=None)
                if cpm.unlock_all_cars_siren():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 14:  # Unlock w16 Engine
                console.print("[%] Unlocking w16 Engine: ", end=None)
                if cpm.unlock_w16():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 15:  # Unlock All Horns
                console.print("[%] Unlocking All Horns: ", end=None)
                if cpm.unlock_horns():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 16:  # Disable Engine Damage
                console.print("[%] Unlocking Disable Damage: ", end=None)
                if cpm.disable_engine_damage():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 17:  # Unlimited Fuel
                console.print("[%] Unlocking Unlimited Fuel: ", end=None)
                if cpm.unlimited_fuel():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 18:  # Unlock House 3
                console.print("[%] Unlocking House 3: ", end=None)
                if cpm.unlock_houses():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 19:  # Unlock Smoke
                console.print("[%] Unlocking Smoke: ", end=None)
                if cpm.unlock_smoke():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 20:  # Unlock Smoke
                console.print("[%] Unlocking Wheels: ", end=None)
                if cpm.unlock_wheels():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(8)
            elif service == 21:  # Unlock Smoke
                console.print("[%] Unlocking Equipaments Male: ", end=None)
                if cpm.unlock_equipments_male():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 22:  # Unlock Smoke
                console.print("[%] Unlocking Equipaments Female: ", end=None)
                if cpm.unlock_equipments_female():
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print("[bold red]Please Try Again[/bold red]")
                    sleep(2)
                    continue
            elif service == 23:  # Change Races Wins
                console.print(
                    "[bold yellow] '[!] Insert how much races you win[/bold yellow]"
                )
                amount = IntPrompt.ask("[?] Amount")
                console.print("[%] Changing your data: ", end=None)
                if (
                    amount > 0
                    and amount
                    <= 999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
                ):
                    if cpm.set_player_wins(amount):
                        console.print("[bold yellow] 'SUCCESSFUL[/bold yellow]")
                        console.print(
                            "[bold yellow] '======================================[/bold yellow]"
                        )
                        answ = Prompt.ask(
                            "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                        )
                        if answ == "y":
                            console.print(
                                "[bold white] Thank You for using my tool[/bold white]"
                            )
                        else:
                            continue
                    else:
                        console.print("[bold red]FAILED[/bold red]")
                        console.print("[bold red]Please Try Again[/bold red]")
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print(
                        "[bold yellow] '[!] Please use valid values[/bold yellow]"
                    )
                    sleep(2)
                    continue
            elif service == 24:  # Change Races Loses
                console.print(
                    "[bold yellow] '[!] Insert how much races you lose[/bold yellow]"
                )
                amount = IntPrompt.ask("[?] Amount")
                console.print("[%] Changing your data: ", end=None)
                if (
                    amount > 0
                    and amount
                    <= 999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
                ):
                    if cpm.set_player_loses(amount):
                        console.print("[bold yellow] 'SUCCESSFUL[/bold yellow]")
                        console.print(
                            "[bold yellow] '======================================[/bold yellow]"
                        )
                        answ = Prompt.ask(
                            "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                        )
                        if answ == "y":
                            console.print(
                                "[bold white] Thank You for using my tool[/bold white]"
                            )
                        else:
                            continue
                    else:
                        console.print("[bold red]FAILED[/bold red]")
                        console.print(
                            "[bold yellow] '[!] Please use valid values[/bold yellow]"
                        )
                        sleep(2)
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print(
                        "[bold yellow] '[!] Please use valid values[/bold yellow]"
                    )
                    sleep(2)
                    continue
            elif service == 25:  # Clone Account
                console.print(
                    "[bold yellow] '[!] Please Enter Account Detalis[/bold yellow]"
                )
                to_email = prompt_valid_value(
                    "[?] Account Email", "Email", password=False
                )
                to_password = prompt_valid_value(
                    "[?] Account Password", "Password", password=False
                )
                console.print("[%] Cloning your account: ", end=None)
                if cpm.account_clone(to_email, to_password):
                    console.print("[bold green]SUCCESSFUL (✔)[/bold green]")
                    console.print(
                        "[bold green]======================================[/bold green]"
                    )
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print(
                        "[bold yellow] '[!] THAT RECIEVER ACCOUNT IS GMAIL PASSWORD IS NOT VALID OR THAT ACCOUNT IS NOT REGISTERED[/bold yellow]"
                    )
                    sleep(2)
                    continue
            elif service == 26:
                console.print(
                    "[bold yellow][!] Note[/bold yellow]: original speed can not be restored!."
                )
                console.print("[bold yellow][!] Enter Car Details.[/bold yellow]")
                car_id = IntPrompt.ask("[bold][?] Car Id[/bold]")
                new_hp = IntPrompt.ask("[bold][?]Enter New HP[/bold]")
                new_inner_hp = IntPrompt.ask("[bold][?]Enter New Inner Hp[/bold]")
                new_nm = IntPrompt.ask("[bold][?]Enter New NM[/bold]")
                new_torque = IntPrompt.ask("[bold][?]Enter New Torque[/bold]")
                console.print(
                    "[bold yellow][%] Hacking Car Speed[/bold yellow]:", end=None
                )
                if cpm.hack_car_speed(car_id, new_hp, new_inner_hp, new_nm, new_torque):
                    console.print("[bold green]SUCCESFUL (✔)[/bold green]")
                    console.print("================================")
                    answ = Prompt.ask(
                        "[?] Do You want to Exit ?", choices=["y", "n"], default="n"
                    )
                    if answ == "y":
                        console.print(
                            "[bold white] Thank You for using my tool[/bold white]"
                        )
                    else:
                        continue
                else:
                    console.print("[bold red]FAILED[/bold red]")
                    console.print(
                        "[bold yellow] '[!] Please use valid values[/bold yellow]"
                    )
                    sleep(2)
                    continue
            else:
                continue
            break
        break
