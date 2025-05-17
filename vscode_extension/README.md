# Send to Blender VSCode Extension

Send Python code from Visual Studio Code directly to Blender for rapid prototyping and development.

![](blender_vscode.gif)

## Features

- Send selected Python code or the entire file to Blender.
- Print, pretty-print, or describe variables in Blender's output.
- Show help or signatures for selected variables.
- Configurable Blender host and port.

## Requirements

- Blender running with a the vscode_port addon
- Visual Studio Code.

## Installation

From the vscode extensions, click the 3 dots to install from .vsix, navigate to the package/sendtoblender-{version}.vsix

Add the bundled vscode_port addon to blender.

## Usage

1. Open a Python file in VSCode.
2. Select code or place the cursor in a Python file.
3. Use the Command Palette (`Ctrl+Shift+P`) and search for:
   - **Blender: Send Python Code to Blender**
   - **Blender: Print the selected variable in Output console**
   - **Blender: Pretty print the selected variable in Output console**
   - **Blender: Describe the selected variable (with signatures) in Output console**
   - **Blender: Show help for the selected variable in Output console**
4. The output from Blender will appear in the "Blender" output panel.

## Extension Settings

- `sendtoblender.hostname`: Hostname of the machine running Blender (default: `localhost`)
- `sendtoblender.port`: Port for sending Python commands to Blender (default: `8080`)
- `sendtoblender.telemetry`: Enable/disable telemetry (default: `true`)

## Troubleshooting

- Ensure Blender is running and listening on the configured port with the vscode_port addon
- Check the Output panel for connection errors.

## License

MIT License. See [LICENSE](./LICENSE).
