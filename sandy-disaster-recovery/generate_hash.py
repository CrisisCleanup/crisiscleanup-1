import hashlib
import logging
import env

def hash_string(string):
	try:
		return hashlib.sha512(str(string) + env.SALT).hexdigest()
	except Exception, e:
		logging.error(e.message)
		raise

def recursive_hash(string):
	for i in range(0, 50):
		string = hash_string(string)
	return string
