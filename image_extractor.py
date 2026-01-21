#!/usr/bin/env python3
"""
画像図面拾いツール (Image Drawing Extraction Tool)
画像形式の建築図面から寸法を抽出するツール
"""

import os
from typing import List, Tuple, Optional
import json

from drawing_extractor import DrawingExtractor, Measurement, MeasurementType


class ImageDrawingExtractor(DrawingExtractor):
    """画像図面から抽出する拡張クラス"""

    def __init__(self, scale: float = 1.0):
        super().__init__(scale)
        self.pil_available = self._check_pil()
        self.cv2_available = self._check_opencv()
        self.ocr_available = self._check_ocr()

    def _check_pil(self) -> bool:
        """PILの利用可能性をチェック"""
        try:
            from PIL import Image
            return True
        except ImportError:
            return False

    def _check_opencv(self) -> bool:
        """OpenCVの利用可能性をチェック"""
        try:
            import cv2
            return True
        except ImportError:
            return False

    def _check_ocr(self) -> bool:
        """OCRライブラリの利用可能性をチェック"""
        try:
            import pytesseract
            return True
        except ImportError:
            try:
                import easyocr
                return True
            except ImportError:
                return False

    def extract_from_image(self, image_path: str) -> List[Measurement]:
        """
        画像ファイルから測定値を抽出

        Args:
            image_path: 画像ファイルのパス

        Returns:
            測定結果のリスト
        """
        if not os.path.exists(image_path):
            print(f'エラー: ファイルが見つかりません: {image_path}')
            return []

        print(f'画像を処理中: {image_path}')

        # OCRでテキストを抽出
        text = self._extract_text_from_image(image_path)
        if text:
            print('OCRでテキストを抽出しました')
            return self.extract_from_text(text)
        else:
            print('OCRライブラリが利用できないため、テキスト抽出をスキップします')
            return []

    def _extract_text_from_image(self, image_path: str) -> str:
        """
        画像からOCRでテキストを抽出

        Args:
            image_path: 画像ファイルのパス

        Returns:
            抽出されたテキスト
        """
        # pytesseractを試す
        try:
            import pytesseract
            from PIL import Image

            # 日本語OCRの設定
            custom_config = r'--oem 3 --psm 6 -l jpn+eng'
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, config=custom_config)
            return text

        except ImportError:
            pass
        except Exception as e:
            print(f'pytesseractでのOCRに失敗: {e}')

        # easyocrを試す
        try:
            import easyocr
            reader = easyocr.Reader(['ja', 'en'])
            results = reader.readtext(image_path)
            text = ' '.join([result[1] for result in results])
            return text

        except ImportError:
            print('OCRライブラリがインストールされていません')
            print('pip install pytesseract または pip install easyocr を実行してください')
            return ''
        except Exception as e:
            print(f'easyocrでのOCRに失敗: {e}')
            return ''

    def detect_lines(self, image_path: str,
                    threshold: int = 100) -> List[Tuple[int, int, int, int]]:
        """
        画像から直線を検出

        Args:
            image_path: 画像ファイルのパス
            threshold: 直線検出の閾値

        Returns:
            検出された直線のリスト [(x1, y1, x2, y2), ...]
        """
        if not self.cv2_available:
            print('OpenCVがインストールされていません')
            print('pip install opencv-python を実行してください')
            return []

        try:
            import cv2
            import numpy as np

            # 画像を読み込み
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # エッジ検出
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)

            # 直線検出
            lines = cv2.HoughLinesP(
                edges,
                rho=1,
                theta=np.pi/180,
                threshold=threshold,
                minLineLength=50,
                maxLineGap=10
            )

            if lines is not None:
                line_list = []
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    line_list.append((x1, y1, x2, y2))

                print(f'{len(line_list)} 本の直線を検出しました')
                return line_list
            else:
                print('直線が検出されませんでした')
                return []

        except Exception as e:
            print(f'直線検出中にエラーが発生しました: {e}')
            return []

    def calculate_line_length(self, x1: int, y1: int,
                             x2: int, y2: int,
                             pixels_per_mm: float = 1.0,
                             label: str = '') -> Measurement:
        """
        画像上の直線の長さを計算

        Args:
            x1, y1: 始点座標
            x2, y2: 終点座標
            pixels_per_mm: 1mmあたりのピクセル数
            label: ラベル

        Returns:
            長さの測定結果
        """
        import math

        # ピクセル距離を計算
        pixel_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # 実際の長さに変換
        actual_length = (pixel_length / pixels_per_mm) * self.scale

        measurement = Measurement(
            type=MeasurementType.LENGTH,
            value=actual_length,
            unit='mm',
            label=label or f'Line ({x1},{y1})-({x2},{y2})',
            location=(x1, y1),
            description=f'{pixel_length:.1f}ピクセル = {actual_length:.1f}mm'
        )

        self.measurements.append(measurement)
        return measurement

    def visualize_detections(self, image_path: str, output_path: str):
        """
        検出結果を画像に描画

        Args:
            image_path: 入力画像ファイルのパス
            output_path: 出力画像ファイルのパス
        """
        if not self.cv2_available:
            print('OpenCVがインストールされていません')
            return

        try:
            import cv2

            image = cv2.imread(image_path)

            # 直線の検出と描画
            lines = self.detect_lines(image_path)
            for x1, y1, x2, y2 in lines:
                cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # 測定点の描画
            for m in self.measurements:
                if m.location:
                    x, y = int(m.location[0]), int(m.location[1])
                    cv2.circle(image, (x, y), 5, (0, 0, 255), -1)
                    cv2.putText(
                        image,
                        m.label,
                        (x + 10, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 0, 0),
                        1
                    )

            cv2.imwrite(output_path, image)
            print(f'検出結果を {output_path} に保存しました')

        except Exception as e:
            print(f'可視化中にエラーが発生しました: {e}')


