from typing import Union


class Password:
    def __init__(self, password: str):
        self.password = password

    def validate(self) -> Union[str, bool]:
        vals = {
            # "Password must contain an uppercase letter.": lambda s: any(x.isupper() for x in s),
            "Password must contain a lowercase letter.": lambda s: any(x.islower() for x in s),
            # "Password must contain a digit.": lambda s: any(x.isdigit() for x in s),
            # "Password must be at least 8 characters.": lambda s: len(s) >= 8,
            # "Password cannot contain white spaces.": lambda s: not any(x.isspace() for x in s),
        }
        valid = True
        for n, val in vals.items():
            if not val(self.password):
                valid = False
                return n
        return valid

    def compare(self, password_confirmation: str) -> Union[str, bool]:
        is_valid = self.validate()

        if is_valid is not True:
            return is_valid

        if self.password != password_confirmation:
            return "Password and password confirmation not match"

        return True
