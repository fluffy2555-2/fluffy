# 図面拾いツール (Drawing Extraction Tool)

建築図面から自動的に寸法、面積、数量を抽出・計算するPythonツールです。

## 概要

このツールは建築・建設業界における「図面拾い」（積算作業）を効率化するために開発されました。PDF図面や画像ファイルから寸法情報を自動抽出し、面積や数量の計算を行い、CSV/JSON形式で出力できます。

## 主な機能

### 📊 測定・計算機能
- **寸法抽出**: テキストから長さ、面積、数量を自動認識
- **面積計算**: 長方形の面積を自動計算（スケール対応）
- **周長計算**: 壁や部屋の周囲長さを計算
- **数量管理**: 設備や建具の数量を記録

### 📄 入力対応
- **PDFファイル**: PDF図面からテキストを抽出（PyPDF2, pdfplumber対応）
- **画像ファイル**: PNG/JPG等の画像図面に対応
- **OCR機能**: 画像からテキストを自動認識（pytesseract, easyocr対応）
- **手動入力**: プログラムで直接データを入力

### 💾 出力形式
- **JSON**: 構造化されたデータ形式
- **CSV**: Excelで開けるスプレッドシート形式
- **サマリー表示**: コンソールでの見やすい集計表示

## インストール

### 基本インストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd fluffy

# 必要なライブラリをインストール
pip install -r requirements.txt
```

### 最小構成（PDF処理のみ）

```bash
pip install PyPDF2 pdfplumber
```

### フル機能（画像処理・OCR含む）

```bash
pip install PyPDF2 pdfplumber Pillow opencv-python pytesseract easyocr numpy pandas
```

## 使い方

### 基本的な使い方

```python
from drawing_extractor import PDFDrawingExtractor

# ツールの初期化（1/100スケールの図面）
extractor = PDFDrawingExtractor(scale=0.01)

# 面積の計算
extractor.calculate_area(5400, 7200, unit='mm', label='リビング')

# 数量の追加
extractor.add_count(4, 'コンセント')
extractor.add_count(2, '照明器具')

# 結果の表示
extractor.print_summary()

# ファイルにエクスポート
extractor.export_to_json('result.json')
extractor.export_to_csv('result.csv')
```

### テキストからの自動抽出

```python
from drawing_extractor import PDFDrawingExtractor

extractor = PDFDrawingExtractor(scale=0.01)

# 図面に記載されているテキスト
text = """
居室: 15.5㎡
寸法: 3,500mm × 4,500mm
天井高: 2,400mm
"""

# 自動抽出
measurements = extractor.extract_from_text(text)
extractor.print_summary()
```

### PDFファイルからの抽出

```python
from drawing_extractor import PDFDrawingExtractor

extractor = PDFDrawingExtractor(scale=0.01)

# PDFから自動抽出
measurements = extractor.extract_from_pdf('drawing.pdf')
extractor.print_summary()
```

### 画像ファイルからの抽出

```python
from image_extractor import ImageDrawingExtractor

extractor = ImageDrawingExtractor(scale=0.01)

# 画像からOCRで抽出
measurements = extractor.extract_from_image('drawing.png')

# 直線の検出
lines = extractor.detect_lines('drawing.png')

# 検出結果を画像で確認
extractor.visualize_detections('drawing.png', 'result.png')
```

## サンプルコード

### 基本例の実行

```bash
python example_basic.py
```

このスクリプトは以下の3つの例を実行します：
1. 手動入力での図面拾い
2. テキストからの自動抽出
3. 建築工事の数量拾い（詳細な例）

### メインツールの実行

```bash
# 基本的なデモ
python drawing_extractor.py

# 画像処理のデモ
python image_extractor.py
```

## ファイル構成

```
fluffy/
├── README.md                    # このファイル
├── CLAUDE.MD                    # Claude Code用の指示ファイル
├── requirements.txt             # 必要なライブラリ一覧
├── config.json                  # 設定ファイル
├── drawing_extractor.py         # メインの図面拾いツール
├── image_extractor.py           # 画像処理用拡張ツール
└── example_basic.py             # 使用例集
```

## 設定ファイル

`config.json`で以下の設定をカスタマイズできます：

- **default_scale**: デフォルトのスケール（1/100なら0.01）
- **units**: 使用する単位
- **extraction_patterns**: テキスト抽出の正規表現パターン
- **output_formats**: 出力フォーマットの設定
- **pdf_settings**: PDF処理の設定
- **image_settings**: 画像処理・OCRの設定
- **room_types**: 認識する部屋タイプ
- **standard_dimensions**: 標準寸法の定義

## 測定タイプ

ツールは以下の4種類の測定をサポートしています：

| タイプ | 説明 | 単位 |
|--------|------|------|
| LENGTH | 長さ | mm |
| AREA | 面積 | m² |
| COUNT | 数量 | 個 |
| PERIMETER | 周長 | mm |

## 出力例

### JSON形式

```json
{
  "scale": 0.01,
  "measurements": [
    {
      "type": "面積",
      "value": 15.75,
      "unit": "m²",
      "label": "リビング",
      "description": "幅3500mm × 高さ4500mm"
    }
  ],
  "summary": {
    "total_measurements": 10,
    "by_type": {
      "面積": 5,
      "数量": 5
    }
  }
}
```

### CSV形式

```csv
タイプ,値,単位,ラベル,説明
面積,15.75,m²,リビング,幅3500mm × 高さ4500mm
数量,4,個,コンセント,
```

## 対応フォーマット

### 入力
- PDF (.pdf)
- PNG (.png)
- JPEG (.jpg, .jpeg)
- その他Pillowがサポートする画像形式

### 出力
- JSON (.json)
- CSV (.csv)

## スケールについて

建築図面のスケールを正しく設定することで、図面上の寸法を実際の寸法に変換します：

- **1/100スケール**: `scale=0.01`
- **1/50スケール**: `scale=0.02`
- **1/200スケール**: `scale=0.005`

## 活用例

### 建築積算
- 床面積の計算
- 壁面積の計算
- 設備数量の集計

### 建設見積もり
- 材料数量の算出
- 工事項目ごとの集計
- 見積書作成の基礎データ

### リフォーム計画
- 既存建物の採寸
- 改修範囲の数量確認
- 必要資材の概算

## 注意事項

1. **OCR精度**: 画像の品質やフォントによってOCRの精度は変動します
2. **スケール設定**: 正確な計算のため、図面のスケールを正しく設定してください
3. **単位の統一**: 混在する単位は自動的にmm/m²に変換されます
4. **手動確認**: 自動抽出結果は必ず目視で確認してください

## トラブルシューティング

### PDFが読み込めない
```bash
pip install --upgrade PyPDF2 pdfplumber
```

### 画像からテキストが抽出できない
```bash
# Tesseractのインストール（Ubuntuの場合）
sudo apt-get install tesseract-ocr tesseract-ocr-jpn

# Pythonライブラリのインストール
pip install pytesseract
```

### OpenCVが動作しない
```bash
pip install --upgrade opencv-python
```

## ライセンス

このプロジェクトはオープンソースです。

## 貢献

バグ報告や機能提案は、GitHubのIssuesでお願いします。

## 今後の開発予定

- [ ] DXF/DWGファイル対応
- [ ] AI/機械学習による図面要素の自動認識
- [ ] 3D図面への対応
- [ ] Webインターフェースの追加
- [ ] Excel形式の出力
- [ ] 複数図面の一括処理
- [ ] データベース連携機能

## お問い合わせ

質問や提案がありましたら、GitHubのIssuesまでお願いします。