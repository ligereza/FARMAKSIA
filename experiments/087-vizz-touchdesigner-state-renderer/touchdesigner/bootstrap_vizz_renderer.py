"""Create the first VIZZ renderer network inside TouchDesigner.

Run later from TouchDesigner 2023.12000. This file is intentionally inert when
it is merely imported by an external Python interpreter and contains no host
capture, camera, input, process or network startup.
"""

CHANNELS = (
    "state_valid",
    "state_unknown",
    "state_confidence",
    "head_x",
    "head_y",
    "head_z",
    "head_rx",
    "head_ry",
    "head_rz",
    "focus_x",
    "focus_y",
    "focus_w",
    "focus_h",
    "focus_interest",
    "keyboard_activity",
    "pointer_x",
    "pointer_y",
    "pointer_active",
    "permission_camera",
    "permission_capture",
    "permission_overlay",
    "permission_input_remap",
)


def _set_constant_channels(node, values):
    """Configure a Constant CHOP without accepting arbitrary payload keys."""

    node.par.const.numBlocks = len(CHANNELS)
    for index, name in enumerate(CHANNELS):
        block = node.par.const[index]
        block.par.name = name
        block.par.value = float(values.get(name, 0.0))


def _connect(destination, source, index=0):
    destination.inputConnectors[index].connect(source)


def build(root=None, osc_port=7001):
    """Build a deterministic, passive renderer scaffold.

    `osc_port` is retained as a documented future parameter but is not used:
    the OSC node is created inactive and no listener is enabled.
    """

    if root is None:
        root = parent()
    if root.op("vizz_td_renderer") is not None:
        raise RuntimeError("vizz_td_renderer already exists; refusing to overwrite it")

    container = root.create("baseCOMP", "vizz_td_renderer")
    container.par.display = 1

    manual = container.create("constantCHOP", "manual_state")
    _set_constant_channels(
        manual,
        {
            "state_valid": 1.0,
            "state_confidence": 1.0,
            "focus_x": 0.5,
            "focus_y": 0.5,
            "focus_w": 0.0,
            "focus_h": 0.0,
        },
    )

    osc = container.create("oscinCHOP", "osc_state")
    osc.par.active = 0
    osc.par.port = int(osc_port)

    source = container.create("switchCHOP", "state_source")
    source.par.index = 0
    _connect(source, manual, 0)
    _connect(source, osc, 1)

    filtered = container.create("filterCHOP", "state_filtered")
    _connect(filtered, source)
    filtered.par.type = "oneeuro"
    filtered.par.effect = 1.0
    filtered.par.cutoff = 1.0
    filtered.par.speedcoeff = 0.001
    filtered.par.slopecutoff = 1.0

    surface = container.create("constantTOP", "base_surface")
    surface.par.colorr = 0.035
    surface.par.colorg = 0.045
    surface.par.colorb = 0.065
    surface.par.colora = 1.0

    motion = container.create("transformTOP", "motion_plane")
    _connect(motion, surface)
    motion.par.tx.expr = "op('state_filtered')['head_x'] * 0.05"
    motion.par.ty.expr = "op('state_filtered')['head_y'] * 0.05"
    motion.par.sx.expr = "1 + op('state_filtered')['head_z'] * 0.02"
    motion.par.sy.expr = "1 + op('state_filtered')['head_z'] * 0.02"

    output = container.create("nullTOP", "outTOP")
    _connect(output, motion)
    output.viewer = True
    return container
