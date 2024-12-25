# Robot MRPiZ2
# Auteur : Nicolas
# Date dernière modification: 24/12/24
# Firmware du robot MRPiZ2 (carte Raspberry Pi Pico)
# Version : 0.1

#lib
import time, re
import robot
import uasyncio as asyncio
from machine import UART, Pin
import gc


# variables globales
_data_simple = 0 # si reception d'une commande simple sans paramètre (exemple : #BAT! ou #FV!)
deux_para = 0 # si reception d'une commande avec 2 paramètres
send_data = 0
data_send = 0

# configuration du l'UART 
uart0 = UART(0, baudrate=230400, tx=Pin(16), rx=Pin(17))


led_int = Pin(25, Pin.OUT)  # broche GP25 ou WL_GPI00 en sortie



async def uart_sender(uart):
    global send_data, data_send
    writer = asyncio.StreamWriter(uart, {})
    while True:
        if(send_data == 1):
          send_data = 0
          writer.write(str(data_send)+'\n')
          print("Send 3.14")
          
          await writer.drain()
        await asyncio.sleep(0.2)

async def uart_receiver(uart):
    global _data_simple, deux_para, send_data, data_send
    reader = asyncio.StreamReader(uart)
    while True:
        try:
          message = await reader.readline()

          data = message.decode('utf-8')#conversion en chaine de caractère
          print(data)
          ################################
          # extraction de la commande :
          try:
            cmd_recu = re.search(r'#([A-Za-z]+),', data)
            cmd_recu = str(cmd_recu.group(1)) # conversion
          except: # c'est une commande avec un paramètre
            _data_simple = 1 # reception d'une commande simple, sans paramètre
          
          if (_data_simple == 1):
            # reception d'une commande simple sans paramètre
            cmd_recu = re.search(r'#([A-Za-z]+)!', data)
            cmd_recu = str(cmd_recu.group(1)) # conversion
          else:
            ################################
            # extraction du paramètre n°1 :
            #parametre1_recu = re.search(r",(\d+)", data)
            try:
              parametre1_recu = re.search(r',([0-9]+),', data)
              print("Paramètre n°1 :", parametre1_recu.group(1))
              deux_para = 1
              print("Commande avec 2 paramètres")
            except:
              # S'il y a 1 paramètre : 
              parametre1_recu = re.search(r',([0-9]+)!', data)
              parametre1_recu = int(parametre1_recu.group(1))
          
            ################################
            # extraction du paramètre n°2 :
            if (deux_para == 1):
              try:
                parametre2_recu = re.search(r',([0-9]+)!', data)
                parametre2_recu = int(parametre2_recu.group(1))
              except:
                print("Pas de paramètre n°2")
				
        except:
          print("Erreur reception")
          
        
        print('CMD RECU:', cmd_recu)

        if(cmd_recu == "FV"):
            send_data = 1
            data_send = 0.1
            print("send data")

        if(cmd_recu == "BAT"):
            send_data = 1
            data_send = robot.battery()
            print("send data")

        if(cmd_recu == "PROX"):
            send_data = 1
            data_send = robot.proxRead(parametre1_recu)
            print("send data")

        if(cmd_recu == "MF"):
            robot.forward(parametre1_recu)
            print("send data")

        if(cmd_recu == "MB"):
            robot.back(parametre1_recu)
            print("send data")

        if(cmd_recu == "STP"):
            send_data = 0
            robot.stop()
            print("send data")

        if(cmd_recu == "TR"):
            robot.turnRight(parametre1_recu)
            print("turn right")
            
        if(cmd_recu == "TL"):
            robot.turnLeft(parametre1_recu)
            print("turn left")            
            
        if(cmd_recu == "RGB"):
            robot.ledRgb(1,1,1)           

        if(cmd_recu == "EDL"):
            send_data = 1
            data_send = robot.encoderLeft()

        # lecture encodeur right
        if(cmd_recu == "EDR"):
            send_data = 1
            data_send = robot.encoderRight()








print("MRPiZ2 Start")


asyncio.create_task(uart_receiver(uart0))
asyncio.create_task(uart_sender(uart0))

async def main():
  while True:
    led_int.toggle()
    # run activities
    await asyncio.sleep(1)
    print('Running...')

asyncio.run(main())



# End file

