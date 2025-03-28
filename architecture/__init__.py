# Live2D
try:
    import live2d.v3 as live2d
    from .addon import v3 as addon
except (OSError, SystemError, ImportError):
    import live2d.v2 as live2d
    from .addon import v2 as addon
