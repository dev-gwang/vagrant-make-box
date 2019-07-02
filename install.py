#coding=utf-8

import logging
import subprocess
import sys
import os

def logger():
	logging.basicConfig(format="[%(asctime)s] [%(process)s] [%(filename)-20.20s:%(lineno)-7.7s] %(levelname)7.7s - %(message)s",			 level=logging.INFO, handlers=[
			logging.FileHandler("result.log"),
			logging.StreamHandler()
		])

class Execute:
	def command(self, command, exit_true):
		_subprocess = subprocess.Popen(command, shell=True, close_fds=True, stderr=subprocess.PIPE)
		_subprocess.wait()
		out, err = _subprocess.communicate()

		if _subprocess.returncode == 0:
			logging.info("command (%s) Success (message : %s)" %(command, out))

			return _subprocess.returncode
		else:
			logging.error("command (%s) Failed (message : %s)" %(command,err))

			if exit_true == True:
				sys.exit(1)

class InstallVboxVagrant:
	def __init__(self):
		logging.info("Start Install Vbox Vagrant")

	'''
		GCC Devel 설치
	'''
	def install_kernel_devel_with_gcc(self):
		find_file = True

		if not os.path.isfile("result"):

			find_file = False
			Execute().command("yum remove -y kernel-*", False)
			exit_code = Execute().command("yum install -y kernel-* make gcc perl bzip2 tar", False)

		if find_file == False:
			logging.info("Please reboot")
			Execute().command("touch result", False)
			sys.exit(0)

	def remove_kernel_devel_with_gcc(self):
		Execute().command("yum remove -y make gcc perl", False)
	

	def mount_and_install_vbox_linux_additions(self):
		Execute().command("mount -r /dev/cdrom /media/", False)
		Execute().command("""/media/VBoxLinuxAdditions.run --nox11 << END_SCRIPT
								yes
								yes
							END_SCRIPT""", False)

	'''
		계정 설정 부분
	'''
	def set_user(self):
		Execute().command("useradd vboxadd", False)
		Execute().command("groupadd vboxsf", False)
		Execute().command("usermod -u 471 vboxadd", False)
		Execute().command("groupmod -g 471 vboxsf", False)

		Execute().command("groupadd -g 470 vagrant", False)
		Execute().command("useradd -g vagrant -u 470 vagrant", False)

		Execute().command("""passwd vagrant << END_SCRIPT
vagrant
vagrant
END_SCRIPT""", False)

		Execute().command("chown vagrant.vagrant /home/vagrant", False)

	'''
		Make 개발 환경 세팅 시작
	'''
	def make_vboxadd(self):
		Execute().command("/opt/VBoxGuestAdditions-6.0.8/init/vboxadd setup", True)

	def add_sudoers(self):
		Execute().command("""echo '
Defaults    env_keep += \"SSH_AUTH_SOCK\"
%vagrant        ALL=(ALL)       NOPASSWD: ALL
Defaults:vagrant !requiretty' >> /etc/sudoers""", False)

	def ssh_configure(self):
		Execute().command("yum install wget -y", False)
		Execute().command("""cd ~vagrant; 
							 mkdir .ssh;
							 
							 wget --no-check-certificate https://raw.github.com/mitchellh/vagrant/master/keys/vagrant.pub -O .ssh/authorized_keys;
							 chmod 0700 .ssh;
							 chmod 0600 .ssh/authorized_keys;
							 chown -R vagrant.vagrant .ssh;
							 """, True)
		Execute().command('''echo "
Port 22
AllowUsers vagrant
PubkeyAuthentication yes
AuthorizedKeysFile      .ssh/authorized_keys" >> /etc/ssh/sshd_config''', False)
							 

def main():
	install_vbox_vagrant = InstallVboxVagrant()
	install_vbox_vagrant.install_kernel_devel_with_gcc()
	install_vbox_vagrant.mount_and_install_vbox_linux_additions()
	install_vbox_vagrant.set_user()
	install_vbox_vagrant.make_vboxadd()
	install_vbox_vagrant.add_sudoers()
	install_vbox_vagrant.ssh_configure()

	
if __name__ == '__main__':
	logger()
	main()