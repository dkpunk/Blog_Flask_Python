import json
import requests
from flask_babel import _
from app import app

def translate(text, source_language,dest_language):
	r=requests.get("https://translate.googleapis.com/translate_a/single?client=gtx&sl={}&tl={}&dt=t&q={}".format(source_language,dest_language,text))
	if r.status_code!=200:
		return _('Error : the translation service failed.')
	text=r.content.decode('utf-8')
	list1=json.loads(text)
	return list1[0][0][0]
