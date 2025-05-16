'use strict';
// This code is derived from https://github.com/artbycrunk/vscode-maya/blob/master/src/extension.ts
import * as vscode from 'vscode';
import { Socket } from 'net';
import * as os from 'os';
import * as fs from 'fs';
import * as path from 'path';
var net = require('net');
import { TelemetryReporter } from '@vscode/extension-telemetry';
import { TextEncoder } from 'util';

let blenderportStatusBar: vscode.StatusBarItem;
let socket_blender: Socket;
let port_blender: string;
// Removed reporter variable

const extensionId = 'minimalefforttech.blendercode';
const extensionVersion = vscode.extensions.getExtension(extensionId).packageJSON.version;

function updateStatusBarItem(): void {
  let text: string;
  if (socket_blender instanceof Socket == true && socket_blender.destroyed == false) {
    text = `Blender Port : ${port_blender}`;
    blenderportStatusBar.text = text;
    blenderportStatusBar.show();
  } else {
    blenderportStatusBar.hide();
  }
}

export class Logger {
  private static _outputPanel;

  public static registerOutputPanel(outputPanel: vscode.OutputChannel) {
    this._outputPanel = outputPanel;
  }

  public static info(log: string) {
    this.typeLog(log, 'INFO');
  }

  public static error(log: string) {
    this.typeLog(log, 'ERROR');
    vscode.window.showErrorMessage(log);
  }

  private static typeLog(log: String, type: String) {
    if (!this._outputPanel) {
      return;
    }
    let util = require('util');
    let time = new Date().toISOString();
    this._outputPanel.appendLine(util.format('BlenderCode-%s [%s][%s]\t %s', extensionVersion, time, type, log));
  }
}

export function activate(context: vscode.ExtensionContext) {
  let outputPanel = vscode.window.createOutputChannel('Blender');
  Logger.registerOutputPanel(outputPanel);

  var config = vscode.workspace.getConfiguration('blendercode');

  // Removed telemetry event due to compatibility issues

  function ensureConnection() {
    let socket = socket_blender;
    let hostname: string = config.get('hostname');
    let port: number = config.get('port');

    port_blender = port.toString();

    if (socket instanceof Socket == true && socket.destroyed == false) {
      Logger.info(`Already connected to Blender on Port ${port}`);
      updateStatusBarItem();
    } else {
      socket = net.createConnection({ port: port, host: hostname }, () => {
        Logger.info(`Connected to Blender on Port ${port}`);
        updateStatusBarItem();
      });

      socket.on('error', (error) => {
        let errorMsg = `Unable to connect to Blender on Port ${port}. Ensure Blender is running with the correct port open.`;
        Logger.error(errorMsg);
      });

      socket.on('data', (data: Buffer) => {
        Logger.info(`Received from Blender: ${data.toString()}`);
      });

      socket.on('end', () => {
        Logger.info(`Disconnected from Blender on Port ${port}`);
        updateStatusBarItem();
      });
    }
    return socket;
  }

  function sendPythonCodeToBlender(text: string) {
    // Stream: send 8-byte header (code length), then code
    const encoder = new TextEncoder();
    const codeBuffer = encoder.encode(text);
    const lengthHeader = Buffer.byteLength(codeBuffer).toString().padStart(8, '0');
    send(Buffer.concat([Buffer.from(lengthHeader), codeBuffer]));
  }

  function send(data: Buffer | string) {
    socket_blender = ensureConnection();
    if (!socket_blender.destroyed) {
      let buffer: Buffer;
      if (typeof data === 'string') {
        buffer = Buffer.from(data + '\n');
      } else {
        buffer = data;
      }
      let success = socket_blender.write(buffer);
      if (success) {
        Logger.info(`Sent Python code to Blender`);
      }
    }
  }

  function getText() {
    let editor = vscode.window.activeTextEditor;
    let selection = editor.selection;
    let text: string;

    if (!selection.isEmpty) {
      text = editor.document.getText(selection);
    } else {
      text = editor.document.getText();
    }
    return text;
  }

  const command = vscode.commands.registerCommand('blendercode.sendPythonToBlender', () => {
    socket_blender = ensureConnection();
    if (!socket_blender.destroyed) {
      let text = getText();
      sendPythonCodeToBlender(text);
    }
  });

  context.subscriptions.push(command);

  blenderportStatusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
  context.subscriptions.push(blenderportStatusBar);

  updateStatusBarItem();
}

export function deactivate() {
  // No reporter to dispose
}
