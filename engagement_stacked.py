#!/usr/bin/env python
""" 
This is a command line email analysis tool

python3 imap.py --help

OUTPUT: A pandas dataframw with aggregated interactions 
 
"""

import argparse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os.path
import os
import subprocess
import time

def main():
    parser = argparse.ArgumentParser(description='Build a stacked-bar-chart')
    parser.add_argument('directory',help='directory to use',action='store')
    parser.add_argument('-p', '--anonymise-people', action='store_true', help='Change names of people to "Person 1...n"')
    parser.add_argument('-g', '--anonymise-groups', action='store_true', help='Change names of groups to "Group 1...n"')
    parser.add_argument('-s', '--show_plots', action='store_true', help='Show plots.')


    args = parser.parse_args()
    frames = []
    print(os.listdir(args.directory))
    for dir in os.listdir(args.directory):
        print(dir)
        path = os.path.join(args.directory, dir, "interaction_data.csv")
        print(path)
        if os.path.exists(path):
            frames.append(pd.DataFrame.from_csv(path))
        
    df = pd.concat(frames)
    if args.anonymise_people:
        row_names = {}
        x = 0
        for name, _ in df.transpose().items():
            row_names[name] = "Person %s" % str(x)
            x += 1
        df = df.rename(row_names)

    df = df.transpose()

        
    if args.anonymise_groups:

        row_names = {}
        x = 0
        for name, _ in df.transpose().items():
            row_names[name] = "Group %s" % str(x)
            x += 1
        df = df.rename(row_names)



    
    row = df.sum(axis=1)
    row.plot.bar()
    img_path = os.path.join(args.directory, "interaction_data.png")
    plt.tight_layout()
    plt.savefig(img_path)
    print("Saved image: ", img_path)
    if args.show_plots:
        plt.show(block=False)
        
    df.plot.bar(stacked=True)
    plt.tight_layout()
    img_path = os.path.join(args.directory, "interaction_data_stacked.png")
    
    plt.savefig(img_path)
    print("Saved image: ", img_path)
    if args.show_plots:
        plt.show()
   

     


    
if __name__ == "__main__":
    main()
