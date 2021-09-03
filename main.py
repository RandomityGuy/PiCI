
import pici.app as app
import os
import shutil

print("PiCI: 1.0.0")
print("Commands:")
print("help: show help")
print("load <app.json>: build app.json")
print("apps: list available apps")
print("list: list running apps")
print("start <app_name>: start app with name <app_name>")
print("stop <app_name>: stop app with name <app_name>")
print("reload <app_name>: reload app with name <app_name>")
print("build <app_name> [-s]: build app with name <app_name>, -s: silent")
print("tail <app_name>: tail log of app with name <app_name>")
print("output <app_name>: output log of app with name <app_name>")
print("error <app_name>: error log of app with name <app_name>")
print("exit: exit PiCI")

os.makedirs('.pici/apps', exist_ok=True)
os.makedirs('.pici/configs', exist_ok=True)

apps: list[app.App] = []

for config in os.listdir('.pici/configs'):
    if not config.endswith('.json'):
        continue
    thisapp = app.App()
    if thisapp.load(os.path.join('.pici/configs', config)):
        apps.append(thisapp)

while True:
    cmd = input(">>> ")
    cmd_args = cmd.split(" ")

    if cmd_args[0] == "help":
        print("Commands:")
        print("help: show help")
        print("load <app.json>: build app.json")
        print("apps: list available apps")
        print("list: list running apps")
        print("start <app_name>: start app with name <app_name>")
        print("stop <app_name>: stop app with name <app_name>")
        print("reload <app_name>: reload app with name <app_name>")
        print("build <app_name> [-s]: build app with name <app_name>, -s: silent")
        print("tail <app_name>: tail log of app with name <app_name>")
        print("output <app_name>: output log of app with name <app_name>")
        print("error <app_name>: error log of app with name <app_name>")
        print("exit: exit PiCI")

    if cmd_args[0] == "load":
        if len(cmd_args) == 2:
            thisapp = app.App()
            if thisapp.load(cmd_args[1]):
                apps.append(thisapp)
                print("Loaded " + cmd_args[1])
                shutil.copy(cmd_args[1], '.pici/configs/' + thisapp.name + '.json')
            else:
                print("Error loading " + cmd_args[1])

    if cmd_args[0] == "apps":
        print("Apps:")
        # Get directories in .pici/
        toprint = []
        for path in os.listdir('.pici/apps'):
            if os.path.isdir(os.path.join('.pici/apps', path)):
                toprint.append(path)
        for a in apps:
            if a.name not in toprint:
                toprint.append(a.name)
        for a in toprint:
            print(a)

    if cmd_args[0] == "list":
        print("Running apps:")
        for a in apps:
            if a.is_running():
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

    if cmd_args[0] == "reload":
        if len(cmd_args) == 2:
            # Get app
            for a in apps:
                if a.name == cmd_args[1]:
                    a.restart()

    if cmd_args[0] == "build":
        if len(cmd_args) >= 2:
            # Get app
            for a in apps:
                if a.name == cmd_args[1]:
                    if len(cmd_args) == 3 and cmd_args[2] == "-s":
                        a.build(False)
                    else:
                        a.build()

    if cmd_args[0] == "tail":
        if len(cmd_args) == 2:
            # Get app
            for a in apps:
                if a.name == cmd_args[1]:
                    a.tail()

    if cmd_args[0] == "output":
        if len(cmd_args) == 2:
            # Get app
            if os.path.isfile('.pici/outputs/' + cmd_args[1] + '.out.log'):
                with open('.pici/outputs/' + cmd_args[1] + '.out.log', 'r') as myfile:
                    print(myfile.read())

    if cmd_args[0] == "error":
        if len(cmd_args) == 2:
            # Get app
            if os.path.isfile('.pici/outputs/' + cmd_args[1] + '.err.log'):
                with open('.pici/outputs/' + cmd_args[1] + '.err.log', 'r') as myfile:
                    print(myfile.read())
                    

    if cmd_args[0] == "exit":
        break


