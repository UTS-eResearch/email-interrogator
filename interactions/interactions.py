import re
# Email & directory stuff
import imaplib
import pyzmail
import ldap3

# Build a graph - not using this ATM, but maybe one day
import networkx as nx

# The usual data and plotting libraries
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import os, os.path
import subprocess

class Interactions(object):
    def __init__(self, args):        
        self.args = args
        self.dept_lookup = json.load(open(args.mapping))  if args.mapping else {}

        # Set up LDAP connection
        self.ldap_connection = ldap3.Connection(args.ldap, auto_bind=True)

        # Set up email connection
        self.M = imaplib.IMAP4_SSL(args.server)
        self.M.login(args.username, args.password)
        self.M.select('"%s"' % self.args.folder)
        self.interactions = nx.MultiGraph()
        self.sent_to_summary = {}

    def lookup_dept(self, dept):
        """ Return a short-name for a department, as returned by LDAP, if there is one, looks in the mapping file"""
        return self.dept_lookup[dept] if  dept in self.dept_lookup else dept

    def lookup_ldap_unit(self, from_email):
        self.ldap_connection.search('o=UTS', '(mail=%s)' % from_email, attributes=[self.args.unit_string])
        if len(self.ldap_connection.entries):
            unit =  str(self.ldap_connection.entries[0][self.args.unit_string])
        else:
            unit = "EXTERNAL"
        unit = self.lookup_dept(unit)
        return unit

    def deal_with_the_emails(self):
        typ, data = self.M.search(None, '(%s)' % self.args.query)
        for num in data[0].split():
            #(UID BODY[TEXT])
            # http://stackoverflow.com/questions/19540192/imap-get-sender-name-and-body-text
            typ, data = self.M.fetch(num, '(RFC822)')
            # fetch the email body (RFC822) 
            raw_email = data[0][1]
            message = pyzmail.PyzMessage.factory(raw_email)


            print("::SUBJECT::", message.get_subject(), end="")
            if not self.args.ignore_headers:
                from_name, from_email = message.get_address('from')
                # If we're looking at sent mail, want to be able to force the name of the sending unit 
                if self.args.from_unit:
                    from_unit = self.args.from_unit
                else:
                    from_unit = self.lookup_ldap_unit(from_email)

                from_email = from_email.lower()
                self.interactions.add_node(from_unit)
                for (to_name,to_email) in message.get_addresses('to') + message.get_addresses('cc'):
                    print (":TO:", to_email, end="")
                    to_email = to_email.lower()
                    to_unit = self.lookup_ldap_unit(to_email)

                    to_unit = self.lookup_dept(to_unit)
                    if to_unit:
                        if to_unit in self.sent_to_summary:
                            self.sent_to_summary[to_unit] += 1
                        else:
                            self.sent_to_summary[to_unit] = 1
                        self.interactions.add_node(to_unit)
                        self.interactions.add_edge(from_unit, to_unit)

                print("")

                
            
                
    def report(self):
        """ Output data files """

        # Experimental network graph
        #nx.draw_spring(self.interactions,with_labels=True)
        #plt.show()

        interactions_frame = nx.to_pandas_dataframe(self.interactions)
        print(interactions_frame)
        to_series = pd.Series(self.sent_to_summary)
        df = pd.DataFrame()
        for dept, count in to_series.items():
            df.set_value(self.args.username, dept, count)
        
        print(df)
        save_to_dir = os.path.join(".", "Output", self.args.query, self.args.username.replace("@","_at_"))
        if not os.path.exists(save_to_dir):
            os.makedirs(save_to_dir)
     
        df.to_csv(os.path.join(save_to_dir, "interaction_data.csv"))
        to_series.plot(kind='bar')
        plt.tight_layout()
        img_path = os.path.join(save_to_dir, "interaction_data.png")
        plt.savefig(img_path)
        subprocess.call(["open", img_path])
        print(df)
        
    def close(self):
        self.M.close()
        self.M.logout()
