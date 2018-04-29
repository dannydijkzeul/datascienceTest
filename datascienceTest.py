'''
Authors: Danny Dijkzeul
         10554386
'''
class Article():
    # Creates article object with all information of the articles content
    def __init__(self, docno, docid, date, section, length, headline):
        self.docno = docno
        self.docid = docid
        self.date = date
        self.section = section
        self.length = length
        self.headline = headline
        self.byline = ""
        self.text = ""
        self.graphic = ""

    # Add byline content to article object
    def addByline(self, byline):
        self.byline = byline

    # Add text content to article object
    def addText(self, text):
        self.text = text

    # Add graphic content to article object
    def addGraphic(self, graphic):
        self.graphic = graphic

    # Returns an array of all words that where found in a single article
    def getAllText(self):
        text = self.docno + " " + self.docid + " " + self.date
        text += " " + self.section + " " + self.length + " " + self.headline
        text += " " + self.byline + " " + self.text + " " + self.graphic
        # Remove puncuation using regex
        text = re.sub(r'[^\w\s]',' ',text)
        # Make the string fully lowercase
        text.lower()
        # Split the text into an array
        self.wordArray = text.split(" ")
        return self.wordArray

def createArticleObjects(args):
    articles = []
    # Open given file
    with open(args.file) as f:
        line = f.readline().rstrip('\n')
        while line:
            if line == "<doc>":
                docno = f.readline().rstrip('\n').split(' ')[1]
                docid = f.readline().rstrip('\n').split(' ')[1]
                # This array contains information of the article which is
                #  date, section, length, headline in that order
                informationArray = []
                # Loop through the first part of the document and fill the
                #  informationArray
                for i in range(0,3):
                    next(f)
                    next(f)

                    info = f.readline().rstrip('\n')
                    informationArray.append(info)
                    for i in range(0,2):
                        next(f)
                line = f.readline().rstrip('\n')
                # Add headline to informationArray and check for mutliple line
                # headline
                if line == "<headline>":
                    line = f.readline()
                    headline = ""
                    while line != "</headline>":
                        if "p>" not in line:
                            headline += line
                        line = f.readline().rstrip('\n')
                    informationArray.append(headline)
                # Creates the article object using the informationArray
                article = Article(docno, docid, informationArray[0],
                    informationArray[1],informationArray[2],informationArray[3])
                articles.append(article)
            line = f.readline().rstrip('\n')

            # Checks for the byline in the article and adds these to the
            # article object
            if line == "<byline>":
                line = f.readline()
                byline = ""
                while line != "</byline>":
                    if "p>" not in line:
                        byline += " " + line
                    line = f.readline().rstrip('\n')
                article.addByline(byline)

            # Checks for the text in the article and adds these to the
            # article object
            if line == "<text>":
                line = f.readline()
                text = ""
                while "</text>" not in line:
                    if "p>" not in line:
                        text += " " + line
                    line = f.readline().rstrip('\n')
                article.addText(text)

            # Checks for the grahic in the article and adds these to the
            # article object
            if line == "<graphic>":
                line = f.readline()
                graphic = ""
                while "</graphic>" not in line:
                    if "p>" not in line:
                        graphic += " " + line
                    line = f.readline().rstrip('\n')
                article.addGraphic(graphic)
    return articles

def createWordDict(articles):
    # Creates a dict where new keys always have an empty list as value
    wordDict = defaultdict(list)
    for i in range(0, len(articles)):
        # Counts all words in the array given by getAllText
         countedWords = Counter(articles[i].getAllText())
         # Adds the count to the defaultdict with the correct article number
         for j in countedWords.keys():
             wordDict[j].append([i+1, countedWords[j]])
    # Delete empty word
    del wordDict[""]
    return wordDict

def findSimilarWords(wordDict):
    deletedKeys = []
    for i in wordDict.keys():
        for j in wordDict.keys():
            # Use the Levenshtein Distance algorithm with fuzzy wuzzy package
            #  to find the similarities between words. When 90% is similar
            #  The wordcount is added togehter
            if fuzz.ratio(i,j) > 90 and i is not j:
                wordDict[i] = addWordsCounts(wordDict[i], wordDict[j])
                # Check if word was not already know
                if j not in deletedKeys:
                    deletedKeys.append(j)
    # Delete the words that were added togehter
    for a in deletedKeys:
        del wordDict[a]
    return wordDict

def addWordsCounts(wordCount1, wordCount2):
    for i in range(0, len(wordCount2)):
        for j in range(0, len(wordCount1)):
            # Adds count if the word was in the same document
            if wordCount1[j][0] == wordCount2[i][0]:
                wordCount1[j][1] += wordCount2[i][1]
                break
            # Adds count if the word did not appear in other documents
            elif (j == len(wordCount1)-1) and wordCount1[j][0] != wordCount2[i][0]:
                wordCount1.append(wordCount2[i])
    return wordCount1

def makeHistogram(wordDict):
    countedWords = []
    # Extract all wordcounts from the word dictonairy
    for i in wordDict.keys():
        oneWordOccurance = 0
        for j in wordDict[i]:
            oneWordOccurance += j[1]
        countedWords.append(oneWordOccurance)
    # Create numpy array for the histogram
    countedWords = np.asarray(countedWords)
    # Make histogram
    hist, bins = np.histogram(countedWords, bins = max(countedWords))
    plt.hist(hist, bins)
    plt.title("histogram")
    plt.show()



# program entry point.
if __name__ == '__main__':
    import sys
    import argparse
    import re
    from collections import Counter, defaultdict
    from fuzzywuzzy import fuzz
    import numpy as np
    from matplotlib import pyplot as plt

    # Argparser which takes the file as argument
    p = argparse.ArgumentParser()
    p.add_argument('--file', help='article that needs to be parsed',
                                                        default='article.txt')
    args = p.parse_args(sys.argv[1:])

    articles = createArticleObjects(args)
    wordDict = createWordDict(articles)
    wordDict = findSimilarWords(wordDict)
    makeHistogram(wordDict)
    # print(wordDict)
