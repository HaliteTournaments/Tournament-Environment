#packages needed to run everthing
#these packages are suited for gcloud instance Debian 9
#follow instruction at https://cloud.google.com/compute/docs/instances/enable-nested-virtualization-vm-instances
#before procending

sudo apt-get update

wget https://releases.hashicorp.com/vagrant/2.0.2/vagrant_2.0.2_x86_64.deb
sudo dpkg -i vagrant_2.0.2_x86_64.deb
rm vagrant_2.0.2_x86_64.deb

wget https://download.virtualbox.org/virtualbox/5.2.8/virtualbox-5.2_5.2.8-121009~Debian~stretch_amd64.deb
sudo dpkg -i virtualbox-5.2_5.2.8-121009~Debian~stretch_amd64.deb
sudo apt-get install -f -y
sudo apt-get install linux-headers-amd64
sudo apt-get install gcc perl make
sudo /sbin/vboxconfig
sudo apt-get upgrade
rm virtualbox-5.2_5.2.8-121009~Debian~stretch_amd64.deb

sudo apt-get install python3 python3-pip
sudo pip3 install discord
