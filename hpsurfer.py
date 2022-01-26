# hpsurfer : 
# ce programme interroge le site HPE PartSurfer pour une liste de numeros de serie , 
#recupere pour chage numero de serie les informations Product number,Product description; Part Number , part description , Part Quantity 
#et les enregistrent dans 4 fichiers textes permettant d'inxploiter ces infos 
# les numeros de serie en input sont lus dans un fichier text
# tous les fichiers ( input / ouptut sont dans le meme repertoire 
# le programme se lance sous l'interperteur python ( python hpepartsurfer.py )
# Reprise : 
# le programme fait un check point a chaque numero de serie traité 
# en cas de pb réseau , il peut etre relancé sans modification , il reprendra le traitement a partir du dernier ns traité 
# le fichier outputserialfiledone contient ns deja traité, ce fichier doit 
# exister lors lors du traitement ( meme vide , touch outputserialdone ) 
# Rejets 
# lorsque le ns est bien présent dans la base HPE , mais que les données html
# ne correspondent pas au format attendu ( cas du ns non unique :
# html demande de choisir entre plusieurs modeles .. )  alors le ns est 
# enregistré dans le fichier outputserial_todo_manual : il faut regarder alors
# dans ce fichier de quoi il retourne en interrogeant manuellement hpe 


from bs4 import BeautifulSoup
import requests 

def mydecode(col,idi): 
    # utilitaire extraction content 
    part=col.find_all(id=idi) 
    #print("partnumber=",partnumber)
    if len(part):
        #  print("partnumber not empty",len(partnumber)) 
        for i in range(len(part)):
            #  print("partnumber[",i,"]=",partnumber[i])
            partdecode=part[i].decode_contents()
            #  print("decode  parnumber ",partdecode) 
            return partdecode  

# url du site HPE Partsurfer / à compléter par le ns 
urlHPSurfer   = "https://partsurfer.hpe.com/Search.aspx?SearchText="

idserialnumber  ="ctl00_BodyContentPlaceHolder_lblSerialNumber"
idproductnumber ="ctl00_BodyContentPlaceHolder_lblProductNumber"
iddescription   ="ctl00_BodyContentPlaceHolder_lblDescription"
idtable         ="ctl00_BodyContentPlaceHolder_gridCOMBOM" 
idNoDataFound   ="ctl00_BodyContentPlaceHolder_lblNoDataFound" 
idpnlProductList="ctl00_BodyContentPlaceHolder_pnlProductList" 
serialdone=[]

# fichier des numeros de serie ( 1 / ligne ) 
inputserialfile=open("./inputserialfile.txt","r")
#inputserialfile=open("./inputtrace.txt","r")
# fichier aide debug 
outputdetailfile=open("./outputdetailfile","w")
# recuperation des sn deja traités car le traitement plante et necessite des points de reprises 
outputserialfiledone=open("./outputserialfiledone","r")
for sn  in outputserialfiledone:
    serialdone.append(sn)
outputserialfiledone.close()

sndonelen=len(serialdone)

print(" reprise traitement avec ",sndonelen," objets deja traités") 

outputserialfiledone=open("./outputserialfiledone","a")
outputserial_productnumber=open("./outputserial_productnumber.txt","a")
outputpartnumber_partdesc=open("./outputpartnumber_partdesc","a")
outputproductnumber_description=open("./outputproductnumber_description.txt","a")
outputserial_partnumber_partqty=open("./outputserial_partnumber_partqty.txt","a")
outputserial_todo_manual=open("./outputserial_todo_manual.txt","a")


