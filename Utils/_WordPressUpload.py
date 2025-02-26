import base64
import requests
import os

def init_WordPressUpload(name):
	try:
		suffix = b'_' + name.encode('ascii')
	except UnicodeEncodeError:
		suffix = b'U_' + name.encode('punycode').replace(b'-',b'_')
	return b'PyInit' + suffix

def cleanFilename(s):
	if not s:
		return ''
	badchars = '\\/:*?\"\'<>|'
	for c in badchars:
		s = s.replace(c, '')
	return s

class WordPressUpload:
	def __init__(self, user, password, url, title, theHTML, wpstatus: str="draft", imgpath: str=""):
		self.user = user
		self.password = password
		self.url = url
		self.imgpath = imgpath
		if len(self.imgpath) < 3: doImg=False
		else: doImg=True
		sendingData = {"title": title, "content": theHTML, "status": wpstatus}
		try:
			if doImg: sendingData["featured_media"] = self.uploadImg(user, password, url, imgpath)
		except:
			#print("Failure Uploading to WP")
			#print(theImg)
			pass
		self.postToWP(user, password, url, sendingData)
	def uploadImg(self, user, password, url, imgPath: str):
		#url='http://xxxxxxxxxxxx.com/wp-json/wp/v2/media'
		imgdata = open(f'output/images/{cleanFilename(imgPath)}', 'rb').read()
		fileName = os.path.basename(f'output/images/{imgPath}')
		mediaurl = f'{url}/wp-json/wp/v2/media'
		credentials = user + ':' + password
		token = base64.b64encode(credentials.encode())
		res = requests.post(url=mediaurl,
							data=imgdata,
							headers={'Authorization': 'Basic ' + token.decode('utf-8'), 
										'Content-Type': 'image/jpg',
										'Content-Disposition' : f'attachment; filename={cleanFilename(fileName)}'},
							auth=(user, password))
		if res.status_code < 400: 
			newDict=res.json()
			newID= newDict.get('id')
			link = newDict.get('guid').get('rendered')
		else:
			newID = 1
			link = ''
		return newID

	def postToWP(self, user, password, url, data):
		"""Posts the data to Wordpress

		Args:
			user (str): username
			password (str): password
			url (str): https://yoururl.com
			data (dict): {
				'title':title,
				'content':content,
				'status':status
			}
		"""
		postsURL = url + '/wp-json/wp/v2/posts'
		credentials = user + ':' + password
		token = base64.b64encode(credentials.encode())
		header = {'Authorization': 'Basic ' + token.decode('utf-8')}
		responce = requests.post(postsURL, headers = header, json=data)
		return responce.status_code