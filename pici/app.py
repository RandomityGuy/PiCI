import os, subprocess, shlex, shutil, json;


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

    def build(self):
        # Build the shit
        if not os.path.exists('.pici/apps/' + self.name):
            print('PICI: Building app')
            os.makedirs('.pici/apps/' + self.name, exist_ok=True)
            self.setup_outputs()
            self.buildproc = subprocess.Popen(['/usr/bin/git', 'clone', self.git, '.pici/apps/' + self.name], stdout=self.stdout, stderr=self.stderr)
            self.buildproc.wait()
            with open('.picigit', 'w') as f:
                print(self.git, file=f)
        else:
            self.setup_outputs()
            old_git = None
            with open('.picigit', 'r') as f:
                old_git = f.read()
            if old_git != self.git:
                print('PICI: Rebuilding app')
                shutil.rmtree('.pici/apps/' + self.name)
                self.buildproc = subprocess.Popen(['/usr/bin/git', 'clone', self.git, '.pici/apps/' + self.name], stdout=self.stdout, stderr=self.stderr)
                self.buildproc.wait()
                with open('.picigit', 'w') as f:
                    print(self.git, file=f)
            else:
                print('PICI: Pulling changes')
                self.buildproc = subprocess.Popen(['/usr/bin/git', 'pull'], cwd='.pici/apps/' + self.name, stdout=self.stdout, stderr=self.stderr)
                self.buildproc.wait()
                
        print("PICI: Running build command")
        self.buildproc = subprocess.Popen(shlex.split(self.build_command), stdout=self.stdout, stderr=self.stderr)
        self.buildproc.wait()
        self.generate_nginx_conf()
        self.close_outputs()
        print("PICI: Done building app")

    def start(self):
        print("PICI: Starting app")
        self.setup_outputs()
        self.startproc = subprocess.Popen(shlex.split(self.start_command), stdout=self.stdout, stderr=self.stderr)

    def stop(self):
        self.startproc.kill()
        self.close_outputs()

    def tail(self):
        tailproc = subprocess.Popen(['/usr/bin/tail', '-f', '.pici/apps/' + self.name + '/logs/out.log'])
        tailproc.wait()

    def setup_outputs(self):
        if self.stdout == None:
            self.stdout = open('.pici/apps/' + self.name + '/out.log', 'a')
        if self.stderr == None:
            self.stderr = open('.pici/apps/' + self.name + '/err.log', 'a')

    def close_outputs(self):
        if self.stdout != None:
            self.stdout.close()
        if self.stderr != None:
            self.stderr.close()

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


