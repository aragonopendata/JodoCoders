# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

$script = <<SCRIPT
# reconfigura los locales para evitar mensajes molestos
locale-gen UTF-8
# instalar git y mysql
apt-get update
apt-get install -y git python-dev

# make sure mysql won't ask for pwd when installing
echo 'mysql-server mysql-server/root_password password root' | debconf-set-selections
echo 'mysql-server mysql-server/root_password_again password root' | debconf-set-selections
# instalar MySQL
apt-get install -y mysql-server mysql-client libmysqlclient-dev
# crear BBDD Datos
echo "CREATE DATABASE Datos" | mysql -uroot -proot
# importar Datos
mysql -uroot -proot Datos < /vagrant/data/datos.sql

# instalar pip, gestor de paquetes de python
curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
python get-pip.py

# aislar entornos dependencias python
pip install virtualenvwrapper
mkdir $HOME/.virtualenvs
echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
echo "export WORKON_HOME=$HOME/.virtualenvs" >> ~/.bashrc
echo "export PROJECT_HOME=/vagrant" >> ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
source ~/.bashrc
mkvirtualenv jodocoders  # usar 'workon jodocoders' si ya aprovisionaste

# instalar deps del requirements.txt
cd /vagrant  # (/vagrant es tu repo en el host)
pip install -r requirements.txt

# copiar el fichero de configuración con nuestros settings
cp settings.py.example settings.py

# inicia servidor demonizado
gunicorn --error-logfile logs/error.log web:app -b 0.0.0.0:5000 -D
# usa sudo killall gunicorn  # para pararlo
SCRIPT

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  # Image
  config.vm.box = "ubuntu/trusty64"

  # Network
  config.vm.network :forwarded_port, guest: 5000, host: 8888

  # Provisioning
  config.vm.provision "shell", inline: $script

  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
  end

end