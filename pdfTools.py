#!/bin/env python3
import sys
import os
import argparse
import re
from subprocess import call


def main():
    args = processArgs()
    filename = os.path.splitext(args.file)[0]

    if args.type == 'financial':
        with open(args.file, 'r') as fh:
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
                    ytd = amts.split(' ')[2]
                    # print('ytd', ytd)
                    mtd = float(mtd.replace('$', '').replace(',', ''))
                    ytd = float(ytd.replace('$', '').replace(',', ''))

                    label = label.replace('$', '').strip()
                    print('{}\t{}\t{}\t{}'.format(acct, label, mtd, ytd))
                else:
                    amtMatch = re.search(r'([^\s\$]+$)', amts)
                    amt = float(amtMatch.groups(1)[0].replace('$', '').replace(',', ''))
                    print('{}\t{}\t{}'.format(acct, label, amt))


         # cat MULT\ CITYSIDE\ 12-31-14_rawFin.txt| perl -ne 's/\$//g;($acct, $rest) = split(" ",$_,2);$rest=~/([^\d]+)(.*)/;print "$acct\t$1\t$2\n"' > MULT\ CITYSIDE\ 12-31-14_importable.txt

    elif args.type == 'convert':
        os.system('convert -density 300 -depth 8 {0}.pdf {0}.tiff'.format(filename))
        os.system('tesseract {0}.tiff {0}'.format(filename))


def processArgs():
    class MyParser(argparse.ArgumentParser):
        def error(self, message):
            sys.stderr.write('\nError: {}\n\n'.format(message))
            self.print_help()
            sys.exit(2)


    #argParser = MyParser(usage=("%s (sourceDir & filter) | filterFile" % (os.path.basename(sys.argv[0]))))
    argParser = MyParser(description="""Run tesseract on pdf or process financials for monthly reports
                         """)

    argParser.add_argument('file', help="Path to the file you want to process")
    argParser.add_argument('type', choices=['financial', 'convert'], help="Type of parsing you want to do")
    ap = argParser.parse_args()
    return ap


#This is required because by default this is a module.  Running this makes it execute main as if it is a script
if __name__ == '__main__':
    main()
