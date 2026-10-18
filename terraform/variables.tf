variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "instance_type" {
  description = "EC2 instance type (must be free-plan eligible)"
  type        = string
  default     = "t3.micro"
}

variable "docker_image" {
  description = "Docker Hub image to run, for example myuser/rural-telemedicine:latest"
  type        = string
}

variable "password_parameter" {
  description = "SSM Parameter Store name that holds the doctor password"
  type        = string
  default     = "/rural-telemedicine/doctor-password"
}