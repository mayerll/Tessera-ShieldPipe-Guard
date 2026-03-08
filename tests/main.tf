
resource "aws_s3_bucket" "insecure_bucket" {
  bucket = "my-very-secret-data"
  acl    = "public-read"
}

resource "aws_security_group" "bad_sg" {
  name        = "open-ssh"
  description = "Allow SSH from anywhere"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

