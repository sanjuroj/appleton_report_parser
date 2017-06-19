#!/bin/env python3
import sys
import os
import argparse
import re
import glob
from dateutil import parser
import pandas as pd
import datetime


def main():
    args = processArgs()
    dfz = pd.DataFrame()
    
    if os.path.isfile(args.path):
        filename = os.path.splitext(args.path)[0]
        dateVal = getDateVal(filename)
        if args.t:
            if '.TXT' not in args.path.upper():
                print('File must be a text file with the .txt extension. Exiting.')
                sys.exit()
            dfz = extractFinancial(args.path, dateVal)
        else:
            if '.PDF' not in args.path.upper():
                print('File must be a PDF. Exiting.')
                sys.exit()
            tesseract(args.path)
            dfz = extractFinancial(filename + '.txt', dateVal)

    elif os.path.isdir(args.path):
        fileList = []
        data = pd.DataFrame()
        if args.t:
            fileList = glob.glob(os.path.join(args.path, '*.txt'))
        else:
            fileList = glob.glob(os.path.join(args.path, '*.pdf'))
            fileList.extend(glob.glob(os.path.join(args.path, '*.PDF')))

        for file in fileList:
            print('Processing', file)
            filename = os.path.splitext(file)[0]
            dateVal = getDateVal(filename)
            if not args.t:
                print('Converting', file)
                tesseract(file)

            newDF = extractFinancial(filename+'.txt', dateVal)
            dfz = dfz.join(newDF, how='outer')

    else:
        print("Not a valid path, exiting")
        sys.exit()

    dfz = dfz.fillna(0)
    dfz.sort_index(axis=1, inplace=True)
    # print(dfz)
    dfz.to_excel('ExtractData_{:%H-%M}.xlsx'.format(datetime.datetime.now()))


def getDateVal(fileName):
    """
    Gets the report date from the report's file name.
    """
    matchObj = re.search('(\d\d?-\d\d?-\d+)', fileName)
    if not matchObj:
        print("Can't parse date for {}.  Please rename file and try again".format(filename))
        sys.exit()
    return parser.parse(matchObj.group(1))


def extractFinancial(filePath, dateVal):
    """
    Parses the text file and extracts the relevant financial information.  
    """
    dateString = '{:%Y-%m-%d}'.format(dateVal)
    amtDict = {}
    with open(filePath, 'r') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if 'Reference' in line:
                break
            match = re.search(r'^(\d{4})\s+(\D+)(.*)', line)
            if not match:
                continue
            (acct, label, amts) = match.groups()
            # print('acct={}, label={}, amts={}'.format(acct, label, amts))
            # print('amts', amts)
            if int(acct) >= 4000:
                mtd = amts.split(' ')[0]
                mtdSign = -1 if ')' in mtd else 1
                mtd = mtdSign * float(''.join(re.findall('[\d.]+', mtd)))
                label = label.replace('$', '').strip()
                amtDict[acct] = mtd
            else:
                amtMatch = re.search(r'([^\s\$]+$)', amts)
                amtSign = -1 if ')' in amtMatch.group(1) else 1
                amt = amtSign * float(''.join(re.findall('\d+', amtMatch.group(1))))
                amtDict[acct] = amt

    df = pd.DataFrame.from_dict(amtDict, orient='index')
    df.columns = [dateString]
    return df


def tesseract(fileName):
    """
    Runs convert and tesseract on a file
    """
    fileNameRaw = os.path.splitext(fileName)[0]
    os.system('convert -density 300 -depth 8 "{}" "{}.tiff"'.format(fileName, fileNameRaw))
    os.system('tesseract "{0}.tiff" "{0}"'.format(fileNameRaw))


def processArgs():
    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('\nError: {}\n\n'.format(message))
            self.print_help()
            sys.exit(2)

    argParser = MyParser(description="""Run tesseract on pdf or process financials for monthly reports""")
    argParser.add_argument('path', help="Path to process.  Can be file or directory.")
    argParser.add_argument('-t', action='store_true', help="Proecess text files rather than PDFs")
    ap = argParser.parse_args()
    return ap


if __name__ == '__main__':
    main()
