provider "aws" {
  region = "us-east-1" # Or your preferred region that has free tier options
}

# Data sources for default VPC and subnets
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# EC2 Security Group
resource "aws_security_group" "ec2_sg" {
  name        = "chrono-guess-ec2-sg"
  description = "Allow SSH, HTTP to EC2"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # WARNING: For production, restrict this to your IP
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000 # Default Django port
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Adjust if your Django app uses a different port
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# RDS Security Group
resource "aws_security_group" "rds_sg" {
  name        = "chrono-guess-rds-sg"
  description = "Allow traffic from EC2 instances to RDS"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port       = 5432 # PostgreSQL default port
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Store the password in AWS Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name        = "database-password"
  description = "Database password for PostgreSQL instance"
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = random_password.db_password.result
}

# RDS PostgreSQL Instance (Free Tier Eligible)
resource "aws_db_instance" "chronoguess_db" {
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "17.6"        # Use a free-tier eligible version
  instance_class         = "db.t3.micro" # Free tier eligible
  db_name                = "chronoguessdb"
  username               = "chronos"
  password               = random_password.db_password.result
  port                   = 5432
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot    = true  # For testing, set to false for production
  publicly_accessible    = false # Best practice
  multi_az               = false # For free tier
  storage_type           = "gp2" # General Purpose SSD
  identifier             = "chronoguess-db-instance"
  apply_immediately      = true # Apply changes immediately

  tags = {
    Name = "ChronoGuess-RDS-DB"
  }
}

resource "aws_key_pair" "ssh_key" {
  key_name   = "ssh-key"
  public_key = file("~/.ssh/id_ed25519.pub")
}

# EC2 Instance (Free Tier Eligible)
resource "aws_instance" "chronoguess_app" {
  ami                    = "ami-084568db4383264d4" # Amazon Linux 2023 AMI (us-east-1), free tier eligible
  instance_type          = "t3.micro"              # Free tier eligible
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  key_name               = aws_key_pair.ssh_key.key_name
  tags = {
    Name = "ChronoGuess-App-Server"
  }

  user_data = <<-EOF
              #!/bin/bash
              echo "DB_HOST=\"${aws_db_instance.chronoguess_db.address}\"" >> /etc/environment
              echo "DB_PORT=\"${aws_db_instance.chronoguess_db.port}\"" >> /etc/environment
              echo "DB_NAME=\"${aws_db_instance.chronoguess_db.db_name}\"" >> /etc/environment
              echo "DB_USER=\"${aws_db_instance.chronoguess_db.username}\"" >> /etc/environment
              echo "DB_PASSWORD=\"${random_password.db_password.result}\"" >> /etc/environment
              EOF
}


resource "aws_eip" "app_ip" {
  domain = "vpc"
}

resource "aws_eip_association" "app_ip_assoc" {
  instance_id   = aws_instance.chronoguess_app.id
  allocation_id = aws_eip.app_ip.id
}

# Outputs
output "ec2_public_ip" {
  description = "The public IP address of the EC2 instance"
  value       = aws_instance.chronoguess_app.public_ip
}

output "rds_endpoint" {
  description = "The endpoint address of the RDS database"
  value       = aws_db_instance.chronoguess_db.address
}

output "rds_port" {
  description = "The port of the RDS database"
  value       = aws_db_instance.chronoguess_db.port
}

output "rds_username" {
  description = "The username for the RDS database"
  value       = aws_db_instance.chronoguess_db.username
}

output "rds_dbname" {
  description = "The database name for the RDS instance"
  value       = aws_db_instance.chronoguess_db.db_name
}
