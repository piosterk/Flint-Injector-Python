import roblox
import time

def main():
    print("Injecting", roblox.robloxver.upper())

    Utility = roblox.Utility

    Injection = roblox.Injection()
    ToInstance = roblox.toInstance
    Offsets = roblox.Offsets

    ClientReplicator = ToInstance(Injection.ClientReplicator)

    if ClientReplicator.Name == "ClientReplicator":
        print("Found", ClientReplicator.Name, hex(ClientReplicator.address))

        Game = ClientReplicator.GetLastAncestor()
        print("Found", Game.Name, hex(Game.address))

        Workspace = Game.FindFirstClass("Workspace")
        print("Found", Workspace.Name, hex(Workspace.address))

        Players = Game.FindFirstClass("Players")
        print("Found", Players.Name, hex(Players.address))

        LocalPlayer = ToInstance(Utility.readQword(Players.address + Offsets[-1]))
        print("Found", LocalPlayer.Name, hex(LocalPlayer.address))

        Backpack = LocalPlayer.FindFirstClass("Backpack")
        print("Found", Backpack.Name, hex(Backpack.address))

        Tool = Backpack.FindFirstClass("Tool")
        print("Found", Tool.Name, hex(Tool.address))

        if Tool:

            ToolScript = Tool.FindFirstClass("LocalScript")

            InjectionScript = ToInstance(InjectionAddress)
            InjectionBytes = Utility.readBytes(InjectionScript.address + 0x100, 0x150)

            if ToolScript:
                print("Found", ToolScript.Name, hex(ToolScript.address))

                print("Getting inject script...")
                InjectionAddress = Injection.FindInject()

                if InjectionAddress:
                    print("Got inject script!")

                    InjectionScript = ToInstance(InjectionAddress)
                    InjectionBytes = Utility.readBytes(InjectionScript.address + 0x100, 0x150)
                    
                    Utility.writeBytes(ToolScript.address + 0x100, InjectionBytes, 0x150)

                    print("Equip", Tool.Name)
                else:
                    print("Inject script not found")
            else:
                print("Localscript not found.")
        else:
            print("Tool not found.")
    else:
        print("Inject failed, please join a game.")

    print("Closing in 5 seconds")

    time.sleep(5)

main()