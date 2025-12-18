---

# Mini-LISP Interpreter (Python)

本專案是一個以 **Python** 實作的 **Mini-LISP 直譯器**，支援基本的 Lisp 語法、函數定義、閉包（closure）、巢狀 `define`、運算式計算，以及簡單的型別檢查。

此直譯器分為四個主要階段：

1. **Tokenizer（詞彙分析）**
2. **Parser（語法分析，產生 AST）**
3. **Runtime Environment（環境與閉包）**
4. **Evaluator（直譯執行）**

---

## 📌 Features

* 支援 **整數與布林值**
* 支援 **S-expression 語法**
* 支援 **變數定義 (`define`)**
* 支援 **函數 (`fun`) 與閉包 (closure)**
* 支援 **函數內巢狀 define**
* 支援 **條件判斷 (`if`)**
* 支援 **算術、比較、邏輯運算**
* 具備 **基本型別檢查（number / boolean）**
* 錯誤時符合 Mini-LISP 規格輸出 `syntax error` 或 `Type error!`

---

## 🚀 Usage

### 執行方式

```bash
python mini_lisp.py < input.lisp
```

或直接指定檔案：

```bash
python mini_lisp.py input.lisp
```

---

## ✍️ Example

### Input

```lisp
(define dist-square
  (fun (x y)
    (define square (fun (x) (* x x)))
    (+ (square x) (square y))))

(print-num (dist-square 3 4))
```

### Output

```
25
```

---

## 🧩 Language Specification

### Literals

* Integer：`0`, `-10`, `42`
* Boolean：`#t`, `#f`

### Variables

```lisp
(define x 10)
```

---

### Functions

#### Function Definition

```lisp
(fun (a b) (+ a b))
```

#### Nested `define` inside function body

```lisp
(fun (x)
  (define y 10)
  (+ x y))
```

函數內部的 `define` 會在**呼叫時建立區域環境**，並正確支援 closure。

---

### Function Call

```lisp
((fun (x) (* x x)) 5)
```

---

### Conditional

```lisp
(if (> x 0) 1 0)
```

---

### Arithmetic Operators

| Operator | Description |
| -------- | ----------- |
| `+`      | 加法（多參數）     |
| `-`      | 減法          |
| `*`      | 乘法（多參數）     |
| `/`      | 整數除法        |
| `mod`    | 取餘數         |

---

### Comparison Operators

| Operator | Description |
| -------- | ----------- |
| `>`      | 大於          |
| `<`      | 小於          |
| `=`      | 相等（多參數）     |

---

### Logical Operators

| Operator | Description |
| -------- | ----------- |
| `and`    | 邏輯且         |
| `or`     | 邏輯或         |
| `not`    | 邏輯非         |

---

### Print

```lisp
(print-num 10)
(print-bool #t)
```

---

## 🧠 Interpreter Architecture

### 1️⃣ Tokenizer

* 手動掃描字串
* 支援：

  * 括號 `(` `)`
  * 整數 / 負數
  * Boolean (`#t`, `#f`)
  * 識別字（含 `-`）
  * 運算子
  * 註解（`;` 開頭）

---

### 2️⃣ Parser

* 使用 **Recursive Descent Parsing**
* 產生 AST（tuple-based）
* 支援：

  * 多參數運算
  * 函數定義與呼叫
  * 巢狀 `define`
  * 語法錯誤直接丟出 `SyntaxError`

---

### 3️⃣ Runtime Environment

```python
Environment(parent)
```

* 使用 **linked environment（靜態作用域）**
* `define` 僅能在當前 scope 定義
* `lookup` 會一路往 parent 查找
* 確保 closure 正確運作

---

### 4️⃣ Function & Closure

```python
Function(params, body, closure_env)
```

* 函數會攜帶**定義時的環境**
* 呼叫時建立新的 local environment
* 完整支援 lexical scoping

---

### 5️⃣ Type Checking

* 透過 `TYPE_CHECKING` 開關控制
* 規則：

  * `bool` 不能當作 `number`
  * 算術運算只接受 `int`
  * 邏輯運算只接受 `bool`
* 發生錯誤時：

```text
Type error!
```

---

## ⚠️ Error Handling

| 情況            | 輸出             |
| ------------- | -------------- |
| 語法錯誤          | `syntax error` |
| 型別錯誤          | `Type error!`  |
| 其他 runtime 錯誤 | 依作業規格忽略輸出      |

---

## 🛠 Implementation Notes

* AST 使用 Python `tuple` 表示，方便 pattern matching
* `bool` 是 `int` 子類，型別檢查特別處理
* `/` 使用整數除法 (`//`)
* `define` 不允許重複定義同名變數

---

## 📚 Requirements

* Python **3.8+**
* 無需額外套件

---

## 📎 License

This project is for **educational use** (Mini-LISP interpreter / Programming Languages course).

---
