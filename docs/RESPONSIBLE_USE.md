# Responsible Use and Limitations

## 1. Ethical Compute Sharing Principles
- **Transparency**: All node telemetry (CPU, RAM, battery, network) is transparently logged in audit events.
- **Resource Ownership**: Worker nodes retain sovereign control over their hardware. Node owners may pause participation at any time.
- **Privacy First**: Sensitive institutional research must be placed in `local_only` or `trusted_nodes` privacy classes.

## 2. Limitations
- **Large Model VRAM Limits**: Local inference speed depends on node VRAM. Quantized models (e.g., GGUF 4-bit / 8-bit) are recommended for edge hardware.
- **Network Partitions**: During prolonged network splits ($>60\text{s}$), tasks on disconnected nodes are assumed lost and re-queued on available mesh peers.
