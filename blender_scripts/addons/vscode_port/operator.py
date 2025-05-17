# Copyright (c) 2025 Alex Telford. All rights reserved.
import bpy
import logging
import io
import sys
from .server import VSCodePortServer, ReadState

LOG = logging.getLogger(__name__)

GLOBALS = {}  # Global vars for excecution

def _capture_and_exec(code, scope="global"):
    """
    Execute code and capture stdout/stderr, returning the output.
    """
    print(f"[VSCodePort] Executing code in {scope} scope...")
    print(code)
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    try:
        if scope == "global":
            exec(code, GLOBALS)
        else:
            exec(code, {})
        output = sys.stdout.getvalue() + sys.stderr.getvalue()
    except Exception as e:
        output = sys.stdout.getvalue() + sys.stderr.getvalue()
        output += f"\n[VSCodePort] Exception: {e}"
        LOG.error(f"[VSCodePort] Error executing code: {e}")
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    return output

def execute_python_file(filepath, scope="global"):
    """
    Execute a Python file.

    :param filepath: Path to the Python file to execute.
    :param scope: Execution scope ('global' or 'local').
    """
    LOG.debug(f"[VSCodePort] Executing file: {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        return _capture_and_exec(code, scope)
    except Exception as e:
        LOG.error(f"[VSCodePort] Error executing file: {e}")
        return f"[VSCodePort] Error executing file: {e}"

def execute_python_code(code, scope="global"):
    """
    Execute Python code received as a string.

    :param code: Python code to execute.
    :param scope: Execution scope ('global' or 'local').
    """
    LOG.debug(f"[VSCodePort] Executing streamed code...")
    return _capture_and_exec(code, scope)

class VSCodePortOperator(bpy.types.Operator):
    bl_idname = "wm.vscode_port_modal_op"
    bl_label = "VSCode Port Socket Modal Operator"

    _timer = None

    @staticmethod
    def _connect_to_server():
        server = VSCodePortServer.instance()
        try:
            server.accept_client()
            LOG.debug(f"[VSCodePort] Connected to {server._client_address}")
        except BlockingIOError:
            return

    @staticmethod
    def _wait_for_data():
        server = VSCodePortServer.instance()
        message, state = server.read()
        if state == ReadState.WAITING:
            return
        if state == ReadState.ERROR:
            LOG.error("[VSCodePort] Failed to read message")
            return
        if state == ReadState.DISCONNECTED:
            LOG.debug("[VSCodePort] Client disconnected")
            return
        if state == ReadState.MESSAGE:
            LOG.debug(f"[VSCodePort] Received code: {message}")
            preferences = bpy.context.preferences.addons[__package__].preferences
            scope = preferences.execution_scope
            output = execute_python_code(message, scope)
            # Send output back to client
            if output is not None:
                try:
                    LOG.debug(f"[VSCodePort] Sending output back to client: {output[:200]}{'...' if len(output) > 200 else ''}")
                    server.send_output(output)
                except Exception as e:
                    LOG.error(f"[VSCodePort] Failed to send output: {e}")

    def modal(self, context, event):
        if not context.window_manager.vscode_port_enabled:
            return {"FINISHED"}
        if event.type == "TIMER":
            try:
                server = VSCodePortServer.instance()
                if server.is_connected():
                    self._wait_for_data()
                else:
                    self._connect_to_server()
            except Exception as e:
                LOG.error(f"[VSCodePort] Modal error: {e}")
        return {"PASS_THROUGH"}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        wm = context.window_manager
        if self._timer:
            wm.event_timer_remove(self._timer)
        server = VSCodePortServer.instance()
        server.stop()
        # Clear any global variables from the session
        global GLOBALS
        GLOBALS = {}
