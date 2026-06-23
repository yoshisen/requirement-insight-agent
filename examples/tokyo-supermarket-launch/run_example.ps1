$ErrorActionPreference = 'Stop'

ria run-example `
  --config examples/tokyo-supermarket-launch/example_config.json `
  --prompt-kind survey `
  --agent-limit 5 `
  --base-units 900 `
  --output-dir .local/examples/tokyo-supermarket-launch