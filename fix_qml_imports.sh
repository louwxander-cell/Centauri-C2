#!/bin/bash
# Fix QML imports by adding missing QtQuick.Effects and QtQuick.Layouts

cd "$(dirname "$0")/qml/TriAD"

# Files that need QtQuick.Effects (for MultiEffect)
effects_files="SensorIndicator.qml TrackRow.qml TrackMarker.qml ZoomButton.qml EngageButton.qml"

# Files that need QtQuick.Layouts
layouts_files="LeftPanel.qml RightPanel.qml StatusCard.qml TrackDetailsCard.qml LegendItem.qml ModeToggle.qml"

for f in $effects_files; do
    if [ -f "$f" ]; then
        if ! grep -q "import QtQuick.Effects" "$f"; then
            # Add after the last import QtQuick line
            sed -i '' '/^import QtQuick$/a\
import QtQuick.Effects
' "$f"
            echo "Added QtQuick.Effects to $f"
        fi
    fi
done

for f in $layouts_files; do
    if [ -f "$f" ]; then
        if ! grep -q "import QtQuick.Layouts" "$f"; then
            # Add after the last import QtQuick line
            sed -i '' '/^import QtQuick$/a\
import QtQuick.Layouts
' "$f"
            echo "Added QtQuick.Layouts to $f"
        fi
    fi
done

echo "Import fixes complete"
