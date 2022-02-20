from validation import Validation

data = {
	'month_day':'5522',
	'old_password':'asdf',
	'new_password':'@$#%$%$$#$#$#',
	'new_password_confirmation':'222322222',
	'phone':'0796359038',
	'birthday':'-2212-20',
	'email':'walid',
	'host':'172.30.30.20',
	'website':'www.oogle.com',
	'nationality':'afghan',
	'active':'1',
	"age":"12",
}

rules = {
	'month_day':r"required|regex:([a-zA-Z]+)",
	'birthday':'required|date_format:%m-%d-%Y|after:10-10-1995|before:02-25-2010|date',
	'old_password':'required',
	'new_password':'different:old_password|alpha|confirmed',
	'new_password_confirmation':'same:new_password',
	'phone':'phone|required|max:4|min:2|size:23',
	'email':'required|email|present',
	'host':'ip',
	'website':'website|size:',
	'nationality':'in:',
	'active':'boolean',
	'age':'between:18,66'
}

my_messages = {
	"_comment": "You did not provide any field named <feld_name> in your data dictionary",
	"field_name.rule":"You did not provide any field named field_name in your data dictionary",
	"month_day.regex":"You did not provide any field named month_day in your data dictionary",
	"phone.max":"You did not provide any field named phone in your data dictionary",
	"month_day.required":"You did not provide any field named month_day in your data dictionary",
	"new_password_confirmation.same":"You did not provide any field named new_password_confirmation in your data dictionary",
	"phone.no_field":"You did not provide any field named phone in your data dictionary",
	"birthday.date_format":"You did not provide any field named birthday in your data dictionary",
	"new_password.alpha":"field new_password can only have alphabet values",
	"host.no_field":"You did not provide any field named host in your data dictionary",
	"email.no_field":"You did not provide any field named email in your data dictionary",
	"nationality.no_field":"You did not provide any field named nationality in your data dictionary",
	"active.no_field":"You did not provide any field named active in your data dictionary",
	"age.no_field":"You did not provide any field named age in your data dictionary"
}

validation = Validation()

errors = validation.validate(data,rules) 

for error in errors:
	print error