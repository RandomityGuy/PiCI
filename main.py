from os import mkdir
import pici.app as app
import os

print("PICI: 1.0.0")
print("Commands:")
print("load <app.json>: build app.json")
print("apps: list available apps")
print("list: list running apps")
print("start <app_name>: start app with name <app_name>")
print("stop <app_name>: stop app with name <app_name>")
print("build <app_name>: build app with name <app_name>")
print("tail <app_name>: tail log of app with name <app_name>")
print("exit: exit pici")

os.makedirs('.pici/apps', exist_ok=True)

apps: list[app.App] = []

while True:
    cmd = input(">>> ")
    cmd_args = cmd.split(" ")
    if cmd_args[0] == "load":
        if len(cmd_args) == 2:
            thisapp = app.App()
            if thisapp.load(cmd_args[1]):
                apps.append(thisapp)
                print("Loaded " + cmd_args[1])
            else:
                print("Error loading " + cmd_args[1])
    if cmd_args[0] == "apps":
        print("Apps:")
        # Get directories in .pici/
        toprint = []
        for path in os.listdir('.pici/'):
            if os.path.isdir(os.path.join('.pici/', path)):
                toprint.append(path)
        for a in apps:
            if a.name not in toprint:
                toprint.append(a.name)
        for a in toprint:
            print(a)
    if cmd_args[0] == "list":
        print("Running apps:")
        for a in apps:
            if a.startproc != None:
                print(a.name)
    if cmd_args[0] == "start":
        if len(cmd_args) == 2:
            # Get app
            for a in apps:
                if a.name == cmd_args[1]:
                    a.start()

    if cmd_args[0] == "stop":
        if len(cmd_args) == 2:
            # Get app
            for a in apps:
                if a.name == cmd_args[1]:
                    a.stop()

    if cmd_args[0] == "build":
        if len(cmd_args) == 2:
            # Get app
            for a in apps:
                if a.name == cmd_args[1]:
                    a.build()

    if cmd_args[0] == "tail":
        if len(cmd_args) == 2:
            # Get app
            for a in apps:
                if a.name == cmd_args[1]:
                    a.tail()

    if cmd_args[0] == "exit":
        break


