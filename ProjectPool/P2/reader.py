# Caleb anthony, DOCKER PROJECT 2
import socket

def sortKey(data,datb):
    return data.count < datb

def checkKey(dic, key):
    if key in dic.keys():
        #print("Present, ", end =" ")
        #print("value =", dic[key])
        return True
    else:
        return False
        #print("Not present")


def countWords(file):
    wordList = {}
    with open(file) as file:
        data = file.read().replace('\n',' ')
   
    words = data.split(" ")
    for word in words:
        if checkKey(wordList,word):
            wordList[word] +=1
        else:
            wordList[word] = 1
    return wordList


def getWordCount(file):
    with open(file) as file:
        data = file.read().replace('\n',' ')
    words = data.split(" ")
    count = len(words)
    return count


def write(text):
    with open("./output/result.txt","a") as file1:
        # Writing data to a file
        file1.write(text)
        file1.write("\n")

def main():
    limerickFile = "./data/IF-1.txt"
    ifFile = "./data/Limerick-3.txt"
    #outputFile  = open("./output/result.txt","w+")

    countLimerik = getWordCount(limerickFile)
    countIf = getWordCount(ifFile)
    write("Count of words in Limerick-3: " + str(countLimerik))
    write("Count of words in IF-1: " + str(countIf))
    write("Total words in both files: " + str(countIf + countLimerik))

    write("\n")
    wordList = countWords(ifFile)
    res = {key: val for key, val in sorted(wordList.items(), key = lambda ele: ele[1], reverse = True)}
    resList =[(k, v) for k, v in res.items()]
    write("Top word counts: " + str(resList[0][0] + ": " + str(resList[0][1])) + ",   " +str(resList[1][0] + ": " + str(resList[1][1])) +",  "+ str(resList[2][0] + ": " + str(resList[2][1])))

    h_name = socket.gethostname()
    IP_addres = socket.gethostbyname(h_name)
    write("Computer IP Address is:" + IP_addres)
    print("finished")






    

main()
