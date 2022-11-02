import cwbar.cmd


def edit_file(ssh_server, file_name):
    if ssh_server:
        file_name = "scp://jboss@" + ssh_server + "/" + file_name
    cmd = "vim " + file_name
    cwbar.cmd.execute(cmd)
