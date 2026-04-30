# Thin wrapper around doccano's official backend image at the version
# this sample tracks. Pinning here (rather than in each lane script
# under keploy/integrations / keploy/enterprise) means a future
# doccano release that changes the bug-triggering shape is a one-line
# retag in this repo, not a hunt across the CI tree.
#
# Upstream tag: doccano/doccano:backend (the rolling backend tag)
# Source pin:   doccano/doccano @ v1.8.5
#               https://github.com/doccano/doccano/releases/tag/v1.8.5
#
# v1.8.5 was the version exercised on keploy/enterprise pipeline 3556
# (PR #1889) and pipeline 3572 (PR #1964 minimal repro) where the
# bug originally manifested.
FROM doccano/doccano:backend
