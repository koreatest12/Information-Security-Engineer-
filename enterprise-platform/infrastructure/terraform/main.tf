provider "aws" {
  region = "ap-northeast-2"
}

resource "aws_instance" "app_server" {
  ami           = "ami-0c9c942bd7bf113a2" # Ubuntu 22.04 LTS Example
  instance_type = "t3.medium"
  key_name      = var.key_name
  
  security_groups = [aws_security_group.app_firewall.name]

  tags = {
    Name = "enterprise-platform-server"
  }
}
