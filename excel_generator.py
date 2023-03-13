import random
from openpyxl import Workbook

positions = {
    "Генеральный директор/Управляющий директор": 2,
    "Операционный менеджер": 4,
    "Менеджер по персоналу": 3,
    "Бухгалтер/бухгалтер": 5,
    "Менеджер по маркетингу": 2,
    "Менеджер по продажам": 4,
    "Менеджер по работе с клиентами": 3,
    "Административный помощник": 5,
    "IT/техническая поддержка": 4,
    "Графический дизайнер": 3,
    "Веб-разработчик": 2,
    "Писатель контента": 3,
    "Менеджер социальных сетей": 2,
    "Менеджер по складу/инвентаризации": 3,
    "Менеджер по производству": 2,
    "Специалист по контролю качества": 3,
    "Клерк по отгрузке и приемке": 4,
    "Специалист по закупкам": 3,
    "Receptionist": 5,
    "Менеджер по развитию бизнеса": 2,
}


def generate_employee():
    position = random.choice(list(positions.keys()))
    positions[position] -= 1
    if positions[position] == 0:
        del positions[position]

    if "Manager" in position:
        sex = random.choice(["M", "F"])
    else:
        sex = "F" if random.random() < 0.5 else "M"

    if sex == "M":
        names = ["Даниил", "Петр", "Алексей", "Дмитрий", "Максим", "Сергей", "Марк"]
        surnames = [
            "Жданов",
            "Андронов",
            "Оглоблин",
            "Кварацхелия",
            "Висягин",
            "Клевцов",
            "Савельев",
            "Гумеров",
        ]
        patronymics = [
            "Иванович",
            "Петрович",
            "Алексеевич",
            "Дмитриевич",
            "Максимович",
            "Сергеевич",
            "Камилевич",
        ]

    else:
        names = ["Диана", "Милана", "Алина", "Кристина", "Виктория", "Татьяна"]
        surnames = [
            "Жданова",
            "Андронова",
            "Оглоблина",
            "Кварацхелия",
            "Висягина",
            "Клевцова",
            "Савельева",
        ]
        patronymics = [
            "Ивановна",
            "Петровна",
            "Алексеевна",
            "Дмитриевна",
            "Максимовна",
            "Сергеевна",
        ]

    name = random.choice(names)
    surname = random.choice(surnames)
    patronymic = random.choice(patronymics)

    birthday_data = (
        f"{random.randint(1, 31)}.{random.randint(1, 12)}.{random.randint(1960, 2000)}"
    )

    passport_series = "".join(random.choices("0123456789", k=4))
    passport_number = "".join(random.choices("0123456789", k=6))
    passport_data = f"{passport_series} {passport_number}"

    tin = "".join(random.choices("0123456789", k=10))

    phone = f"+7-(9{random.randint(10, 99)})-{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"

    return [
        position,
        name,
        surname,
        patronymic,
        birthday_data,
        passport_data,
        tin,
        phone,
    ]


wb = Workbook()
ws = wb.active
ws.append(
    [
        "Должность",
        "Имя",
        "Фамилия",
        "Отчество",
        "Дата рождения",
        "Паспортные данные",
        "Номер ИНН",
        "Телефонный номер",
    ]
)

num_employees = random.randint(20, 30)
for i in range(num_employees):
    employee_data = generate_employee()
    ws.append(employee_data)
wb.save("employees1.xlsx")

print(f"{num_employees} employees generated and saved to employees.xlsx")
