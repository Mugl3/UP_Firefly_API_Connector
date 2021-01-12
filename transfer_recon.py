#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 13:47:18 2020

@author: gustav du preez
"""

import json
import requests
import glob
import os
import sys
#When running as cron, user is root and default directory is somewhere else. This changes dir tto the script location
os.chdir(sys.path[0])
headersAPIUP = {'accept': 'application/json','Authorization': 'Bearer up:yeah:enter your own numbers here',}
headersAPIFirefly = {'accept': 'application/json','Authorization': 'Bearer enter_your_own_starting_with_EY_here',}
sTagToSearch = 'https://your_firefly_url/api/v1/tags/'
##This matrix relates accounts on UP API to Firefly API
accountmatrix={"account_id_1_matched_to_integer_for_firefly_after_this_semicolon":3,"enter_all_account_ids_in_this_manner":11,}
#Initiate empty arrays to for files to be deleted.
tfdelete=[]
ttdelete=[]

#Save an array with the names of each transfer from file.
tfarray = glob.glob('tf*.json')
#Loop over every Transfer From file
for i in tfarray:
    #Open the tf file
    with open(i, "r") as read_file:
        tfdata=json.load(read_file)
    #Assign the relevant attributes
    tfcurrency = tfdata['data']['attributes']['amount']['currencyCode']
    tfamount = float(tfdata['data']['attributes']['amount']['value'])
    tfdate = tfdata['data']['attributes']['createdAt'][0:9]
    
    #Loop over each tt file.
    ttarray = glob.glob('tt*.json')
    for j in ttarray:
        with open(j, "r") as read_file:
            ttdata=json.load(read_file)
        ttcurrency = ttdata['data']['attributes']['amount']['currencyCode']
        ttamount = float(ttdata['data']['attributes']['amount']['value'])
        ttdate = ttdata['data']['attributes']['createdAt'][0:9]
        if (tfcurrency==ttcurrency) and (tfdate==ttdate) and (abs(tfamount)==abs(ttamount)):
            #These are the same files. Upload the transaction and exit out of the loops. Save the names of these files and deleted them after upload. 
            #See if this has been uploaded to firefly previously
            sTagToSearch='https://your_firefly_url_here/api/v1/tags/'+tfdata['data']['id']+ttdata['data']['id']+'/transactions'
            r = requests.get(sTagToSearch,headers=headersAPIFirefly)
            fireflyApiResponse = r.json()
            try:
                    if fireflyApiResponse['message']=='Resource not found' or fireflyApiResponse['meta']['pagination']['total']==0:
                        #Transaction does not exist, so upload it.
                        txFirefly = {"type": "transfer","currency_code": "AUD"}
                        txFirefly["date"]=tfdata['data']['attributes']['createdAt'][0:16]+tfdata['data']['attributes']['createdAt'][19:]
                        if tfamount<0: #If tf is the account making the payment then it is the source.
                            txFirefly["source_id"]=str(accountmatrix[tfdata['data']['relationships']['account']['data']['id']])
                            txFirefly["destination_id"]=str(accountmatrix[ttdata['data']['relationships']['account']['data']['id']])
                        else:
                            txFirefly["source_id"]=str(accountmatrix[ttdata['data']['relationships']['account']['data']['id']])
                            txFirefly["destination_id"]=str(accountmatrix[tfdata['data']['relationships']['account']['data']['id']])
                        txFirefly["amount"]=str(abs(tfamount))
                        txFirefly["tags"]=tfdata['data']['id']+ttdata['data']['id']
                        description_firefly=tfdata['data']['attributes']['description']+' '
                        if not(tfdata['data']['attributes']['rawText']==None):    
                            description_firefly=description_firefly+tfdata['data']['attributes']['rawText']
                        if not(tfdata['data']['attributes']['message']==None): 
                            description_firefly=description_firefly+' '+tfdata['data']['attributes']['message']
                        txFirefly["description"]=description_firefly
                        #Now upload all the prepared data
                        fireflyapiupload='https://your_firefly_url/api/v1/transactions'
                        payload = {"transactions":[txFirefly]}
                        print(payload)
                        r = requests.post(fireflyapiupload,headers=headersAPIFirefly,json=payload)
                        newtransaction = r.json()
                        print(newtransaction)
                        tfdelete.append(i)
                        ttdelete.append(j)
            except:
                    #Transaction exists, so ensure the tx is deleted.
                    tfdelete.append(i)
                    ttdelete.append(j)               
                    print(fireflyApiResponse)
                    print("Transaction already exists. Not saving for later upload. 3")
uniquedelete=[]
for i in tfdelete:
    if i not in uniquedelete:
    	uniquedelete.append(i)
for i in uniquedelete:
    print("Deleting "+i)
    os.remove(i) 
uniquedelete=[]
for j in ttdelete:
    if j not in uniquedelete:
    	uniquedelete.append(j)
#print(os.getcwd())    	
#final=input("press to exit")
for j in uniquedelete:
    print("Should delete "+j)
    os.remove(j)
