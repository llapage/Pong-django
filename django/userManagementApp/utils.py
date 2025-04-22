import re
from django.contrib.auth.models import User
from .models import PlayerProfile

def goodEmailFormat(email):
	regex_email = r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
	return re.match(regex_email, email)

def goodPasswordFormat(pwd):
	regex_password = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$"
	return re.match(regex_password, pwd)

def goodNameFormat(name):
	regex_name = r"^[a-zA-Z0-9_]*$"
	return re.match(regex_name, name)

def usernameInDB(username):
	return User.objects.filter(username=username).exists()

def nicknameInDB(nickname):
	return PlayerProfile.objects.filter(nickname=nickname).exists()

def emailInDB(email):
	return User.objects.filter(email=email).exists()

def emailErrFind(email):
	if not email or not goodEmailFormat(email):
		return 'invalid format'
	elif emailInDB(email):
		return 'already in use'
	return None

def usernameErrFind(username):
	if not username or not goodNameFormat(username):
		return 'invalid format'
	elif usernameInDB(username):
		return 'already in use'
	return None

def nicknameErrFind(nickname):
	if not nickname or not goodNameFormat(nickname):
		return 'invalid format'
	elif len(nickname) > 15:
		return 'over 15 characters limit'
	elif nicknameInDB(nickname):
		return 'already in use'
	return None

def duplicateErrFind(target, string, stringConf):
	if string != stringConf:
		return 'unmatching {}'.format(target)
	return None

def passwordErrFind(password):
	if not password or not goodPasswordFormat(password):
		return 'invalid format'
	return None 

def userDataErrorFinder(data, *argv):
	responseObj = {}
	error = ""
	if len(argv) == 0:
		argv = data.keys()
	for arg in argv:
		match arg:
			case "email":
				error = emailErrFind(data.get('email'))
			case "email confirmation":
				error = duplicateErrFind('email', data.get('email'), data.get('email confirmation'))
			case "username":
				error = usernameErrFind(data.get('username'))
			case "nickname":
				error = nicknameErrFind(data.get('nickname'))
			case "password":
				error = passwordErrFind(data.get('password'))
			case "password confirmation":
				error = duplicateErrFind('password', data.get('password'), data.get('password confirmation'))
			case _:
				print("userDataErrFind() data anomaly: arg={}".format(arg))
		if error:
			responseObj[arg] = error
	return responseObj
