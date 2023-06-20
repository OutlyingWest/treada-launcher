# This is a script, which installs missing packages.
import os
import sys
import subprocess
import urllib.request
import urllib.error

import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict
import logging


def main():
    requirements_list = read_requirements('requirements.txt')
    if sys.argv[1] == '--no-internet':
        try:
            install_packages(requirements_list, has_internet=False)
        except Exception as expt:
            print(expt)
            logger.warning(expt)
            logger.critical('Unable to install dependencies with --no-internet option.')
            print('Unable to install dependencies.')
            print(f'Provide the correct dependencies locally and')
            print(f'run {sys.argv[0]} script with --no-internet option')
    elif sys.argv[1] == '--try-internet':
        repos_url = 'https://pypi.org/'
        if try_internet_access(repos_url):
            try:
                install_packages(requirements_list, has_internet=True)
            except Exception as expt:
                print(expt)
                logger.warning(expt)
                logger.critical('Unable to install dependencies with --try-internet option in spite of access to repo.')
                print(f'Try to run {sys.argv[0]} script with --no-internet option.')
        else:
            logger.warning(f'Unable to access: {repos_url}')
            try:
                install_packages(requirements_list, has_internet=False)
            except Exception as expt:
                print(expt)
                logger.warning(expt)
                logger.critical('Unable to install dependencies with --try-internet option.')
                print('Unable to install dependencies.')
                print('Check your internet connection and')
                print(f'run {sys.argv[0]} script with --try-internet option again.')
                print(f'Or provide the correct dependencies locally and')
                print(f'run {sys.argv[0]} script with --no-internet option.')

    else:
        print('Wrong command args.')
        logger.critical('Wrong command args.')


def try_internet_access(url: str):
    try:
        _ = urllib.request.urlopen(url)
        print(f'It is possible to access the website {url}')
        return True
    except urllib.error.URLError:
        print(f'Unable to access website {url}')
        return False


def read_requirements(requirements_path: str):
    with open(requirements_path, 'r') as requirements_file:
        requirements = requirements_file.readlines()
    return requirements


def should_install_requirement(requirement):
    should_install = False
    try:
        pkg_resources.require(requirement)
    except (DistributionNotFound, VersionConflict):
        should_install = True
    return should_install


def install_packages(requirements_list, has_internet: bool):
    requirements = [
        requirement
        for requirement in requirements_list
        if should_install_requirement(requirement)
    ]
    if len(requirements) > 0:
        if has_internet:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *requirements])
        else:
            script_path = os.path.dirname((os.path.abspath(__file__)))
            dependencies_path = os.path.join(script_path, 'dependencies')
            pip_args = [
                'install',
                '--no-index',
                f'--find-links=file:///{dependencies_path}',
            ]
            subprocess.check_call([sys.executable, "-m", "pip", *pip_args, *requirements])
    else:
        logger.info("Requirements already satisfied.")


if __name__ == '__main__':
    # Logging settings
    log_file_name = sys.argv[0].strip("\\.py")
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s [%(levelname)s] %(message)s',  # Format of messages
        filename=f'{log_file_name}.log',
        filemode='a'
    )
    # Creation of logger object
    logger = logging.getLogger(__name__)
    # Run main function
    main()
