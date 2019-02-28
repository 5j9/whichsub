from os import unlink, chdir
from os.path import expanduser
from subprocess import check_call, CalledProcessError


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

    chdir(HOME + '/www/python/src')
    check_call('git pull', shell=True)
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
