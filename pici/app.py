import os, subprocess, shlex, shutil, json, sys;
from pici import outputstream;


class DomainConfig:
    domain = None
    outport = 0
    localport = 0

    def __init__(self, domain, outport, localport):
        self.domain = domain
        self.outport = outport
        self.localport = localport

class App:
    name: str = None
    git: str = None

    build_command: str = None
    start_command: str = None
    domains: list[DomainConfig] = None

    stdout = None
    stderr = None

    buildproc = None
    startproc = None

    def __init__(self):
        pass

    def load(self, path):
        try:
            with open(path, 'r') as f:
                d = json.load(f)
                self.name = d['name']
                self.git = d['git']
                self.build_command = d['build_command']
                self.start_command = d['start_command']
                self.domains = []
                for domain in d['domains']:
                    self.domains.append(DomainConfig(domain['domain'], domain['outport'], domain['localport']))
        except Exception as e:
            print('PICI: Error loading app config file')
            print(e)
            return False
        return True

    def is_running(self):
        return self.startproc != None and self.startproc.poll() == None

    def build(self, outputHere = True):
        # Build the shit
        self.setup_outputs()

        appstdout = self.stdout if not outputHere else sys.stdout
        appstderr = self.stderr if not outputHere else sys.stderr

        if not os.path.exists('.pici/apps/' + self.name):
            print('PiCI: Building app')
            os.makedirs('.pici/apps/' + self.name, exist_ok=True)
            self.buildproc = subprocess.Popen(['/usr/bin/git', 'clone', self.git, '.pici/apps/' + self.name], stdout=appstdout, stderr=appstderr)
            self.buildproc.wait()
            with open('.picigit', 'w') as f:
                print(self.git, file=f)
        else:
            old_git = None
            with open('.picigit', 'r') as f:
                old_git = f.read()
            if old_git != self.git:
                print('PiCI: Rebuilding app')
                shutil.rmtree('.pici/apps/' + self.name)
                self.buildproc = subprocess.Popen(['/usr/bin/git', 'clone', self.git, '.pici/apps/' + self.name], stdout=appstdout, stderr=appstderr)
                self.buildproc.wait()
                with open('.picigit', 'w') as f:
                    print(self.git, file=f)
            else:
                print('PiCI: Pulling changes')
                self.buildproc = subprocess.Popen(['/usr/bin/git', 'pull'], cwd='.pici/apps/' + self.name, stdout=appstdout, stderr=appstderr)
                self.buildproc.wait()
                
        print("PiCI: Running build command")
        self.buildproc = subprocess.Popen(shlex.split(self.build_command), cwd='.pici/apps/' + self.name, stdout=appstdout, stderr=appstderr)
        self.buildproc.wait()
        self.generate_nginx_conf()
        self.close_outputs()
        print("PiCI: Done building app")

    def start(self):
        print("PiCI: Starting app")
        self.setup_outputs()
        self.startproc = subprocess.Popen(shlex.split(self.start_command), cwd='.pici/apps/' + self.name, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outputstream.append_process(self.startproc, self.stdout, self.stderr)
        print("PiCI: Started app")

    def stop(self):
        print("PiCI: Stopping app")
        self.startproc.terminate()
        self.startproc.wait()
        self.close_outputs()
        print("PiCI: Stopped app")

    def tail(self):
        outputstream.tail_process(self.startproc)
        while True:
            try:
                inp = input()
                if inp == 'q':
                    break
            except KeyboardInterrupt:
                break
        outputstream.remove_tail_process()

    def setup_outputs(self):
        os.makedirs('.pici/outputs/', exist_ok=True)
        if self.stdout == None:
            self.stdout = open('.pici/outputs/' + self.name + '.out.log', 'ab', buffering=0)
        if self.stderr == None:
            self.stderr = open('.pici/outputs/' + self.name + '.err.log', 'ab', buffering=0)

    def close_outputs(self):
        if self.stdout != None:
            self.stdout.close()
        if self.stderr != None:
            self.stderr.close()
        self.stdout = None
        self.stderr = None

    def generate_nginx_conf(self):
        with open('.pici/apps/' + self.name + '/nginx.conf', 'w') as f:
            for domain in self.domains:
                print('server {', file=f)
                print('    listen ' + str(domain.outport) + ';', file=f)
                print('    server_name ' + domain.domain + ';', file=f)
                print('    location / {', file=f)
                print('        proxy_set_header Host $host;', file=f)
                print('        proxy_pass http://127.0.0.1:' + str(domain.localport) + ';', file=f)
                print('        proxy_redirect off;', file=f)
                print('    }', file=f)
                print('}', file=f)


