# VSCode send to blender addon
This is a simple extension for sending code from vscode to Blender.\
It requires both an extension loaded into VSCode and an addon installed into Blender, both are included.\
Once installed, it can be enabled from the file menu.

This started as a derivitive of [vscode-maya](https://github.com/artbycrunk/vscode-maya/) but morphed into the current implementation.

![](vscode_extension/blender_vscode.gif)

# Installation

## Installing the Blender Python Addon

You have two options:

### 1. Install the Addon in Blender

- In Blender, go to **Edit > Preferences > Add-ons > Install...**
- Select the Python addon file `packages/vscode_port.zip`.
- Enable the addon in the list after installation.

### 2. Add the Addon Path Directly

- Find the path to the addon directory in this repository.
- In Blender, go to **Edit > Preferences > File Paths > Scripts**.
- Add the path to the `git_repo/blender_scripts` directory.
- Refresh the addons list.
- Enable the addon in **Edit > Preferences > Add-ons**.


# Building the extension manually

## Prerequisites

- **Node.js & npm**: Download and install from [https://nodejs.org/](https://nodejs.org/)
- **vsce (Visual Studio Code Extension Manager)**: Install globally with  
  ```
  npm install -g @vscode/vsce
  ```

## Building the VSCode Extension

To build the VSCode extension, follow these steps:

1. Navigate to the `vscode_extension` directory.
2. Run `npm install` to install the necessary dependencies.
3. Run `vsce package` to compile the extension.
4. Install with `code --install-extension sendtoblender-{version}.vsix`  
   Or navigate to it via the extension browser.