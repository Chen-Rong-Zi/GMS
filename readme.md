## rust是怎么实现move语义的？
### 一、rust的编译流程

```mermaid
graph LR
    S[源代码] --> AST
    AST --> HIR
    HIR --> MIR
    MIR --> LLVM_IR
    LLVM_IR --> Bin
```
1. AST (抽象语法树)

基础结构：完全保留源码的语法结构
核心功能：词法/语法分析的结果，处理宏展开

2.  HIR (高级中间表示)

完成类型推断（Type Inference）
添加显式类型标注（Type Annotation）
脱糖（Desugaring）语法糖结构（如?操作符、for循环）

3. MIR (中级中间表示)
显式化控制流（Basic Blocks）
低层级数据流分析 ()
优化移动语义检查


### 二、实现move检查的控制流程图分析
> https://zh.wikipedia.org/zh-cn/%E6%95%B0%E6%8D%AE%E6%B5%81%E5%88%86%E6%9E%90


```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1;          // 发生移动
    println!("{}", s1);  // 触发编译错误
}
```
