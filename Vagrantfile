Vagrant.configure("2") do |config|
  config.vm.define "webscraper" do |webscraper|
    webscraper.vm.box = "ubuntu/trusty64"
    webscraper.vm.hostname = 'webscraper'
    webscraper.vm.box_url = "ubuntu/trusty64"

    webscraper.vm.network :private_network, ip: "10.0.0.11"
    webscraper.vm.network :forwarded_port, guest: 1020, host: 1260

    webscraper.vm.provider :virtualbox do |v|
      v.memory = "4096"
      v.name = "webscraper"
      v.cpus = 2
    end
  end
  
  config.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install -y python3-pip
      pip3 install virtualenv
      virtualenv -p python3.4 scraper
      source scraper/bin/activate
      pip3 install flickrapi
      apt-get install -y sqlite3 libsqlite3-dev
    SHELL
end