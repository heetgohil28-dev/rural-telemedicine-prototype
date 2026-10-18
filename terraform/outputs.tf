output "public_ip" {
  value = aws_instance.app.public_ip
}

output "website_url" {
  value = "http://${aws_instance.app.public_ip}:8501"
}

output "instance_id" {
  value = aws_instance.app.id
}