def main():
    """使用例のメイン関数"""
    print('画像図面拾いツール - Image Drawing Extraction Tool')
    print('=' * 60)

    # 画像抽出ツールの作成 (1/100スケール)
    extractor = ImageDrawingExtractor(scale=0.01)

    # ライブラリの状態を表示
    print('\nライブラリの状態:')
    print(f'  PIL (Pillow): {"✓ 利用可能" if extractor.pil_available else "✗ 未インストール"}')
    print(f'  OpenCV: {"✓ 利用可能" if extractor.cv2_available else "✗ 未インストール"}')
    print(f'  OCR: {"✓ 利用可能" if extractor.ocr_available else "✗ 未インストール"}')

    # サンプル使用例
    print('\n使用例:')
    print('1. 画像からテキスト抽出:')
    print('   extractor.extract_from_image("drawing.png")')

    print('\n2. 直線の検出:')
    print('   lines = extractor.detect_lines("drawing.png")')

    print('\n3. 長さの計算:')
    print('   extractor.calculate_line_length(100, 100, 500, 100, pixels_per_mm=10, label="壁")')

    print('\n4. 検出結果の可視化:')
    print('   extractor.visualize_detections("drawing.png", "result.png")')

    # サンプルデータで動作確認
    print('\n\nサンプルデータでの動作確認:')
    extractor.calculate_area(5000, 8000, unit='mm', label='部屋A')
    extractor.calculate_area(3000, 4000, unit='mm', label='部屋B')
    extractor.add_count(6, '窓')
    extractor.add_count(3, 'ドア')

    extractor.print_summary()
    extractor.export_to_json('image_extraction_result.json')

    print('\n処理が完了しました！')
    print('\n注意: 画像からの自動抽出には、以下のライブラリが必要です:')
    print('  pip install Pillow opencv-python pytesseract')


if __name__ == '__main__':
    main()
