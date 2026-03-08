
# 1. S3 Bucket with Public Access (The most common cloud leak)
resource "aws_s3_bucket" "insecure_bucket" {
  bucket = "my-very-secret-data"
  acl    = "public-read" # SECURITY RISK: Data is publicly accessible
}

# 2. Security Group with "Open to the World" SSH
resource "aws_security_group" "bad_sg" {
  name        = "open-ssh"
  description = "Allow SSH from anywhere"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # SECURITY RISK: Brute force target
  }
}

# 3. Unencrypted EBS Volume
resource "aws_ebs_volume" "unencrypted" {
  availability_zone = "us-west-2a"
  size              = 40
  encrypted         = false # SECURITY RISK: Data at rest should be encrypted
}

# 4. Hardcoded Secrets in Terraform (Never do this)
resource "aws_db_instance" "default" {
  allocated_storage    = 10
  engine               = "mysql"
  instance_class       = "db.t3.micro"
  db_name              = "mydb"
  username             = "admin"
  password             = "Password123!" # SECURITY RISK: Plaintext password in code/state
  skip_final_snapshot  = true
}

