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
    resource "random_pet" "this" {}
    output "name" { value = random_pet.this.id }
  }
}
script "plan" {
  description = "plan this leaf"
  job { commands = [["tofu", "init", "-input=false"], ["tofu", "plan", "-input=false", "-lock=false", "-out=stack.otplan"]] }
}
script "apply" {
  description = "apply this leaf"
  job { commands = [["tofu", "init", "-input=false"], ["tofu", "apply", "-input=false", "-lock=false", "-auto-approve", "stack.otplan"]] }
}
