#install all packages required for running bot

sudo apt-get update

sudo apt-get cmake

curl -sf -L https://static.rust-lang.org/rustup.sh | sh

sudo apt-get install -y default-jre
sudo apt-get install default-jdk

sudo apt-get install -y ruby

curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install -y nodejs

sudo apt-get install -y python3-pip
sudo pip3 install tensorflow
sudo pip3 install numpy

sudo apt-get install apt-transport-https
sudo sh -c 'curl https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -'
sudo sh -c 'curl https://storage.googleapis.com/download.dartlang.org/linux/debian/dart_stable.list > /etc/apt/sources.list.d/dart_stable.list'
sudo apt-get update
export PATH=/usr/lib/dart/bin:$PATH
sudo sh -c 'curl https://storage.googleapis.com/download.dartlang.org/linux/debian/dart_unstable.list > /etc/apt/sources.list.d/dart_unstable.list'
sudo apt-get install dart

wget https://dl.google.com/go/go1.10.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.10.linux-amd64.tar.gz
rm go1.10.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bi
sudo apt-get install gccgo-go

#setup firewall
sudo ufw default deny outgoing
sudo ufw default deny incoming
sudo ufw allow ssh
sudo ufw disable
sudo ufw enable
