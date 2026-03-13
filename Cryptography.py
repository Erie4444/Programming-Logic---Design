'''
Eric Zhao
3/2/2026
Encrypts/decrypts a message using one of the three available cipher methods:
caesar
scytale
vingenere
'''
import math
def caesar (msg,shift,encrypt):
    outputMsg = ""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ##making the shifted alphabet
    shiftAlphabet = alphabet[shift:]+alphabet[:shift]
    ##goes through each letter in the message
    for letter in msg:
        if encrypt:
            ##finds the index of the current letter in the alphabet
            ##then finds the letter in the shifted alphabet at the same index
            outputMsg+=shiftAlphabet[findIndex(alphabet,letter)]
        else:
            ##reverses the encrypt sequence
            outputMsg+=alphabet[findIndex(shiftAlphabet,letter)]
    return outputMsg

def scytale (msg,rows,encrypt):
    outputMsg = ""
    ##finds the number of columns in the scytale matrix
    cols = math.ceil(len(msg)/rows)
    ##adding padding to the end of the message in order to fill all elements in the matrix
    msg+=" "*(rows*cols-len(msg))
    if encrypt:
        ##converting the message into matrix form
        matrix = [[msg[index+rowNum*cols] for index in range(cols)] for rowNum in range(rows)]
    else:
        ##converting the message into matrix form (transposed version compared to encrypt)
        matrix = [[msg[index+colNum*rows] for index in range(rows)] for colNum in range(cols)]
    
    ##to read the matrix up to down, we transpose it so all we need to do is read the rows
    for row in transpose(matrix):
        for item in row:
            if item != " ":
                outputMsg+=item
    return outputMsg


def vigenere (msg,keyword,encrypt):
    outputMsg = ""
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ##index helps determine when to loop back in the keyword
    for index,letter in enumerate(msg):
        ##just runs a caesar based on the index of the current keyword letter in the alphabet
        outputMsg+=caesar(letter,findIndex(alphabet,keyword[index%len(keyword)]),encrypt)
    return outputMsg

##transposes a matrix, or flipping it over its diagonal
def transpose(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    return [[matrix[j][i] for j in range(rows)] for i in range(cols)]

##more pretty form to print the matrix (for debugging)
def printMatrix(matrix):
    for row in matrix:
        print(row)

##finds the index of a letter in a string (used for finding which index a letter is in the alphabet)
def findIndex(string,letter):
    for index,i in enumerate(string):
        if letter == i:
            return index

def processMessage(msg):
    processedMsg = ""
    for letter in msg:
        ##only adds the current character if its an alphabetical character
        if letter.isalpha():
            processedMsg+=letter.upper() ##makes sure its in uppercase
    return processedMsg

##basically an input() that repeatedly asks for a prompt until the answer is in the options parameter
def askMsg(prompt,options):
    user = input(prompt).lower()
    ##waiting until the input is in the options parameter
    while not user in options:
        user = input(prompt)
    return user

def console():
    print("Welcome!")
    message = processMessage(input("Please input a message to cipher/decipher >>"))
    ##making sure only ciphers available to choose are caesar, scytale, and vingenere
    cipher = askMsg("Please choose your cipher (caesar, scytale, vingenere)",["caesar","scytale","vingenere"])
    ##makes sure only options are yes or no, and then converts that to true or false
    encrypt = True if askMsg("Are you encrypting this message? (yes, no)",["yes","no"]) == "yes" else False
    ##runs the correct cipher depending on what was inputted
    if cipher == "caesar":
        ##asks for the shift number
        shift = int(askMsg("how many letters to shift by?",[str(i) for i in range(26)]))
        output = caesar(message,shift,encrypt)
    elif cipher == "scytale":
        ##asks for the number of rows in the matrix
        rows = int(askMsg("how many rows?",[str(i) for i in range(len(message))]))
        output = scytale(message,rows,encrypt)
    elif cipher == "vingenere":
        ##asks for the keyword of the ciphers
        keyword = processMessage(input("what is the keyword?"))
        output = vigenere(message,keyword,encrypt)
    else:
        ##I have no idea when this will run as the only options are caesar, scytale, and vingenere
        print("how did you get here")
    print(output)

console()
