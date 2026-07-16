# repo-example-folders

Sample repo proving the **shipmate** GitHub Actions generalize to the
**folder-per-env/region** IaC layout: one leaf directory per
environment × region × component, each owning its own hardcoded state. Null
resources only, local backend, **zero cloud credentials**.

The engine and its three workflows (`preview.yml` / `deploy.yml` / `drift.yml`)
are identical to the other sample repos — only the env model differs. That's
the point: the same actions drive all three layouts.

## Environment model: the path *is* the environment

Unlike the DRY (`repo-example-stacks`) and workspace (`repo-example-workspaces`)
layouts, **nothing is injected** here. A leaf's env and region are fixed by its
position in the tree, and each leaf owns a plain in-directory
`terraform.tfstate`:

```
envs/
  dev-eu/eu-west-1/
    platform/        # env/dev-eu
    app/             # env/dev-eu, after /envs/dev-eu/eu-west-1/platform
  dev-us/us-east-1/
    dns/             # env/dev-us, standalone
root.tm.hcl          # codegen (local backend, providers, main) + plan/apply scripts
terramate.tm.hcl     # experiments = ["scripts"]
```

So the corresponding GitHub Environments inject **no** `TF_VAR_*` /
`TF_WORKSPACE` at all — the Environment is still the unit of apply-gating and
protection, it just carries no variables.

**Trade-off:** this layout gives up shipmate's "add an env = GitHub Environment
+ tags, zero code" property. Adding an environment here means adding leaf
directories — a code change. It's included to prove the engine doesn't *require*
the DRY model, not as the recommended layout.

## Tags and ordering

Env membership is still carried by Terramate **tags** (`env/dev-eu`,
`env/dev-us` — slash form, same convention as the other samples). `after`
references absolute stack paths; the only edge is
`platform → app` (dev-eu), with `dns` standalone. `deploy.yml` walks that DAG in
waves exactly as in the other layouts.

## Toolchain

- Terramate 0.17.1
- OpenTofu 1.12.4

## Fresh-clone walkthrough

```bash
terramate generate                       # codegen into every leaf
terramate list --tags env/dev-eu         # -> the dev-eu leaves
terramate experimental run-graph         # platform -> app; dns isolated

# Drive one leaf. No TF_VAR_* / TF_WORKSPACE — the path fixes env/region.
cd envs/dev-eu/eu-west-1/platform
tofu init -input=false
tofu plan -input=false                    # random_pet to add
```

No environment variables are needed to drive a leaf.

## License

Apache License 2.0 — see [LICENSE](LICENSE).
