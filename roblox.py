import pymem
import os
import glob
import re
import time

os.system("title Flint")

# Some of the code are from Big dick jay_howdy so credits to him

pm = None
Offsets = None
LogsFolder = None

def isProcessOpen(Name):
    try:
        return pymem.Pymem(Name)
    except:
        return False
    
UWP = [
    0x48, #Name
    0x60, #Parent
    0x50, #Children
    0x230 #LocalPlayer
]

Web = [
    0x48, #Name
    0x60, #Parent
    0x50, #Children
    0x240 #LocalPlayer
]

LogsPath = [
    os.path.expandvars(r'%LOCALAPPDATA%\Roblox\logs'),
    os.path.expandvars(r'%LOCALAPPDATA%\Packages\ROBLOXCORPORATION.ROBLOX_55nm5eh3cm0pr\LocalState\logs')
]

patterns = [
    b'\x50\x6C\x61\x79\x65\x72\x73.........\x07\x00\x00\x00\x00\x00\x00\x00\x0F', # Players
    b'\x49\x6E\x6A\x65\x63\x74..........\x06' #Inject LocalScript
]

ProcessNames = ["RobloxPlayerBeta.exe", "Windows10Universal.exe"]

if isProcessOpen(ProcessNames[0]):
    pm = pymem.Pymem(ProcessNames[0])
    Offsets = Web
    LogsFolder = LogsPath[0]

    robloxver = "Web"
elif isProcessOpen(ProcessNames[1]):
    pm = pymem.Pymem(ProcessNames[1])
    Offsets = UWP
    LogsFolder = LogsPath[1]

    robloxver = "Uwp"
else:
    print("No roblox proccess found.")
    print("Closing in 5 seconds")
    time.sleep(5)
    exit()

class Utility:
    def aobscan(pattern):
        try:
            return pymem.pattern.pattern_scan_all(pm.process_handle, pattern, return_multiple=True)
        except:
            return []
        
    def allocateMemory(memory):
        try:
            return pm.allocate(memory)
        except:
            return False

    def intToBytes(val):
        t = [ val & 0xFF ]
        for i in range(1, 8):
            t.append((val >> (8 * i)) & 0xFF)

        return t
    
    # Credits to big dick jay_howdy

    def bytesToPattern(val):
        newpattern = ""
        for byte in val:
            newpattern = newpattern + '\\x' + format(byte, "02X")
        
        return bytes(newpattern, encoding="utf-8")

    def readQword(address):
        try:
            return pm.read_ulonglong(address)
        except:
            return False
        
    def readString(address):
        try:
            return pm.read_string(address)
        except:
            return False
        
    def readBytes(address, length):
        try:
            return pm.read_bytes(address, length)
        except:
            return False

    def writeQword(address, value):
        try:
            return pm.write_ulonglong(address, value)
        except:
            return False
        
    def writeBytes(address, value, length):
        try:
            return pm.write_bytes(address, value, length)
        except:
            return False

class toInstance: # Credits to big dick jay_howdy
        def __init__(self, address):
            self.address = address

        @property
        def Name(self):
            pointer = Utility.readQword(self.address + Offsets[0])

            if pointer:
                fl = Utility.readQword(pointer + 0x18)
                if fl == 0x1F:
                    pointer = Utility.readQword(pointer)
                
                return Utility.readString(pointer)
            
            return "???"
        
        @property
        def ClassName(self):
            pointer = Utility.readQword(self.address + 0x18)
            pointer = Utility.readQword(pointer + 0x8)

            if pointer:
                fl = Utility.readQword(pointer + 0x18)
                if fl == 0x1F:
                    pointer = Utility.readQword(pointer)

                return Utility.readString(pointer)
        
            return "???"
        
        @property
        def Parent(self):
            return toInstance(Utility.readQword(self.address + Offsets[1]))
        
        def GetChildren(self):
            instances = []
            
            pointer = Utility.readQword(self.address + Offsets[2])

            if pointer:
                childstart = Utility.readQword(pointer + 0)
                childend = Utility.readQword(pointer + 8)
                at = childstart
                while at < childend:
                    child = Utility.readQword(at)
                    
                    instances.append(toInstance(child))
                    
                    at = at + 16
            
            return instances
        
        def GetDescendants(self):
            descendant = []
            def Scan(Object):
                for child in Object.GetChildren():
                    descendant.append(child)
                    Scan(child)

            Scan(self)

            return descendant
        
        def FindFirstChild(self, name):
            for v in self.GetChildren():
                if v.Name == name:
                    return v
        
        def FindFirstClass(self, name):
           for v in self.GetChildren():
                if v.ClassName == name:
                    return v
                
        def GetLastAncestor(self):
            Ancestors = []

            def GetAncestor(Object):
                if Object.Parent.Name != "???":
                    GetAncestor(Object.Parent)
                    Ancestors.append(Object.Parent)
            
            GetAncestor(self.Parent)

            return Ancestors[-1]
        
        def SetParent(self, other):
            pass
            #Utility.writeQword(self.address + Offsets[1], other.address)

class Injection:
    def __init__(self):
        LLFP = max(glob.glob(LogsFolder + "/*"), key=os.path.getmtime)
        File = open(LLFP, "r")

        Results = re.findall("Replicator created: (\w+)", File.read())

        if len(Results) > 0:
            self.ClientReplicator = int(Results[-1], 16)
    
    def FindInject(self):
        injectscript = False
        for result in Utility.aobscan(patterns[1]):
            bytesresult = Utility.intToBytes(result)
            
            for result in Utility.aobscan(Utility.bytesToPattern(bytesresult)):
                if (Utility.readQword(result - Offsets[0] + 8) == result - Offsets[0]):
                    injectscript = result - Offsets[0]

        # Credits to big dick jay_howdy

        return injectscript

# pls dont judge my bad code :(
