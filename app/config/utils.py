def get_str_case_by_count(value: int, form1, form2, form5):
    last_digit = int(str(value)[-1])
    prelast_digit = int(str(value)[-2]) if value > 9 else 0

    if last_digit == 1 and prelast_digit != 1:
        return form1
    if 2 <= last_digit <= 4 and prelast_digit == 1:
        return form5
    if 2 <= last_digit <= 4:
        return form2
    return form5
