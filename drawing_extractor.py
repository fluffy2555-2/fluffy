#!/usr/bin/env python3
"""
図面拾いツール (Drawing Extraction Tool)
建築図面から自動的に寸法、面積、数量を抽出するツール
"""

import os
import re
import json
import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class MeasurementType(Enum):
    """測定タイプの列挙"""
    LENGTH = "長さ"
    AREA = "面積"
    COUNT = "数量"
    PERIMETER = "周長"


@dataclass
class Measurement:
    """測定結果を保持するデータクラス"""
    type: MeasurementType
    value: float
    unit: str
    label: str
    location: Optional[Tuple[float, float]] = None
    description: Optional[str] = None

    def to_dict(self):
        """辞書形式に変換"""
        return {
            'type': self.type.value,
            'value': self.value,
            'unit': self.unit,
            'label': self.label,
            'location': self.location,
            'description': self.description
        }


class DrawingExtractor:
    """図面から測定値を抽出するメインクラス"""

    def __init__(self, scale: float = 1.0):
        """
        初期化

        Args:
            scale: 図面のスケール (1/100なら0.01)
        """
        self.scale = scale
        self.measurements: List[Measurement] = []

    def extract_from_text(self, text: str) -> List[Measurement]:
        """
        テキストから寸法情報を抽出

        Args:
            text: 抽出元のテキスト

        Returns:
            測定結果のリスト
        """
        measurements = []

        # 長さの抽出 (例: "3,000", "3000mm", "3.5m")
        length_pattern = r'(\d+[,\.]?\d*)\s*(mm|m|cm)'
        for match in re.finditer(length_pattern, text):
            value_str = match.group(1).replace(',', '')
            value = float(value_str)
            unit = match.group(2)

            # 単位をmmに統一
            if unit == 'm':
                value *= 1000
            elif unit == 'cm':
                value *= 10

            measurements.append(Measurement(
                type=MeasurementType.LENGTH,
                value=value,
                unit='mm',
                label=f'{match.group(1)}{unit}'
            ))

        # 面積の抽出 (例: "15.5㎡", "15.5m2")
        area_pattern = r'(\d+[,\.]?\d*)\s*(㎡|m2|m²)'
        for match in re.finditer(area_pattern, text):
            value_str = match.group(1).replace(',', '')
            value = float(value_str)

            measurements.append(Measurement(
                type=MeasurementType.AREA,
                value=value,
                unit='m²',
                label=f'{match.group(1)}{match.group(2)}'
            ))

        self.measurements.extend(measurements)
        return measurements

    def calculate_area(self, width: float, height: float,
                      unit: str = 'mm', label: str = '') -> Measurement:
        """
        長方形の面積を計算

        Args:
            width: 幅
            height: 高さ
            unit: 単位
            label: ラベル

        Returns:
            面積の測定結果
        """
        # mmで計算してm²に変換
        if unit == 'm':
            width *= 1000
            height *= 1000
        elif unit == 'cm':
            width *= 10
            height *= 10

        area_mm2 = width * height * (self.scale ** 2)
        area_m2 = area_mm2 / 1_000_000

        measurement = Measurement(
            type=MeasurementType.AREA,
            value=area_m2,
            unit='m²',
            label=label or f'{width}×{height}',
            description=f'幅{width}mm × 高さ{height}mm'
        )

        self.measurements.append(measurement)
        return measurement

    def calculate_perimeter(self, width: float, height: float,
                           unit: str = 'mm', label: str = '') -> Measurement:
        """
        長方形の周長を計算

        Args:
            width: 幅
            height: 高さ
            unit: 単位
            label: ラベル

        Returns:
            周長の測定結果
        """
        # mmで計算
        if unit == 'm':
            width *= 1000
            height *= 1000
        elif unit == 'cm':
            width *= 10
            height *= 10

        perimeter = 2 * (width + height) * self.scale

        measurement = Measurement(
            type=MeasurementType.PERIMETER,
            value=perimeter,
            unit='mm',
            label=label or f'{width}×{height}周長',
            description=f'(幅{width}mm + 高さ{height}mm) × 2'
        )

        self.measurements.append(measurement)
        return measurement

    def add_count(self, count: int, label: str,
                  description: Optional[str] = None) -> Measurement:
        """
        数量を追加

        Args:
            count: 数量
            label: ラベル
            description: 説明

        Returns:
            数量の測定結果
        """
        measurement = Measurement(
            type=MeasurementType.COUNT,
            value=count,
            unit='個',
            label=label,
            description=description
        )

        self.measurements.append(measurement)
        return measurement

    def get_summary(self) -> Dict[str, List[Measurement]]:
        """
        測定結果をタイプ別に集計

        Returns:
            タイプ別の測定結果辞書
        """
        summary = {
            MeasurementType.LENGTH: [],
            MeasurementType.AREA: [],
            MeasurementType.COUNT: [],
            MeasurementType.PERIMETER: []
        }

        for measurement in self.measurements:
            summary[measurement.type].append(measurement)

        return summary

    def export_to_json(self, filename: str):
        """
        結果をJSONファイルにエクスポート

        Args:
            filename: 出力ファイル名
        """
        data = {
            'scale': self.scale,
            'measurements': [m.to_dict() for m in self.measurements],
            'summary': {
                'total_measurements': len(self.measurements),
                'by_type': {
                    k.value: len(v) for k, v in self.get_summary().items()
                }
            }
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f'結果を {filename} に出力しました')

    def export_to_csv(self, filename: str):
        """
        結果をCSVファイルにエクスポート

        Args:
            filename: 出力ファイル名
        """
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['タイプ', '値', '単位', 'ラベル', '説明'])

            for m in self.measurements:
                writer.writerow([
                    m.type.value,
                    m.value,
                    m.unit,
                    m.label,
                    m.description or ''
                ])

        print(f'結果を {filename} に出力しました')

    def print_summary(self):
        """測定結果のサマリーを表示"""
        print('\n=== 図面拾い結果 ===\n')

        summary = self.get_summary()

        for type_key, measurements in summary.items():
            if measurements:
                print(f'\n【{type_key.value}】')
                for m in measurements:
                    print(f'  {m.label}: {m.value:.2f} {m.unit}')
                    if m.description:
                        print(f'    ({m.description})')

        print(f'\n合計測定数: {len(self.measurements)}')


