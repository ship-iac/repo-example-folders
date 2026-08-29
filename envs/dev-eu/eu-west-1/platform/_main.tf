// TERRAMATE: GENERATED AUTOMATICALLY DO NOT EDIT

resource "random_pet" "this" {
  keepers = {
    version = "2"
  }
}
output "name" {
  value = random_pet.this.id
}
