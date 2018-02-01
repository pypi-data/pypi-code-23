import os
# import sys
import datetime
from time import sleep
import schedule
# from helpers import rclone
# from sh import rsync
# from helpers import terminal_command
from helpers import schedule_weekly
import logging


SUDO_PSWD = ""
INSTALL_DIR = ""
HOME_FOLDER = "/home/pi/"
BACKUP_FOLDER_SMART_HOME_SYSTEM = "/opt/fhem/backup/"
BACKUP_FOLDER_IN_HOME_FOLDER = "./fhem.files/backups/"
DAY_FOR_BACKUP = "Wednesday"
FILES_TO_KEEP_IN_BACKUP = 5
DAY_FOR_CLEANUP_BACKUP_FOLDER = "Thursday"
DAY_FOR_LOCAL_MIRRORING = "Friday"
DAY_FOR_CLOUD_MIRRORING = "Sunday"
DATE_FOR_REBOOT = 15
EXECUTION_TIME = "03:00"
# RCLONE_PATH = ("~/Dropbox/Files\ Exchange/Programming/python_projects/" +
#                "pi_backup/bin/rclone-v1.39-osx-amd64/rclone")
RCLONE_PATH = ("..\\bin\\rclone\\windows\\amd64\\rclone")
# RCLONE_PATH = ("../bin/rclone/linux/386/rclone")


def main():
    """ Main routine controlling actions of backup system. """

    # few test calls of functions
    # terminal_command('ls', '-al')
    # terminal_command("echo", "Hallo Welt!")
    # rclone(RCLONE_PATH, "lsd drive:")

    # setup logging
    logging.basicConfig(filename='pi_backup.log', level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')

    # example messages from tutorial, just here as a reminder
    # logging.debug('This message should go to the log file')
    # logging.info('So should this')
    # logging.warning('And this, too')

    initialize_jobs()
    while True:
        schedule.run_pending()
        sleep(1)


def initialize_jobs():
    """ Configure scheduling of tasks that shall run periodically. """
    # test job to see whether scheduling is working
    # schedule.every(5).seconds.do(lambda: print('scheduled output...'))

    # initialize backup process
    schedule_weekly(DAY_FOR_BACKUP, EXECUTION_TIME, fhem_backup)
    # schedule_weekly(DAY_FOR_BACKUP, EXECUTION_TIME, iobroker_backup)

    # initialize cleanup of backup folder
    schedule_weekly(DAY_FOR_CLEANUP_BACKUP_FOLDER, EXECUTION_TIME,
                    clean_backup_folder)

    # initialize local mirroring
    schedule_weekly(DAY_FOR_LOCAL_MIRRORING, EXECUTION_TIME,
                    mirror_local_backup_folders)

    # initialize cloud mirroring
    schedule_weekly(DAY_FOR_CLOUD_MIRRORING, EXECUTION_TIME,
                    mirror_local_folder_to_cloud)

    # initialize system reboot
    # scheduling only formally to every day; reboot routine checks whether date
    # is right, as should reboot every 15th of the month
    # schedule.every().day.at('01:00').do(reboot)


def fhem_backup():
    # get command line based perl command to do fhem backup
    cur_dir = os.getcwd()
    os.chdir('/opt/fhem/')
    cmd = './fhem.pl 7072 "backup"'
    os.system(cmd)
    os.chdir(cur_dir)


def iobroker_backup():
    # do iobroker backup in /opt/iobroker
    cur_dir = os.getcwd()
    os.chdir('/opt/iobroker/')
    cmd = 'iobroker backup'
    os.system(cmd)
    os.chdir(cur_dir)


def clean_backup_folder():
    # create path for backup folder
    path = os.path.join(HOME_FOLDER, BACKUP_FOLDER_IN_HOME_FOLDER)

    # check if backup folder exists, else create
    if not os.path.isdir(path):
        os.mkdir(path)

    # check number of files in backup folder
    file_list = os.listdir(path)

    # if less than or equal to 5 files do not clean
    if len(file_list) <= 5:
        return

    # create list of files with creation time
    cur_dir = os.getcwd()
    os.chdir(path)
    file_list_change_time = []
    for file in file_list:
        creation_time = os.path.getctime(file)
        file_list_change_time.append((file, creation_time))

    # sort by date or better change time
    file_list_change_time.sort(key=lambda tp: tp[1])

    # delete oldest until 5 left
    for tp in file_list_change_time[:-5]:
        os.remove(tp[0])

    # change back to old directory
    os.chdir(cur_dir)


def mirror_local_backup_folders():
    # rsync fhem or iobroker backup folder to home folder based backup folder
    cmd = ('rsync -va --delete --progress /opt/fhem/backup/ ' +
           '/home/pi/fhem.files/backups/')
    os.system(cmd)
    pass


def mirror_local_folder_to_cloud():
    # rclone home folder based fhem or iobroker folder to gdrive
    cmd = ('/home/pi/fhem.files/bin/rclone -v sync /home/pi/fhem.files/backups/ ' +
           'drive:/backups/fhem.upstairs/')
    os.system(cmd)


def reboot():
    reboot_today = datetime.date.today().day == DATE_FOR_REBOOT
    if reboot_today:
        cmd = 'sudo reboot'
        os.system(cmd)
    else:
        pass


if __name__ == "__main__":
    main()
