stack {
  name        = "app"
  description = "app"
  tags        = ["env/dev-eu"]
  after       = ["/envs/dev-eu/eu-west-1/platform"]
  id          = "7d3c1537-9a1e-4cb7-92f9-6b5a115ee81b"
}
