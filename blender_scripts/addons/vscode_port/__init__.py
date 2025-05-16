import bpy
import logging
from .operator import VSCodePortOperator
from .server import VSCodePortServer

bl_info = {
    "name": "VSCode PORT",
    "author": "Alex Telford",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "TOPBAR_MT_file",
    "description": "Allows execution of Python code from VSCode",
    "warning": "",
    "doc_url": "https://example.com/vscode-port-docs",
    "tracker_url": "https://example.com/vscode-port-issues",
    "category": "Development",
}

LOG = logging.getLogger(__name__)


class VSCodePortPreferences(bpy.types.AddonPreferences):
    """
    Preferences for the VSCode Port addon.
    """

    bl_idname = __name__

    port: bpy.props.IntProperty(
        name="Port",
        description="Port to listen on",
        default=8080,
        min=1024,
        max=65535,
    )

    execution_scope: bpy.props.EnumProperty(
        name="Execution Scope",
        description="Scope for executing Python code",
        items=[
            (
                "global",
                "Global",
                "Execute code in the global scope, sharing variables across executions",
            ),
            (
                "local",
                "Local",
                "Execute code in a local scope, isolating variables for each execution",
            ),
        ],
        default="global",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "port")
        layout.prop(self, "execution_scope")


def update_vscode_port(self, context):
    wm = context.window_manager
    if wm.vscode_port_enabled:
        preferences = context.preferences.addons[__name__].preferences
        VSCodePortServer.instance().start(preferences.port)
        bpy.ops.wm.vscode_port_modal_op('INVOKE_DEFAULT')
    else:
        VSCodePortServer.instance().stop()
        for op in wm.operators:
            if op.bl_idname == "WM_OT_vscode_port_modal_op":
                op.cancel(context)


def menu_func(self, context):
    self.layout.prop(
        context.window_manager,
        "vscode_port_enabled",
        text="Enable VSCode Port",
        toggle=True,
    )


def register():
    bpy.utils.register_class(VSCodePortPreferences)
    bpy.utils.register_class(VSCodePortOperator)
    bpy.types.WindowManager.vscode_port_enabled = bpy.props.BoolProperty(
        name="Enable VSCode Port",
        description="Enable or disable the VSCode Port server",
        default=False,
        update=update_vscode_port,
    )
    bpy.types.TOPBAR_MT_file.append(menu_func)


def unregister():
    bpy.utils.unregister_class(VSCodePortPreferences)
    bpy.utils.unregister_class(VSCodePortOperator)
    del bpy.types.WindowManager.vscode_port_enabled
    bpy.types.TOPBAR_MT_file.remove(menu_func)
    VSCodePortServer.instance().stop()


if __name__ == "__main__":
    register()
