from shutil import rmtree
from os import unlink
from subprocess import check_call, DEVNULL, CalledProcessError


def main():
    try:
        check_call('kubectl get pods', shell=True)
    except CalledProcessError:
        pass
    else:
        raise SystemExit(
            'Please run this script from the container shell.\n'
            'Run: webservice --backend=kubernetes python shell')

    try:
        rmtree('~/www/python/venv')
    except FileNotFoundError:
        pass
    check_call('python3 -m venv ~/www/python/venv', shell=True)

    try:
        rmtree('~/www/python/src')
    except FileNotFoundError:
        pass
    check_call(
        'git clone --depth=1'
        ' https://github.com/5j9/whichsub.git'
        ' ~/www/python/src',
        shell=True)

    check_call(
        '. ~/www/python/venv/bin/activate\n'
        'pip install --upgrade pip\n'
        'pip install -rU ~/www/python/src/requirements.txt',
        shell=True)

    check_call('webservice stop', shell=True, stderr=DEVNULL, stdout=DEVNULL)
    check_call(
        'webservice --backend=kubernetes stop',
        shell=True, stderr=DEVNULL, stdout=DEVNULL)
    unlink('uwsgi.log')
    unlink('error.log')
    check_call('webservice --backend=kubernetes python start', shell=True)


if __name__ == '__main__':
    main()
