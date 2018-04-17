from PyQt5.QtWidgets import (QLineEdit, QMessageBox, QProgressBar)
from PyQt5.QtWidgets import (QLabel,  QHBoxLayout, QVBoxLayout, QWidget, QBoxLayout)
from PyQt5.QtWidgets import (QApplication, QPushButton)
import os
import sys
import pexpect
import getpass
from udrivencrypt.encrypt import Encrypt
from udrivencrypt.add import Add
from udrivencrypt.delete import Delete
import re


names_dev = []
labels_dev = []

class Window(QWidget):
    def __init__(self):
        """
        The function which sets layout for main application window.
        """
        super(Window, self).__init__()
        self.layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.setLayout(self.layout)
        self.setWindowTitle("udrivencrypt")
        self.setFixedSize(500, 500)
        Encrypt(self)
        Add(self)
        Delete(self)
        self.Dcheck.toggle()
        self.Acheck.toggle()
        self.Echeck.toggle()

    def list_device(self):
        """
        The function to list all connected USB drives.
        It uses 'lsblk' command to filter connected USB drives by checking TYPE.

        :return:
            labels_dev: list of labels of connected USB drives.
        """
        os.system("lsblk -o NAME,TYPE,RM,LABEL -l -n > devices")
        with open('devices') as f:
            for line in f:
                blk_list = re.split('\s+', line)
                if str(blk_list[1]) == "part" and int(blk_list[2]) == 1:
                    names_dev.append(blk_list[0])
                    labels_dev.append(blk_list[3])
                    #dev_dict.append({'Name':blk_list[0],'Label':blk_list[3]})
                    print(names_dev)
                    print(labels_dev)
        return labels_dev

    def Entoggle(self):
        """
        The function to check whether 'Echeck' is checked or not and perform actions accordingly.

        :return: None
        """
        if self.Echeck.isChecked() is True:
            self.EgroupBox.setVisible(True)
            self.Acheck.setChecked(False)
            self.Dcheck.setChecked(False)
        else:
            self.EgroupBox.setVisible(False)

    def Atoggle(self):
        """
        The function to check whether 'Acheck' is checked or not and perform actions accordingly.

        :return: None
        """
        if self.Acheck.isChecked() is True:
            self.AgroupBox.setVisible(True)
            self.Echeck.setChecked(False)
            self.Dcheck.setChecked(False)
        else:
            self.AgroupBox.setVisible(False)

    def Dtoggle(self):
        """
        The function to check whether 'Dcheck' is checked or not and perform actions accordingly.

        :return: None
        """
        if self.Dcheck.isChecked() is True:
            self.DgroupBox.setVisible(True)
            self.Echeck.setChecked(False)
            self.Acheck.setChecked(False)
        else:
            self.DgroupBox.setVisible(False)


    def check(self):
        """
        The function to check which checkbox is checked, whether any drive from corresponding
        drop-down menu is selected or not and prompt message accordingly.

        :return: None
        """
        if self.Acheck.isChecked():
            if self.AcomboBox.currentIndex() == 0:
                QMessageBox.information(self, 'Alert', "Please Select Drive", QMessageBox.Close)
            else:
                choices = QMessageBox.question(self, 'Message',
                                               "To add new key you need to enter user password.Do you want to continue?",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                self.complete = 0
                if choices == QMessageBox.Yes:
                    self.password_popup(self.addKey)


        elif self.Dcheck.isChecked():
            if self.DcomboBox.currentIndex() == 0:
                QMessageBox.information(self, 'Alert', "Please Select Drive", QMessageBox.Close)
            else:
                choices = QMessageBox.question(self, 'Message',
                                               "To delete key you need to enter user password.Do you want to continue?",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                self.complete = 0
                if choices == QMessageBox.Yes:
                    self.password_popup(self.delKey)


        elif self.Echeck.isChecked():
            if self.EcomboBox.currentIndex() == 0:
                QMessageBox.information(self, 'Alert', "Please Select Drive", QMessageBox.Close)
            else:
                choices = QMessageBox.question(self, 'Message',
                                               "To format disk you need to enter user password.Do you want to continue?",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                self.complete = 0
                if choices == QMessageBox.Yes:
                    self.password_popup(self.format)



    def password_popup(self,name):
        """
        The function to show popup window for superuser password.
        :param name: function to be called when 'Continue' button is clicked.
        :return: None
        """
        self.password_t = QLineEdit()
        self.password_t.setEchoMode(QLineEdit.Password)
        labelpass_t = QLabel()
        labelpass_t.setText("Enter user password:")
        btncontinue_t = QPushButton("Continue")
        self.hboxpass_t = QVBoxLayout()
        self.hboxpass_t.addWidget(labelpass_t)
        self.hboxpass_t.addWidget(self.password_t)
        self.hboxpass_t.addWidget(btncontinue_t)
        self.widget_t = QWidget()
        self.widget_t.setLayout(self.hboxpass_t)
        self.widget_t.setWindowTitle('Password Window')
        self.widget_t.show()
        btncontinue_t.clicked.connect(name)


    def format(self):
        """
        The function to unmount the device and erase all signatures.

        :return: None
        """
        self.progressLabel = QLabel('Progress Bar:', self)
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)
        self.btn = QPushButton("Cancel", self)
        self.hboxLayout = QHBoxLayout(self)
        self.hboxLayout.addWidget(self.progressLabel)
        self.hboxLayout.addWidget(self.progressBar)
        self.hboxLayout.addWidget(self.btn)
        command = 'umount %s' % "/dev/"+names_dev[labels_dev.index(self.EcomboBox.currentText())]
        command1 = 'wipefs -a %s' % "/dev/"+names_dev[labels_dev.index(self.EcomboBox.currentText())]
        x = os.system("echo %s |sudo -S %s" % (self.password_t.text(), command))

        if x == 0:
            y = os.system("echo %s |sudo -S %s" % (self.password_t.text(), command1))
            if y == 0:
                self.widget = QWidget()
                self.widget.setLayout(self.hboxLayout)
                self.widget.setWindowTitle('Dialog with Progressbar')
                self.widget.setGeometry(50, 50, 500, 100)
                self.widget_t.close()
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
        """
        The function to show popup window for label to be given to device.

        :return: None
        """
        if self.Etextbox.text()==self.Etextbox1.text():
            label=QLabel("Enter new name for drive")
            self.map=QLineEdit()
            btnmapcontinue=QPushButton("Continue")
            self.hboxLayoutmap = QVBoxLayout(self)
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
        """
        The function to encrypt device using cryptsetup commands.

        :return: None
        """
        dname = "/dev/"+names_dev[labels_dev.index(self.EcomboBox.currentText())]
        self.mapwidget.close()
        child = pexpect.spawn('sudo cryptsetup luksFormat %s'% dname)
        child.expect_exact('[sudo] password for %s:'% getpass.getuser())
        child.sendline(self.password_t.text())
        child.expect_exact('\r\nWARNING!\r\n========\r\nThis will overwrite data on %s irrevocably.\r\n\r\nAre you sure? (Type uppercase yes):'% dname)
        child.sendline('YES\n')
        child.expect_exact('Enter passphrase:')
        child.sendline(self.Etextbox.text())
        child.expect_exact('Verify passphrase:')
        child.sendline(self.Etextbox1.text())
        child.expect(pexpect.EOF, timeout=None)
            #print(filesystem[devicename.index(self.EcomboBox.currentText())],self.map.text(),self.password_t.text())
        child1=pexpect.spawn('sudo cryptsetup luksOpen %s %s'% (dname,self.map.text()))
        child1.expect_exact('[sudo] password for %s:' % getpass.getuser())
        child1.sendline(self.password_t.text())
        child1.expect_exact('Enter passphrase for %s:'% dname)
        child1.sendline(self.Etextbox.text())
        child1.expect(pexpect.EOF, timeout=None)
        command4='mkfs.ext4 /dev/mapper/%s -L %s'%(self.map.text(),self.map.text())
        command5='cryptsetup luksClose %s'%(self.map.text())
        x=os.system("echo %s | sudo -S %s"% (self.password_t.text(),command4))
        if x==0:
            y=os.system("echo %s | sudo -S %s"%(self.password_t.text(),command5))
            if y==0:
                choice = QMessageBox.information(self, 'Message',
                                                     "Eject the drive and reconnect it. Now restart application for further use.",
                                                     QMessageBox.Yes)
                if choice == QMessageBox.Yes:
                        sys.exit()


    def listEncryptedDevices(self):
        """
        The function to list all already encrypted devices.
        It uses 'lsblk' command to filter only encrypted devices by checking FSTYPE.

        :return:
            devicename1: list of labels for each encrypted device
        """
        os.system("lsblk --raw | grep 'crypt'> device ")
        with open("device", "r") as f:
            UUID = []
            devicename1 = []
            self.filesystem = []

            for line in f.readlines():
                devicename1.append(os.path.basename(line.split()[6]))
                UUID.append(line.split()[0])

        for i in UUID:
            os.system("findfs UUID=%s > device" % i[5:])

        with open("device", "r") as f:
            for line in f.readlines():
                self.filesystem.append(line.split()[0])

       # print(devicename1)
       # print(self.filesystem)
        return devicename1

    def addKey(self):
        """
        The function to a add new backup key for already encrypted device.

        :return: None
        """
        self.widget_t.close()
        if self.Atextbox1.text()!= self.Atextbox2.text():
            QMessageBox.warning(self, 'Warning', "Password doesn't match", QMessageBox.Ok)
            if (QMessageBox.Ok):
                self.Atextbox1.setText("")
                self.Atextbox2.setText("")

        else:
            device_list = self.listEncryptedDevices()
            for i in device_list:
                if str(self.AcomboBox.currentText())==i:
                    dname = self.filesystem[device_list.index(i)]
                    print(dname)
            try:
                child = pexpect.spawn(
                'sudo cryptsetup luksAddKey %s' % dname)
                child.expect_exact('[sudo] password for %s:' % getpass.getuser())
                child.sendline(self.password_t.text())
                try:
                    index = child.expect_exact(['Enter any existing passphrase:','Sorry, try again.'])
                    if index == 0:
                        child.sendline(self.Atextbox.text())
                        try:
                            index1 = child.expect_exact(
                                ['Enter new passphrase for key slot:', 'No key available with this passphrase.'])
                            if index1 == 0:
                                child.sendline(self.Atextbox1.text())
                                child.expect_exact('Verify passphrase:')
                                child.sendline(self.Atextbox2.text())
                                #child.expect(pexpect.EOF, timeout=None)
                                try:
                                    index2 = child.expect_exact([pexpect.EOF,'All key slots full.'])
                                    if index2 == 0:
                                        QMessageBox.warning(self, 'Message', "Key successfully added.", QMessageBox.Ok)
                                    elif index2 == 1:
                                        QMessageBox.warning(self, 'Message', "All key slots full.", QMessageBox.Ok)
                                except:
                                    QMessageBox.warning(self, 'Warning', "Try again.", QMessageBox.Ok)
                            elif index1 == 1:
                                QMessageBox.warning(self, 'Message', "No key available with this passphrase.", QMessageBox.Ok)
                        except:
                            QMessageBox.warning(self, 'Warning', "Try again", QMessageBox.Ok)
                    elif index == 1:
                        raise Exception
                except:
                    QMessageBox.warning(self, 'Warning', "Incorrect user password", QMessageBox.Ok)
            except:
                QMessageBox.warning(self, 'Warning', "Try again", QMessageBox.Ok)

    def delKey(self):
        """
        The function to delete an existing key.

        :return: None
        """
        self.widget_t.close()
        device_list = self.listEncryptedDevices()
        for i in device_list:
            if str(self.DcomboBox.currentText())==i:
                dname = self.filesystem[device_list.index(i)]
                print(dname)
        try:
            child = pexpect.spawn(
                'sudo cryptsetup luksRemoveKey %s' % dname)
            child.expect_exact('[sudo] password for %s:' % getpass.getuser())
            child.sendline(self.password_t.text())
            try:
                index = child.expect_exact(['Enter passphrase to be deleted:','Sorry, try again.'])
                if index == 0:
                    child.sendline(self.Dtextbox.text())
                    try:
                        index1 = child.expect_exact([pexpect.EOF, 'No key available with this passphrase.',
                                                     '\r\nWARNING!\r\n========\r\nThis is the last keyslot. Device will become unusable after purging this key.\r\n\r\nAre you sure? (Type uppercase yes):'])
                        if index1 == 0:
                            QMessageBox.warning(self, 'Message', "Key deleted successfully.", QMessageBox.Ok)
                        elif index1 == 1:
                            QMessageBox.warning(self, 'Message', "No key available with this passphrase.", QMessageBox.Ok)
                        elif index1 == 2:
                            choice = QMessageBox.warning(self, 'Warning',
                                                         "This is the last keyslot. Device will become unusable after purging this key.",
                                                         QMessageBox.Ok | QMessageBox.Cancel,QMessageBox.Cancel)
                            if choice == QMessageBox.Ok:
                                child.sendline("YES\n")
                                child.expect_exact(pexpect.EOF)
                                QMessageBox.warning(self, 'Message', "Key deleted successfully.", QMessageBox.Ok)
                    except:
                        QMessageBox.warning(self, 'Message', "Try again.", QMessageBox.Ok)

                elif index ==1:
                    raise Exception
            except:
                QMessageBox.warning(self, 'Message', "Incorrect user password.", QMessageBox.Ok)
        except:
            QMessageBox.warning(self, 'Warning', "Try again", QMessageBox.Ok)

def main():
    """
    udrivencrypt: GUI to encrypt USB drives.
    """
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())


