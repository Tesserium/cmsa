from requests import get
import re
import os
import threading
from math import ceil
from wget import download
from operator import attrgetter

username = "FedhasFedhasFedhas"

CUE = "https://underhound.eu/crawl/morgue/" + username
CXC = "https://crawl.xtahua.com/crawl/morgue/" + username
CPO = "https://crawl.project357.org/morgue/" + username
CKO = "https://crawl.kelbi.org/crawl/morgue/" + username
CBR2 = "https://cbro.berotato.org/morgue/" + username
CAO = "http://crawl.akrasiac.org/rawdata/" + username

url = CKO

def getAllFiles(dire):
	response = get(dire)
	text = response.text
	rematch = "morgue-" + username + "[0123456789-]*.[txt|txt.gz]*'"
	return re.findall(rematch, text)

urlf = getAllFiles(url)
files = []
urls = []
for i in urlf:
	files.append(i[:-1])
	urls.append(url + "/" + i[:-1])

path = os.getcwd() + "/" + username

if os.path.exists(path) == 0:
	os.mkdir(path)

def retrieveFiles(l, r):
	for i in range(l, r + 1):
		if files[i][-1] == 't' and os.path.exists(path + "/" + files[i] + ".gz"):
			print("File " + str(i + 1) + " / " + str(len(urls)) + " " + files[i] + ".gz" + " Exists, Skipping")		
			unzipCommand = "gzip -nd " + path + "/" + temp
			os.system(unzipCommand)
		elif files[i][-1] == 'z' and os.path.exists(path + "/" + files[i][:-3]):
			print("File " + str(i + 1) + " / " + str(len(urls)) + " " + files[i][:-3] + " Exists, Skipping")
		elif os.path.exists(path + "/" + files[i]):
			print("File " + str(i + 1) + " / " + str(len(urls)) + " " + files[i] + " Exists, Skipping")
		else:
			print("Downloading file " + str(i + 1) + " / " + str(len(urls)), files[i])
			download(urls[i], path, None)
			if files[i][-1] == 'z':
				unzipCommand = "gzip -nd " + path + "/" + files[i]
				os.system(unzipCommand)
		if files[i][-1] == 'z':
			files[i] = path + "/" + files[i][:-3]
		else:
			files[i] = path + "/" + files[i]

threadlist = []
bs = ceil(len(urls) / 13)
for i in range(12):
	l = bs * i
	r = min(bs * (i + 1) - 1, len(urls) - 1)
	tt = threading.Thread(target = retrieveFiles, args = (l, r, ))
	tt.start()
	threadlist.append(tt)

for i in threadlist:
	i.join()

def parseCombo(comb):
	res = re.split(" ", comb)
	if len(res) == 2:
		return re.split(" ", comb)
	elif len(res) == 3:
		if res[1] == "Draconian":
			return res[1:]
		if res[1] == "Elf" or res[1] == "Orc" or res[1] == "Stalker":
			return [res[0] + " " + res[1], res[2]]
		else:
			return [res[0], res[1] + " " + res[2]]
	else:
		return [res[0] + " " + res[1], res[2] + " " + res[3]]
	

class Game:
	def __init__(self, sc, ver, comb, rt, turn, g, pl, xl, spr):
		self.score = sc
		self.version = ver
		self.comboo = comb
		self.realtime = rt
		self.turns = turn
		self.god = g
		self.place = pl
		self.level = xl
		self.sprint = spr

games = []
leveledBranches = "Dungeon|Lair|Orc|Elven|Vaults|Depths|Zot|Cocytus|Gehenna|Tartarus|Dis|Swamp|Shoals|Snake|Spider|Slime|Crypt|Tomb|Abyss"
otherBranches = "Hell|Pandemonium|bailey|sewer|ossuary|cave|volcano|wizard|ziggurat|bazaar|trove|gauntlet|desolation"

for i in files:
	if os.path.exists(i) == 0:
		continue
	pf = open(i)
	print("Processing " + i + "...")
	content = pf.read()
	sc = int(re.search("[0-9]+ \w", content)[0][:-2])
	ver = re.search("version .[0-9a-zA-Z-.]*", content)[0][8:]
	comb = parseCombo(re.search("( as a|as an) .* o", content)[0][6:-2])
	rt = re.search("[0-9]+:[0-9]+:[0-9]+", content)[0]
	turn = re.search("[0-9]+ t", content)[0][:-2]
	if re.search("worshipped", content) == None:
		god = "Atheist"
	else:
		god = re.search("pped .*\n", content)[0][5:-2]
	xl = re.search("l [0-9]+,", content)[0][2:-1]
	sprint = 0
	if re.search("Escaped with the Orb", content) != None:
		place = "Win!"
	else:
		state = re.search("You were (in|on) .*\n", content)[0]
		place = re.search(leveledBranches + "|" + otherBranches, state)[0]
		if place == "Elven":
			place = "Elf"
		if re.search("[0-9]+", state) != None:
			level = re.search("[0-9]+", state)[0]
			place += ":" + str(level)
		else:
			if place == "Dungeon":
				sprint = 1
				
	if place[0] >= 'a' and place[0] <= 'z':
		place = place[0].upper() + place[1:]
	games.append(Game(sc, ver, comb, rt, turn, god, place, xl, sprint))
	
games.sort(key = attrgetter('score', 'turns'), reverse = True)
print("Score".ljust(10), "Version".ljust(25), "Species".ljust(20), "Background".ljust(20), "Real Time".ljust(9), "Turncount".ljust(9), "God".ljust(20), "Place".ljust(15), "Exp Level".ljust(10), "Game Mode".ljust(6))
for i in games:
	if i.sprint == 1:
		spr = "Sprint"
	else: 
		spr = "Crawl"
	print(str(i.score).ljust(10), i.version.ljust(25), i.comboo[0].ljust(20), i.comboo[1].ljust(20), i.realtime.ljust(9), i.turns.ljust(9), i.god.ljust(20), i.place.ljust(15), ("Lv." + i.level).ljust(10), spr.ljust(6))
