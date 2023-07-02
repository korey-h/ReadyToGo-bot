from config import REG_MESSAGE


def about_reg(reg_process_obj) -> str:
    name = reg_process_obj.race['name']
    return REG_MESSAGE['lets_reg'] % (name)
