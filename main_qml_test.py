#!/usr/bin/env python3
"""
Simple QML test to verify window display works
"""

import sys
from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

def main():
    app = QGuiApplication(sys.argv)
    app.setApplicationName("QML Test")
    
    engine = QQmlApplicationEngine()
    
    # Simple inline QML
    qml_content = """
import QtQuick
import QtQuick.Window

Window {
    visible: true
    width: 800
    height: 600
    title: "QML Test Window"
    color: "#1a1a1a"
    
    Rectangle {
        anchors.centerIn: parent
        width: 400
        height: 200
        color: "#3a3a3a"
        radius: 10
        
        Text {
            anchors.centerIn: parent
            text: "QML Window Test\\n\\nIf you can see this,\\nQML is working!"
            font.pixelSize: 24
            color: "#00ff00"
            horizontalAlignment: Text.AlignHCenter
        }
    }
}
"""
    
    engine.loadData(qml_content.encode('utf-8'), QUrl())
    
    if not engine.rootObjects():
        print("ERROR: Failed to create window")
        return -1
    
    print("Window should be visible now...")
    print("If you see a green text window, QML is working!")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
