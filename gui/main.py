from PyQt5.QtWidgets import (QLineEdit, QMessageBox, QProgressBar)
from PyQt5.QtWidgets import (QLabel,  QHBoxLayout, QWidget, QBoxLayout)
from PyQt5.QtWidgets import (QApplication, QPushButton)
import os
import sys
import pexpect
import getpass
from encrypt import Encrypt
from add import Add
from delete import Delete
import re

filesystem = []
devicename = []
names = []
labels = []


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.setLayout(self.layout)
        self.setWindowTitle("GUI")
        self.setFixedSize(500, 500)
        Encrypt(self)
        Add(self)
        Delete(self)
        self.Dcheck.toggle()
        self.Acheck.toggle()
        self.Echeck.toggle()

    def list_device(self):
        os.system("df -h > device")
        with open("device", "r") as f:
            device = []
            device1 = []
            for line in f.readlines()[1:]:
                device.append(line.split()[5])
                device1.append(line.split()[0])
            for s in device:
                if "/run/media" in s:
                    filesystem.append(device1[device.index(s)])
                    devicename.append(os.path.basename(s))
        return devicename

    def Entoggle(self):
        if self.Echeck.isChecked() is True:
            self.EgroupBox.setVisible(True)
            self.Acheck.setChecked(False)
            self.Dcheck.setChecked(False)
        else:
            self.EgroupBox.setVisible(False)

    def Atoggle(self):
        if self.Acheck.isChecked() is True:
            self.AgroupBox.setVisible(True)
            self.Echeck.setChecked(False)
            self.Dcheck.setChecked(False)
        else:
            self.AgroupBox.setVisible(False)

    def Dtoggle(self):
        if self.Dcheck.isChecked() is True:
            self.DgroupBox.setVisible(True)
            self.Echeck.setChecked(False)
            self.Acheck.setChecked(False)
        else:
            self.DgroupBox.setVisible(False)

    def format(self):
        if self.EcomboBox.currentIndex() == 0:
            QMessageBox.information(self, 'Alert', "Please Select Drive", QMessageBox.Close)
        else:
            choices = QMessageBox.question(self, 'Message', "To format disk you need to enter user password.Do you want to continue?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            self.complete = 0
            if choices == QMessageBox.Yes:
                self.password = QLineEdit()
                self.password.setEchoMode(QLineEdit.Password)
                labelpass = QLabel()
                labelpass.setText("Enter your password")
                btncontinue = QPushButton("Continue")
                self.hboxpass = QHBoxLayout()
                self.hboxpass.addWidget(labelpass)
                self.hboxpass.addWidget(self.password)
                self.hboxpass.addWidget(btncontinue)
                self.widget1 = QWidget()
                self.widget1.setLayout(self.hboxpass)
                self.widget1.setWindowTitle('Password window')
                self.widget1.show()
                btncontinue.clicked.connect(self.passwordfun())

    def passwordfun(self):
        self.progressLabel = QLabel('Progress Bar:', self)
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)
        self.btn = QPushButton("Cancel", self)
        self.hboxLayout = QHBoxLayout(self)
        self.hboxLayout.addWidget(self.progressLabel)
        self.hboxLayout.addWidget(self.progressBar)
        self.hboxLayout.addWidget(self.btn)
        command = 'umount %s' % filesystem[devicename.index(self.EcomboBox.currentText())]
        command1 = 'wipefs -a %s' % filesystem[devicename.index(self.EcomboBox.currentText())]
        x = os.system("echo %s |sudo -S %s" % (self.password.text(), command))

        if x == 0:
            y = os.system("echo %s |sudo -S %s" % (self.password.text(), command1))
            if y == 0:
                self.widget = QWidget()
                self.widget.setLayout(self.hboxLayout)
                self.widget.setWindowTitle('Dialog with Progressbar')
                self.widget.setGeometry(50, 50, 500, 100)
                self.widget1.close()
                self.widget.show()
                connect = 0
                while connect < 100:
                    connect += 0.001
                    self.progressBar.setValue(connect)
                    self.widget.close()
                QMessageBox.information(self, 'Message', "Drive is formatted.Now you can set password", QMessageBox.Ok)
                    
                if(QMessageBox.Ok):
                    self.Etextbox.setEnabled(True)
                    self.Etextbox1.setEnabled(True)
            else:
                choice = QMessageBox.information(self, 'Error', "Cannot format drive.Please verify that password is correct ", QMessageBox.Retry | QMessageBox.Close, QMessageBox.Retry)
                if choice == QMessageBox.Retry:
                    self.widget1.show()

    def Finish(self):

            if self.Etextbox.text()==self.Etextbox1.text():


                label=QLabel("Mapper name")
                self.map=QLineEdit()
                btnmapcontinue=QPushButton("Continue")

                self.hboxLayoutmap = QHBoxLayout(self)
                self.hboxLayoutmap.addWidget(label)
                self.hboxLayoutmap.addWidget(self.map)
                self.hboxLayoutmap.addWidget(btnmapcontinue)

                self.mapwidget = QWidget()
                self.mapwidget.setLayout(self.hboxLayoutmap)
                self.mapwidget.setWindowTitle('Map Window')
                self.mapwidget.setGeometry(50, 50, 500, 100)
                self.mapwidget.show()

                btnmapcontinue.clicked.connect(self.create_luks_partition)



            else:
                QMessageBox.warning(self,'Warning',"Password doesn't match",QMessageBox.Ok)
                if(QMessageBox.Ok):
                    self.EtextBox.setText("")
                    self.EtextBox1.setText("")





    def create_luks_partition(self):

        self.mapwidget.close()

        child = pexpect.spawn('sudo cryptsetup luksFormat %s'% filesystem[devicename.index(self.EcomboBox.currentText())])
        child.expect_exact('[sudo] password for %s:'% getpass.getuser())
        child.sendline(self.password.text())
        child.expect_exact('\r\nWARNING!\r\n========\r\nThis will overwrite data on %s irrevocably.\r\n\r\nAre you sure? (Type uppercase yes):'% filesystem[devicename.index(self.EcomboBox.currentText())])
        child.sendline('YES\n')

        child.expect_exact('Enter passphrase:')
        child.sendline(self.Etextbox.text())
        child.expect_exact('Verify passphrase:')
        child.sendline(self.Etextbox1.text())
        child.expect(pexpect.EOF, timeout=None)


        print(filesystem[devicename.index(self.EcomboBox.currentText())],self.map.text(),self.password.text())

        child1=pexpect.spawn('sudo cryptsetup luksOpen %s %s'% (filesystem[devicename.index(self.EcomboBox.currentText())],self.map.text()))
        child1.expect_exact('[sudo] password for %s:' % getpass.getuser())
        child1.sendline(self.password.text())
        child1.expect_exact('Enter passphrase for %s:'% filesystem[devicename.index(self.EcomboBox.currentText())])
        child1.sendline(self.Etextbox.text())
        child1.expect(pexpect.EOF, timeout=None)

        command4='mkfs.ext4 /dev/mapper/%s -L %s'%(self.map.text(),self.map.text())

        x=os.system("echo %s | sudo -S %s"% (self.password.text(),command4))

        if x==0:

            choice = QMessageBox.information(self, 'Message',
                                             "Drive is encrypted.Click 'No' to end .Click 'Yes'to add new key",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.Acheck.setChecked(True)
            else:
                sys.exit()

    def list_encrypted_devices(self):
        os.system("lsblk -fs -l -n > devices")
        with open('devices') as f:
            for line in f:
                blk_list = re.split('\s+',line)
                if blk_list[1] == "crypto_LUKS":
                    names.append(blk_list[0])
                    id = blk_list[3]
                    for line1 in f:
                        blk_list1 = re.split('\s+',line1)
                        if "luks-"+id in blk_list1[0]:
                            #device_dict = {'name':blk_list[0],'label':blk_list1[2]}
                            labels.append(blk_list1[2])





        return labels


    def addKey(self):
        if self.AcomboBox.currentIndex() == 0:
            QMessageBox.information(self, 'Alert', "Please Select Drive", QMessageBox.Close)
        else:
            if self.Atextbox1.text()!= self.Atextbox2.text():
                QMessageBox.warning(self, 'Warning', "Password doesn't match", QMessageBox.Ok)
                if (QMessageBox.Ok):
                    self.Atextbox1.setText("")
                    self.Atextbox2.setText("")

            else:
                dname = "/dev/"+names[labels.index(self.AcomboBox.currentText())]
                try:
                    child = pexpect.spawn(
                        'sudo cryptsetup luksAddKey %s' % dname)
                    child.expect_exact('[sudo] password for %s:' % getpass.getuser())
                    child.sendline(self.Atextbox_t.text())
                    child.expect_exact('Enter any existing passphrase:')
                    child.sendline(self.Atextbox.text())
                    child.expect_exact('Enter new passphrase for key slot:')
                    child.sendline(self.Atextbox1.text())
                    child.expect_exact('Verify passphrase:')
                    child.sendline(self.Atextbox2.text())
                    child.expect(pexpect.EOF, timeout=None)
                    QMessageBox.warning(self, 'Message', "Key added.", QMessageBox.Ok)
                except:
                    QMessageBox.warning(self, 'Warning', "Try again", QMessageBox.Ok)


def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())


