fa_numbers = '۱۲۳۴۵۶۷۸۹۰'
en_numbers = '1234567890'


def convert_fa_number_to_en(value: str) -> str:
    translation_table = str.maketrans(fa_numbers, en_numbers)
    return value.translate(translation_table)
