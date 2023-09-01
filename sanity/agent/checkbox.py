import os
from sanity.agent.mail import mail
from sanity.agent.cmd import syscmd
from sanity.agent.err import *
from sanity.agent.net import *
from sanity.agent.data import dev_data

def run_checkbox(con, cbox, runner_cfg, secure_id, desc):
    retry = 0
    status = -1

    ADDR = get_ip(con)
    if (ADDR == FAILED):
        return FAILED

    if (check_net_connection(ADDR) == FAILED):
        return FAILED

    syscmd('sshpass -p ' + dev_data.device_pwd + ' scp -v -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" ' + runner_cfg + ' ' + dev_data.device_uname + '@' + ADDR + ':~/')

    con.write_con('sudo snap set ' + cbox + ' slave=disabled')

    con.write_con_no_wait('sudo ' + cbox + '.checkbox-cli ' + runner_cfg )
    while True:
        mesg = con.read_con()
        if mesg.find('file:///home/'+ dev_data.device_uname +'/report.tar.xz') != -1:
            syscmd('sshpass -p ' + dev_data.device_pwd + ' scp -v -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" ' + dev_data.device_uname + '@' + ADDR + ':report.tar.xz .')
            fileT= time.strftime("%Y%m%d%H%M")
            mailT=time.strftime("%Y/%m/%d %H:%M")

            if os.path.exists('report.tar.xz') == False:
                mail.send_mail(FAILED, dev_data.project + ' auto sanity was failed, checkbox report is missing. - ' + mailT)
                print('auto sanity is failed')
            else:
                report_name = 'report-' + fileT + '.tar.xz'
                syscmd('mv report.tar.xz ' + report_name)
                print('checkbox.checkbox-cli submit -m ' + desc + ' '  + secure_id + " " + report_name)
                syscmd('checkbox.checkbox-cli submit -m ' + desc + ' ' + secure_id + " " + report_name)
                mail.send_mail(SUCCESS, dev_data.project + " run " + runner_cfg + ' auto sanity was finished on ' + mailT, report_name)
                print('auto sanity is finished')
            return
