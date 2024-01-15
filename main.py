from requests import get
import re
import os
import sys
import threading
from random import random 
from time import sleep
from math import ceil
from wget import download
from operator import attrgetter

CUE = "https://underhound.eu/crawl/morgue/"
CXC = "https://crawl.xtahua.com/crawl/morgue/"
CPO = "https://crawl.project357.org/morgue/"
CKO = "https://crawl.kelbi.org/crawl/morgue/"
CBR2 = "https://cbro.berotato.org/morgue/"
CAO = "http://crawl.akrasiac.org/rawdata/"

username = "FedhasFedhasFedhas"
files = []
path = os.getcwd() + "/" + username
urls = []
bs = ceil(len(urls) / 64)
debug = 0

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

def getAllFiles(dire):
	response = get(dire)
	text = response.text
	rematch = "morgue-" + username + "-.[0-9]*-.[0-9]*.[txt|txt.gz]*['|\"]"
	return re.findall(rematch, text)	

def retrieveFiles(l, r):
	for i in range(l, r + 1):
		if files[i][-1] == 't' and os.path.exists(path + "/" + files[i] + ".gz"):
			if debug > 0:
				print("File " + str(i + 1) + " / " + str(len(urls)) + " " + files[i] + ".gz" + " Exists, Skipping")		
			unzipCommand = "gzip -nd " + path + "/" + files[i] + ".gz"
			os.system(unzipCommand)
		elif files[i][-1] == 'z' and os.path.exists(path + "/" + files[i][:-3]):
			if debug > 0:
				print("File " + str(i + 1) + " / " + str(len(urls)) + " " + files[i][:-3] + " Exists, Skipping")
		elif os.path.exists(path + "/" + files[i]):
			if debug > 0:
				print("File " + str(i + 1) + " / " + str(len(urls)) + " " + files[i] + " Exists, Skipping")
		else:
			if debug > 0:
				print("Downloading file " + str(i + 1) + " / " + str(len(urls)), files[i])
			download(urls[i], path, None)
			if files[i][-1] == 'z':
				unzipCommand = "gzip -nd " + path + "/" + files[i]
				os.system(unzipCommand)
		if files[i][-1] == 'z':
			files[i] = path + "/" + files[i][:-3]
		else:
			files[i] = path + "/" + files[i]

def parseCombo(comb):
	res = re.split(" ", comb)
	if len(res) == 2:
		return re.split(" ", comb)
	elif len(res) == 3:	
		if res[1] == "Draconian":
			return res[1:]
		if res[1] == "Elf" or res[1] == "Orc" or res[1] == "Stalker" or res[1] == "Dwarf":
			return [res[0] + " " + res[1], res[2]]
		else:
			return [res[0], res[1] + " " + res[2]]
	elif len(res) == 4:
		return [res[0] + " " + res[1], res[2] + " " + res[3]]
	else:
		return None

def extr(url, server):
	if debug > 0:
		print("Start downloading from", url)
	urlf = getAllFiles(url)
	global urls
	global files
	urls = []
	for i in urlf:
		files.append(i[:-1])
		urls.append(url + "/" + i[:-1])
		
	global path
	path = os.getcwd() + "/" + username + "/" + server

	if os.path.exists(os.getcwd() + "/" + username) == 0:
		os.mkdir(os.getcwd() + "/" + username)

	if os.path.exists(path) == 0:
		os.mkdir(path)

	global bs
	bs = ceil(len(urls) / 64)
	threadlist = []
	for i in range(64):
		l = bs * i
		r = min(bs * (i + 1) - 1, len(urls) - 1)
		tt = threading.Thread(target = retrieveFiles, args = (l, r, ))
		tt.start()
		threadlist.append(tt)

	for i in threadlist:
		i.join()


def main(argv):
	servers = {'a' : CAO, 'b' : CBR2, 'k' : CKO, 'p' : CPO, 'u' : CUE, 'x' : CXC}
	abbrMapping = {'a' : "CAO", 'b' : "CBR2", 'k' : "CKO", 'p' : "CPO", 'u' : "CUE", 'x' : "CXC"}
	url = []
	abbr = []
	for i in range(1, len(argv)):
		if i > 0 and argv[i - 1] == '--username':
			continue
		if argv[i][0] != '-':
			print("Invalid argument:", argv[i][0])
			exit()
		if argv[i][1] != '-':
			for j in argv[i][1:]:
				if j in servers:
					url.append(servers[j])
					abbr.append(abbrMapping[j])
				else:
					print("Invalid argument:", '-' + j)
					exit()
				
		else:
			cont = argv[i][2:]
			if cont == "username":
				global username
				username = argv[i + 1]
			elif cont == "debug":
				global debug 
				debug = 1
		
	games = []
	leveledBranches = "Dungeon|Lair|Orc|Elven|Vaults|Depths|Zot|Cocytus|Gehenna|Tartarus|Dis|Swamp|Shoals|Snake|Spider|Slime|Crypt|Tomb|Abyss"
	otherBranches = "Temple|Hell|Pandemonium|bailey|sewer|ossuary|cave|volcano|wizard|ziggurat|bazaar|trove|Gauntlet|Desolation"

	for i in range(len(url)):
		extr(url[i] + username, abbr[i])
	
	for i in files:
		if os.path.exists(i) == 0:
			continue
		pf = open(i)
		if debug > 0:
			print("Processing " + i + "...")
		content = pf.read()
		sc = int(re.search("[0-9]+ \w", content)[0][:-2])
		ver = re.search("version .[0-9a-zA-Z-.]*", content)[0][8:]
		if re.search("( as a|as an) .* o", content) == None:
			if debug > 0:
				print("Can't find combo in morgue file " + i + ", Skipping")
			continue
		comb = parseCombo(re.search("( as a|as an) .* o", content)[0][6:-2])
		if comb == None:
			if debug > 0:
				print("Can't find combo in morgue file " + i + ", Skipping")
			continue
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
		elif re.search("You escaped", content) != None:
			place = "Escaped Alive."
		else:
			state = re.search("You were (in|on) .*\n", content)[0]
			place = re.search(leveledBranches + "|" + otherBranches, state)[0]
			if place == "Elven":
				place = "Elf"
			elif place == "wizard":
				place = "WizLab"
			elif place == "cave":
				place == "Ice Cave"
			if re.search("[0-9]+", state) != None:
				level = re.search("[0-9]+", state)[0]
				place += ":" + str(level)
			else:
				if place == "Dungeon":
					sprint = 1
					
		if place[0] >= 'a' and place[0] <= 'z':
			place = place[0].upper() + place[1:]
		if re.search("Sprint", content) != None:
			sprint = 1
		games.append(Game(sc, ver, comb, rt, turn, god, place, xl, sprint))
		
	games.sort(key = attrgetter('score', 'turns'), reverse = True)
	print("Score".ljust(10), "Version".ljust(25), "Species".ljust(20), "Background".ljust(20), "Real Time".ljust(9), "Turncount".ljust(9), "God".ljust(20), "Place".ljust(15), "Exp Level".ljust(10), "Game Mode".ljust(6))
	for i in games:
		if i.sprint == 1:
			spr = "Sprint"
		else: 
			spr = "Crawl"
		print(str(i.score).ljust(10), i.version.ljust(25), i.comboo[0].ljust(20), i.comboo[1].ljust(20), i.realtime.ljust(9), i.turns.ljust(9), i.god.ljust(20), i.place.ljust(15), ("Lv." + i.level).ljust(10), spr.ljust(6))


if __name__ == "__main__":
	main(sys.argv)