configlist=[]
for sn in inputserialfile:
    # test si le reccord sn a deja eté traité 
    statussn="todo" 
    for snt in serialdone : 
        # print(sn.rstrip('\n'),snt)
        if sn.rstrip('\n') == snt.rstrip('\n') :
            statussn="done"
            print(sn.rstrip('\n'), " deja traité ")     
    if statussn=="todo":
        vgm_url = urlHPSurfer + sn 
        print("url in progress = ",vgm_url )
        html_text = requests.get(vgm_url).text 
        # print("debug htmltext=>",html_text)
        soup=BeautifulSoup(html_text,'html.parser') 
        # print("debug soup=",soup ) 
        # meme process sans le mode text 
        html1=requests.get(vgm_url).content
        soup=BeautifulSoup(html1,'html.parser')

        print(" id in progress = ",idserialnumber)
        # test si NoDataFound 
        NoDataFound=soup.find_all(id=idNoDataFound)
        pnlProductList=soup.find_all(id=idpnlProductList)
        if ( NoDataFound or pnlProductList ): 
            if NoDataFound :
                print("No reccord for serial",sn) 
                outputserialfiledone.write(sn)
                serialdone.append(sn)
            if pnlProductList :
                print(" Serial ",sn," is not unique : cant be processed : please check manually ")
                outputserial_todo_manual.write(sn)
                outputserialfiledone.write(sn)
                serialdone.append(sn)
        else:  
            # recuperation serial number et productnumber 
            serialnumberspan=soup.find_all(id=idserialnumber)
            print("debug serial number span=>", serialnumberspan)
            serialnumberdecode=serialnumberspan[0].decode_contents() 
            # recuperation serial number et productnumber 
            productnumberspan=soup.find_all(id=idproductnumber)
            #print(productnumberspan)
            productnumberdecode=productnumberspan[0].decode_contents() 
            print("product number decode",productnumberdecode) 
            # recuperation description  
            descriptionspan=soup.find_all(id=iddescription)
            #print(productnumberspan)
            descriptiondecode=descriptionspan[0].decode_contents() 
            print("description  decode",descriptiondecode) 
     
            print(" id in progress = ",idtable)
            find_all_id = soup.find_all(id=idtable)
            if not find_all_id :
                print(" no detail for ",sn," check manually" ) 
                outputserial_todo_manual.write(sn)
                outputserialfiledone.write(sn)
            else: 
                partno=  "ctl00_BodyContentPlaceHolder_gridCOMBOM_ctl00_lblPartno"
                partdesc="ctl00_BodyContentPlaceHolder_gridCOMBOM_ctl00_lblpartdesc1"
                partdesc_id="ctl00_BodyContentPlaceHolder_gridCOMBOM_ctl00_lblpartdesc1"
                partqty= "ctl00_BodyContentPlaceHolder_gridCOMBOM_ctl00_lblpartqty1"
        
        
                mytr=find_all_id[0].find_all('tr')
                mytrtotal=len(mytr) 
                print("mytr length = ",mytrtotal) 
                rownumber=0
                buffer_partnumber_partdesc=""
                buffer_serial_partnumber_partqty=""
    
                for row in mytr: 
                    #print("row=",row)
                    rownumber=rownumber+1
                    rownumber_str=str(rownumber)
                    if rownumber < 10 : 
                        rownumber_str="0"+rownumber_str 
                    col_id=0   
                    partnumberdecode=""
                    partnumberdescdecode=""
                    partqtydecode=""
                    #buffer_partnumber_partdesc=""
                    #buffer_serial_partnumber_partqty=""
                    for col in row.find_all('td'):
#                       print("col = ",col)
                        partnumber_id="ctl00_BodyContentPlaceHolder_gridCOMBOM_ctl21_lblPartno"
                        partdesc_id="ctl00_BodyContentPlaceHolder_gridCOMBOM_ctl00_lblpartdesc1"
                        partnumber_id=partno[:43] + rownumber_str + partno[45:]
                        partdesc_id=partdesc[:43] + rownumber_str + partdesc[45:]
                        partqty_id=partqty[:43] + rownumber_str + partqty[45:]
                        #print(partnumber_id)
                        #print(partdesc_id)
                        #print(partqty_id)
                        if col_id==1 : 
                            partnumberdecode=mydecode(col,partnumber_id)
                        if col_id==2 : 
                            partdescdecode=mydecode(col,partdesc_id)
                        if col_id==3 :
                            partqtydecode=mydecode(col,partqty_id)
                            buffer_partnumber_partdesc=buffer_partnumber_partdesc+partnumberdecode +"*"+ partdescdecode + '\n'
                            buffer_serial_partnumber_partqty=buffer_serial_partnumber_partqty+sn.rstrip('\n')+"*"+partnumberdecode+"*"+partqtydecode+'\n'
                            #outputpartnumber_partdesc.write(partnumberdecode +"*" + partdescdecode + '\n')
                            #outputserial_partnumber_partqty.write(sn.rstrip('\n')+"*" +partnumberdecode + "*" +partqtydecode +'\n')
                            print("serial*",sn.rstrip('\n'),"productnumber*",productnumberdecode,"rowid*",rownumber,"part number*", partnumberdecode,"part qty*",partqtydecode,  "part desc*",partdescdecode) 
                            if (rownumber==mytrtotal) : 
                                # fin de la recuperation des elements pour cet equipement on log l'equipement dans les equipements done
                                outputpartnumber_partdesc.write(buffer_partnumber_partdesc)
                                outputserial_partnumber_partqty.write(buffer_serial_partnumber_partqty)
                                outputserial_productnumber.write(sn.rstrip('\n')+"*"+productnumberdecode + '\n')
                                outputproductnumber_description.write(productnumberdecode+"*"+descriptiondecode +'\n')
                                outputserialfiledone.write(sn)
                                serialdone.append(sn)
                                buffer_partnumber_partdesc=""
                                buffer_serial_partnumber_partqty=""
                                print("==> stored to files ! ",sn) 
                        col_id=col_id+1







