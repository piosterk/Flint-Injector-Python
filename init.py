import roblox
import time

def Check(Instance):
    print(Instance.Name, hex(Instance.address), "ClassName:", Instance.ClassName)
    return Instance or False

def main():
    Utility = roblox.Util

    Injection = roblox.Injection()
    ToInstance = roblox.toInstance

    if Injection.ClientReplicator:
        ClientReplicator = ToInstance(Injection.ClientReplicator)

        if ClientReplicator.ClassName == "ClientReplicator": # Checks if its valid instance
            Game = Check(ClientReplicator.GetLastAncestor())

            Players = Check(Game.FindFirstClass("Players"))
            
            LocalPlayer = Check(Players.LocalPlayer)

            Backpack = Check(LocalPlayer.FindFirstClass("Backpack"))

            CurrentTool, ToolScript = None, None

            for Children in Backpack.GetChildren():
                if Children.ClassName == "Tool" and Children.FindFirstClass("LocalScript", True):
                    CurrentTool = Check(Children)
                    ToolScript = Check(Children.FindFirstClass("LocalScript", True))
                    break
            
            print("\nGetting injection script...")

            InjectionAddress = Injection.FindInject()

            if InjectionAddress:
                InjectionScript = Check(ToInstance(InjectionAddress))
                Length = 0x150
                
                newBytes = Utility.readBytes(InjectionScript.address + 0x100, Length)
                Utility.writeBytes(ToolScript.address + 0x100, newBytes, Length)

                print("Equip", CurrentTool.Name)
            else:
                print("Failed to get injection script.")
    else:
        print("Failed to inject, join a game first.")
    
    print("Closing in 5 seconds")
    time.sleep(5)
    exit()

main()
