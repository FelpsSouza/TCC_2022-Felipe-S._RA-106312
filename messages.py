# Classe Mensagens
from app import order
from colorama import Style, Fore
from art import *


class Messages:

    def __init__(self):
        print("msg-class")

    def get_open(self):
        return self.open

    def set_open(self, open):

        print("\n\n\n#==============================================================================#")
        print(Fore.GREEN)
        tprint("Robo  Magnata")
        print(Style.RESET_ALL)
        print("#==============================================================================#\n")

    #def get_data(self):
