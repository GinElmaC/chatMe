
import platform
import subprocess
import sys
from typing import Optional


class NotificationManager:
    """系统通知管理器，支持 macOS 和其他平台"""
    
    @staticmethod
    def send_notification(title: str, message: str, subtitle: Optional[str] = None) -> bool:
        """发送系统通知
        
        Args:
            title: 通知标题
            message: 通知内容
            subtitle: 副标题（可选）
            
        Returns:
            bool: 是否成功发送通知
        """
        system = platform.system()
        
        try:
            if system == "Darwin":
                # macOS 系统通知
                return NotificationManager._send_macos_notification(title, message, subtitle)
            elif system == "Linux":
                # Linux 系统通知
                return NotificationManager._send_linux_notification(title, message, subtitle)
            elif system == "Windows":
                # Windows 系统通知
                return NotificationManager._send_windows_notification(title, message, subtitle)
            else:
                # 不支持的平台
                return False
        except Exception as e:
            print(f"发送通知失败: {e}", file=sys.stderr)
            return False
    
    @staticmethod
    def _send_macos_notification(title: str, message: str, subtitle: Optional[str] = None) -> bool:
        """发送 macOS 系统通知"""
        try:
            # 使用 osascript 发送通知
            script = f'display notification "{message}" with title "{title}"'
            if subtitle:
                script = f'display notification "{message}" with title "{title}" subtitle "{subtitle}"'
            
            subprocess.run(['osascript', '-e', script], check=True, capture_output=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def _send_linux_notification(title: str, message: str, subtitle: Optional[str] = None) -> bool:
        """发送 Linux 系统通知"""
        try:
            # 使用 notify-send
            cmd = ['notify-send', title]
            if subtitle:
                cmd.append(subtitle)
            cmd.append(message)
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def _send_windows_notification(title: str, message: str, subtitle: Optional[str] = None) -> bool:
        """发送 Windows 系统通知"""
        try:
            # 使用 PowerShell 发送通知
            full_title = title
            if subtitle:
                full_title = f"{title} - {subtitle}"
            
            ps_script = f"""
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
            $textNodes = $template.GetElementsByTagName('text')
            $textNodes.Item(0).AppendChild($template.CreateTextNode('{full_title}')) | Out-Null
            $textNodes.Item(1).AppendChild($template.CreateTextNode('{message}')) | Out-Null
            $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
            $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Python')
            $notifier.Show($toast)
            """
            
            subprocess.run(['powershell', '-Command', ps_script], check=True, capture_output=True)
            return True
        except Exception:
            return False

