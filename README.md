# Markov Chain Matrix Generator

這個專案會從多個 Excel 標註檔中讀取狀態序列，建立零階、一階與二階 Markov 機率矩陣，並將結果儲存為 NumPy 陣列及視覺化圖片。

## 功能

從手術器具標記的Excel 檔案讀取標註資料，計算零階、一階及二階 Markov 機率矩陣，並輸出 `.npy` 矩陣檔與 `.png` 視覺化圖表

## 專案結構

```text
markov_chain/
├── config.py                # 定義有效狀態
├── gen_markov_matrix.py     # 矩陣計算與視覺化主程式
├── dataset/                 # 輸入資料（手術器具標記的Excel）
├── results/                 # NumPy 矩陣輸出（執行時建立）
└── visualized/              # 圖片輸出（執行時建立）
```

## 環境需求

- Python 3
- pandas
- NumPy
- Matplotlib
- seaborn
- openpyxl（供 pandas 讀取 `.xlsx`）

安裝相依套件：

```bash
pip install pandas numpy matplotlib seaborn openpyxl
```

## 資料格式

輸入目錄可放置多個 `.xlsx` 檔案。程式會依檔名排序後逐一處理，並讀取每個檔案的 D 欄：

- 有效狀態定義於 `config.py`。
- 目前預設狀態為：`剪刀`、`電刀`、`血管夾`、`手術刀`。
- 自轉移狀態會被合併

例如，D 欄內容為：

```text
工具
剪刀
剪刀
電刀
血管夾
```

程式會將連續重複狀態合併，得到以下序列：

```text
剪刀 → 電刀 → 血管夾
```

## 使用方式

使用預設路徑執行：

```bash
python gen_markov_matrix.py
```

預設路徑如下：

- 輸入資料夾：`./dataset/train`
- 矩陣輸出資料夾：`./results/markov_matrices`
- 圖片輸出資料夾：`./visualized/markov_matrices`

也可以自訂路徑：

```bash
python gen_markov_matrix.py \
  --input_dir ./dataset/GT/train \
  --output_dir ./results/GT_markov_matrices \
  --vis_dir ./visualized/GT_markov_matrices
```


如果輸入目錄不存在，程式會拋出 `FileNotFoundError`；輸出目錄則會自動建立。

## 輸出結果

矩陣目錄會產生：

| 檔案 | 內容 | 維度 |
| --- | --- | --- |
| `zero_order_markov_matrix.npy` | 各狀態在所有有效序列中的出現機率 | `(S,)` |
| `first_order_markov_matrix.npy` | 目前狀態轉移到下一狀態的條件機率(一階) | `(S, S)` |
| `second_order_markov_matrix.npy` | 已知前兩個狀態時，下一狀態的條件機率(二階) | `(S, S, S)` |

其中 `S` 是 `config.py` 中定義的狀態數量。

視覺化目錄會產生：

- `zero_order_markov_matrix.png`：狀態機率長條圖
- `first_order_markov_matrix.png`：一階轉移矩陣熱圖
- `second_order_markov_matrix.png`：依前一狀態分組的二階轉移矩陣熱圖



## 自訂狀態

編輯 `config.py` 中的 `states` 即可調整狀態名稱與排列順序：

```python
CONFIG = {
    "states": ["剪刀", "電刀", "血管夾", "手術刀"],
}
```

狀態順序會直接影響輸出矩陣各維度的索引與熱圖座標。

## 注意事項

- 每個 Excel 檔案都視為一段獨立序列，不會在不同檔案之間建立轉移。
- 圖表預設使用 `Arial Unicode MS`。若系統未安裝此字型，Matplotlib 可能顯示字型警告或無法正確顯示中文，可在 `visualize_markov_matrix()` 中改成系統已有的中文字型。
