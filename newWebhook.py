from flask import Flask, request, Response
import json
import requests

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
#with open('39w.json', "r") as read_file:
#    data=json.load(read_file)

def respond():
#if (data['data']['attributes']['eventType'])=='TRANSACTION_CREATED':
    headersAPI= {'accept': 'application/json','Authorization': 'Bearer your_UP_token_here',}
    headersAPIFirefly = {'accept': 'application/json','Authorization': 'Bearer your_Firefly_token_here',}
    fireflyURL = 'https://your_firefly_url'
    sTagToSearch = fireflyURL+'/api/v1/tags/'
    accountmatrix={"UP Account IDs here followed with the integer for the matching firefly account":3,"add as many as you want":11,}    
    filecount = -1
    fname = str(filecount)+'w.json'
    fileexists = 1
    while fileexists==1:
        filecount=filecount+1
        fname=str(filecount)+'w.json'
        try:
            with open(fname) as file:
                for line in file:
                    fileexists=1
        except IOError:
            fileexists=0
    newfilename=fname
    print('Incoming Webhook listed below:') 
    print(request.json); 
    print('Saved as *w.json') 
    with open(newfilename, 'w') as json_file: 
        json.dump(request.json, json_file) 
    with open(newfilename, "r") as read_file: 
        data=json.load(read_file) 
    if (data['data']['attributes']['eventType'])=='TRANSACTION_CREATED':	
        stringtolookfor=data['data']['relationships']['transaction']['links']['related'] 
        r = requests.get(stringtolookfor,headers=headersAPI) 
        newtransaction = r.json() 
        print('') 
        print('Transaction downloaded as below:') 
        print(newtransaction) 
        print('Saved as *.json') 
        filecount = -1 
        txname = str(filecount)+'.json' 
        fileexists = 1 
        while fileexists ==1: 
            filecount+=1 
            txname=str(filecount)+'.json' 
            try: 
                with open(txname) as file:
                    for line in file: 
                        fileexists=1 
            except IOError as e: 
                fileexists=0 
            newtxname=txname 
        with open(newtxname, 'w') as json_file: 
            json.dump(newtransaction, json_file)
		##############
        txdesc=newtransaction['data']['attributes']['description']
		##This section checks if the transaction is a transfer, if it is the transfers are saved depending on if to or from an account. 
    		##Logic is that another program will then match the two sides of a transfer and upload simultaneously to Firefly and deleting the relevant files.    
        if txdesc[0:11]=='Transfer to':
            print('Transfer to, thus saving this transaction for future reconciliation & uploading. 1')
       		#Now actually save the file
       		#see if this transaction is already on firefly.
            sTagToSearch=fireflyURL+'/api/v1/tags/'+newtransaction['data']['id']+'/transactions'
			#Ask firefly api if tag exists        
            r = requests.get(sTagToSearch,headers=headersAPIFirefly)
            fireflyApiResponse = r.json()
            try:
                if fireflyApiResponse['message']=='Resource not found' or fireflyApiResponse['meta']['pagination']['total']==0:
                    print('transaction not found in firefly saving to file for recon & upload, please create it. 2')
                    filecount = -1 
                    fname = 'tt'+str(filecount)+'.json'
                    fileexists = 1
                    while fileexists==1:    
                        filecount+=1
                        fname = 'tt'+str(filecount)+ '.json'                    
                        try:
                            with open(fname) as file:
                                for line in file:
                                    fileexists=1
                        except IOError:
                            fileexists=0

                print("Saving as: "+fname)
                with open(fname, 'w') as outfile:
                    json.dump(newtransaction, outfile)
            except:
                print("Transaction already exists. Not saving for later upload. 3")           
        elif txdesc[0:13]=='Transfer from':
            print("Transfer from, thus saving this transaction for future reconciliation & uploading. 4")
        	#Check if this transaction is present
            sTagToSearch=fireflyURL+'/api/v1/tags/'+newtransaction['data']['id']+'/transactions'
        	#Ask firefly api if tag exists        
            r = requests.get(sTagToSearch,headers=headersAPIFirefly)
            fireflyApiResponse = r.json()
            print(fireflyApiResponse)
            try:
                if fireflyApiResponse['message']=='Resource not found' or fireflyApiResponse['meta']['pagination']['total']==0:
                    print('transaction not found in firefly, saving for later upload & recon. 5')
##This section saves the transfer into a file for later processing and uploading.
                    filecount = -1
                    fname = 'tf'+str(filecount)+'.json'
                    fileexists = 1
                    while fileexists==1:    
                        filecount+=1
                        fname = 'tf'+str(filecount)+ '.json'
                        try:
                            with open(fname) as file:
                                for line in file:
                                    fileexists=1
                        except IOError:
                            fileexists=0
   ##All transfer to transactions are saved with tf as start of name.
                print("Saving as: "+fname)
                with open(fname, 'w') as outfile:
                    json.dump(newtransaction, outfile)

            except:
                print("Transaction already exists in firefly. Not saving 6")
