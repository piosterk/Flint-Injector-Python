import pymem
import os
import glob
import re
import time
import random
import string

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# // Some of the code are from Big dick jay_howdy so credits to him

os.system("title Flint")

Process = None
Selection = None
LogsFolder = None

class Misc:
    Web = {
        "Name": 0x48,
        "ClassName": 0x18,
        "Parent": 0x60,
        "Children": 0x50,
        "LocalPlayer": 0x240,
        "Logs": os.path.expandvars(r'%LOCALAPPDATA%\Roblox\logs')
    }

    Uwp = {
        "Name": 0x48,
        "ClassName": 0x18,
        "Parent": 0x60,
        "Children": 0x50,
        "LocalPlayer": 0x230,
        "Logs": os.path.expandvars(r'%LOCALAPPDATA%\Packages\ROBLOXCORPORATION.ROBLOX_55nm5eh3cm0pr\LocalState\logs')
    }
    
    Patterns = {
        "Players": b'\x50\x6C\x61\x79\x65\x72\x73.........\x07\x00\x00\x00\x00\x00\x00\x00\x0F',
        "Inject": b'\x49\x6E\x6A\x65\x63\x74..........\x06'
    }

    ProcessNames = ["RobloxPlayerBeta.exe", "Windows10Universal.exe"]

class Util:
    def aobScan(pattern):
        try:
            return pymem.pattern.pattern_scan_all(Process.process_handle, pattern, return_multiple=True)
        except:
            return []
        
    def allocateMemory(memory):
        try:
            return Process.allocate(memory)
        except:
            return False

    def intToBytes(val):
        t = [ val & 0xFF ]
        for i in range(1, 8):
            t.append((val >> (8 * i)) & 0xFF)

        return t

    def bytesToPattern(val):
        newpattern = ""
        for byte in val:
            newpattern = newpattern + '\\x' + format(byte, "02X")
        
        return bytes(newpattern, encoding="utf-8")

    def readQword(address):
        try:
            return Process.read_ulonglong(address)
        except:
            return False
        
    def readString(address):
        try:
            return Process.read_string(address)
        except:
            return False
        
    def readBytes(address, length):
        try:
            return Process.read_bytes(address, length)
        except:
            return False
        
    def writeInt(address, val):
        try:
            return Process.write_int(address, val)
        except:
            return False
        
    def writeString(address, val):
        try:
            return Process.write_string(address, val)
        except:
            return False

    def writeQword(address, value):
        try:
            return Process.write_ulonglong(address, value)
        except:
            return False
        
    def writeBool(address, value):
        try:
            return Process.write_bool(address, value)
        except:
            return False
        
    def writeBytes(address, value, length):
        try:
            return Process.write_bytes(address, value, length)
        except:
            return False
        
class toInstance: # Credits to big dick jay_howdy
        def __init__(self, address):
            self.address = address

        @property
        def Name(self):
            Pointer = Util.readQword(self.address + Selection["Name"])

            if Pointer:
                QWord = Util.readQword(Pointer + 0x18)

                if QWord == 0x1F:
                    Pointer = Util.readQword(Pointer)
                
                return Util.readString(Pointer)
            
            return "???"
        
        @property
        def ClassName(self):
            Pointer = Util.readQword(self.address + Selection["ClassName"])
            Pointer = Util.readQword(Pointer + 0x8)

            if Pointer:
                QWord = Util.readQword(Pointer + 0x18)
                
                if QWord == 0x1F:
                    Pointer = Util.readQword(Pointer)
                
                return Util.readString(Pointer)
            
            return "???"
        
        @property
        def Parent(self):
            return toInstance(Util.readQword(self.address + Selection["Parent"]))
        
        @property
        def LocalPlayer(self):
            if self.ClassName == "Players":
                return toInstance(Util.readQword(self.address + Selection["LocalPlayer"]))
        
        def GetChildren(self):
            Instances = []
            
            Pointer = Util.readQword(self.address + Selection["Children"])

            if Pointer:
                Top = Util.readQword(Pointer)
                End = Util.readQword(Pointer + 8)

                Current = Top

                while Current < End:
                    ChildInstance = Util.readQword(Current)
                    
                    Instances.append(toInstance(ChildInstance))
                    
                    Current = Current + 16
            
            return Instances
        
        def GetDescendants(self):
            Descendant = []

            def Scan(Object):
                for Child in Object.GetChildren():
                    Descendant.append(Child)
                    Scan(Child)

            Scan(self)

            return Descendant
        
        def FindFirstChild(self, name, scandescendant=False):
            selection = None

            if scandescendant == False:
                selection = self.GetChildren()
            elif scandescendant == True:
                selection = self.GetDescendants()

            for Child in selection:
                if Child.Name == name:
                    return Child
                
        def FindFirstClass(self, name, scandescendant=False):
            selection = None

            if scandescendant == False:
                selection = self.GetChildren()
            elif scandescendant == True:
                selection = self.GetDescendants()

            for Child in selection:
                if Child.ClassName == name:
                    return Child
                
        def GetLastAncestor(self):
            Ancestors = []

            def GetAncestor(Object):
                if Object.Parent.Name != "???":
                    GetAncestor(Object.Parent)
                    Ancestors.append(Object.Parent)
            
            GetAncestor(self.Parent)

            return Ancestors[-1]
        
class Injection:
    ClientReplicator = False

    def __init__(self):
        Latest = max(glob.glob(LogsFolder + "/*"), key=os.path.getmtime)
        File = open(Latest, "r")

        Results = re.findall("Replicator created: (\w+)", File.read())

        if len(Results) > 0:
            self.ClientReplicator = int(Results[-1], 16)

    def FindInject(self):
        InjectScript = None
        
        for Result in Util.aobScan(Misc.Patterns["Inject"]):
            bytesResult = Util.intToBytes(Result)
            
            for Result in Util.aobScan(Util.bytesToPattern(bytesResult)):
                if (Util.readQword(Result - Selection["Name"] + 8) == Result - Selection["Name"]):
                    InjectScript = Result - Selection["Name"]

        return InjectScript

def isProcessOpen(Name):
    try:
        return pymem.Pymem(Name)
    except:
        return False
    
print('''
▄████  █    ▄█    ▄     ▄▄▄▄▀ 
█▀   ▀ █    ██     █ ▀▀▀ █    
█▀▀    █    ██ ██   █    █    
█      ███▄ ▐█ █ █  █   █     
 █         ▀ ▐ █  █ █  ▀      
  ▀            █   ██         
                              ''')

input("Press enter to start the injection.\n")

if isProcessOpen(Misc.ProcessNames[0]):
    Process = pymem.Pymem(Misc.ProcessNames[0])
    Selection = Misc.Web
    LogsFolder = Selection["Logs"]

    Version = "Web"
elif isProcessOpen(Misc.ProcessNames[1]):
    Process = pymem.Pymem(Misc.ProcessNames[1])
    Selection = Misc.Uwp
    LogsFolder = Selection["Logs"]

    Version = "Uwp"
else:
    print("No roblox proccess found.")

    print("Closing in 5 seconds")
    time.sleep(5)
    exit()
