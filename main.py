import os
import winreg

# Путь для хранения бэкапа реестра
BACKUP_FILE = "power_settings_backup.reg"
POWER_SETTINGS_PATH = r"SYSTEM\CurrentControlSet\Control\Power\PowerSettings"


def create_backup():
    """Создает резервную копию раздела реестра PowerSettings."""
    if not os.path.exists(BACKUP_FILE):
        print("Создаем резервную копию реестра...")
        try:
            # Экспорт раздела реестра в файл
            os.system(f'reg export "HKLM\\{POWER_SETTINGS_PATH}" {BACKUP_FILE}')
            print(f"Резервная копия успешно создана: {BACKUP_FILE}")
        except Exception as e:
            print(f"Ошибка при создании бэкапа: {e}")
    else:
        print(f"Бэкап уже существует: {BACKUP_FILE}")


def restore_backup():
    """Восстанавливает резервную копию реестра."""
    if os.path.exists(BACKUP_FILE):
        print("Восстанавливаем настройки из бэкапа...")
        try:
            # Импорт раздела реестра из файла
            os.system(f'reg import {BACKUP_FILE}')
            print("Настройки успешно восстановлены!")
        except Exception as e:
            print(f"Ошибка при восстановлении бэкапа: {e}")
    else:
        print("Бэкап не найден. Сначала создайте бэкап.")


def enable_hidden_power_settings():
    """Изменяет все значения Attributes с 1 на 2."""
    try:
        # Открываем раздел реестра
        power_settings_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, POWER_SETTINGS_PATH, 0, winreg.KEY_ALL_ACCESS)

        # Получаем количество подразделов (групп параметров)
        num_subkeys = winreg.QueryInfoKey(power_settings_key)[0]

        print("Начинаем обработку скрытых параметров...")

        for i in range(num_subkeys):
            # Получаем имя подраздела (GUID группы параметров)
            group_guid = winreg.EnumKey(power_settings_key, i)
            group_path = f"{POWER_SETTINGS_PATH}\\{group_guid}"

            # Открываем подраздел группы
            group_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, group_path, 0, winreg.KEY_ALL_ACCESS)

            # Получаем количество подразделов внутри группы (конкретные параметры)
            num_settings = winreg.QueryInfoKey(group_key)[0]

            for j in range(num_settings):
                # Получаем имя параметра (GUID параметра)
                setting_guid = winreg.EnumKey(group_key, j)
                setting_path = f"{group_path}\\{setting_guid}"

                # Открываем подраздел параметра
                setting_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, setting_path, 0, winreg.KEY_ALL_ACCESS)

                try:
                    # Читаем текущее значение Attributes
                    attributes, _ = winreg.QueryValueEx(setting_key, "Attributes")

                    if attributes == 1:
                        print(f"Изменяем Attributes для параметра: {setting_path}")

                        # Меняем значение Attributes с 1 на 2
                        winreg.SetValueEx(setting_key, "Attributes", 0, winreg.REG_DWORD, 2)
                except FileNotFoundError:
                    # Если ключ Attributes отсутствует, пропускаем
                    pass

                # Закрываем подраздел параметра
                winreg.CloseKey(setting_key)

            # Закрываем подраздел группы
            winreg.CloseKey(group_key)

        # Закрываем основной раздел
        winreg.CloseKey(power_settings_key)

        print("Все скрытые параметры успешно обработаны!")

    except Exception as e:
        print(f"Произошла ошибка: {e}")


def main_menu():
    """Главное меню скрипта."""
    while True:
        print("\n=== Главное меню ===")
        print("1. Открыть все скрытые параметры электропитания")
        print("2. Вернуть значения по умолчанию (восстановить бэкап)")
        print("3. Выход")

        choice = input("Выберите действие (1/2/3): ").strip()

        if choice == "1":
            create_backup()  # Создаем бэкап, если его еще нет
            enable_hidden_power_settings()
        elif choice == "2":
            restore_backup()
        elif choice == "3":
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


# Запуск скрипта
if __name__ == "__main__":
    main_menu()