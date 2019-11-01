# -----------------------------------------------------
#                         ROUGH
# -----------------------------------------------------
# Please address any complaints to yakuhito
# so he can redirect them to /dev/null
# Bot invite url: invite_url.txt

# DO NOT CHANGE THIS
guild_name = "ROUGH"
vote_cooldown = 10 # minutes

import discord
import time
import json
import string

guild_id = 0
voting_channel = 0
admins = {} # key - user ID, value - last vote casted
votes = []
users_that_created_votes = []
server_admins = []

token = open("./token", "r").read().strip()

client = discord.Client()

# Request from community
async def ping(ip):
	os.system("ping {}".format(ip))

class Vote:
	id = None
	text = None
	vote_time = None
	votes = None
	start_time = None
	vote_msg = None
	reveal_vote = None
	vote_to_reveal = None
	def __init__(self, text, vote_time):
		self.id = len(votes) + 1
		self.text = text.replace("[EOL]", "\n")
		self.vote_time = vote_time * 60 * 60 # in seconds, not hours
		self.start_time = int(time.time())
		self.votes = []
		self.vote_msg = "YAKUHITO"
		self.reveal_vote = False
		self.vote_to_reveal = 0

	def makeReveal(self, vt):
		self.reveal_vote = True
		self.vote_to_reveal = vt

	def setMsg(self, msg):
		self.vote_msg = msg

	def getText(self):
		txt = "Vote #{}\n".format(self.id)
		txt += "--------" + "-" * len(str(self.id) * 2) + "\n"
		txt += "Total vote duration: {}h\n\n".format(self.vote_time // (60 * 60))
		if not self.reveal_vote:
			txt += self.text
			txt += "\n\nVotes:\n"
			dict = {}
			for v in self.votes:
				if dict.get(v[1], -1) == -1:
					dict[v[1]] = 0
				dict[v[1]] += 1
			for vote_str, num in dict.items():
				txt += "{} - {} vote(s)\n".format(vote_str, num)
			txt += "To vote, send the following text to the bot:\n"
			txt += "/vote {} [your_option]".format(self.id)
		else:
			txt += "Reveal vote #{}?\n".format(self.vote_to_reveal)
			txt += "Vote anything for 'yes', stay silent for no\n"
			txt += "Curent votes: {}/3".format(len(self.votes))
		return txt

	async def check(self):
		if self.vote_msg == "YAKUHITO":
			return
		if self.reveal_vote:
			if len(self.votes) > 2:
				await self.vote_msg.channel.send('The author of vote #{} is {}'.format(self.vote_to_reveal, users_that_created_votes[self.vote_to_reveal - 1]))
		await self.vote_msg.edit(content=self.getText())

	async def vote(self, user, vote):
		user_id = user
		if int(time.time()) - self.start_time > self.vote_time:
			await self.check()
			return
		admin = str(user) in server_admins
		if not admin and self.reveal_vote:
			return
		for i in range(len(self.votes)):
			if self.votes[i][0] == user_id:
				self.votes[i] = (user_id, vote)
				await self.check()
				return
		self.votes.append((user_id, vote))
		await self.check()

async def calibrate():
	global guild_id
	global guild_name
	global voting_channel
	global server_admins
	for guild in client.guilds:
		if guild.name == guild_name:
			guild_id = guild.id
			for channel in guild.channels:
				if channel.name == 'voting':
					voting_channel = channel
	server_admins = []
	for user in voting_channel.members:
		if admins.get(user.id, -1) == -1:
			admins[user.id] = int(time.time()) - 120 * 60 * 60 # map new user
		for role in user.roles:
			if "admin" in role.name.lower():
				server_admins.append(str(user))
								

@client.event
async def on_ready():
	global guild_id
	print(f'{client.user} if now online!')
	# Calibrate
	await calibrate()

async def cmd_help(message):
	resp = ""
	resp += "This bot supports 5 commands:\n"
	resp += "1. /ping - makes bot reply pong\n"
	resp += "2. /help - displays this menu\n"
	resp += "3. /createvote [text with spaces] [number of hours users can vote for] - create a vote; [EOL] will be replaced with new lines (\\n)\n"
	resp += "4. /reveal [vote_id] - you probably know what this does\n"
	resp += "5. vote [vote_id] [value] - registers your vote [only works in private channls]"
	await message.channel.send(resp)

async def cmd_createvote(message):
	global votes
	global users_that_created_votes
	global admins
	global voting_channel
	if int(time.time()) - admins[message.author.id] < vote_cooldown * 60:
		await message.channel.send('Please wait 10 minutes before casting anothe vote.')
		return
	arr = msg.split(" ")[1:]
	text = ' '.join(arr[:-1])
	try:
		vtime = int(arr[-1])
	except:
		await message.channel.send('Invalid duration!')
		return
	v = Vote(text, vtime)
	m = await voting_channel.send(v.getText())
	v.setMsg(m)
	votes.append(v)
	users_that_created_votes.append(str(message.author))
	admins[message.author.id] = int(time.time())

async def cmd_ping(message):
	global votes
	await calibrate()
	for i in range(len(votes)):
		await votes[i].check()
	await message.channel.send('Pong!')

async def cmd_vote(message):
	global votes
	arr = msg.split(" ")[1:]
	priv_ch = type(message.channel) is discord.DMChannel
	if not priv_ch:
		return
	try:
		id = int(arr[0])
	except:
		await message.channel.send('id should be an integer!')
		return
	ans = arr[1]
	if ans != "da" and ans != "nu":
		await message.channel.send('Allowed options: da/nu')
		return
	if id > len(votes) and id > 0:
		return
	await votes[id - 1].vote(message.author, ans)
	await message.channel.send('Your vote has been recorded.')

async def cmd_reveal(message):
	global admins
	global votes
	global voting_channel
	global users_that_created_votes
	if int(time.time()) - admins[message.author.id] < vote_cooldown * 60:
		return
	if not str(message.author) in server_admins:
		return
	arr = msg.split(" ")[1:]
	try:
		id = int(arr[0])
	except:
		await message.channel.send('id should be an integer!')
	if id <= 0 or id > len(votes):
		return
	if votes[id - 1].reveal_vote:
		await message.channel.send('That\'s a reveal vote!')
		return
	v = Vote("yakuhito is da best", 1337)
	v.makeReveal(id)
	m = await voting_channel.send(v.getText())
	v.setMsg(m)
	votes.append(v)
	users_that_created_votes.append(str(message.author))
	admins[message.author.id] = int(time.time())

@client.event
async def on_message(message):
	global voting_channel
	if message.author == client.user:
		return
	if admins.get(message.author.id, -1) == -1:
		return
	msg = message.clean_content
	if not msg.startswith('/reveal') and not msg.startswith('vote') and not msg.startswith('/createvote') and msg != '/ping' and msg != '/help':
		return
	if msg == '/help':
		cmd_help(message)
		return
	if msg == '/ping':
		cmd_ping(message)
		return
	if msg.startswith('/createvote'):
		cmd_createvote(message)
		return
	if msg.startswith('vote'):
		cmd_vote(message)
		return
	if msg.startswith('/reveal'):
		cmd_reveal(message)
		return

client.run(token)
