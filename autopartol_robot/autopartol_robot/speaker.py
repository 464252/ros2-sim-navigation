#!/usr/bin/env python3
import asyncio
import subprocess

import edge_tts
import rclpy
from rclpy.node import Node
from autopatol_interfaces.srv import SpeechText

class Speaker(Node):
    def __init__(self, name):
        super().__init__(name)
        self.speech_service_ = self.create_service(
            SpeechText, 'speech_text', self.speech_text_callback
        )
        self.get_logger().info('语音服务已启动，使用 edge-tts 引擎')
        # ==========================================
        # 就是这行！想换声音改这里
        self.voice_ = 'zh-CN-XiaoxiaoNeural'
        # 其他可选：zh-CN-YunxiNeural（男声）
        #           zh-CN-XiaohanNeural（知性女声）
        # ==========================================

    def speech_text_callback(self, request, response):
        self.get_logger().info(f'正在准备朗读 {request.text}')
        try:
            communicate = edge_tts.Communicate(request.text, self.voice_)
            asyncio.run(communicate.save('/tmp/tts_output.mp3'))
            subprocess.run(
                ['mpv', '/tmp/tts_output.mp3'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            response.result = True
        except Exception as e:
            self.get_logger().error(f'语音合成失败: {e}')
            response.result = False
        return response

def main():
    rclpy.init()
    node = Speaker('speaker')
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()