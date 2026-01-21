#!/usr/bin/env python3
"""
基本的な使用例
図面拾いツールの基本的な使い方を示すサンプルコード
"""

from drawing_extractor import PDFDrawingExtractor


def example_manual_input():
    """手動入力での使用例"""
    print('=' * 60)
    print('例1: 手動入力での図面拾い')
    print('=' * 60)

    # ツールの初期化 (1/100スケール)
    extractor = PDFDrawingExtractor(scale=0.01)

    # 部屋の面積を計算
    print('\n1. 部屋の面積計算:')
    extractor.calculate_area(5400, 7200, unit='mm', label='リビング')
    extractor.calculate_area(3600, 5400, unit='mm', label='寝室')
    extractor.calculate_area(1800, 2700, unit='mm', label='浴室')

    # 周長の計算
    print('\n2. 周長の計算:')
    extractor.calculate_perimeter(5400, 7200, unit='mm', label='リビング')

    # 数量の追加
    print('\n3. 設備数量の入力:')
    extractor.add_count(8, 'コンセント', 'リビング・寝室')
    extractor.add_count(4, '照明器具', 'リビング・寝室・浴室')
    extractor.add_count(2, 'エアコン', 'リビング・寝室')
    extractor.add_count(3, '窓', '各部屋')
    extractor.add_count(3, 'ドア', '各部屋')

    # 結果の表示
    extractor.print_summary()

    # ファイルにエクスポート
    print('\n4. 結果のエクスポート:')
    extractor.export_to_json('example_manual_result.json')
    extractor.export_to_csv('example_manual_result.csv')


def example_text_extraction():
    """テキスト抽出での使用例"""
    print('\n' + '=' * 60)
    print('例2: テキストからの自動抽出')
    print('=' * 60)

    extractor = PDFDrawingExtractor(scale=0.01)

    # 図面に記載されているテキストデータ
    drawing_text = """
    【1階平面図】

    リビングダイニング: 25.5㎡
    寸法: 5,400mm × 7,200mm
    天井高: 2,400mm

    主寝室: 10.8㎡
    寸法: 3,600mm × 5,400mm
    天井高: 2,400mm

    浴室: 3.5㎡
    寸法: 1,800mm × 2,700mm
    天井高: 2,200mm

    廊下幅: 900mm
    開口部: 800mm × 2,000mm
    """

    print('\n図面テキスト:')
    print(drawing_text)

    print('\nテキストから自動抽出中...')
    measurements = extractor.extract_from_text(drawing_text)

    print(f'\n{len(measurements)} 件の測定値を抽出しました')

    # 追加の計算
    extractor.calculate_area(5400, 7200, unit='mm', label='リビングダイニング(計算)')
    extractor.add_count(1, '浴室ユニット')
    extractor.add_count(5, '室内ドア')

    # 結果の表示
    extractor.print_summary()

    # エクスポート
    extractor.export_to_json('example_text_result.json')
    extractor.export_to_csv('example_text_result.csv')


def example_construction_estimate():
    """建築見積もりの使用例"""
    print('\n' + '=' * 60)
    print('例3: 建築工事の数量拾い')
    print('=' * 60)

    extractor = PDFDrawingExtractor(scale=0.01)

    print('\n【躯体工事】')
    # 床面積
    extractor.calculate_area(10000, 8000, unit='mm', label='1階床面積')
    extractor.calculate_area(10000, 8000, unit='mm', label='2階床面積')

    # 壁の長さ（周長）
    extractor.calculate_perimeter(10000, 8000, unit='mm', label='外壁')

    print('\n【内装工事】')
    # 各部屋の壁・床面積
    rooms = [
        ('リビング', 6000, 8000),
        ('ダイニング', 4000, 4500),
        ('キッチン', 3000, 3600),
        ('主寝室', 4500, 5400),
        ('子供部屋1', 3600, 4500),
        ('子供部屋2', 3600, 4500),
        ('浴室', 2000, 2500),
        ('洗面所', 1800, 2200),
        ('トイレ', 1500, 2000),
    ]

    for room_name, width, height in rooms:
        # 床面積
        extractor.calculate_area(width, height, unit='mm',
                                label=f'{room_name}床面積')
        # 壁面積（概算: 周長 × 天井高）
        perimeter_mm = 2 * (width + height)
        ceiling_height = 2400
        wall_area_m2 = (perimeter_mm * ceiling_height * (extractor.scale ** 2)) / 1_000_000
        from drawing_extractor import Measurement, MeasurementType
        extractor.measurements.append(
            Measurement(
                type=MeasurementType.AREA,
                value=wall_area_m2,
                unit='m²',
                label=f'{room_name}壁面積',
                description=f'周長{perimeter_mm}mm × 天井高{ceiling_height}mm'
            )
        )

    print('\n【建具工事】')
    extractor.add_count(8, '室内ドア', '一般的な片開きドア')
    extractor.add_count(2, '玄関ドア', '断熱性能付き')
    extractor.add_count(15, 'アルミサッシ窓', '一般的なサイズ')
    extractor.add_count(3, 'シャッター付き窓', 'バルコニー用')

    print('\n【設備工事】')
    extractor.add_count(1, 'キッチンセット', 'システムキッチン 2.4m')
    extractor.add_count(1, 'ユニットバス', '1616サイズ')
    extractor.add_count(2, '洗面化粧台', '幅750mm')
    extractor.add_count(2, 'トイレ', 'タンクレス')
    extractor.add_count(3, 'エアコン', '各部屋用')
    extractor.add_count(20, 'コンセント', '2口・3口混在')
    extractor.add_count(12, '照明器具', 'LED照明')
    extractor.add_count(1, '給湯器', 'エコキュート')

    # 結果の表示
    extractor.print_summary()

    # エクスポート
    extractor.export_to_json('example_construction_result.json')
    extractor.export_to_csv('example_construction_result.csv')

    print('\n見積書作成のための数量拾いが完了しました！')


def main():
    """すべての例を実行"""
    print('図面拾いツール - 使用例集')
    print('=' * 60)

    # 例1: 手動入力
    example_manual_input()

    # 例2: テキスト抽出
    example_text_extraction()

    # 例3: 建築見積もり
    example_construction_estimate()

    print('\n' + '=' * 60)
    print('すべての例が完了しました！')
    print('=' * 60)
    print('\n生成されたファイル:')
    print('  - example_manual_result.json / .csv')
    print('  - example_text_result.json / .csv')
    print('  - example_construction_result.json / .csv')


if __name__ == '__main__':
    main()
