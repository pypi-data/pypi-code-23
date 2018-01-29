import readItems
import parse
import sys

def doCMD():
    filename = sys.argv[1]
    outputname = sys.argv[2]

    allText = readItems.readSourceMD(filename)
    html = ""
    html = html + readItems.readQuoteStyle()
    html = html + readItems.readCodeStyle()
    html = html + parse.parse(allText)
    html = html + readItems.readCodeJS()

    readItems.output(html, outputname)

def do(filePath, filename, outputPath, outputName):
    allText = readItems.readSourceMD(filePath, filename)
    html = ""
    html = html + readItems.readQuoteStyle()
    html = html + readItems.readCodeStyle()
    html = html + parse.parse(allText)
    html = html + readItems.readCodeJS()

    readItems.output(html, outputPath, outputName)


if __name__ == "__main__":
    do("/Users/ecohnoch/Desktop/Markdown-Html/Markdown","test.md", "/Users/ecohnoch/Desktop/Markdown-Html/Markdown/output","fuck.html")