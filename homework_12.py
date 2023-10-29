from collections import UserDict
from datetime import datetime
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

class Phone(Field):
    def __init__(self, phone):
        if self.validate_phone(phone):
            self.value = phone
        else:
            raise ValueError("Номер телефону недійсний.")

    @staticmethod
    def validate_phone(phone):
        if phone.isdigit() and len(phone) == 10:
            return True
        return False

class Birthday(Field):
    def __init__(self, birthday=None):
        super().__init__(birthday)

    @Field.value.setter
    def value(self, new_birthday):
        if self.validate_birthday(new_birthday):
            self._value = new_birthday
        else:
            raise ValueError("Некоректна дата народження.")

    @staticmethod
    def validate_birthday(birthday):
        try:
            datetime.strptime(birthday, "%Y-%m-%d")
            return True
        except ValueError:
            return False

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        if birthday:
            self.birth_date = Birthday(birthday)  
        else:
            self.birth_date = None

    def add_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        print("Такий номер телефону не знайдений.")

    def edit_name(self, new_name):
        self.name = Name(new_name)

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                self.phones.remove(phone)  
                self.add_phone(new_phone)  
                return
        self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def days_to_birthday(self):
        if self.birth_date and isinstance(self.birth_date, Birthday) and self.birth_date.value:
            today = datetime.today()
            birth_date = datetime.strptime(self.birth_date.value, "%Y-%m-%d")
            next_birthday = datetime(today.year, birth_date.month, birth_date.day)
            if next_birthday < today:
                next_birthday = datetime(today.year + 1, birth_date.month, birth_date.day)
            days_remaining = (next_birthday - today).days
            return days_remaining
        return None

class AddressBook(UserDict):
    def add_record(self, record):
        if record.name.value in self.data:
            print("Запис з таким іменем вже існує.")
        else:
            self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            print(f"Запис з іменем {name} не знайдений.")

    def iterator(self, n=10):
        records = list(self.data.values())
        total_records = len(records)
        start = 0

        while start < total_records:
            yield records[start:start + n]
            start += n
    
    def save_to_file(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)

    def load_from_file(self, filename):
        try:
            with open(filename, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            print(f"Файл '{filename}' не знайдений. Створюємо новий список контактів.")
            self.data = {}

    def search(self, query):
        matching_records = []
        for record in self.data.values():
            if query in record.name.value:
                matching_records.append(record)
            for phone in record.phones:
                if query in phone.value:
                    matching_records.append(record)
        return matching_records

def main():
    address_book = AddressBook()

    try:
        address_book.load_from_file('address_book.pickle')
    except Exception as e:
        print(f"Помилка при завантаженні з файлу: {e}")

    instruction = """
    Вітаю! Я ваш бот-помічник. Ось, що я можу для вас зробити:

    1. Додавати контакти та номери телефонів. Для цього використовуйте команду 'add'. 

    2. Показувати вам список всіх контактів та їх номерів телефонів. 
    Для цього використовуйте команду 'show all'.

    3. Змінювати номер існуючого контакту. Використовуйте команду 'change'.

    4. Виводити номер телефону для зазначеного контакту. Використовуйте команду 'phone'.

    5. Виводити дні до наступного дня народження для зазначеного контакту. Використовуйте команду 'birthday'.

    6. Для завершення роботи введіть, good bye, exit, bye, close або вийти.

    Будь ласка, користуйтесь цими командами для взаємодії зі мною. 
    Я готовий допомогти вам у керуванні вашими контактами.
    """

    print(instruction)

    while True:
        user_input = input("Введіть команду: ").lower()

        if user_input in ('вийти', 'good bye', 'close', 'exit', 'bye'):
            print("Good bye")
            break
        elif user_input == 'привіт' or user_input == 'hello':
            print("How can I help you?")
        elif user_input.startswith('add '):
            parts = user_input[4:].split()
            name = parts[0]
            phones = []
            birthday = None
            for arg in parts[1:]:
                if "-" in arg:  
                    birthday = arg
                else:
                    phones.append(arg)
            record = Record(name, birthday)
            for phone in phones:
                record.add_phone(phone)
            address_book.add_record(record)
            print(f"Контакт {name} з номерами {', '.join(phones)} та датою народження {birthday} доданий.")
        elif user_input.startswith('change '):
            parts = user_input[7:].split()
            if len(parts) == 2:
                name = parts[0]
                new_phone = parts[1]
                if name in address_book.data:
                    record = address_book.data[name]
                    record.edit_phone(record.find_phone(new_phone), new_phone)
                    print(f"Номер телефону для контакту {name} змінено на {new_phone}")
                else:
                    print(f"Контакт з ім'ям {name} не знайдений.")
            else:
                print("Для команди 'change' потрібно вказати ім'я контакту та новий номер телефону.")
        elif user_input.startswith('phone '):
            name = user_input[6:]
            if name in address_book.data:
                record = address_book.data[name]
                phone_list = [str(phone.value) for phone in record.phones]
                print(f"Номер телефону для контакту {name}: {', '.join(phone_list)}")
            else:
                print(f"Контакт з ім'ям {name} не знайдений.")
        elif user_input.startswith('birthday '):
            name = user_input[9:]
            if name in address_book.data:
                record = address_book.data[name]
                days_to_birthday = record.days_to_birthday()
                if days_to_birthday is not None:
                    print(f"Дні до наступного дня народження для контакту {name}: {days_to_birthday} днів")
                else:
                    print(f"Для контакту {name} не вказана дата народження.")
            else:
                print(f"Контакт з ім'ям {name} не знайдений.")
        elif user_input == 'show all':
            if not address_book.data:
                print("Список контактів порожній.")
            else:
                for i, batch in enumerate(address_book.iterator(), 1):
                    print(f"Сторінка {i}:")
                    for record in batch:
                        phone_list = [str(phone.value) for phone in record.phones]
                        print(f"{record.name.value}: {', '.join(phone_list)}")
        else:
            print("Спробуйте ще раз.")

    address_book.save_to_file('address_book.pickle')

if __name__ == "__main__": 
    main()