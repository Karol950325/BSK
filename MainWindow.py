import cipher as cipher
#import fin
from Cryptodome.Cipher import AES
import tkinter as tk
from tkinter import messagebox
import zmq
import time
import os
import struct
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
import random
from Crypto import Random


class MainWindow(object):
    """description of class"""
    nonce=''
    ciphertext=''
    tag=''
    nonceRec=''
    ciphertextRec=''
    tagRec=''

    def __init__(self, *args, **kwargs):

        return super().__init__(*args, **kwargs)

    def makeWindow(self):

        window = tk.Tk()  # tworzenie okna głównego
        window.title("Szyfrowanie i przesyl danych")  # ustawienie tytułu okna głównego
        window.geometry("500x360")
        menu=tk.Label(text="MENU", bg="lightblue",height="5",width="21")
        menu.place(x=0,y=0)
        przeslanaWiadomosc=tk.Label(text='miejsce na wyswietlenie odszyfrowanej wiadomosci',bg="darkgray",height="18",width="40")
        przeslanaWiadomosc.place(x=150,y=0)
        przeslijDaneButton = tk.Button(window, text="Przeslij dane", command=self.przeslijDane, height="2",width="20")
        przeslijDaneButton.place(x=0,y=80)
        przyjmijDaneButton = tk.Button(window, text="Przyjmij dane", command=self.przyjmijDane, height="2",width="20")
        przyjmijDaneButton.place(x=0,y=120)
        szyfrujDaneButton = tk.Button(window, text="Szyfrowanie danych", command=self.szyfrowanieDanych, height="2",width="20")
        szyfrujDaneButton.place(x=0,y=160)
        odszyfrujDaneButton = tk.Button(window, text="Odszyfrowanie danych", command=self.odszyfrowanieDanych, height="2",width="20")
        odszyfrujDaneButton.place(x=0,y=200)
        stopka=tk.Label(window, text="Karol Kwiatek i Maciej Pławski")
        stopka.pack(side='bottom')
        help=tk.Button(window, text="Help", command=self.onClickHelp, height="2",width="20")
        help.place(x=0, y=240)
        fileEnc = tk.Button(window, text="Szyfruj plik", command=self.szyfrowaniePliku(), height="2", width="20")
        fileEnc.place(x=0, y=280)
        fileDec = tk.Button(window, text="Odszyfruj plik", command=self.odszyfrowaniePliku(), height="2", width="20")
        fileDec.place(x=0, y=320)
        tk.mainloop()  # wywołanie pętli komunikatów

        return 0

    def przeslijDane(self):
        # 1...............................................
        arr=[self.nonce,self.ciphertext,self.tag]
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5005")
        for request in range(3):
            print("Sending request %s …" % arr[request])
            socket.send(arr[request])

            message = socket.recv()
            print("Received reply %s [ %s ]" % (request, message))

        socket.close()

        return 0
        # 1...............................................

    def przyjmijDane(self):
        # 2....................klient nasluchuje na odebranie danych
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5005")
        timer=3
        index=0
        arrRec=[self.nonceRec,self.ciphertextRec,self.tagRec]
        while timer!=0:
            message = socket.recv()
            arrRec[index]=message
            print("Received request: %s" % message)

            time.sleep(1)

            socket.send(b"World")
            timer -= 1
            index += 1
        socket.close()

        self.nonceRec=arrRec[0]
        self.ciphertextRec=arrRec[1]
        self.tagRec=arrRec[2]
        return 0
        # 2.........................................



    def szyfrowaniePliku(self):

        key = b'Sixteen byte key'
        #key1=bytes(key)
        in_filename = "demofile.txt"
        out_filename = "test.txt"
        chunksize = 64 * 1024
        if not out_filename:
            out_filename = in_filename + '.enc'

        #iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
        iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
        iv1=b'Sixteen byte key'
        #iv1=bytes(iv)
        encryptor = AES.new(key, AES.MODE_CBC, iv1)
        filesize = os.path.getsize(in_filename)

        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                outfile.write(struct.pack('<Q', filesize))
                outfile.write(iv1)

                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += str.encode(' ' * (16 - len(chunk) % 16))

                    outfile.write(encryptor.encrypt(chunk)) #tutaj dodalem str.encode()


        return 0;

    def odszyfrowaniePliku(selfself):

        key = b'Sixteen byte key'
        # key1=bytes(key)
        in_filename = "test.txt"
        out_filename = "rozszyfrowany.txt"
        chunksize = 64 * 1024
        if not out_filename:
            out_filename = os.path.splitext(in_filename)[0]

        with open(in_filename, 'rb') as infile:
            origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
            iv = infile.read(16)
            decryptor = AES.new(key, AES.MODE_CBC, iv)

            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(decryptor.decrypt(chunk))

                outfile.truncate(origsize)
        return 0;

    def szyfrowanieDanych(self):
        print("Wpisz w konsoli wiadomosc ktora chesz zaszyfrowac i przeslac")
        dane=input()
        daneb=bytes(dane,'utf-8')
        key = b'Sixteen byte key' #testowy klucz, DO ZAMIANY w finalnej wersji
        cipher = AES.new(key, AES.MODE_ECB)
        self.nonce = cipher.nonce
        self.ciphertext, self.tag = cipher.encrypt_and_digest(daneb)

        return 0

    def odszyfrowanieDanych(self):
        key = b'Sixteen byte key'  # testowy klucz, DO ZAMIANY w finalnej wersji
        cipher = AES.new(key, AES.MODE_EAX, nonce=self.nonceRec)
        plaintext = cipher.decrypt(self.ciphertextRec)
        try:
            cipher.verify(self.tagRec)
            print("Wiadomosc po odkodowaniu: ", plaintext)
        except ValueError:
            print("Key incorrect or message corrupted")
        return 0

    def onClickHelp(self):
        tk.messagebox.showinfo("Pomoc", '1.Przeslij dane:   Zaszyfrowane dane zostają wyslane na serwer. '
                                        'Najpierw musisz zaszyfrowac dane za pomacą przycisku szyfruj dane.\n\n'
                                        '2.Odbierz dane:    Przycisk musi byc wcisniety u jednej osoby aby dane'
                                        ' po wcisnieciu przeslij dane od drugiej osoby mogly zostac '
                                        'przeslane przez serwer i odebrane u osoby pierwszej. '
                                        'Najpierw wciskamy odbierz dane u jednej osoby, '
                                        'a dopiero wtedy druga osoba moze wcisnac preslij dane.\n\n'
                                        '3.Szyfrowanie danych:  Przycisk ten pobiera od uzytkownika '
                                        'wiadomosc z konsoli(tymczasowo), a po wpisaniu wiadomosci szyfruje ja. '
                                        'Taka wiadomosc jest gotowa do wyslania przyciskiem przeslij dane.\n\n '
                                        '4.Odszyfrowanie danych:    Przycisk ten odszyfrowuje dane otrzymane od innego uzytkownika, '
                                        'a nastepnie wyswietla odszyfrowana juz wiadomosc.\n\n '
                                        '5.Help:    Pomoc')







