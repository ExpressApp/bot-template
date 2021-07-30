"""Numeral macros."""

from collections import namedtuple
from enum import Enum, auto
from typing import List, Tuple


class Sex(Enum):
    male = auto()
    female = auto()


Unit = namedtuple("Unit", ["male", "female"])
UNITS = (  # Названия цифр, 1 и 2 имеют два рода
    Unit("ноль", "ноль"),
    Unit("один", "одна"),
    Unit("два", "две"),
    Unit("три", "три"),
    Unit("четыре", "четыре"),
    Unit("пять", "пять"),
    Unit("шесть", "шесть"),
    Unit("семь", "семь"),
    Unit("восемь", "восемь"),
    Unit("девять", "девять"),
)
TEENS = (  # Названия чисел, содержащих две цифры
    "десять",
    "одиннадцать",
    "двенадцать",
    "тринадцать",
    "четырнадцать",
    "пятнадцать",
    "шестнадцать",
    "семнадцать",
    "восемнадцать",
    "девятнадцать",
)
TENS = (  # Названия десятков
    "двадцать",
    "тридцать",
    "сорок",
    "пятьдесят",
    "шестьдесят",
    "семьдесят",
    "восемьдесят",
    "девяносто",
)
HUNDREDS = (  # Названия сотен
    "сто",
    "двести",
    "триста",
    "четыреста",
    "пятьсот",
    "шестьсот",
    "семьсот",
    "восемьсот",
    "девятьсот",
)
Order = namedtuple("Order", ["words", "sex"])
ORDERS = (  # Названия порядков и их род
    Order(("тысяча", "тысячи", "тысяч"), Sex.female),
    Order(("миллион", "миллиона", "миллионов"), Sex.male),
    Order(("миллиард", "миллиарда", "миллиардов"), Sex.male),
)
MINUS = "минус"


def _get_words_from_thousand(rest: int, sex: Sex) -> List[str]:
    """Преобразовывает тройку чисел в числительное с указанием рода."""
    words = []

    # Делим число на цифры
    unit = rest % 10
    ten = rest % 100 // 10
    hundred = rest // 100

    # Если последние две цифры превращаются в одно слово (напр. двенадцать)
    if 10 <= rest % 100 <= 19:
        words.append(TEENS[rest % 100 - 10])

        # Если сотни существуют
        if hundred:
            words.append(HUNDREDS[hundred - 1])
    else:
        # Слово ноль писать не нужно
        if unit != 0:
            if sex == Sex.male:
                unit_word = UNITS[unit].male
            else:
                unit_word = UNITS[unit].female

            words.append(unit_word)

        # Если десятки или сотни существуют
        if ten:
            words.append(TENS[ten - 2])
        if hundred:
            words.append(HUNDREDS[hundred - 1])

    return words


def _get_plural(thousand: int) -> int:  # type: ignore
    """Возвращает степень множественности.

    0: одна поликлиникА
    1: две, три, четыре поликлиникИ
    2: пять, ... поликлиник
    """
    # Для числительных из двух слов (двенадцать) последнее число не влияет
    if 10 <= thousand % 100 <= 19:
        return 2

    # Определяем множественность по последнему числу
    unit = thousand % 10
    if unit == 1:
        return 0
    elif 2 <= unit <= 4:
        return 1
    elif unit > 4:
        return 2


def get_numeral(number: int, sex: Sex = Sex.male) -> str:
    """Преобразовывает число в числительное.

    Возвращает числительное
    12342 - двенадцать тысяч триста сорок два
    2345, Sex.female - две тысячи триста сорок две
    """
    words = []
    position = 0
    rest = abs(number)

    while rest > 0:
        # Берем последние 3 числа
        thousand = rest % 1000
        # И степень множественности
        plural = _get_plural(thousand)

        if position == 0:
            # При первой итерации мы не добавляем порядок
            # и используем переданный род (одИН вагон, одНА поликлиника)
            words += _get_words_from_thousand(thousand, sex)
        else:
            # Добавляем порядок с полученной степенью множественности
            # (тысячА, тысяч, тысячИ)
            words.append(ORDERS[position - 1].words[plural])
            # Добавляем числительные с указанием их рода
            # (одНА тысяча, одИН миллион)
            words += _get_words_from_thousand(thousand, ORDERS[position - 1].sex)

        position += 1
        rest = int(rest / 1000)

    if number < 0:
        words.append(MINUS)

    words.reverse()
    return " ".join(words)


def agree_with_number(
    word: Tuple[str, str, str], number: int, by_first_number: bool = True
) -> str:
    """Согласовывает слово с числом.

    word - tuple из 3 слов со степенью множественности по возрастанию
    например: ("поликлиника", "поликлиники", "поликлиник")
    1 элемент используется при числе 1,
    2 элемент при числах 2-4,
    3 при всех остальных

    by_first_number, можно передать False и тогда согласование будет опираться
    на первую тройку цифр. Например, чтобы получить строку:
    "Найдена одна тысяча двести семьдесят пять",
    тут слово "найдена" смотрит на первую тройку ("001") и приводит слово к
    единственному числу.
    """
    if by_first_number:
        plural = _get_plural(number % 1000)
        return word[plural]

    while number >= 1000:
        number = int(number / 1000)

    plural = _get_plural(number)
    return word[plural]
