Vagrant.configure("2") do |config|
  config.vm.define "webscraper" do |webscraper|
    webscraper.vm.box = "ubuntu/trusty64"
    webscraper.vm.hostname = 'webscraper'
    webscraper.vm.box_url = "ubuntu/trusty64"

    webscraper.vm.network :private_network, ip: "10.0.0.10"
    webscraper.vm.network :forwarded_port, guest: 1030, host: 1254

    webscraper.vm.provider :virtualbox do |v|
      v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      v.customize ["modifyvm", :id, "--memory", 1024]
      v.customize ["modifyvm", :id, "--name", "webscraper"]
    end
  end
  
  config.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install -y python3-pip
      pip3 install virtualenv
      virtualenv -p python3.4 scraper
    SHELL
end