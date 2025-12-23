// RadarConfigDialog.qml - Radar configuration dialog
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root
    
    title: "Radar Configuration - EchoGuard"
    modal: true
    standardButtons: Dialog.Ok | Dialog.Cancel
    
    property bool radarOnline: false
    
    // Configuration values
    property var config: ({
        label: "R1",
        ipv4_address: "192.168.1.25",
        product_mode: "EchoGuard",
        mission_set: "cUAS",
        latitude: -25.848810,
        longitude: 28.997978,
        altitude: 1.4,
        heading: 30.0,
        pitch: 19.8,
        roll: -0.3,
        range_min: 21,
        range_max: 500,
        search_az_min: -60,
        search_az_max: 60,
        search_el_min: -40,
        search_el_max: 40,
        track_az_min: -60,
        track_az_max: 60,
        track_el_min: -40,
        track_el_max: 40,
        freq_channel: 0
    })
    property string syncStatus: "unknown"  // "synced", "out_of_sync", "unknown"
    
    signal configurationChanged(var newConfig)
    signal refreshRequested()
    signal verifyRequested()
    
    width: 500
    height: 850
    
    // Update fields when config changes
    onConfigChanged: {
        console.log("[RadarConfigDialog] Configuration updated:", JSON.stringify(config))
        updateFields()
    }
    
    // Update all input fields from config
    function updateFields() {
        labelField.text = config.label || "R1"
        ipField.text = config.ipv4_address || "192.168.1.25"
        latField.text = (config.latitude !== undefined ? config.latitude : -25.848810).toFixed(6)
        lonField.text = (config.longitude !== undefined ? config.longitude : 28.997978).toFixed(6)
        altField.text = (config.altitude !== undefined ? config.altitude : 1.4).toFixed(1)
        headingField.text = (config.heading !== undefined ? config.heading : 30.0).toFixed(1)
        pitchField.text = (config.pitch !== undefined ? config.pitch : 19.8).toFixed(1)
        rollField.text = (config.roll !== undefined ? config.roll : -0.3).toFixed(1)
        rangeMinSpin.value = config.range_min !== undefined ? config.range_min : 21
        rangeMaxSpin.value = config.range_max !== undefined ? config.range_max : 500
        searchAzMinSpin.value = config.search_az_min !== undefined ? config.search_az_min : -60
        searchAzMaxSpin.value = config.search_az_max !== undefined ? config.search_az_max : 60
        searchElMinSpin.value = config.search_el_min !== undefined ? config.search_el_min : -40
        searchElMaxSpin.value = config.search_el_max !== undefined ? config.search_el_max : 40
        trackAzMinSpin.value = config.track_az_min !== undefined ? config.track_az_min : -60
        trackAzMaxSpin.value = config.track_az_max !== undefined ? config.track_az_max : 60
        trackElMinSpin.value = config.track_el_min !== undefined ? config.track_el_min : -40
        trackElMaxSpin.value = config.track_el_max !== undefined ? config.track_el_max : 40
        freqChannelCombo.currentIndex = config.freq_channel !== undefined ? config.freq_channel : 0
    }
    
    Component.onCompleted: {
        updateFields()
    }
    
    // Scroll view for all settings
    ScrollView {
        anchors.fill: parent
        clip: true
        
        ColumnLayout {
            width: parent.width - 20
            spacing: 15
            
            // Header with sync status
            Rectangle {
                Layout.fillWidth: true
                height: 80
                color: "#1E293B"
                radius: 4
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 12
                    spacing: 12
                    
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 4
                        
                        Text {
                            text: "GLOBAL - Radar 1"
                            font.family: "SF Pro Display"
                            font.pixelSize: 14
                            font.weight: Font.Bold
                            color: "#F8FAFC"
                        }
                        
                        Text {
                            text: radarOnline ? "● LIVE CONFIGURATION" : "○ Default Configuration"
                            font.family: "SF Pro Display"
                            font.pixelSize: 10
                            color: radarOnline ? "#10B981" : "#64748B"
                        }
                        
                        // Sync status indicator
                        Text {
                            visible: radarOnline
                            text: {
                                if (syncStatus === "verifying") return "⟳ Verifying..."
                                if (syncStatus === "synced") return "✓ Synced with radar"
                                if (syncStatus === "out_of_sync") return "⚠ Out of sync"
                                return "? Not verified - Click Verify"
                            }
                            font.family: "SF Pro Display"
                            font.pixelSize: 9
                            color: {
                                if (syncStatus === "verifying") return "#3B82F6"
                                if (syncStatus === "synced") return "#10B981"
                                if (syncStatus === "out_of_sync") return "#F59E0B"
                                return "#64748B"
                            }
                        }
                    }
                    
                    // Verify button
                    Button {
                        id: verifyButton
                        visible: radarOnline
                        text: syncStatus === "unknown" ? "Verify" : "Re-verify"
                        Layout.preferredWidth: 90
                        Layout.preferredHeight: 32
                        
                        background: Rectangle {
                            color: verifyButton.pressed ? "#0EA5E9" : (verifyButton.hovered ? "#38BDF8" : "#0284C7")
                            radius: 4
                        }
                        
                        contentItem: Text {
                            text: verifyButton.text
                            font.family: "SF Pro Display"
                            font.pixelSize: 11
                            font.weight: Font.Medium
                            color: "#FFFFFF"
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                        
                        onClicked: {
                            console.log("[RadarConfigDialog] Verify button clicked")
                            syncStatus = "verifying"
                            verifyRequested()
                        }
                    }
                }
            }
            
            // Basic Settings
            GroupBox {
                Layout.fillWidth: true
                title: "Basic Settings"
                
                GridLayout {
                    anchors.fill: parent
                    columns: 2
                    rowSpacing: 10
                    columnSpacing: 10
                    
                    Label { text: "Label:" }
                    TextField {
                        id: labelField
                        Layout.fillWidth: true
                        text: config.label
                        enabled: !radarOnline
                    }
                    
                    Label { text: "IPv4 Address:" }
                    TextField {
                        id: ipField
                        Layout.fillWidth: true
                        text: config.ipv4_address
                        enabled: !radarOnline
                    }
                    
                    Label { text: "Product Mode:" }
                    ComboBox {
                        id: productModeCombo
                        Layout.fillWidth: true
                        model: ["EchoGuard", "EchoFlight", "EchoDrone"]
                        currentIndex: 0
                        enabled: !radarOnline
                    }
                    
                    Label { text: "Mission Set:" }
                    ComboBox {
                        id: missionSetCombo
                        Layout.fillWidth: true
                        model: ["cUAS", "Surveillance", "Tracking"]
                        currentIndex: 0
                        enabled: !radarOnline
                    }
                }
            }
            
            // Platform Position (Read-only when online)
            GroupBox {
                Layout.fillWidth: true
                title: "Platform Position"
                
                GridLayout {
                    anchors.fill: parent
                    columns: 2
                    rowSpacing: 10
                    columnSpacing: 10
                    
                    Label { text: "Latitude (°):" }
                    TextField {
                        id: latField
                        Layout.fillWidth: true
                        text: config.latitude.toFixed(6)
                        enabled: !radarOnline
                        validator: DoubleValidator { bottom: -90; top: 90; decimals: 6 }
                    }
                    
                    Label { text: "Longitude (°):" }
                    TextField {
                        id: lonField
                        Layout.fillWidth: true
                        text: config.longitude.toFixed(6)
                        enabled: !radarOnline
                        validator: DoubleValidator { bottom: -180; top: 180; decimals: 6 }
                    }
                    
                    Label { text: "Altitude (m):" }
                    TextField {
                        id: altField
                        Layout.fillWidth: true
                        text: config.altitude.toFixed(1)
                        enabled: !radarOnline
                        validator: DoubleValidator { bottom: -500; top: 10000; decimals: 1 }
                    }
                    
                    Label { text: "Heading (°):" }
                    TextField {
                        id: headingField
                        Layout.fillWidth: true
                        text: config.heading.toFixed(1)
                        enabled: !radarOnline
                        validator: DoubleValidator { bottom: 0; top: 359.9; decimals: 1 }
                    }
                }
            }
            
            // Platform Orientation (Read-only when online)
            GroupBox {
                Layout.fillWidth: true
                title: "Platform Orientation"
                
                GridLayout {
                    anchors.fill: parent
                    columns: 2
                    rowSpacing: 10
                    columnSpacing: 10
                    
                    Label { text: "Pitch (°):" }
                    TextField {
                        id: pitchField
                        Layout.fillWidth: true
                        text: config.pitch.toFixed(1)
                        enabled: !radarOnline
                        validator: DoubleValidator { bottom: -90; top: 90; decimals: 1 }
                    }
                    
                    Label { text: "Roll (°):" }
                    TextField {
                        id: rollField
                        Layout.fillWidth: true
                        text: config.roll.toFixed(1)
                        enabled: !radarOnline
                        validator: DoubleValidator { bottom: -180; top: 180; decimals: 1 }
                    }
                }
            }
            
            // Range Settings (Can edit while online)
            GroupBox {
                Layout.fillWidth: true
                title: "Range Settings"
                
                GridLayout {
                    anchors.fill: parent
                    columns: 2
                    rowSpacing: 10
                    columnSpacing: 10
                    
                    Label { text: "Range Min (m):" }
                    SpinBox {
                        id: rangeMinSpin
                        Layout.fillWidth: true
                        from: 20
                        to: 5987
                        value: config.range_min
                        editable: true
                    }
                    
                    Label { text: "Range Max (m):" }
                    SpinBox {
                        id: rangeMaxSpin
                        Layout.fillWidth: true
                        from: 20
                        to: 5987
                        value: config.range_max
                        editable: true
                    }
                }
            }
            
            // Search FOV (Can edit while online)
            GroupBox {
                Layout.fillWidth: true
                title: "Search Field of View"
                
                GridLayout {
                    anchors.fill: parent
                    columns: 2
                    rowSpacing: 10
                    columnSpacing: 10
                    
                    Label { text: "Search Az Min (°):" }
                    SpinBox {
                        id: searchAzMinSpin
                        Layout.fillWidth: true
                        from: -60
                        to: 60
                        value: config.search_az_min
                        editable: true
                        enabled: !radarOnline
                    }
                    
                    Label { text: "Search Az Max (°):" }
                    SpinBox {
                        id: searchAzMaxSpin
                        Layout.fillWidth: true
                        from: -60
                        to: 60
                        value: config.search_az_max
                        editable: true
                        enabled: !radarOnline
                    }
                    
                    Label { text: "Search El Min (°):" }
                    SpinBox {
                        id: searchElMinSpin
                        Layout.fillWidth: true
                        from: -40
                        to: 40
                        value: config.search_el_min
                        editable: true
                        enabled: !radarOnline
                    }
                    
                    Label { text: "Search El Max (°):" }
                    SpinBox {
                        id: searchElMaxSpin
                        Layout.fillWidth: true
                        from: -40
                        to: 40
                        value: config.search_el_max
                        editable: true
                        enabled: !radarOnline
                    }
                }
            }
            
            // Track FOV (Can edit while online)
            GroupBox {
                Layout.fillWidth: true
                title: "Track Field of View"
                
                GridLayout {
                    anchors.fill: parent
                    columns: 2
                    rowSpacing: 10
                    columnSpacing: 10
                    
                    Label { text: "Track Az Min (°):" }
                    SpinBox {
                        id: trackAzMinSpin
                        Layout.fillWidth: true
                        from: -60
                        to: 60
                        value: config.track_az_min
                        editable: true
                    }
                    
                    Label { text: "Track Az Max (°):" }
                    SpinBox {
                        id: trackAzMaxSpin
                        Layout.fillWidth: true
                        from: -60
                        to: 60
                        value: config.track_az_max
                        editable: true
                    }
                    
                    Label { text: "Track El Min (°):" }
                    SpinBox {
                        id: trackElMinSpin
                        Layout.fillWidth: true
                        from: -40
                        to: 40
                        value: config.track_el_min
                        editable: true
                    }
                    
                    Label { text: "Track El Max (°):" }
                    SpinBox {
                        id: trackElMaxSpin
                        Layout.fillWidth: true
                        from: -40
                        to: 40
                        value: config.track_el_max
                        editable: true
                    }
                }
            }
            
            // Classification Settings
            GroupBox {
                Layout.fillWidth: true
                title: "Track Classification"
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 10
                    
                    // Classifier Enable
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        
                        CheckBox {
                            id: classifierEnabledCheck
                            text: "Enable Classifier"
                            checked: config.classifier_enabled !== undefined ? config.classifier_enabled : true
                            ToolTip.visible: hovered
                            ToolTip.text: "Enable ML-based track classification (UAV, Bird, Plane, etc.)"
                        }
                    }
                    
                    // Operation Mode
                    GridLayout {
                        Layout.fillWidth: true
                        columns: 2
                        rowSpacing: 10
                        columnSpacing: 10
                        
                        Label { text: "Operation Mode:" }
                        ComboBox {
                            id: operationModeCombo
                            Layout.fillWidth: true
                            model: ["0 - Walkers", "1 - Small Drones (cUAS)", "2 - Crewed Aircraft"]
                            currentIndex: config.operation_mode !== undefined ? config.operation_mode : 1
                            ToolTip.visible: hovered
                            ToolTip.text: "Optimizes radar parameters for target type"
                        }
                    }
                    
                    // Class Declaration Threshold
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 5
                        
                        Label {
                            text: "Class Declaration Threshold: " + classThresholdSlider.value + "%"
                            font.pixelSize: 11
                        }
                        
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10
                            
                            Label {
                                text: "0"
                                font.pixelSize: 9
                                color: "#94A3B8"
                            }
                            
                            Slider {
                                id: classThresholdSlider
                                Layout.fillWidth: true
                                from: 0
                                to: 100
                                value: config.class_declaration_threshold !== undefined ? config.class_declaration_threshold : 90
                                stepSize: 5
                                snapMode: Slider.SnapAlways
                                ToolTip.visible: hovered
                                ToolTip.text: "Minimum confidence % to declare a track class"
                            }
                            
                            Label {
                                text: "100"
                                font.pixelSize: 9
                                color: "#94A3B8"
                            }
                        }
                    }
                    
                    // Show Classes
                    Label {
                        text: "Show Classes:"
                        font.pixelSize: 11
                        font.weight: Font.Bold
                        Layout.topMargin: 5
                    }
                    
                    GridLayout {
                        Layout.fillWidth: true
                        columns: 2
                        rowSpacing: 5
                        columnSpacing: 10
                        
                        CheckBox {
                            id: showUavCheck
                            text: "UAV"
                            checked: config.show_classes && config.show_classes.uav !== undefined ? config.show_classes.uav : true
                        }
                        CheckBox {
                            id: showUavMultiRotorCheck
                            text: "UAV (Multi-Rotor)"
                            checked: config.show_classes && config.show_classes.uav_multi_rotor !== undefined ? config.show_classes.uav_multi_rotor : true
                        }
                        CheckBox {
                            id: showUavFixedWingCheck
                            text: "UAV (Fixed Wing)"
                            checked: config.show_classes && config.show_classes.uav_fixed_wing !== undefined ? config.show_classes.uav_fixed_wing : true
                        }
                        CheckBox {
                            id: showWalkerCheck
                            text: "Walker"
                            checked: config.show_classes && config.show_classes.walker !== undefined ? config.show_classes.walker : false
                        }
                        CheckBox {
                            id: showPlaneCheck
                            text: "Plane"
                            checked: config.show_classes && config.show_classes.plane !== undefined ? config.show_classes.plane : false
                        }
                        CheckBox {
                            id: showBirdCheck
                            text: "Bird"
                            checked: config.show_classes && config.show_classes.bird !== undefined ? config.show_classes.bird : true
                        }
                        CheckBox {
                            id: showVehicleCheck
                            text: "Vehicle"
                            checked: config.show_classes && config.show_classes.vehicle !== undefined ? config.show_classes.vehicle : false
                        }
                        CheckBox {
                            id: showClutterCheck
                            text: "Clutter"
                            checked: config.show_classes && config.show_classes.clutter !== undefined ? config.show_classes.clutter : true
                        }
                        CheckBox {
                            id: showUndeclaredCheck
                            text: "Undeclared"
                            checked: config.show_classes && config.show_classes.undeclared !== undefined ? config.show_classes.undeclared : true
                            Layout.columnSpan: 2
                        }
                    }
                }
            }
            
            // Frequency Channel (Read-only when online)
            GroupBox {
                Layout.fillWidth: true
                title: "Frequency"
                
                GridLayout {
                    anchors.fill: parent
                    columns: 2
                    rowSpacing: 10
                    columnSpacing: 10
                    
                    Label { text: "Freq Channel:" }
                    ComboBox {
                        id: freqChannelCombo
                        Layout.fillWidth: true
                        model: ["0", "1", "2", "3", "4"]
                        currentIndex: config.freq_channel
                        enabled: !radarOnline
                    }
                }
            }
            
            // Status message
            Rectangle {
                Layout.fillWidth: true
                height: 60
                color: radarOnline ? "#FEF3C7" : "#DBEAFE"
                radius: 4
                border.color: radarOnline ? "#F59E0B" : "#3B82F6"
                border.width: 1
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 5
                    
                    Text {
                        text: radarOnline ? "⚠ Radar Online" : "ℹ Radar Offline"
                        font.family: "SF Pro Display"
                        font.pixelSize: 12
                        font.weight: Font.Bold
                        color: radarOnline ? "#92400E" : "#1E40AF"
                    }
                    
                    Text {
                        text: radarOnline ? 
                            "Some settings cannot be changed while radar is streaming." :
                            "All settings can be changed when radar is offline."
                        font.family: "SF Pro Display"
                        font.pixelSize: 10
                        color: radarOnline ? "#92400E" : "#1E40AF"
                        wrapMode: Text.WordWrap
                        Layout.fillWidth: true
                    }
                }
            }
        }
    }
    
    onAccepted: {
        // Gather all configuration values
        var newConfig = {
            label: labelField.text,
            ipv4_address: ipField.text,
            product_mode: productModeCombo.currentText,
            mission_set: missionSetCombo.currentText,
            latitude: parseFloat(latField.text),
            longitude: parseFloat(lonField.text),
            altitude: parseFloat(altField.text),
            heading: parseFloat(headingField.text),
            pitch: parseFloat(pitchField.text),
            roll: parseFloat(rollField.text),
            range_min: rangeMinSpin.value,
            range_max: rangeMaxSpin.value,
            search_az_min: searchAzMinSpin.value,
            search_az_max: searchAzMaxSpin.value,
            search_el_min: searchElMinSpin.value,
            search_el_max: searchElMaxSpin.value,
            track_az_min: trackAzMinSpin.value,
            track_az_max: trackAzMaxSpin.value,
            track_el_min: trackElMinSpin.value,
            track_el_max: trackElMaxSpin.value,
            freq_channel: freqChannelCombo.currentIndex,
            operation_mode: operationModeCombo.currentIndex,
            classifier_enabled: classifierEnabledCheck.checked,
            class_declaration_threshold: classThresholdSlider.value,
            show_classes: {
                uav: showUavCheck.checked,
                uav_multi_rotor: showUavMultiRotorCheck.checked,
                uav_fixed_wing: showUavFixedWingCheck.checked,
                walker: showWalkerCheck.checked,
                plane: showPlaneCheck.checked,
                bird: showBirdCheck.checked,
                vehicle: showVehicleCheck.checked,
                clutter: showClutterCheck.checked,
                undeclared: showUndeclaredCheck.checked
            }
        }
        
        console.log("[RadarConfig] Configuration updated:", JSON.stringify(newConfig))
        configurationChanged(newConfig)
    }
}