##All transfer processing is done, now move onto withdrawals, deposits. 
        else:
        #We now know its not a transfer, so proceed as a Xydeposit or withdrawal.
        #In both instances ensure that the file hasn't already been uploaded to firefly, so wont create duplicates.
        #Transactions can only be searched for in a meaningful way if using tags, else we can only filter by values & dates which is a hassle.
        #As such all transactions will be tagged with the ID from UP's API in Firefly.
            sTagToSearch=fireflyURL+'/api/v1/tags/'+newtransaction['data']['id']+'/transactions'
        		#Ask firefly api if tag exists        
            r = requests.get(sTagToSearch,headers=headersAPIFirefly)
            fireflyApiResponse = r.json()
            try:
                if fireflyApiResponse['message']=='Resource not found' or fireflyApiResponse['meta']['pagination']['total']==0:
                    print('transaction not found, please create it. 7')
                    print(newtransaction['data']['attributes']['amount']['value'])
                    if float(newtransaction['data']['attributes']['amount']['value'])<=0:
						#Check if this is a quick save, if so then don't create a withdrawal.
                        print("This is a withdrawal. Starting firefly withdrawal update. 8")
                        txFirefly = {"type": "withdrawal","currency_code": "AUD"}
                        			#Set clear json TxFirefly to send as new transaction and fill with the incoming data from Up.
                        txFirefly["date"]=newtransaction['data']['attributes']['createdAt'][0:16]+newtransaction['data']['attributes']['createdAt'][19:]
                        txFirefly["source_id"]=accountmatrix[newtransaction['data']['relationships']['account']['data']['id']]
                        txFirefly["destination_name"]=newtransaction['data']['attributes']['description']
                        			#All firefly values must be positive, so use the absolute.
                        txFirefly["amount"]=newtransaction['data']['attributes']['amount']['value'][1:]
                        			#Category might be coded wrongly, check if categories have been assigned. If so assign one.
                        if not(newtransaction['data']['relationships']['category']['data']==None): 
                            txFirefly["category_name"]=newtransaction['data']['relationships']['category']['data']['id']
                        txFirefly["tags"]=newtransaction['data']['id']
                        txFirefly["description"]=''			#Ensure some sort of description is uploaded
                        if not(newtransaction['data']['attributes']['rawText']==None):    
                            txFirefly["notes"]=newtransaction['data']['attributes']['rawText']
                            txFirefly["description"]=txFirefly["description"]+' '+newtransaction['data']['attributes']['rawText']
                        if not(newtransaction['data']['attributes']['message']==None): 
                            txFirefly["description"]=txFirefly["description"]+' '+newtransaction['data']['attributes']['message']
                            txFirefly["notes"]=newtransaction['data']['attributes']['message']
                        else:
                            txFirefly["description"]=txFirefly["description"]+newtransaction['data']['attributes']['description']
                        			#Upload the tx
                        fireflyapiupload=fireflyURL+'/api/v1/transactions'
                        payload = {"transactions":[txFirefly]}
                        r = requests.post(fireflyapiupload,headers=headersAPIFirefly,json=payload)
                        newtransaction = r.json()
                        print('9')
                        print(newtransaction)

                    elif float(newtransaction['data']['attributes']['amount']['value'])>=0:
                        print("Moving into deposit steps")
                        txFirefly={"type":"deposit","currency_code":"AUD"}
						#Check if deposit or actually a round up.
						#Also check for quick saves.
                        if newtransaction['data']['attributes']['description']=='Round Up':
                            print("This is a round Up.")
                            #mes from transaction account.
                            txFirefly["type"]='transfer'
                            txFirefly["source_id"]=accountmatrix["your_UP_transaction_account_ID_here"]
                        else:
                            txFirefly["source_name"]=newtransaction['data']['attributes']['description']
                            print("This is a deposit, starting deposit firefly update. 10")
						#Set clear json TxFirefly to send as new transaction and fill with the incoming data from Up.
                    				#Remove seconds from the date time submitted.
                        txFirefly["date"]=newtransaction['data']['attributes']['createdAt'][0:16]+newtransaction['data']['attributes']['createdAt'][19:]
                        txFirefly["destination_id"]=str(accountmatrix[newtransaction['data']['relationships']['account']['data']['id']])
                        txFirefly["amount"]=newtransaction['data']['attributes']['amount']['value']
                    				#Category might be coded wrongly, check if categories have been assigned. If so assign one.
                        if not(newtransaction['data']['relationships']['category']['data'])==None:
                            txFirefly["category_name"]=newtransaction['data']['relationships']['category']['data']['id']
                        txFirefly["description"]=''
                        if not(newtransaction['data']['attributes']['rawText']==None):    
                            txFirefly["description"]=txFirefly["description"]+' '+newtransaction['data']['attributes']['rawText']
                        if not(newtransaction['data']['attributes']['message']==None): 
                            txFirefly["description"]=txFirefly["description"]+' '+newtransaction['data']['attributes']['message']
                        else:
                            txFirefly["description"]=txFirefly["description"]+' '+newtransaction['data']['attributes']['description']
                        txFirefly["tags"]=newtransaction['data']['id']
                        fireflyapiupload=fireflyURL+'/api/v1/transactions'
                        payload = {"transactions":[txFirefly]}
                        r = requests.post(fireflyapiupload,headers=headersAPIFirefly,json=payload)
                        newtransaction = r.json()
                        print('11')
                        print(newtransaction)
            except:
                print("Either error or transaction already exists on firefly. 12")
                print(fireflyApiResponse)
###############################
        return Response(status=200)
