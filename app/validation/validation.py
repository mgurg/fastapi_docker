import datetime
import json
import re
import sys


class Validation:
    # List to store the error messages in
    errors = []

    error_message_templates = {}

    def validate(self, data, rules, custom_messages=None):
        """Validate the 'data' according to the 'rules' given, returns a list of errors named 'errors'"""

        self.error_message_templates = self.load_json_file("error_message_templates.json")

        if not custom_messages:
            self.custom_error_messages = self.load_json_file("custom_error_messages.json")
        else:
            self.custom_error_messages = custom_messages

        # iterate through the rules dictionary, fetching each rule name (dictionary key) one by one
        for field_name in rules:

            # fetch the rule (value of dictionary element) from "rules" dictionary for the current rule name (dictionary key) and split it to get a list
            field_rules = rules[field_name].split("|")

            # field_errors will keep the errors for a particular field, which will be appended to the main "errors" list
            field_errors = []

            # now looping through rules of one field one rule at a time with each iteration
            for rule in field_rules:

                # validate the data based on the rule assigned

                if rule.startswith("after"):
                    field_errors.extend(self.__validate_after_date_fields(data, field_name, field_rules, rule))

                elif rule == "alpha":
                    field_errors.extend(self.__validate_alpha_fields(data, field_name))

                elif rule == "alpha_num":
                    field_errors.extend(self.__validate_alpha_num_fields(data, field_name))

                elif rule.startswith("before"):
                    field_errors.extend(self.__validate_before_date_fields(data, field_name, field_rules, rule))

                elif rule.startswith("between"):
                    field_errors.extend(self.__validate_between_fields(data, field_name, rule))

                elif rule == "boolean":
                    field_errors.extend(self.__validate_boolean_fields(data, field_name))

                elif rule.startswith("confirmed"):
                    field_errors.extend(self.__validate_confirmed_fields(data, field_name))

                elif rule == "date":
                    field_errors.extend(self.__validate_date_fields(data, field_name, field_rules))

                elif rule == "digits":
                    field_errors.extend(self.__validate_integer_fields(data, field_name))

                elif rule.startswith("different"):
                    field_errors.extend(self.__validate_different_fields(data, field_name, rule))

                elif rule == "email":
                    field_errors.extend(self.__validate_email_fields(data, field_name))

                elif rule.startswith("in"):
                    field_errors.extend(self.__validate_in_fields(data, field_name, rule))

                elif rule == "ip":
                    field_errors.extend(self.__validate_ip_fields(data, field_name))

                elif rule.startswith("max"):
                    field_errors.extend(self.__validate_max_fields(data, field_name, rule))

                elif rule.startswith("min"):
                    field_errors.extend(self.__validate_min_fields(data, field_name, rule))

                elif rule.startswith("not_in"):
                    field_errors.extend(self.__validate_not_in_fields(data, field_name, rule))

                elif rule == "present":
                    field_errors.extend(self.__validate_present_fields(data, field_name))

                elif rule == "phone":
                    field_errors.extend(self.__validate_phone_fields(data, field_name))

                elif rule.startswith("regex"):
                    field_errors.extend(self.__validate_regex_fields(data, field_name, rule))

                elif rule == "required":
                    field_errors.extend(self.__validate_required_fields(data, field_name))

                elif rule.startswith("same"):
                    field_errors.extend(self.__validate_same_fields(data, field_name, rule))

                elif rule.startswith("size"):
                    field_errors.extend(self.__validate_size_fields(data, field_name, rule))

                elif rule == "website":
                    field_errors.extend(self.__validate_website_fields(data, field_name))

            self.errors.extend(field_errors)

        return self.errors

    def __validate_required_fields(self, data, field_name):
        """Used for validating required fields, returns a list of error messages"""

        errs = []
        try:
            if data[field_name] == "":
                errs.append(self.return_field_message(field_name, "required"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "required"))

        return errs

    def __validate_date_fields(self, data, field_name, field_rules):
        """Used for validating date fields, returns a list of error messages"""

        errs = []
        date_format = self.retrieve_date_format(field_rules)

        try:
            datetime.datetime.strptime(data[field_name], date_format)
        except ValueError:
            errs.append(self.return_field_message(field_name, "date"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "date"))

        return errs

    def __validate_before_date_fields(self, data, field_name, field_rules, rule):
        """Used for validating fields for a date before the specified date value, returns a list of error messages"""

        # retrieve the value for that before rule
        before_date_value = rule.split(":")[1]

        errs = []
        date_format = self.retrieve_date_format(field_rules)

        try:
            date_entered = datetime.datetime.strptime(data[field_name], date_format).date()
            before_date = datetime.datetime.strptime(before_date_value, date_format).date()

            if date_entered >= before_date:
                errs.append(self.return_field_message(field_name, "before"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "before"))
        except ValueError:
            # because the value will not be a valid date according to the format
            errs.append(self.return_field_message(field_name, "date"))

        return errs

    def __validate_after_date_fields(self, data, field_name, field_rules, rule):
        """Used for validating fields for a date after the specified date value, returns a list of error messages"""

        # retrieve the value for that after rule
        after_date_value = rule.split(":")[1]

        errs = []
        date_format = self.retrieve_date_format(field_rules)

        try:
            date_entered = datetime.datetime.strptime(data[field_name], date_format).date()
            after_date = datetime.datetime.strptime(after_date_value, date_format).date()

            if date_entered <= after_date:
                errs.append(self.return_field_message(field_name, "after"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "after date"))
        except ValueError:
            # because the value will not be a valid date according to the format
            errs.append(self.return_field_message(field_name, "date"))

        return errs

    def __validate_integer_fields(self, data, field_name):
        """Used for validating integer fields, returns a list of error messages"""

        errs = []
        try:
            if not data[field_name].isdigit():
                errs.append(self.return_field_message(field_name, "integer"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "integer"))
        return errs

    def __validate_email_fields(self, data, field_name):
        """Used for validating email fields, returns a list of error messages"""

        regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        errs, result = self.match_regular_expression(regex, data[field_name], "website")

        # in case the RE did not match or their was a key error
        if not result:
            errs.append(self.return_field_message(field_name, "email"))
        return errs

    def __validate_regex_fields(self, data, field_name, rule):
        """Used for validating field data to match a regular expression, returns a list of error messages"""

        regex = str(rule.split(":")[1])
        errs, result = self.match_regular_expression(regex, data[field_name], "regex")

        # in case the RE did not match or their was a key error
        if not result:
            errs.append(self.return_field_message(field_name, "regex"))
        return errs

    def __validate_present_fields(self, data, field_name):
        """Used for validating present fields, returns a list of error messages"""

        errs = []
        try:
            if not data.__contains__(field_name):
                errs.append(self.return_field_message(field_name, "present"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "present"))

        return errs

    def __validate_boolean_fields(self, data, field_name):
        """Used for validating boolean fields, returns a list of error messages"""

        errs = []
        bool_values = [1, 0, "1", "0", "false", "true", False, True]

        try:
            if data[field_name] not in bool_values:
                errs.append(self.return_field_message(field_name, "boolean"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "boolean"))
        return errs

    def __validate_ip_fields(self, data, field_name):
        """Used for validating fields having IP Address, returns a list of error messages"""

        regex = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
        errs, result = self.match_regular_expression(regex, data[field_name], "ip")

        # in case the RE did not match or their was a key error
        if not result:
            errs.append(self.return_field_message(field_name, "ip"))
        return errs

    def __validate_phone_fields(self, data, field_name):
        """Used for validating fields having phone numbers, returns a list of error messages"""

        regex = r"^(?:\+?93)?[07]\d{9,13}$"
        errs, result = self.match_regular_expression(regex, data[field_name], "phone")

        # in case the RE did not match or their was a key error
        if not result:
            errs.append(self.return_field_message(field_name, "phone"))

        return errs

    def __validate_website_fields(self, data, field_name):
        """Used for validating fields having website addresses, returns a list of error messages"""

        regex = r"(http(s)?://)?([\w-]+\.)+[\w-]+[\w-]+[\.]+[\.com]+([./?%&=]*)?"
        errs, result = self.match_regular_expression(regex, data[field_name], "website")

        # in case the RE did not match or their was a key error
        if not result:
            errs.append(self.return_field_message(field_name, "website"))

        return errs

    def __validate_alpha_fields(self, data, field_name):
        """Used for validating fields for alphabets only, returns a list of error messages"""

        errs = []
        try:
            if not data[field_name].isalpha():
                errs.append(self.return_field_message(field_name, "alpha"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "alpha"))

        return errs

    def __validate_alpha_num_fields(self, data, field_name):
        """Used for validating fields for alphabets and numbers, returns a list of error messages"""

        errs = []
        try:
            if not data[field_name].isalnum():
                errs.append(self.return_field_message(field_name, "alpha_num"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "alpha numeric"))

        return errs

    def __validate_max_fields(self, data, field_name, rule):
        """Used for validating fields for a maximum integer value, returns a list of error messages"""

        # retrieve the value for that max rule
        max_value = int(rule.split(":")[1])

        errs = []
        try:
            if data[field_name].isdigit():
                if int(data[field_name]) > max_value:
                    errs.append(self.return_field_message(field_name, "max"))
            else:
                if len(data[field_name]) > max_value:
                    errs.append(self.return_field_message(field_name, "max"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "maximum"))

        return errs

    def __validate_min_fields(self, data, field_name, rule):
        """Used for validating fields for a minimum integer value, returns a list of error messages"""

        # retrieve the value for that min rule
        min_value = int(rule.split(":")[1])

        errs = []
        try:
            if data[field_name].isdigit():
                if int(data[field_name]) < min_value:
                    errs.append(self.return_field_message(field_name, "min"))
            else:
                if len(data[field_name]) < min_value:
                    errs.append(self.return_field_message(field_name, "min"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "minimum"))

        return errs

    def __validate_confirmed_fields(self, data, field_name):
        """if the field under validation is a password, a matching password_confirmation field must be present in the data,
        returns a list of error messages"""

        errs = []
        confirmation_field = field_name + "_confirmation"

        try:
            if confirmation_field not in data.keys():
                errs.append(self.return_field_message(field_name, "confirmed"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "confirmed"))
        return errs

    def __validate_size_fields(self, data, field_name, rule):
        """Used for validating fields for a maximum number of characters in a string value, returns a list of error messages"""

        errs = []
        try:
            # retrieve the value for that size rule
            size_value = int(rule.split(":")[1])

            if len(data[field_name]) >= size_value:
                errs.append(self.return_field_message(field_name, "size"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "size"))
        except ValueError:
            errs.append(self.return_field_message(field_name, "size"))

        return errs

    def __validate_not_in_fields(self, data, field_name, rule):
        """Used for validating fields for some number of values to avoid, returns a list of error messages"""

        # retrieve the value for that not_in rule
        ls = rule.split(":")[1].split(",")
        errs = []

        try:
            if data[field_name] in ls:
                errs.append(self.return_field_message(field_name, "not_in"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "not_in"))

        return errs

    def __validate_in_fields(self, data, field_name, rule):
        """Used for validating fields for some number of values to allow, returns a list of error messages"""

        # retrieve the value for that in rule
        ls = rule.split(":")[1].split(",")
        errs = []

        try:
            if data[field_name] not in ls:
                errs.append(self.return_field_message(field_name, "in"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "in"))
        return errs

    def __validate_different_fields(self, data, field_name, rule):
        """Used for validating fields whose value should be different than the value of some other field, returns a list of error messages"""

        # retrieve the value for the different rule
        ls = rule.split(":")[1].split(",")[0]
        errs = []

        try:
            if data[field_name] == data[ls]:
                errs.append(self.return_field_message(field_name, "different"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "different"))
        except Exception:
            errs.append("Error Occured", sys.exc_info())

        return errs

    def __validate_same_fields(self, data, field_name, rule):
        """Used for validating fields whose value should be the same as some other field value, returns a list of error messages"""

        # retrieve the value for the same rule
        ls = rule.split(":")[1].split(",")
        errs = []

        try:
            if data[field_name] != data[ls[0]]:
                errs.append(self.return_field_message(field_name, "same"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "same"))
        return errs

    def __validate_between_fields(self, data, field_name, rule):
        """Used for validating fields for a number between two digits to allow, returns a list of error messages"""

        # retrieve the value for the between rule
        ls = rule.split(":")[1].split(",")
        errs = []

        try:
            if int(data[field_name]) < int(ls[0]) or int(data[field_name]) > int(ls[1]):
                errs.append(self.return_field_message(field_name, "between"))
        except KeyError:
            errs.append(self.return_no_field_message(field_name, "between"))
        except ValueError:
            errs.append(field_name + " can not be empty")
        return errs

    def retrieve_date_format(self, field_rules):

        # loop through each rule for the particular field to check if there is any date_format rule assigned
        for rule in field_rules:
            # if there is a date_format rule assigned then fetch the date format from that
            if rule.startswith("date_format"):
                df_format_index = field_rules.index(rule)
                date_format = field_rules[df_format_index].split(":")[1]
                return date_format

        # if no date_format found, return the default date format
        return "%m/%d/%Y"

    def match_regular_expression(self, regex, field_name, rule_name):

        comp_re = re.compile(regex, re.IGNORECASE)
        errs = []

        try:
            result = comp_re.match(field_name)
        except KeyError:
            errs.append(self.return_no_field_message(field_name, rule_name))
            result = "error"

        return errs, result

    def load_json_file(self, file_name):
        f = open("./app/validation/" + file_name)
        t = f.read()
        f.close()
        return json.loads(t)

    def return_no_field_message(self, field_name, rule_name):
        if self.custom_error_messages.__contains__(field_name + ".no_field"):
            return self.custom_error_messages[field_name + ".no_field"]
        else:
            return self.error_message_templates["no_field"] % (field_name, rule_name)

    def return_field_message(self, field_name, rule_name):
        if self.custom_error_messages.__contains__(field_name + "." + rule_name):
            return self.custom_error_messages[field_name + "." + rule_name]
        else:
            return self.error_message_templates[rule_name] % (field_name)

    def is_valid(self, data, rules):
        """Validates the data according to the rules, returns True if the data is valid, and False if the data is invalid"""

        errors = self.validate(data, rules)
        if not errors:
            return False

        self.errors = errors

        return not len(errors) > 0
