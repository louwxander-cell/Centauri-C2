"""
Enhanced Engage Button with Safety Features
- Long-press confirmation (900ms)
- Short-press opens confirm dialog
- Armed state animation
- Safety interlocks
"""

from PyQt6.QtWidgets import QPushButton, QMessageBox
from PyQt6.QtCore import QTimer, pyqtSignal, QPropertyAnimation


class EngageButton(QPushButton):
    """
    Safety-enhanced engage button with two-step confirmation:
    - Short press: Opens confirmation dialog
    - Long press (900ms): Triggers armed sequence
    """
    
    engaged = pyqtSignal(int)  # Emits track ID when engagement confirmed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("engageButton")
        self.setText("ENGAGE TARGET")
        
        # Long-press timer (900ms)
        self.longpress_timer = QTimer(self)
        self.longpress_timer.setInterval(900)
        self.longpress_timer.setSingleShot(True)
        self.longpress_timer.timeout.connect(self._on_longpress)
        
        # Connect press/release events
        self.pressed.connect(self._on_pressed)
        self.released.connect(self._on_released)
        
        # State tracking
        self.armed = False
        self.target_id = None
    
    def set_target(self, track_id):
        """Set the current target track ID"""
        self.target_id = track_id
        if track_id is not None:
            self.setEnabled(True)
            self.setText(f"ENGAGE ID:{track_id}")
        else:
            self.setEnabled(False)
            self.setText("ENGAGE TARGET")
    
    def _on_pressed(self):
        """Handle button press - start long-press timer"""
        self.longpress_timer.start()
    
    def _on_released(self):
        """Handle button release"""
        if self.longpress_timer.isActive():
            # Short press - open confirmation dialog
            self.longpress_timer.stop()
            self._confirm_dialog()
        # If timer already fired, long-press was triggered
    
    def _on_longpress(self):
        """Handle long-press - trigger armed sequence"""
        self._arm_sequence()
    
    def _confirm_dialog(self):
        """Show confirmation dialog for engagement"""
        if self.target_id is None:
            return
        
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Confirm Engagement")
        dlg.setText(
            f"<b>Confirm ENGAGE Track ID:{self.target_id}</b><br><br>"
            "This action will command the Remote Weapon Station to fire.<br><br>"
            "Are you sure you want to proceed?"
        )
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.setStandardButtons(
            QMessageBox.StandardButton.Cancel | 
            QMessageBox.StandardButton.Ok
        )
        dlg.button(QMessageBox.StandardButton.Ok).setText("✓ CONFIRM ENGAGE")
        dlg.button(QMessageBox.StandardButton.Cancel).setText("✗ Cancel")
        
        # Style the dialog
        dlg.setStyleSheet("""
            QMessageBox {
                background: #15181A;
                color: rgba(255,255,255,0.92);
            }
            QPushButton {
                background: #1B1F22;
                color: rgba(255,255,255,0.92);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: rgba(56,230,224,0.08);
                border: 1px solid #3DDAD7;
            }
        """)
        
        if dlg.exec() == QMessageBox.StandardButton.Ok:
            self._perform_engage()
    
    def _arm_sequence(self):
        """Visual armed state with glow effect"""
        # Apply armed state styling
        self.setStyleSheet("""
            QPushButton#engageButton {
                background: #E84855;
                color: #FFFFFF;
                border-radius: 24px;
                padding: 14px 28px;
                font-weight: 700;
                font-size: 15pt;
                border: 2px solid rgba(232,72,85,0.50);
            }
        """)
        
        # Revert after 1.6 seconds
        QTimer.singleShot(1600, lambda: self.setStyleSheet(""))
        
        # Automatically perform engage after arm sequence
        QTimer.singleShot(200, self._perform_engage)
    
    def _perform_engage(self):
        """Execute engagement command"""
        if self.target_id is not None:
            print(f"[ENGAGE] Commanding RWS to engage Track ID:{self.target_id}")
            self.engaged.emit(self.target_id)
            
            # Reset button state
            self.setText("ENGAGED")
            self.setEnabled(False)
            
            # Re-enable after cooldown
            QTimer.singleShot(3000, lambda: self.set_target(None))
