closure_lib/closure/bin/build/closurebuilder.py \
  --root=closure_lib/ \
  --root=javascript/ \
  --namespace="sandy.main" \
  --output_mode=compiled \
  --compiler_flags="--externs=javascript/externs.js" \
  --compiler_flags="--debug" \
  --compiler_flags="--formatting=PRETTY_PRINT" \
  --compiler_jar=closure_compiler/compiler.jar > javascript/compiled_main.js && \
closure_lib/closure/bin/build/closurebuilder.py \
  --root=closure_lib/ \
  --root=javascript/ \
  --namespace="sandy.demo" \
  --output_mode=compiled \
  --compiler_flags="--externs=javascript/externs.js" \
  --compiler_flags="--debug" \
  --compiler_flags="--formatting=PRETTY_PRINT" \
  --compiler_jar=closure_compiler/compiler.jar > javascript/compiled_demo.js && \
closure_lib/closure/bin/build/closurebuilder.py \
  --root=closure_lib/ \
  --root=javascript/ \
  --namespace="sandy.form" \
  --output_mode=compiled \
  --compiler_flags="--externs=javascript/externs.js" \
  --compiler_flags="--debug" \
  --compiler_flags="--formatting=PRETTY_PRINT" \
  --compiler_jar=closure_compiler/compiler.jar > javascript/compiled_form.js 

