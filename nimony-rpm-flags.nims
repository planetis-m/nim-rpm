import std/envvars

# Nim does not consume the distribution build flags from the environment by
# itself. Apply them to every host-Nim compilation in the Nimony source tree.
let rpmCflags = getEnv("CFLAGS")
let rpmLdflags = getEnv("LDFLAGS")

if rpmCflags.len > 0:
  switch("passC", rpmCflags)
if rpmLdflags.len > 0:
  switch("passL", rpmLdflags)