class PDFDrawingExtractor(DrawingExtractor):
    """PDF図面から抽出する拡張クラス"""

    def __init__(self, scale: float = 1.0):
        super().__init__(scale)
        self.pdf_available = self._check_pdf_library()

    def _check_pdf_library(self) -> bool:
        """PDFライブラリの利用可能性をチェック"""
        try:
            import PyPDF2
            return True
        except ImportError:
            try:
                import pdfplumber
                return True
            except ImportError:
                print('警告: PDFライブラリが見つかりません')
                print('pip install PyPDF2 または pip install pdfplumber を実行してください')
                return False

    def extract_from_pdf(self, pdf_path: str) -> List[Measurement]:
        """
        PDFファイルから測定値を抽出

        Args:
            pdf_path: PDFファイルのパス

        Returns:
            測定結果のリスト
        """
        if not self.pdf_available:
            print('PDFライブラリがインストールされていません')
            return []

        try:
            import pdfplumber

            all_measurements = []
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        print(f'ページ {page_num} を処理中...')
                        measurements = self.extract_from_text(text)
                        all_measurements.extend(measurements)

            return all_measurements

        except ImportError:
            try:
                import PyPDF2

                all_measurements = []
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(pdf_reader.pages, 1):
                        text = page.extract_text()
                        if text:
                            print(f'ページ {page_num} を処理中...')
                            measurements = self.extract_from_text(text)
                            all_measurements.extend(measurements)

                return all_measurements

            except ImportError:
                print('PDFライブラリが見つかりません')
                return []
        except Exception as e:
            print(f'PDFの処理中にエラーが発生しました: {e}')
            return []


def main():
    """使用例のメイン関数"""
    print('図面拾いツール - Drawing Extraction Tool')
    print('=' * 50)

    # 1/100スケールの図面を想定
    extractor = PDFDrawingExtractor(scale=0.01)

    # サンプルテキストから抽出
    sample_text = """
    居室: 15.5㎡
    寸法: 3,500mm × 4,500mm
    天井高: 2,400mm
    開口部: 800mm
    """

    print('\n1. テキストから抽出:')
    extractor.extract_from_text(sample_text)

    # 面積の計算
    print('\n2. 面積の計算:')
    extractor.calculate_area(3500, 4500, unit='mm', label='居室')
    extractor.calculate_area(800, 2000, unit='mm', label='開口部')

    # 周長の計算
    print('\n3. 周長の計算:')
    extractor.calculate_perimeter(3500, 4500, unit='mm', label='居室')

    # 数量の追加
    print('\n4. 数量の追加:')
    extractor.add_count(4, 'コンセント')
    extractor.add_count(2, '照明器具')
    extractor.add_count(1, 'エアコン')

    # 結果の表示
    extractor.print_summary()

    # エクスポート
    print('\n5. エクスポート:')
    extractor.export_to_json('drawing_extraction_result.json')
    extractor.export_to_csv('drawing_extraction_result.csv')

    print('\n処理が完了しました！')


if __name__ == '__main__':
    main()
