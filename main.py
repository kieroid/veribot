import discord
from discord import app_commands
import resend
from functions import *
import time
from pathlib import Path

discordToken = readToken(0)
resend.api_key = readToken(1)
myGuild = discord.Object(1066163609190801500)
OTPTries = {}
OTPWaitlist = {}
class myClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents = intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild = myGuild)
        await self.tree.sync(guild = myGuild)

intents = discord.Intents.default()
client = myClient(intents = intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user} ({client.user.id})")
    logChannel = client.get_channel(1332518941633024010)
    await logChannel.send(content = "Ready.")

@client.tree.command()
@app_commands.describe(email = "Your TTU or TTUHSC TechMail address.")
async def verify(interaction: discord.Interaction, email: str):
    quarantineChannel = client.get_channel(1332534981121150977)
    logChannel = client.get_channel(1332518941633024010)
    member = interaction.user

    if interaction.channel == quarantineChannel:
        if verifyTTUEmail(email) and readCachedOTP(member.id) == -1:
            await interaction.response.send_message(f"{member}, an email containing a One-Time Passcode will be sent to: {email}\n**Please, check your \"Junk Email\"**", ephemeral = True)
            await logChannel.send(content = f"<@{member.id}> entered a valid TTU/TTUHSC email: {email}")
            otp = makeOTP()
            cacheOTP(member.id, otp)
            params: resend.Emails.SendParams = {
                "from": "Linux and Open-Source Computing Organization <loco@shellfish.racing>",
                "to": email,
                "subject": "Your LOCO One-Time Passcode",
                "html": getEmailHTML(member, otp)
            }
            print(resend.Emails.send(params))
            OTPTries[member.id] = 3
            OTPWaitlist[member.id] = time.clock_gettime(time.CLOCK_REALTIME)

        elif verifyTTUEmail(email) and not readCachedOTP(member.id) == -1:
            await interaction.response.send_message(f"{member}, your One-Time Passcode already exists.\nPlease try checking your \"Junk Mail.\"", ephemeral = True)
            await logChannel.send(content =  f"<@{member.id}> attempted to generate more than one OTP.")

        else:
            await interaction.response.send_message(f"{email} is not a valid TechMail address. Please try again.", ephemeral = True)
            await logChannel.send(content = f"<@{member.id}> attempted to verify using {email}")

    else:
        await logChannel.send(content = f"({member.id}){member} attempted to verify from outside quarantine.")
        print(f"<@{member} attempted to verify illegally.")

@client.tree.command()
@app_commands.describe(otp = "The One-Time Passcode that you recieved at your TechMail address.")
async def otp(interaction: discord.Interaction, otp: str):
    quarantineChannel = client.get_channel(1332534981121150977)
    logChannel = client.get_channel(1332518941633024010)
    member = interaction.user
    Role = interaction.guild.get_role(1331839649689243740)
    int(otp)
    if not readCachedOTP(member.id) == -1:
        if OTPTries[member.id] > 0:
            if compareOTP(otp, member.id):
                await logChannel.send(content = f"<@{member.id}> verified successfully.")
                await interaction.response.send_message(f"{member}, you have verified successfully. You will be redirected shortly.", ephemeral = True)
                await member.add_roles(Role)
                Path.unlink(f".cache/{member.id}")

            else:
                await logChannel.send(content = f"<@{member.id}> used an incorrect OTP.")
                await interaction.response.send_message(f"{member}, please try again.", ephemeral = True)
                OTPTries[member.id] = OTPTries[member.id] - 1

        else:
            await logChannel.send(content = f"<@{member.id}> ran out of attempts to enter OTP.")

            timeElapsed = time.clock_gettime(time.CLOCK_REALTIME) - OTPWaitlist[member.id]
            timeLeft = 1800 - timeElapsed

            if(timeLeft < 0):
                await interaction.response.send_message(f"{member}, please verify again.", ephemeral = True)
                Path.unlink(f".cache/{member.id}")
                OTPWaitlist.pop(member.id)
                OTPTries.pop(member.id)
            else:
                await interaction.response.send_message(f"{member}, please wait {timeLeft} seconds.", ephemeral = True)
client.run(discordToken)
