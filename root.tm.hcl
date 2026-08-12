globals {
  version = "1"
}

generate_hcl "_backend.tf" {
  content {
    terraform {
      backend "local" {
        path = "terraform.tfstate"
      }
    }
  }
}
generate_hcl "_providers.tf" {
  content {
    terraform {
      required_providers {
        random = { source = "hashicorp/random", version = "~> 3.0" }
      }
    }
  }
}
generate_hcl "_main.tf" {
  content {
    resource "random_pet" "this" {
      keepers = { version = global.version }
    }
    output "name" { value = random_pet.this.id }
  }
}
