import time, random
from string import Template

def readToken(line):
    token = ""
    with open(".tokens") as tokenfile:
       token = tokenfile.readlines()[line].rstrip()

       # Just like an array, the lines start at 0, not 1.

    tokenfile.close()
    return token

def makeOTP():
    otp = "If you are recieving this, there has been a mistake.\nPlease contact one of the officers for assistance."

    try:
        number = str(int(time.clock_gettime(time.CLOCK_REALTIME) / random.random()))

        otp = number[0:5]
        int(otp)

    except:
        print("Error in OTP creation.")

    return otp

def verifyTTUEmail(email):
    verified = False

    try:
        if "@ttu.edu" in email.lower() or "@ttuhsc.edu" in email.lower():
            verified = True

        else:
            print("Invalid email.")

    except:
        print("Invalid expression.")

    return verified

def cacheOTP(user_id, OTP):
    try:
        with open(f".cache/{user_id}", "r") as cachedOTPFile:
            cachedOTPFile.close()
            Path.unlink(cachedOTPFile)
            cacheOTP(user_id, OTP)

    except:
        with open(f".cache/{user_id}", "w") as cachedOTPFile:
            cachedOTPFile.write(str(OTP))
            cachedOTPFile.close()

def readCachedOTP(user_id):
    cachedOTP = -1
    try:
        with open(f".cache/{user_id}", "r") as cachedOTPFile:
            cachedOTP = cachedOTPFile.readlines()[0].rstrip()
            cachedOTPFile.close()

    except:
        print(f"Cached OTP file {user_id} does not exist.")

    return cachedOTP

def compareOTP(enteredOTP, user_id):
    valid = False
    readOTP = readCachedOTP(user_id)
    if enteredOTP == readOTP:
        valid = True

    return valid

def getEmailHTML(user_name, OTP):
    email = "Internal error."
    try:
        with open("message.html", "r") as messageFile:
            message = messageFile.read()
            email = Template(message).safe_substitute(username=user_name, OTPcode=OTP)
            messageFile.close()

    except:
        print("Missing email HTML message file.")

    return email
