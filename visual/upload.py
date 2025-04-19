# ======================================================================
# >> IMPORTS
# ======================================================================

# Python
from ftplib import FTP

# httshots
import httshots

from httshots import httshots


# ======================================================================
# >> FUNCTIONS
# ======================================================================
def upload_file(full_name, file_name, replace_file=False, ftp_unique_path=False):
    upl = httshots.config.image_upload
    if not upl:
        return None

    if upl == 1:
        url = upload_file_imgur(full_name)
        if url is None and httshots.config.try_reupload_image:
            url = upload_file_imgur(full_name)

    elif upl == 2:
        ftp = FTP(httshots.config.ftp_ip)
        ftp.login(httshots.config.ftp_login, httshots.config.ftp_passwd)
        real_pwd = f"www/{httshots.config.site_name}/{httshots.config.ftp_folder}"
        if not ftp_unique_path:
            pwd = prepare_ftp_folders(ftp)
        else:
            ftp.cwd(ftp_unique_path)
            pwd = ftp.pwd()
        if replace_file:
            folders = ftp.nlst()
            if file_name in folders:
                ftp.voidcmd('DELE '+file_name)
        with open(full_name, 'rb') as upload_file:
            ftp.storbinary('STOR '+file_name, upload_file)
        real_pwd += pwd
        tmp = '/'.join(real_pwd.split('/')[1:])
        url = f'{tmp}/{file_name}'
    return url


def prepare_ftp_folders(ftp):
    cur_game = httshots.cur_game
    folders = ftp.nlst()
    if not cur_game[0] in folders:
        ftp.mkd(cur_game[0])
    ftp.cwd(cur_game[0])
    folders = ftp.nlst()
    if not cur_game[1] in folders:
        ftp.mkd(cur_game[1])
    ftp.cwd(cur_game[1])
    return ftp.pwd()


def remove_file(file_name, ftp_unique_path=False):
    ftp = FTP(httshots.config.ftp_ip)
    ftp.login(httshots.config.ftp_login, httshots.config.ftp_passwd)
    if not ftp_unique_path:
        prepare_ftp_folders(ftp)
    else:
        ftp.cwd(f"{ftp_unique_path}")

    folders = ftp.nlst()
    if file_name in folders:
        ftp.voidcmd('DELE '+file_name)


def upload_file_imgur(file_name):
    try:
        url = httshots.imgur.upload_from_path(file_name)
        if 'link' in url:
            return url['link'].replace('i.', '')
        return None
    except Exception as e:
        httshots.print_log('ImgurError', e)
        return None
