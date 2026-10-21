
variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "docker_image" {
  description = "Docker Hub image to run, for example myuser/rural-telemedicine:latest"
  type        = string
}

variable "doctor_password" {
  description = "Doctor login password supplied through the environment"
  type        = string
  sensitive   = true
  nullable    = false

  validation {
    condition     = length(var.doctor_password) >= 12
    error_message = "The doctor password must be at least 12 characters long."
  }
}
