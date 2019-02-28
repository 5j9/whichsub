from shutil import rmtree
from os import unlink
from os.path import expanduser
from subprocess import check_call, DEVNULL, CalledProcessError


HOME = expanduser('~')


def main():
    try:
        check_call('kubectl get pods', shell=True)
    except CalledProcessError:
        pass
    else:
        raise SystemExit(
            'Please run this script from a container shell.\n'
            'Run: webservice --backend=kubernetes python shell')

    check_call('webservice stop', shell=True, stderr=DEVNULL, stdout=DEVNULL)
    check_call(
        'webservice --backend=kubernetes stop',
        shell=True, stderr=DEVNULL, stdout=DEVNULL)
    try:
        rmtree(HOME + '/www/python/venv')
    except FileNotFoundError:
        pass
    check_call('python3 -m venv ~/www/python/venv', shell=True)

    try:
        rmtree(HOME + '/www/python/src')
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
        'pip install -Ur ~/www/python/src/requirements.txt',
        shell=True)

    try:
        unlink(HOME + '/uwsgi.log')
    except FileNotFoundError:
        pass
    try:
        unlink(HOME + '/error.log')
    except FileNotFoundError:
        pass

    check_call('webservice --backend=kubernetes python restart', shell=True)


if __name__ == '__main__':
    main()
