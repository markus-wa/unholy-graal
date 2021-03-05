# unholy-graal

A write up of the state of GraalVM language support and interop in early 2021.

![GraalVM Language Support Visualisation](unholy-graal.png)

## Python

> GraalVM Python runtime comes with a tool called ginstall

> **which may be used to install a *small* list of packages known to work *to some extent* with GraalVM’s Python runtime.**

Thanks, Oracle

## Go

[LLVM's Go Front-End Was Finally Dropped From The Official Source Tree](https://www.phoronix.com/scan.php?page=news_item&px=LLVM-Drops-LLGO-Golang)

😞

## Rust

```
$ rustc --emit=llvm-bc src/main.rs
$ lli --lib /usr/lib/rustlib/x86_64-unknown-linux-gnu/lib/libstd-*.so main.bc
Hello, world!
```

🥳

... Let's do something more interesting ...

Stolen from https://michaelbh.com/blog/graalvm-and-rust-1/ - because I'm not that crazy.


```
Global variable _ZN12string_cache4atom12STRING_CACHE17h43d70dbc9890e871E is declared but not defined.
	at <llvm> null(Unknown)
```

ok, let's try again ...

```
ERROR: com.oracle.truffle.api.dsl.UnsupportedSpecializationException: Unexpected values provided for <signals.c:36:30>:36 LLVMSignalNodeGen#1: [13, 1], [Integer,Long]
org.graalvm.polyglot.PolyglotException: com.oracle.truffle.api.dsl.UnsupportedSpecializationException: Unexpected values provided for <signals.c:36:30>:36 LLVMSignalNodeGen#1: [13, 1], [Integer,Long]
	at com.oracle.truffle.llvm.runtime.nodes.intrinsics.c.LLVMSignalNodeGen.executeAndSpecialize(LLVMSignalNodeGen.java:76)
	at com.oracle.truffle.llvm.runtime.nodes.intrinsics.c.LLVMSignalNodeGen.executeGeneric(LLVMSignalNodeGen.java:52)
	at com.oracle.truffle.llvm.runtime.nodes.api.LLVMFrameNullerExpression.executeGeneric(LLVMFrameNullerExpression.java:75)
	at com.oracle.truffle.llvm.runtime.nodes.vars.LLVMWriteNodeFactory$LLVMWritePointerNodeGen.execute(LLVMWriteNodeFactory.java:714)
	at com.oracle.truffle.llvm.runtime.nodes.base.LLVMBasicBlockNode$InitializedBlock.execute(LLVMBasicBlockNode.java:154)
	at com.oracle.truffle.llvm.runtime.nodes.control.LLVMDispatchBasicBlockNode.executeGeneric(LLVMDispatchBasicBlockNode.java:81)
	at com.oracle.truffle.llvm.runtime.nodes.control.LLVMFunctionRootNode.executeGeneric(LLVMFunctionRootNode.java:75)
	at com.oracle.truffle.llvm.runtime.nodes.func.LLVMFunctionStartNode.execute(LLVMFunctionStartNode.java:87)
	at <llvm> main(src/libstd/sys/unix/mod.rs:89:0)
	at org.graalvm.polyglot.Value.execute(Value.java:367)
	at com.oracle.truffle.llvm.launcher.LLVMLauncher.execute(LLVMLauncher.java:219)
	at com.oracle.truffle.llvm.launcher.LLVMLauncher.launch(LLVMLauncher.java:63)
	at org.graalvm.launcher.AbstractLanguageLauncher.launch(AbstractLanguageLauncher.java:121)
	at org.graalvm.launcher.AbstractLanguageLauncher.launch(AbstractLanguageLauncher.java:70)
	at com.oracle.truffle.llvm.launcher.LLVMLauncher.main(LLVMLauncher.java:53)
```

maybe one more

```
ERROR: java.lang.IllegalStateException: Missing LLVM builtin: llvm.fshl.i64
org.graalvm.polyglot.PolyglotException: java.lang.IllegalStateException: Missing LLVM builtin: llvm.fshl.i64
	at com.oracle.truffle.llvm.runtime.nodes.intrinsics.llvm.x86.LLVMX86_MissingBuiltin.executeGeneric(LLVMX86_MissingBuiltin.java:48)
	at com.oracle.truffle.llvm.runtime.nodes.api.LLVMFrameNullerExpression.executeGeneric(LLVMFrameNullerExpression.java:75)
	at com.oracle.truffle.llvm.runtime.nodes.op.LLVMArithmeticNodeFactory$PointerToI64NodeGen.executeGeneric_generic1(LLVMArithmeticNodeFactory.java:506)
	at com.oracle.truffle.llvm.runtime.nodes.op.LLVMArithmeticNodeFactory$PointerToI64NodeGen.executeGeneric(LLVMArithmeticNodeFactory.java:479)
	at com.oracle.truffle.llvm.runtime.nodes.op.LLVMArithmeticNodeFactory$LLVMI64ArithmeticNodeGen.executeGeneric_generic3(LLVMArithmeticNodeFactory.java:22
```

ok, just have to re-implement some random function in LLVM assembly

```
define i64 @fshli64(i64 %a, i64 %b, i64 %s) #24 {
  ; Concatenates a and b and then shifts them left by s
  ; The upper 64 bits of this value are then returned
  ; Sign extend all vars to 128 bits
  %a_extended = zext i64 %a to i128
  %b_extended = zext i64 %b to i128
  %s_extended = zext i64 %s to i128
  ; Shift a left 64 bits to allow a to be concatenated
  ; into the upper 64 bits
  %a_shift = shl i128 %a_extended, 64
  ; Concatenate both ints
  %concat = and i128 %a_shift, %b_extended
  ; Do the actual shift
  %shift_cat = shl i128 %concat, %s_extended
  ; Shift right 64 bits to allow the upper 64 bits to be read
  %shift_back = lshr i128 %shift_cat, 64
  ; Truncate back to 64 bits leaving the upper 64
  %re = trunc i128 %shift_back to i64
  ret i64 %re
}
```
